"""
Page 2: Player Profiles, Career Analytics & Head-to-Head Comparison
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from cricbuzz_api import (
    search_player_data,
    fetch_player_info,
    fetch_player_batting_stats,
    fetch_player_bowling_stats
)

FEATURED_PLAYERS = {
    "🇮🇳 Virat Kohli": "1413",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Joe Root": "8019",
    "🇦🇺 Steve Smith": "2250",
    "🇮🇳 Rohit Sharma": "576",
    "🇮🇳 Jasprit Bumrah": "9311",
    "🇦🇺 Pat Cummins": "8095",
    "🇵🇰 Babar Azam": "9360",
    "🇳🇿 Kane Williamson": "6326",
    "🇦🇫 Rashid Khan": "10738"
}


def clean_html(raw_html):
    """Clean raw HTML breaks and tags from bio text."""
    if not raw_html:
        return "No biography available."
    clean_text = re.sub(r'<br\s*/?>', '\n\n', raw_html)
    clean_text = re.sub(r'</?b>', '**', clean_text)
    clean_text = re.sub(r'<.*?>', '', clean_text)
    return clean_text.strip()


def render_player_header(player_id, info):
    """Render player photo, key bio details, and ICC rankings."""
    c_img, c_details, c_rank = st.columns([1, 2.2, 1.3])

    # Player Headshot
    with c_img:
        face_id = info.get("faceImageId") or player_id
        img_url = f"https://images.cricbuzz.com/stats/img/faceImages/{face_id}.jpg"
        st.image(img_url, caption=info.get("name", "Player"), width=160)

    # Core Profile
    with c_details:
        st.markdown(f"## {info.get('fullName') or info.get('name', 'Player Profile')}")
        st.markdown(f"**National Team:** `{info.get('intlTeam', 'N/A')}` | **Role:** `{info.get('role', 'N/A')}`")
        st.markdown(f"🏏 **Batting Style:** {info.get('bat', 'N/A')}")
        st.markdown(f"🎯 **Bowling Style:** {info.get('bowl', 'N/A')}")
        st.markdown(f"🎂 **Born:** {info.get('DoB', 'N/A')} ({info.get('birthPlace', 'N/A')})")
        if info.get("height"):
            st.markdown(f"📏 **Height:** {info.get('height')}")

    # ICC Rankings
    with c_rank:
        st.markdown("#### 🏆 ICC Rankings")
        rankings = info.get("rankings", {})
        bat_rank = rankings.get("bat", {})
        bowl_rank = rankings.get("bowl", {})

        st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; border-left: 3px solid #FF9800;">
                <div><b>Batting Ranks:</b></div>
                <div style="font-size: 0.85rem; margin-top: 3px;">
                    Test: <b>#{bat_rank.get('testRank', bat_rank.get('testBestRank', '-'))}</b> | 
                    ODI: <b>#{bat_rank.get('odiRank', bat_rank.get('odiBestRank', '-'))}</b> | 
                    T20: <b>#{bat_rank.get('t20Rank', bat_rank.get('t20BestRank', '-'))}</b>
                </div>
                <div style="margin-top: 8px;"><b>Bowling Ranks:</b></div>
                <div style="font-size: 0.85rem; margin-top: 3px;">
                    Test: <b>#{bowl_rank.get('testRank', bowl_rank.get('testBestRank', '-'))}</b> | 
                    ODI: <b>#{bowl_rank.get('odiRank', bowl_rank.get('odiBestRank', '-'))}</b> | 
                    T20: <b>#{bowl_rank.get('t20Rank', bowl_rank.get('t20BestRank', '-'))}</b>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Teams Played
    teams = info.get("teams")
    if teams:
        st.markdown("##### 👕 Teams Represented")
        team_chips = [f"`{t.strip()}`" for t in teams.split(",") if t.strip()]
        st.markdown(" ".join(team_chips[:15]))


def render_batting_section(bat_df, player_name):
    """Render structured career batting statistics and comparison charts."""
    if bat_df.empty:
        st.info("No batting records found for this player.")
        return

    st.markdown("### 🏏 Career Batting Statistics")
    st.dataframe(bat_df, use_container_width=True)

    # Batting Visualizations
    formats = ["Test", "ODI", "T20", "IPL"]
    valid_formats = [f for f in formats if f in bat_df.columns]

    if valid_formats:
        c1, c2 = st.columns(2)

        # 1. Total Runs by Format
        with c1:
            if "Runs" in bat_df.index:
                runs_series = []
                for f in valid_formats:
                    raw_val = str(bat_df.loc["Runs", f]).replace(",", "")
                    try:
                        runs_series.append(float(raw_val))
                    except ValueError:
                        runs_series.append(0.0)

                chart_df = pd.DataFrame({"Format": valid_formats, "Runs": runs_series})
                fig_runs = px.bar(
                    chart_df,
                    x="Format",
                    y="Runs",
                    text="Runs",
                    color="Format",
                    title=f"🏏 Total Runs by Format - {player_name}",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_runs.update_traces(textposition='outside')
                fig_runs.update_layout(height=320, showlegend=False)
                st.plotly_chart(fig_runs, use_container_width=True)

        # 2. Centuries & Fifties
        with c2:
            if "100s" in bat_df.index and "50s" in bat_df.index:
                c_100s = []
                c_50s = []
                for f in valid_formats:
                    try:
                        c_100s.append(int(bat_df.loc["100s", f]))
                    except (ValueError, TypeError):
                        c_100s.append(0)
                    try:
                        c_50s.append(int(bat_df.loc["50s", f]))
                    except (ValueError, TypeError):
                        c_50s.append(0)

                milestone_df = pd.DataFrame({
                    "Format": valid_formats,
                    "Centuries (100s)": c_100s,
                    "Half-Centuries (50s)": c_50s
                })
                fig_milestones = px.bar(
                    milestone_df,
                    x="Format",
                    y=["Centuries (100s)", "Half-Centuries (50s)"],
                    barmode="group",
                    title="💯 100s and 50s by Format",
                    color_discrete_sequence=["#e63946", "#457b9d"]
                )
                fig_milestones.update_layout(height=320)
                st.plotly_chart(fig_milestones, use_container_width=True)


def render_bowling_section(bowl_df, player_name):
    """Render structured career bowling statistics and comparison charts."""
    if bowl_df.empty:
        st.info("No bowling records found for this player.")
        return

    st.markdown("### 🎯 Career Bowling Statistics")
    st.dataframe(bowl_df, use_container_width=True)

    formats = ["Test", "ODI", "T20", "IPL"]
    valid_formats = [f for f in formats if f in bowl_df.columns]

    if valid_formats and "Wickets" in bowl_df.index:
        c1, c2 = st.columns(2)

        # 1. Total Wickets
        with c1:
            wkts_series = []
            for f in valid_formats:
                raw_val = str(bowl_df.loc["Wickets", f]).replace(",", "")
                try:
                    wkts_series.append(float(raw_val))
                except ValueError:
                    wkts_series.append(0.0)

            chart_df = pd.DataFrame({"Format": valid_formats, "Wickets": wkts_series})
            fig_wkts = px.bar(
                chart_df,
                x="Format",
                y="Wickets",
                text="Wickets",
                color="Format",
                title=f"🎯 Total Wickets by Format - {player_name}",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_wkts.update_traces(textposition='outside')
            fig_wkts.update_layout(height=320, showlegend=False)
            st.plotly_chart(fig_wkts, use_container_width=True)

        # 2. Economy Rates
        with c2:
            if "Economy" in bowl_df.index:
                econ_series = []
                for f in valid_formats:
                    try:
                        econ_series.append(float(bowl_df.loc["Economy", f]))
                    except (ValueError, TypeError):
                        econ_series.append(0.0)

                econ_df = pd.DataFrame({"Format": valid_formats, "Economy": econ_series})
                fig_econ = px.line(
                    econ_df,
                    x="Format",
                    y="Economy",
                    markers=True,
                    title="📉 Bowling Economy Rate by Format",
                )
                fig_econ.update_layout(height=320)
                st.plotly_chart(fig_econ, use_container_width=True)


def render_recent_form(info):
    """Render recent match performance logs."""
    recent_bat = info.get("recentBatting", {})
    recent_bowl = info.get("recentBowling", {})

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 🏏 Recent Batting Performances")
        rows = recent_bat.get("rows", [])
        if rows:
            bat_logs = []
            for r in rows:
                vals = r.get("values", [])
                if len(vals) >= 4:
                    bat_logs.append({
                        "Score": vals[1],
                        "Opponent": vals[2],
                        "Format": vals[3],
                        "Date": vals[4] if len(vals) > 4 else "Recent"
                    })
            st.dataframe(pd.DataFrame(bat_logs), hide_index=True, use_container_width=True)
        else:
            st.caption("No recent batting logs available.")

    with c2:
        st.markdown("#### 🎯 Recent Bowling Spells")
        rows = recent_bowl.get("rows", [])
        if rows:
            bowl_logs = []
            for r in rows:
                vals = r.get("values", [])
                if len(vals) >= 4:
                    bowl_logs.append({
                        "Figures": vals[1],
                        "Opponent": vals[2],
                        "Format": vals[3],
                        "Date": vals[4] if len(vals) > 4 else "Recent"
                    })
            st.dataframe(pd.DataFrame(bowl_logs), hide_index=True, use_container_width=True)
        else:
            st.caption("No recent bowling spells available.")


def render_comparison_tool():
    """Head-to-head comparison tool for two players."""
    st.markdown("### ⚔️ Player Head-to-Head Comparison")
    st.write("Compare two cricket legends across Test, ODI, T20, and IPL formats.")

    col_p1, col_p2, col_fmt = st.columns([1.5, 1.5, 1])

    with col_p1:
        p1_query = st.text_input("Player 1", value="Virat Kohli", key="cmp_p1_input")
        p1_res = search_player_data(p1_query)
        if not p1_res.empty:
            p1_id = st.selectbox(
                "Select Player 1 Match",
                p1_res["id"],
                format_func=lambda i: f"{p1_res.loc[p1_res['id']==i, 'name'].values[0]} ({p1_res.loc[p1_res['id']==i, 'teamName'].values[0]})",
                key="cmp_p1_select"
            )
            p1_name = p1_res.loc[p1_res['id']==p1_id, 'name'].values[0]
        else:
            p1_id, p1_name = "1413", "Virat Kohli"

    with col_p2:
        p2_query = st.text_input("Player 2", value="Joe Root", key="cmp_p2_input")
        p2_res = search_player_data(p2_query)
        if not p2_res.empty:
            p2_id = st.selectbox(
                "Select Player 2 Match",
                p2_res["id"],
                format_func=lambda i: f"{p2_res.loc[p2_res['id']==i, 'name'].values[0]} ({p2_res.loc[p2_res['id']==i, 'teamName'].values[0]})",
                key="cmp_p2_select"
            )
            p2_name = p2_res.loc[p2_res['id']==p2_id, 'name'].values[0]
        else:
            p2_id, p2_name = "8019", "Joe Root"

    with col_fmt:
        comp_format = st.selectbox("Compare Format", ["Test", "ODI", "T20", "IPL"], index=0)

    if st.button("🚀 Run Comparison", use_container_width=True):
        with st.spinner("Crunching comparison data..."):
            p1_bat = fetch_player_batting_stats(p1_id)
            p2_bat = fetch_player_batting_stats(p2_id)
            p1_info = fetch_player_info(p1_id)
            p2_info = fetch_player_info(p2_id)

        # Profile Cards
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"#### 🛡️ {p1_name}")
            st.caption(f"Role: {p1_info.get('role', 'N/A')} | Country: {p1_info.get('intlTeam', 'N/A')}")
        with c2:
            st.markdown(f"#### ⚔️ {p2_name}")
            st.caption(f"Role: {p2_info.get('role', 'N/A')} | Country: {p2_info.get('intlTeam', 'N/A')}")

        st.markdown(f"#### 📊 {comp_format} Batting Head-to-Head")

        key_metrics = ["Matches", "Innings", "Runs", "Average", "SR", "100s", "50s", "Highest"]
        p1_vals = []
        p2_vals = []

        for m in key_metrics:
            v1 = p1_bat.loc[m, comp_format] if (not p1_bat.empty and m in p1_bat.index and comp_format in p1_bat.columns) else "-"
            v2 = p2_bat.loc[m, comp_format] if (not p2_bat.empty and m in p2_bat.index and comp_format in p2_bat.columns) else "-"
            p1_vals.append(v1)
            p2_vals.append(v2)

        cmp_table = pd.DataFrame({
            "Metric": key_metrics,
            f"{p1_name}": p1_vals,
            f"{p2_name}": p2_vals
        })
        st.table(cmp_table.set_index("Metric"))

        # Comparison Bar Chart
        chart_metrics = ["Runs", "100s", "50s"]
        c_p1_nums = []
        c_p2_nums = []
        for m in chart_metrics:
            try:
                c_p1_nums.append(float(str(p1_bat.loc[m, comp_format]).replace(",", "")))
            except Exception:
                c_p1_nums.append(0.0)
            try:
                c_p2_nums.append(float(str(p2_bat.loc[m, comp_format]).replace(",", "")))
            except Exception:
                c_p2_nums.append(0.0)

        fig_cmp = go.Figure(data=[
            go.Bar(name=p1_name, x=chart_metrics, y=c_p1_nums, marker_color="#1d3557"),
            go.Bar(name=p2_name, x=chart_metrics, y=c_p2_nums, marker_color="#e63946")
        ])
        fig_cmp.update_layout(
            barmode='group',
            title=f"{p1_name} vs {p2_name} in {comp_format} Cricket",
            height=340
        )
        st.plotly_chart(fig_cmp, use_container_width=True)


def app():
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="margin: 0; padding: 0;">👤 Player Profiles & Career Analytics</h1>
            <p style="color: #6c757d; margin-top: 5px; font-size: 1.05rem;">
                Explore ICC rankings, complete career batting & bowling records across formats, and head-to-head comparisons.
            </p>
        </div>
    """, unsafe_allow_html=True)

    main_tabs = st.tabs(["👤 Player Profile & Career Stats", "⚔️ Head-to-Head Comparison"])

    with main_tabs[0]:
        # Quick Search Chips
        st.markdown("**🌟 Quick Pick Popular Stars:**")
        chip_cols = st.columns(len(FEATURED_PLAYERS))
        selected_featured_id = None
        for col, (star_label, star_id) in zip(chip_cols, FEATURED_PLAYERS.items()):
            with col:
                if st.button(star_label, key=f"chip_{star_id}", use_container_width=True):
                    selected_featured_id = star_id

        # Search Bar
        search_query = st.text_input(
            "🔍 Search Player Name",
            placeholder="Type player name (e.g. Jasprit Bumrah, Travis Head, Ben Stokes)..."
        )

        player_id = None
        player_name = None

        if selected_featured_id:
            player_id = selected_featured_id
            player_name = [k for k, v in FEATURED_PLAYERS.items() if v == player_id][0]
        elif search_query.strip():
            with st.spinner("Searching players..."):
                search_results = search_player_data(search_query)

            if search_results.empty:
                st.warning(f"No players found matching '{search_query}'. Try another search.")
                return

            player_idx = st.selectbox(
                "Select Player",
                search_results.index,
                format_func=lambda i: f"{search_results.loc[i, 'name']} ({search_results.loc[i, 'teamName']})"
            )
            player_id = search_results.loc[player_idx, "id"]
            player_name = search_results.loc[player_idx, "name"]
        else:
            # Default to Virat Kohli so page is never empty
            player_id = "1413"
            player_name = "Virat Kohli"

        st.markdown("---")

        # Fetch Player Details
        with st.spinner("Fetching player profile..."):
            info = fetch_player_info(player_id)
            bat_df = fetch_player_batting_stats(player_id)
            bowl_df = fetch_player_bowling_stats(player_id)

        if not info:
            st.error("Failed to load player information. RapidAPI quota might be exhausted.")
            return

        # Render Header Profile
        render_player_header(player_id, info)

        st.markdown("---")

        # Sub-tabs for Batting, Bowling, Recent Form, Biography
        p_tabs = st.tabs(["🏏 Batting Stats", "🎯 Bowling Stats", "🔥 Recent Form", "📖 Career Story"])

        with p_tabs[0]:
            render_batting_section(bat_df, player_name)

        with p_tabs[1]:
            render_bowling_section(bowl_df, player_name)

        with p_tabs[2]:
            render_recent_form(info)

        with p_tabs[3]:
            st.markdown("### 📖 Biography & Career Journey")
            bio_text = clean_html(info.get("bio", ""))
            st.markdown(bio_text)

    with main_tabs[1]:
        render_comparison_tool()
