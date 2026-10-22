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
    fetch_player_bowling_stats,
    fetch_player_image_bytes,
    get_player_image_url,
    get_team_logo_url,
    fetch_team_logo_bytes
)

FEATURED_PLAYERS = {
    "🇮🇳 Virat Kohli": "1413",
    "🇦🇺 Usman Khawaja": "6635",
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
    """Render player photo, key bio details, and ICC rankings using native Streamlit elements."""
    c_img, c_details, c_rank = st.columns([1, 2.2, 1.3])

    # Player Headshot from Cricbuzz CDN
    with c_img:
        p_name = info.get("name", "Player")
        face_id = info.get("faceImageId")
        img_bytes = fetch_player_image_bytes(p_name, face_id, player_id=player_id)
        img_url = get_player_image_url(p_name, face_id)

        if img_bytes:
            st.image(img_bytes, caption=p_name, width=160)
        elif img_url:
            st.image(img_url, caption=p_name, width=160)
        else:
            st.markdown("### 👤")
            st.caption(p_name)

    # Core Profile
    with c_details:
        st.markdown(f"## {info.get('fullName') or info.get('name', 'Player Profile')}")
        intl_team = info.get('intlTeam', 'N/A')
        team_logo = fetch_team_logo_bytes(intl_team) or get_team_logo_url(intl_team)
        col_tl, col_ti = st.columns([1, 6])
        with col_tl:
            if team_logo:
                st.image(team_logo, width=44)
        with col_ti:
            st.markdown(f"**National Team:** `{intl_team}`")
            st.caption(f"Role: {info.get('role', 'N/A')}")
        st.markdown(f"🏏 **Batting Style:** {info.get('bat', 'N/A')}")
        st.markdown(f"🎯 **Bowling Style:** {info.get('bowl', 'N/A')}")
        st.markdown(f"🎂 **Born:** {info.get('DoB', 'N/A')} ({info.get('birthPlace', 'N/A')})")
        if info.get("height"):
            st.markdown(f"📏 **Height:** {info.get('height')}")

    # ICC Rankings
    with c_rank:
        rankings = info.get("rankings", {})
        bat_rank = rankings.get("bat", {})
        bowl_rank = rankings.get("bowl", {})

        with st.container(border=True):
            st.markdown("🏆 **ICC Rankings**")
            st.markdown(f"**Batting:** Test `#{bat_rank.get('testRank', bat_rank.get('testBestRank', '-'))}` | ODI `#{bat_rank.get('odiRank', bat_rank.get('odiBestRank', '-'))}` | T20 `#{bat_rank.get('t20Rank', bat_rank.get('t20BestRank', '-'))}`")
            st.markdown(f"**Bowling:** Test `#{bowl_rank.get('testRank', bowl_rank.get('testBestRank', '-'))}` | ODI `#{bowl_rank.get('odiRank', bowl_rank.get('odiBestRank', '-'))}` | T20 `#{bowl_rank.get('t20Rank', bowl_rank.get('t20BestRank', '-'))}`")

    # Teams Played
    teams = info.get("teams")
    if teams:
        st.markdown("##### 👕 Teams Represented")
        team_chips = [f"`{t.strip()}`" for t in teams.split(",") if t.strip()]
        st.markdown(" ".join(team_chips[:15]))


def render_batting_section(bat_df, player_name):
    """
    Render structured career batting statistics and comparison charts:
    - Separate Runs Chart
    - Clubbed 100s and 50s Chart
    All with base value starting at zero and no negative axes.
    """
    if bat_df.empty:
        st.info("No batting records found for this player.")
        return

    st.markdown("### 🏏 Career Batting Statistics")
    st.dataframe(bat_df, use_container_width=True)

    # Formats to display
    formats = ["Test", "ODI", "T20", "IPL"]
    valid_formats = [f for f in formats if f in bat_df.columns]

    if not valid_formats:
        return

    st.markdown("---")
    st.markdown("### 📊 Career Batting Visualizations")

    # 1. SEPARATE CAREER RUNS CHART
    if "Runs" in bat_df.index:
        runs_series = []
        for f in valid_formats:
            raw_val = str(bat_df.loc["Runs", f]).replace(",", "")
            try:
                val = max(0.0, float(raw_val))
            except ValueError:
                val = 0.0
            runs_series.append(val)

        chart_runs_df = pd.DataFrame({"Format": valid_formats, "Runs": runs_series})
        max_runs = max(runs_series) if runs_series else 100.0

        fig_runs = px.bar(
            chart_runs_df,
            x="Format",
            y="Runs",
            text="Runs",
            color="Format",
            title=f"🏏 Total Career Runs by Format - {player_name}",
            color_discrete_sequence=["#2a9d8f", "#264653", "#e76f51", "#f4a261"]
        )
        fig_runs.update_traces(textposition='outside', texttemplate='%{text:,.0f}')
        fig_runs.update_layout(
            height=340,
            showlegend=False,
            yaxis=dict(
                rangemode="tozero",
                range=[0, max_runs * 1.18 if max_runs > 0 else 100.0],
                title="Total Runs"
            ),
            xaxis=dict(title="Format"),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_runs, use_container_width=True)

    # 2. CLUBBED 100s AND 50s CHART
    if "100s" in bat_df.index and "50s" in bat_df.index:
        c_100s = []
        c_50s = []
        for f in valid_formats:
            try:
                c_100s.append(max(0, int(bat_df.loc["100s", f])))
            except (ValueError, TypeError):
                c_100s.append(0)
            try:
                c_50s.append(max(0, int(bat_df.loc["50s", f])))
            except (ValueError, TypeError):
                c_50s.append(0)

        milestone_df = pd.DataFrame({
            "Format": valid_formats,
            "Centuries (100s)": c_100s,
            "Half-Centuries (50s)": c_50s
        })
        max_m = max(max(c_100s), max(c_50s)) if (c_100s and c_50s) else 5

        fig_milestones = px.bar(
            milestone_df,
            x="Format",
            y=["Centuries (100s)", "Half-Centuries (50s)"],
            barmode="group",
            title=f"💯 Centuries (100s) & ⭐ Half-Centuries (50s) by Format - {player_name}",
            color_discrete_sequence=["#d90429", "#f77f00"]
        )
        fig_milestones.update_traces(textposition='outside')
        fig_milestones.update_layout(
            height=340,
            yaxis=dict(
                rangemode="tozero",
                range=[0, max(5, int(max_m * 1.25))],
                title="Milestone Count"
            ),
            xaxis=dict(title="Format"),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_milestones, use_container_width=True)


def render_bowling_section(bowl_df, player_name):
    """
    Render structured career bowling statistics and comparison charts.
    All charts guaranteed base value starting at zero with no negative axes.
    """
    if bowl_df.empty:
        st.info("No bowling records found for this player.")
        return

    st.markdown("### 🎯 Career Bowling Statistics")
    st.dataframe(bowl_df, use_container_width=True)

    formats = ["Test", "ODI", "T20", "IPL"]
    valid_formats = [f for f in formats if f in bowl_df.columns]

    if valid_formats and "Wickets" in bowl_df.index:
        c1, c2 = st.columns(2)

        # 1. Total Wickets Chart
        with c1:
            wkts_series = []
            for f in valid_formats:
                raw_val = str(bowl_df.loc["Wickets", f]).replace(",", "")
                try:
                    wkts_series.append(max(0.0, float(raw_val)))
                except ValueError:
                    wkts_series.append(0.0)

            max_wkts = max(wkts_series) if wkts_series else 10.0
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
            fig_wkts.update_traces(textposition='outside', texttemplate='%{text:,.0f}')
            fig_wkts.update_layout(
                height=340,
                showlegend=False,
                yaxis=dict(
                    rangemode="tozero",
                    range=[0, max(5.0, max_wkts * 1.2)],
                    title="Wickets Taken"
                ),
                xaxis=dict(title="Format"),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_wkts, use_container_width=True)

        # 2. Economy Rates Chart
        with c2:
            if "Economy" in bowl_df.index:
                econ_series = []
                for f in valid_formats:
                    try:
                        econ_series.append(max(0.0, float(bowl_df.loc["Economy", f])))
                    except (ValueError, TypeError):
                        econ_series.append(0.0)

                max_econ = max(econ_series) if econ_series else 6.0
                econ_df = pd.DataFrame({"Format": valid_formats, "Economy": econ_series})
                fig_econ = px.bar(
                    econ_df,
                    x="Format",
                    y="Economy",
                    text="Economy",
                    color="Format",
                    title=f"📉 Bowling Economy Rate by Format - {player_name}",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                fig_econ.update_traces(textposition='outside', texttemplate='%{text:.2f}')
                fig_econ.update_layout(
                    height=340,
                    showlegend=False,
                    yaxis=dict(
                        rangemode="tozero",
                        range=[0, max(6.0, max_econ * 1.25)],
                        title="Economy (Runs / Over)"
                    ),
                    xaxis=dict(title="Format"),
                    margin=dict(l=20, r=20, t=50, b=20)
                )
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
    """Head-to-head comparison tool for two players with separate runs and clubbed 100s/50s charts."""
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

        # Profile Cards with Headshots & Country Logos
        c1, c2 = st.columns(2)
        with c1:
            p1_face = p1_info.get("faceImageId")
            p1_img = fetch_player_image_bytes(p1_name, p1_face, player_id=p1_id) or get_player_image_url(p1_name, p1_face)
            p1_country = p1_info.get('intlTeam', '')
            p1_tlogo = fetch_team_logo_bytes(p1_country) or get_team_logo_url(p1_country)

            cp1_img, cp1_logo = st.columns([2, 1])
            with cp1_img:
                if p1_img:
                    st.image(p1_img, width=120)
            with cp1_logo:
                if p1_tlogo:
                    st.image(p1_tlogo, width=54)

            st.markdown(f"#### 🛡️ {p1_name}")
            st.caption(f"Role: {p1_info.get('role', 'N/A')} | Country: {p1_country or 'N/A'}")

        with c2:
            p2_face = p2_info.get("faceImageId")
            p2_img = fetch_player_image_bytes(p2_name, p2_face, player_id=p2_id) or get_player_image_url(p2_name, p2_face)
            p2_country = p2_info.get('intlTeam', '')
            p2_tlogo = fetch_team_logo_bytes(p2_country) or get_team_logo_url(p2_country)

            cp2_img, cp2_logo = st.columns([2, 1])
            with cp2_img:
                if p2_img:
                    st.image(p2_img, width=120)
            with cp2_logo:
                if p2_tlogo:
                    st.image(p2_tlogo, width=54)

            st.markdown(f"#### ⚔️ {p2_name}")
            st.caption(f"Role: {p2_info.get('role', 'N/A')} | Country: {p2_country or 'N/A'}")

        st.markdown(f"#### 📊 {comp_format} Batting Head-to-Head Table")

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

        # Visual Comparison Charts: Runs SEPARATE and 100s/50s CLUBBED
        try:
            p1_runs = max(0.0, float(str(p1_bat.loc["Runs", comp_format]).replace(",", "")))
        except Exception:
            p1_runs = 0.0
        try:
            p2_runs = max(0.0, float(str(p2_bat.loc["Runs", comp_format]).replace(",", "")))
        except Exception:
            p2_runs = 0.0

        try:
            p1_100s = max(0, int(p1_bat.loc["100s", comp_format]))
        except Exception:
            p1_100s = 0
        try:
            p2_100s = max(0, int(p2_bat.loc["100s", comp_format]))
        except Exception:
            p2_100s = 0

        try:
            p1_50s = max(0, int(p1_bat.loc["50s", comp_format]))
        except Exception:
            p1_50s = 0
        try:
            p2_50s = max(0, int(p2_bat.loc["50s", comp_format]))
        except Exception:
            p2_50s = 0

        col_cmp_runs, col_cmp_milestones = st.columns(2)

        # 1. SEPARATE COMPARISON RUNS CHART
        with col_cmp_runs:
            fig_cmp_runs = go.Figure(data=[
                go.Bar(name=p1_name, x=[f"{comp_format} Runs"], y=[p1_runs], text=[f"{p1_runs:,.0f}"], textposition='outside', marker_color="#1d3557"),
                go.Bar(name=p2_name, x=[f"{comp_format} Runs"], y=[p2_runs], text=[f"{p2_runs:,.0f}"], textposition='outside', marker_color="#e63946")
            ])
            max_cmp_runs = max(p1_runs, p2_runs, 10.0)
            fig_cmp_runs.update_layout(
                barmode='group',
                title=f"🏏 Total {comp_format} Runs: {p1_name} vs {p2_name}",
                height=350,
                yaxis=dict(rangemode="tozero", range=[0, max_cmp_runs * 1.2], title="Runs Scored"),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_cmp_runs, use_container_width=True)

        # 2. CLUBBED COMPARISON 100s & 50s CHART
        with col_cmp_milestones:
            fig_cmp_milestones = go.Figure(data=[
                go.Bar(name=p1_name, x=["100s", "50s"], y=[p1_100s, p1_50s], text=[p1_100s, p1_50s], textposition='outside', marker_color="#1d3557"),
                go.Bar(name=p2_name, x=["100s", "50s"], y=[p2_100s, p2_50s], text=[p2_100s, p2_50s], textposition='outside', marker_color="#e63946")
            ])
            max_cmp_m = max(p1_100s, p2_100s, p1_50s, p2_50s, 5)
            fig_cmp_milestones.update_layout(
                barmode='group',
                title=f"💯 100s & ⭐ 50s: {p1_name} vs {p2_name} ({comp_format})",
                height=350,
                yaxis=dict(rangemode="tozero", range=[0, max_cmp_m * 1.25], title="Milestone Count"),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_cmp_milestones, use_container_width=True)


def app():
    st.caption("Explore ICC rankings, complete career batting & bowling records across formats, and head-to-head comparisons.")

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
            placeholder="Type player name (e.g. Usman Khawaja, Jasprit Bumrah, Travis Head, Ben Stokes)..."
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
