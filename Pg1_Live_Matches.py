"""
Page 1: Live & Recent Matches Dashboard
Comprehensive cricket match center with tailored 4-innings Test match support.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cricbuzz_api import (
    fetch_matches_data,
    fetch_scorecard_data,
    format_overs
)


def render_innings_charts(inng):
    """Render interactive Plotly visual charts for a given innings."""
    bat_df = inng.get("batting_df")
    bowl_df = inng.get("bowling_df")

    col_chart1, col_chart2 = st.columns(2)

    # 1. Batting Contribution Bar Chart
    with col_chart1:
        if bat_df is not None and not bat_df.empty:
            bat_active = bat_df[bat_df["Balls"] > 0].copy()
            if not bat_active.empty:
                max_r = float(bat_active["Runs"].max()) if not bat_active["Runs"].empty else 10.0
                fig_bat = px.bar(
                    bat_active,
                    x="Runs",
                    y="Batter",
                    orientation="h",
                    color="Runs",
                    color_continuous_scale="Viridis",
                    hover_data=["Balls", "4s", "6s", "SR", "Dismissal"],
                    title=f"🏏 Batting Contributions - {inng.get('bat_team_name')}"
                )
                fig_bat.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    xaxis=dict(rangemode="tozero", range=[0, max(10.0, max_r * 1.15)], title="Runs Scored"),
                    margin=dict(l=10, r=10, t=40, b=10),
                    height=320,
                    showlegend=False
                )
                st.plotly_chart(fig_bat, use_container_width=True)

    # 2. Bowling Figures Bar Chart
    with col_chart2:
        if bowl_df is not None and not bowl_df.empty:
            bowl_active = bowl_df[bowl_df["Runs"] > 0].copy()
            if not bowl_active.empty:
                max_w = float(bowl_active["Wickets"].max()) if not bowl_active["Wickets"].empty else 3.0
                fig_bowl = px.bar(
                    bowl_active,
                    x="Bowler",
                    y="Wickets",
                    color="Economy",
                    color_continuous_scale="Reds",
                    hover_data=["Overs", "Maidens", "Runs", "Economy"],
                    title="🎯 Bowling Wickets & Economy"
                )
                fig_bowl.update_layout(
                    margin=dict(l=10, r=10, t=40, b=10),
                    height=320,
                    yaxis=dict(rangemode="tozero", range=[0, max(3.0, max_w + 1.0)], title="Wickets Taken")
                )
                st.plotly_chart(fig_bowl, use_container_width=True)


def display_innings_tab(inng, index, total_innings):
    """Display scorecard details for one innings."""
    bat_team = inng.get("bat_team_name")
    score = inng.get("score", 0)
    wickets = inng.get("wickets", 0)
    overs = inng.get("overs", "0.0")
    run_rate = inng.get("run_rate", 0.0)
    declared = inng.get("is_declared", False)
    follow_on = inng.get("is_follow_on", False)
    extras = inng.get("extras", {})

    # Innings Header Badges
    status_tags = []
    if declared:
        status_tags.append("🚨 Declared")
    if follow_on:
        status_tags.append("🔁 Follow-on Enforced")

    tag_str = " | ".join(status_tags)
    if tag_str:
        st.markdown(f"**Special Status:** `{tag_str}`")

    # Metrics Summary Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Total Score", f"{score}/{wickets}")
    with m2:
        st.metric("Overs", f"{overs} ov")
    with m3:
        st.metric("Run Rate", f"{run_rate:.2f}" if isinstance(run_rate, (int, float)) else str(run_rate))
    with m4:
        st.metric("Extras Conceded", str(extras.get("total", 0)))
    with m5:
        st.metric("Innings Number", f"{index} of {total_innings}")

    # Batting Scorecard Table
    st.markdown("#### 🏏 Batting Scorecard")
    bat_df = inng.get("batting_df")
    if bat_df is not None and not bat_df.empty:
        # Format highlight markers for 50s and 100s
        styled_bat = bat_df.copy()
        styled_bat["Runs"] = styled_bat["Runs"].apply(
            lambda r: f"💯 {r}" if r >= 100 else (f"⭐ {r}" if r >= 50 else str(r))
        )
        st.dataframe(
            styled_bat,
            column_config={
                "Batter": st.column_config.TextColumn("Batter", width="medium"),
                "Dismissal": st.column_config.TextColumn("Dismissal Info", width="large"),
                "Runs": st.column_config.TextColumn("R"),
                "Balls": st.column_config.NumberColumn("B"),
                "4s": st.column_config.NumberColumn("4s"),
                "6s": st.column_config.NumberColumn("6s"),
                "SR": st.column_config.NumberColumn("SR", format="%.2f"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Batting information not yet recorded for this innings.")

    # Bowling Scorecard Table
    st.markdown("#### 🎯 Bowling Figures")
    bowl_df = inng.get("bowling_df")
    if bowl_df is not None and not bowl_df.empty:
        st.dataframe(
            bowl_df,
            column_config={
                "Bowler": st.column_config.TextColumn("Bowler", width="medium"),
                "Overs": st.column_config.TextColumn("O"),
                "Maidens": st.column_config.NumberColumn("M"),
                "Runs": st.column_config.NumberColumn("R"),
                "Wickets": st.column_config.NumberColumn("W"),
                "Economy": st.column_config.NumberColumn("ECON", format="%.2f"),
                "Dots": st.column_config.NumberColumn("Dots"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Bowling figures not yet recorded for this innings.")

    # Extras & Fall of Wickets
    with st.expander("📦 Extras Breakdown & Fall of Wickets (FOW)", expanded=False):
        c_ex, c_fow = st.columns([1, 2])
        with c_ex:
            st.markdown("**Extras Breakdown**")
            st.write(f"- **Byes:** {extras.get('byes', 0)}")
            st.write(f"- **Leg Byes:** {extras.get('legbyes', 0)}")
            st.write(f"- **Wides:** {extras.get('wides', 0)}")
            st.write(f"- **No Balls:** {extras.get('noballs', 0)}")
            st.write(f"- **Penalty:** {extras.get('penalty', 0)}")
            st.write(f"**Total Extras:** `{extras.get('total', 0)}`")

        with c_fow:
            st.markdown("**Fall of Wickets**")
            fow_df = inng.get("fow_df")
            if fow_df is not None and not fow_df.empty:
                st.dataframe(fow_df, hide_index=True, use_container_width=True)
            else:
                st.caption("No fall of wickets data available for this innings.")

    # Partnerships
    part_df = inng.get("partnerships_df")
    if part_df is not None and not part_df.empty:
        with st.expander("🤝 Batting Partnerships", expanded=False):
            st.dataframe(part_df, hide_index=True, use_container_width=True)

    # Interactive Plots
    render_innings_charts(inng)


def app():
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="margin: 0; padding: 0;">📡 Live & Recent Cricket Matches</h1>
            <p style="color: #6c757d; margin-top: 5px; font-size: 1.05rem;">
                Real-time scores, multi-innings Test match analysis, and interactive full scorecards.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Top Filter Controls
    top_col1, top_col2, top_col3, top_col4 = st.columns([1.5, 1.2, 2, 0.8])

    with top_col1:
        match_category = st.radio(
            "Category",
            ["🔴 Live", "🏁 Recent", "📅 Upcoming"],
            index=1,  # Default to Recent to guarantee completed Test matches with full 4 innings are viewable
            horizontal=True
        )
        cat_key = "live" if "Live" in match_category else ("recent" if "Recent" in match_category else "upcoming")

    with top_col2:
        format_filter = st.selectbox(
            "Format Filter",
            ["All Formats", "TEST", "ODI", "T20"],
            index=0
        )

    with top_col3:
        search_query = st.text_input("🔍 Search Teams or Series", placeholder="e.g. India, Australia, Ranji, Ashes...")

    with top_col4:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Fetch Data
    with st.spinner(f"Loading {cat_key} matches..."):
        matches_df = fetch_matches_data(category=cat_key)

    if matches_df.empty:
        st.warning(f"No {cat_key} matches found. Try switching category (e.g. check Recent Matches for full Test matches).")
        return

    # Apply Filters
    filtered_df = matches_df.copy()
    if format_filter != "All Formats":
        filtered_df = filtered_df[filtered_df["match_format"] == format_filter]

    if search_query.strip():
        q = search_query.strip().lower()
        filtered_df = filtered_df[
            filtered_df["team1_name"].str.lower().str.contains(q) |
            filtered_df["team2_name"].str.lower().str.contains(q) |
            filtered_df["series_name"].str.lower().str.contains(q) |
            filtered_df["venue"].str.lower().str.contains(q)
        ]

    if filtered_df.empty:
        st.info(f"No matches match the selected filter `{format_filter}` or query `{search_query}`. Try resetting filters.")
        return

    # Match Selector
    st.markdown("### Select Match to Inspect")

    def format_match_label(idx):
        row = filtered_df.loc[idx]
        fmt_badge = f"[{row['match_format']}]"
        test_indicator = " (4 Innings)" if row['is_test'] else ""
        return f"{fmt_badge}{test_indicator} {row['team1_name']} vs {row['team2_name']} | {row['series_name']} | {row['status'] or row['state']}"

    selected_index = st.selectbox(
        "Available Matches",
        filtered_df.index,
        format_func=format_match_label,
        label_visibility="collapsed"
    )

    selected_match = filtered_df.loc[selected_index]
    is_test_match = bool(selected_match.get("is_test", False))
    match_id = selected_match["match_id"]

    st.markdown("---")

    # Match Overview Header Card
    with st.container():
        # Badge line
        fmt_badge_color = "#b22222" if is_test_match else ("#0077b6" if selected_match["match_format"] == "ODI" else "#6a0dad")
        test_badge_html = f"""
            <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 8px;">
                <span style="background-color: {fmt_badge_color}; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.85rem;">
                    {selected_match['match_format']} MATCH
                </span>
                {'<span style="background-color: #2e7d32; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.85rem;">🏏 4-Innings Test Architecture</span>' if is_test_match else ''}
                <span style="color: #6c757d; font-size: 0.9rem;">📍 {selected_match['venue']} | 🗓️ {selected_match['start_date']}</span>
            </div>
        """
        st.markdown(test_badge_html, unsafe_allow_html=True)
        st.subheader(f"{selected_match['series_name']} — {selected_match['match_desc']}")

        # Scores Display
        c_t1, c_t2 = st.columns(2)

        with c_t1:
            st.markdown(f"### 🛡️ {selected_match['team1_name']} ({selected_match['team1_short']})")
            if is_test_match:
                t1_i1 = selected_match.get("team1_inngs1", {})
                t1_i2 = selected_match.get("team1_inngs2", {})
                s1_str = f"{t1_i1.get('runs', 0)}/{t1_i1.get('wickets', 0)} ({format_overs(t1_i1.get('overs'))} ov)" if t1_i1 else "Yet to bat"
                s2_str = f"{t1_i2.get('runs', 0)}/{t1_i2.get('wickets', 0)} ({format_overs(t1_i2.get('overs'))} ov)" if t1_i2 else "Yet to bat"
                
                st.markdown(f"""
                    <div style="background-color: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; border-left: 4px solid #4CAF50;">
                        <div><b>1st Innings:</b> {s1_str}</div>
                        <div style="margin-top: 4px;"><b>2nd Innings:</b> {s2_str}</div>
                        <div style="margin-top: 6px; font-size: 1.15rem; font-weight: bold; color: #4CAF50;">Combined: {selected_match['team1_score']}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.metric(
                    label=selected_match["team1_name"],
                    value=selected_match["team1_score"]
                )

        with c_t2:
            st.markdown(f"### ⚔️ {selected_match['team2_name']} ({selected_match['team2_short']})")
            if is_test_match:
                t2_i1 = selected_match.get("team2_inngs1", {})
                t2_i2 = selected_match.get("team2_inngs2", {})
                s1_str = f"{t2_i1.get('runs', 0)}/{t2_i1.get('wickets', 0)} ({format_overs(t2_i1.get('overs'))} ov)" if t2_i1 else "Yet to bat"
                s2_str = f"{t2_i2.get('runs', 0)}/{t2_i2.get('wickets', 0)} ({format_overs(t2_i2.get('overs'))} ov)" if t2_i2 else "Yet to bat"

                st.markdown(f"""
                    <div style="background-color: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; border-left: 4px solid #2196F3;">
                        <div><b>1st Innings:</b> {s1_str}</div>
                        <div style="margin-top: 4px;"><b>2nd Innings:</b> {s2_str}</div>
                        <div style="margin-top: 6px; font-size: 1.15rem; font-weight: bold; color: #2196F3;">Combined: {selected_match['team2_score']}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.metric(
                    label=selected_match["team2_name"],
                    value=selected_match["team2_score"]
                )

        # Status / Match Result Alert
        status_text = selected_match.get("status") or selected_match.get("state")
        if status_text:
            st.info(f"📢 **Status:** {status_text}")

    st.markdown("---")

    # Detailed Scorecard Section
    st.subheader("📋 Match Scorecard & In-Depth Analysis")

    with st.spinner("Fetching full scorecard..."):
        scorecard_res = fetch_scorecard_data(match_id)

    if not scorecard_res.get("success"):
        st.warning(f"Unable to load scorecard: {scorecard_res.get('error', 'Scorecard data not available yet')}")
        return

    innings_list = scorecard_res.get("innings", [])
    if not innings_list:
        st.info("No innings have been recorded yet for this match.")
        return

    # In Test matches, display dynamic 1 to 4 Innings Tabs
    if is_test_match:
        st.markdown(f"""
            > **ℹ️ Test Match Scorecard ({len(innings_list)} of up to 4 Innings Completed):**  
            > Below you will find individual tabs for every innings played in this Test match. 
            > Click through each tab to review full batting figures, bowling spells, extras, fall of wickets, and partnerships.
        """)

    # Build Tab Labels dynamically
    tab_titles = []
    for idx, inng in enumerate(innings_list, 1):
        team_label = inng.get("bat_team_name")
        score_val = inng.get("score", 0)
        wkts_val = inng.get("wickets", 0)
        overs_val = inng.get("overs", "0.0")
        dec_tag = " d" if inng.get("is_declared") else ""
        tab_titles.append(f"Innings {idx}: {team_label} ({score_val}/{wkts_val}{dec_tag})")

    tabs = st.tabs(tab_titles)
    for idx, (tab, inng) in enumerate(zip(tabs, innings_list), 1):
        with tab:
            display_innings_tab(inng, idx, len(innings_list))
