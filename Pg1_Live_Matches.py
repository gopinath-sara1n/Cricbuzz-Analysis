import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Live Matches", page_icon="📡", layout="wide")
# =======================
# CRICKET_OVERS FUNCTION
# =======================
def cricket_overs(over):
    try:
        over = float(over)
        whole = int(over)
        ball = int(round((over - whole)*10))
        if ball >= 6:
            whole += 1
            ball = 0
        return f"{whole}.{ball}" if ball > 0 else str(whole)
    except:
        return "Not Started"

# =======================
# FETCH MATCH LIST DATA 
# =======================
@st.cache_data
def fetch_matches():
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    headers = {
        "x-rapidapi-key": "cd436a9136msh7134d9e6d53e7a4p1ee911jsn476d453f0ea8", 
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    matches = []
    for type_match in data.get("typeMatches", []):
        match_type = type_match.get("matchType")
        for series_match in type_match.get("seriesMatches", []):
            series = series_match.get("seriesAdWrapper", {})
            series_name = series.get("seriesName")
            for match in series.get("matches", []):
                info = match.get("matchInfo", {})
                match_Id = info.get("matchId")
                match_Desc = info.get("matchDesc")
                match_Format = info.get("matchFormat")
                start_Date = info.get("startDate")
                state = info.get("state")
                status = info.get("status")
                team1 = info.get("team1", {})
                team2 = info.get("team2", {})
                venue_Info = info.get("venueInfo", {})
                ground = venue_Info.get("ground")
                matchScore = match.get("matchScore", {})
                team1Score = matchScore.get("team1Score", {}).get("inngs1", {})
                team2Score = matchScore.get("team2Score", {}).get("inngs1", {})

                matches.append({
                    "match_type": match_type,
                    "series_name": series_name,
                    "match_Id": match_Id,
                    "match_Desc": match_Desc,
                    "match_Format": match_Format,
                    "start_Date": pd.to_datetime(pd.to_numeric(start_Date), unit="ms"),
                    "state": state,
                    "status": status,
                    "team1_Name": team1.get("teamName"),
                    "team1_runs": team1Score.get("runs") or 0,
                    "team1_wickets": team1Score.get("wickets") or 0,
                    "team1_overs": cricket_overs(team1Score.get("overs")) or 0,
                    "team2_Name": team2.get("teamName"),
                    "team2_runs": team2Score.get("runs") or 0,
                    "team2_wickets": team2Score.get("wickets") or 0,
                    "team2_overs": cricket_overs(team2Score.get("overs")) or 0,
                    "ground": ground
                })
    return pd.DataFrame(matches)

# =======================
# FETCH SCORECARD FOR SELECTED MATCH 
# =======================
def fetch_scorecard(m_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{m_id}/scard"
    headers = {
        "x-rapidapi-key": "cd436a9136msh7134d9e6d53e7a4p1ee911jsn476d453f0ea8", 
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    innings1_bat, innings1_bowl, innings2_bat, innings2_bowl = [], [], [], []

    for inningsid in data.get("scorecard", []):
        innings_id = inningsid.get("inningsid")

        # Batsmen
        for batter in inningsid.get("batsman", []):
            batter_data = {
                "name": batter.get("name"),
                "runs": batter.get("runs"),
                "balls": batter.get("balls"),
                "fours": batter.get("fours"),
                "sixes": batter.get("sixes"),
                "strike_rate": batter.get("strkrate"),
                "status": batter.get("outdec") or "not played"
            }
            if innings_id == 1:
                innings1_bat.append(batter_data)
            else:
                innings2_bat.append(batter_data)

        # Bowlers
        for bowler in inningsid.get("bowler", []):
            bowler_data = {
                "name": bowler.get("name"),
                "overs": bowler.get("overs"),
                "maidens": bowler.get("maidens"),
                "runs": bowler.get("runs"),
                "wickets": bowler.get("wickets"),
                "economy": bowler.get("economy")
            }
            if innings_id == 1:
                innings1_bowl.append(bowler_data)
            else:
                innings2_bowl.append(bowler_data)

  
    df1 = pd.DataFrame(innings1_bat)
    df2 = pd.DataFrame(innings1_bowl)
    df3 = pd.DataFrame(innings2_bat)
    df4 = pd.DataFrame(innings2_bowl)
    return df1, df2, df3, df4
    

# =======================
# STREAMLIT UI
# =======================
def app():
    st.title("🏏 Live Cricket Score Dashboard")

    matches_df = fetch_matches()

    if matches_df.empty:
        st.warning("No live matches available right now.")
    else:
        # Dropdown to select match
        selected_index = st.selectbox(
            "Select a match:",
            matches_df.index,
            format_func=lambda i: f"{matches_df.loc[i, 'team1_Name']} vs {matches_df.loc[i, 'team2_Name']} | {matches_df.loc[i, 'match_type']} {matches_df.loc[i, 'match_Format']}| {matches_df.loc[i, 'state']}"
        )
        selected_match = matches_df.loc[selected_index]

        # Display match info
        st.subheader(f"{selected_match['team1_Name']} vs {selected_match['team2_Name']}")
        st.write(f"**Series:** {selected_match['series_name']}")
        st.write(f"**Match:** {selected_match['match_Desc']}")
        st.write(f"**Format:** {selected_match['match_Format']}")
        st.write(f"**Venue:** {selected_match['ground']}")
        st.write(f"**Status:** {selected_match['status']}")
        #st.write(f"**Match Id:** {selected_match['match_Id']}")
        #st.write(selected_index)

        # Display scores
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{selected_match['team1_Name']}",
                    f"{selected_match['team1_runs']}/{selected_match['team1_wickets']}",
                    f"Overs: {selected_match['team1_overs']}")
        with col2:
            st.metric(f"{selected_match['team2_Name']}",
                    f"{selected_match['team2_runs']}/{selected_match['team2_wickets']}",
                    f"Overs: {selected_match['team2_overs']}")

        # Scorecard Button
        if st.button("Show Full Scorecard"):
            Match_ID = selected_match['match_Id']
            st.info("Fetching scorecard...")
            df1, df2, df3, df4 = fetch_scorecard(Match_ID)

            st.subheader("Innings 1 Batting")
            st.table(df1)
            st.subheader("Innings 1 Bowling")
            st.table(df2)
            st.subheader("Innings 2 Batting")
            st.table(df3)
            st.subheader("Innings 2 Bowling")
            st.table(df4)
            
