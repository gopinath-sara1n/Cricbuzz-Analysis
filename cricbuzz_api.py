"""
Cricbuzz API Client & Data Transformation Utilities
Supports Live, Recent, and Upcoming matches with full Test match (4 innings) parsing.
"""

import requests
import pandas as pd
import streamlit as st
import re

DEFAULT_API_KEY = "21d336251emsh719e8aa018de93cp1a5081jsn0f37acea4c73"
API_HOST = "cricbuzz-cricket.p.rapidapi.com"


def get_headers(api_key=None):
    key = api_key or st.session_state.get("rapidapi_key") or DEFAULT_API_KEY
    return {
        "x-rapidapi-key": key.strip(),
        "x-rapidapi-host": API_HOST
    }


def format_overs(val):
    """
    Format cricket overs properly.
    E.g. Cricbuzz stores 52.6 as 53.0 (6 balls = full over), 52.1 as 52.1.
    """
    if val is None or val == "":
        return "-"
    try:
        val = float(val)
        whole = int(val)
        ball = int(round((val - whole) * 10))
        if ball >= 6:
            whole += 1
            ball = 0
        return f"{whole}.{ball}" if ball > 0 else f"{whole}.0"
    except Exception:
        return str(val)


def format_innings_score(inng_data):
    """Format single innings dictionary into standard cricket notation (e.g. 245/8 d (45.2 ov))"""
    if not inng_data:
        return None
    runs = inng_data.get("runs", 0)
    wickets = inng_data.get("wickets", 0)
    overs = format_overs(inng_data.get("overs"))
    declared = inng_data.get("isDeclared", False) or inng_data.get("isdeclared", False)

    dec_suffix = " d" if declared else ""
    ov_str = f" ({overs} ov)" if overs != "-" else ""
    return f"{runs}/{wickets}{dec_suffix}{ov_str}"


def format_team_display_score(score_dict, is_test=False):
    """
    Format a team's score across 1 or 2 innings.
    For Test matches, handles both inngs1 and inngs2 (e.g. 166/10 & 251/10).
    """
    if not score_dict:
        return "Yet to Bat"
    
    i1 = score_dict.get("inngs1")
    i2 = score_dict.get("inngs2")

    s1 = format_innings_score(i1)
    s2 = format_innings_score(i2)

    if is_test:
        if s1 and s2:
            return f"{s1} & {s2}"
        elif s1:
            return s1
        return "Yet to Bat"
    else:
        return s1 or "Yet to Bat"


# ==============================================================================
# MATCHES API
# ==============================================================================

@st.cache_data(ttl=60, show_spinner=False)
def fetch_matches_data(category="live", api_key=None):
    """
    Fetch matches from Cricbuzz API for live, recent, or upcoming categories.
    """
    valid_endpoints = {
        "live": "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live",
        "recent": "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent",
        "upcoming": "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming"
    }
    url = valid_endpoints.get(category.lower(), valid_endpoints["live"])
    headers = get_headers(api_key)

    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 429:
            st.error("⚠️ RapidAPI rate limit / quota exceeded for current API key. Please input your personal key in the sidebar.")
            return pd.DataFrame()
        if response.status_code != 200:
            st.warning(f"Unable to fetch matches (HTTP {response.status_code}): {response.text[:120]}")
            return pd.DataFrame()

        data = response.json()
    except Exception as e:
        st.error(f"Error connecting to Cricbuzz API: {e}")
        return pd.DataFrame()

    matches = []
    for type_match in data.get("typeMatches", []):
        match_type = type_match.get("matchType", "Other")  # International, League, Domestic, Women
        for series_match in type_match.get("seriesMatches", []):
            series = series_match.get("seriesAdWrapper", {})
            series_name = series.get("seriesName", "Unknown Series")
            for match in series.get("matches", []):
                info = match.get("matchInfo", {})
                match_id = info.get("matchId")
                match_desc = info.get("matchDesc", "")
                match_format = info.get("matchFormat", "UNKNOWN").upper()
                is_test = match_format == "TEST" or "test" in match_desc.lower()

                start_date_raw = info.get("startDate")
                try:
                    start_date = pd.to_datetime(pd.to_numeric(start_date_raw), unit="ms").strftime("%d %b %Y, %I:%M %p")
                except Exception:
                    start_date = "N/A"

                state = info.get("state", "Unknown")
                status = info.get("status", "")
                team1 = info.get("team1", {})
                team2 = info.get("team2", {})
                venue_info = info.get("venueInfo", {})
                ground = venue_info.get("ground", "Venue TBA")
                city = venue_info.get("city", "")
                full_venue = f"{ground}, {city}".strip(", ") if city else ground

                match_score = match.get("matchScore", {})
                team1_score_dict = match_score.get("team1Score", {})
                team2_score_dict = match_score.get("team2Score", {})

                # Innings 1 & 2 extractions
                t1_i1 = team1_score_dict.get("inngs1", {})
                t1_i2 = team1_score_dict.get("inngs2", {})
                t2_i1 = team2_score_dict.get("inngs1", {})
                t2_i2 = team2_score_dict.get("inngs2", {})

                team1_score_str = format_team_display_score(team1_score_dict, is_test=is_test)
                team2_score_str = format_team_display_score(team2_score_dict, is_test=is_test)

                # Total runs calculated for Test lead/margin comparison
                t1_total_runs = (t1_i1.get("runs") or 0) + (t1_i2.get("runs") or 0)
                t2_total_runs = (t2_i1.get("runs") or 0) + (t2_i2.get("runs") or 0)

                matches.append({
                    "match_id": match_id,
                    "match_desc": match_desc,
                    "series_name": series_name,
                    "match_type": match_type,
                    "match_format": match_format,
                    "is_test": is_test,
                    "start_date": start_date,
                    "state": state,
                    "status": status,
                    "venue": full_venue,
                    "team1_name": team1.get("teamName", "Team 1"),
                    "team1_short": team1.get("teamSName", "T1"),
                    "team1_id": team1.get("teamId"),
                    "team1_image_id": team1.get("imageId"),
                    "team1_score": team1_score_str,
                    "team1_inngs1": t1_i1,
                    "team1_inngs2": t1_i2,
                    "team1_total_runs": t1_total_runs,
                    "team2_name": team2.get("teamName", "Team 2"),
                    "team2_short": team2.get("teamSName", "T2"),
                    "team2_id": team2.get("teamId"),
                    "team2_image_id": team2.get("imageId"),
                    "team2_score": team2_score_str,
                    "team2_inngs1": t2_i1,
                    "team2_inngs2": t2_i2,
                    "team2_total_runs": t2_total_runs,
                })

    return pd.DataFrame(matches)


# ==============================================================================
# SCORECARD API (Dynamic 1 to 4 Innings Support for Test Matches)
# ==============================================================================

@st.cache_data(ttl=60, show_spinner=False)
def fetch_scorecard_data(match_id, api_key=None):
    """
    Fetch comprehensive scorecard data for a match.
    Dynamically processes all innings (up to 4 innings for Test matches).
    Returns list of innings dictionaries with batting, bowling, fow, and extras.
    """
    url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/scard"
    headers = get_headers(api_key)

    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Failed to fetch scorecard (HTTP {response.status_code})",
                "innings": [],
                "match_complete": False
            }
        data = response.json()
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "innings": [],
            "match_complete": False
        }

    raw_scorecard = data.get("scorecard", [])
    is_match_complete = data.get("ismatchcomplete", False)
    status_msg = data.get("status", "")

    parsed_innings = []

    for inng in raw_scorecard:
        inng_id = inng.get("inningsid", len(parsed_innings) + 1)
        bat_team_name = inng.get("batteamname", f"Innings {inng_id}")
        bat_team_short = inng.get("batteamsname", "")
        score = inng.get("score", 0)
        wickets = inng.get("wickets", 0)
        overs = inng.get("overs", 0)
        run_rate = inng.get("runrate", 0.0)
        is_declared = inng.get("isdeclared", False)
        is_follow_on = inng.get("isfollowon", False)
        extras = inng.get("extras", {})

        # Parse Batsmen
        batters_list = []
        for b in inng.get("batsman", []):
            role_badge = ""
            if b.get("iscaptain"): role_badge += " (c)"
            if b.get("iskeeper"): role_badge += " (wk)"

            runs = b.get("runs", 0)
            balls = b.get("balls", 0)
            fours = b.get("fours", 0)
            sixes = b.get("sixes", 0)
            sr = b.get("strkrate", "0.0")

            batters_list.append({
                "Batter": f"{b.get('name', 'Unknown')}{role_badge}",
                "Dismissal": b.get("outdec") or "not out",
                "Runs": runs,
                "Balls": balls,
                "4s": fours,
                "6s": sixes,
                "SR": float(sr) if sr and sr != "-" else 0.0
            })
        bat_df = pd.DataFrame(batters_list)

        # Parse Bowlers
        bowlers_list = []
        for bw in inng.get("bowler", []):
            role_badge = " (c)" if bw.get("iscaptain") else ""
            bowlers_list.append({
                "Bowler": f"{bw.get('name', 'Unknown')}{role_badge}",
                "Overs": bw.get("overs", "0"),
                "Maidens": bw.get("maidens", 0),
                "Runs": bw.get("runs", 0),
                "Wickets": bw.get("wickets", 0),
                "Economy": float(bw.get("economy", 0.0)) if bw.get("economy") and bw.get("economy") != "-" else 0.0,
                "Dots": bw.get("dots", 0)
            })
        bowl_df = pd.DataFrame(bowlers_list)

        # Parse Fall of Wickets
        fow_list = []
        fow_data = inng.get("fow", {}).get("fow", [])
        for f in fow_data:
            fow_list.append({
                "Wkt #": len(fow_list) + 1,
                "Batter": f.get("batsmanname", "Unknown"),
                "Score": f.get("runs", 0),
                "Over": format_overs(f.get("overnbr"))
            })
        fow_df = pd.DataFrame(fow_list)

        # Parse Partnerships
        partnerships = []
        part_data = inng.get("partnership", {}).get("partnership", [])
        for p in part_data:
            partnerships.append({
                "Batter 1": f"{p.get('bat1name', '')} ({p.get('bat1runs', 0)})",
                "Batter 2": f"{p.get('bat2name', '')} ({p.get('bat2runs', 0)})",
                "Partnership Runs": p.get("totalruns", 0),
                "Balls": p.get("totalballs", 0)
            })
        partnerships_df = pd.DataFrame(partnerships)

        parsed_innings.append({
            "innings_id": inng_id,
            "bat_team_name": bat_team_name,
            "bat_team_short": bat_team_short,
            "score": score,
            "wickets": wickets,
            "overs": format_overs(overs),
            "run_rate": run_rate,
            "is_declared": is_declared,
            "is_follow_on": is_follow_on,
            "extras": extras,
            "batting_df": bat_df,
            "bowling_df": bowl_df,
            "fow_df": fow_df,
            "partnerships_df": partnerships_df
        })

    return {
        "success": True,
        "innings": parsed_innings,
        "match_complete": is_match_complete,
        "status": status_msg
    }


# ==============================================================================
# TEAM LOGO API (Cricbuzz Official Static CDN)
# Reference: https://static.cricbuzz.com/a/img/v1/0x0/i1/c776333/new-zealand.jpg
# ==============================================================================

KNOWN_TEAM_IMAGE_IDS = {
    # International Teams
    "india": 776162, "ind": 776162,
    "afghanistan": 776177, "afg": 776177,
    "united states of america": 776186, "united states": 776186, "usa": 776186,
    "west indies": 776191, "wi": 776191,
    "zimbabwe": 776198, "zim": 776198,
    "australia": 776202, "aus": 776202,
    "bangladesh": 776210, "ban": 776210,
    "belgium": 776219,
    "bermuda": 776221,
    "botswana": 776225,
    "canada": 776227, "can": 776227,
    "vanuatu": 776229,
    "denmark": 776232, "den": 776232,
    "uganda": 776233, "uga": 776233,
    "england": 776237, "eng": 776237,
    "united arab emirates": 776242, "uae": 776242,
    "fiji": 776251,
    "sri lanka": 776254, "sl": 776254,
    "germany": 776260, "ger": 776260,
    "hong kong china": 776271, "hong kong": 776271, "hk": 776271,
    "singapore": 776275, "sin": 776275,
    "scotland": 776280, "sco": 776280,
    "iran": 776282,
    "south africa": 776287, "sa": 776287, "rsa": 776287,
    "italy": 776295, "ita": 776295,
    "jersey": 776300,
    "kenya": 776303, "ken": 776303,
    "papua new guinea": 776304, "png": 776304,
    "pakistan": 776308, "pak": 776308,
    "kuwait": 776312, "kuw": 776312,
    "malaysia": 776319, "mas": 776319,
    "namibia": 776326, "nam": 776326,
    "oman": 776328, "oma": 776328,
    "nepal": 776331, "nep": 776331,
    "new zealand": 776333, "nz": 776333,
    "netherlands": 776335, "ned": 776335,
    "ireland": 839366, "ire": 839366,

    # IPL Teams
    "chennai super kings": 860038, "csk": 860038,
    "delhi capitals": 860040, "dc": 860040,
    "kolkata knight riders": 860046, "kkr": 860046,
    "mumbai indians": 860053, "mi": 860053,
    "rajasthan royals": 860055, "rr": 860055,
    "royal challengers bengaluru": 860056, "royal challengers bangalore": 860056, "rcb": 860056,
    "sunrisers hyderabad": 860066, "srh": 860066,
    "gujarat titans": 860068, "gt": 860068,
    "punjab kings": 860084, "pbks": 860084,
    "lucknow super giants": 882545, "lsg": 882545,

    # BBL Teams
    "adelaide strikers": 824977,
    "brisbane heat": 824979,
    "hobart hurricanes": 824981,
    "perth scorchers": 824983,
    "melbourne renegades": 824985,
    "melbourne stars": 824987,
    "sydney sixers": 824989,
    "sydney thunder": 824991,

    # PSL Teams
    "multan sultans": 883178,
    "peshawar zalmi": 883180,
    "lahore qalandars": 883181,
    "quetta gladiators": 883182,
    "islamabad united": 883184,
    "karachi kings": 883188,

    # SA20 & Major League Cricket Teams
    "mi cape town": 831132,
    "joburg super kings": 831131,
    "durbans super giants": 831130,
    "paarl royals": 831135,
    "pretoria capitals": 831133,
    "sunrisers eastern cape": 831134,
    "washington freedom": 825012,
    "mi new york": 825028,
    "san francisco unicorns": 825029,
    "seattle orcas": 825030,
    "texas super kings": 825031,
    "los angeles knight riders": 825025
}


def resolve_team_image_id(team_name, image_id=None):
    """
    Resolve Cricbuzz image ID for a team name, short name, or explicit image ID.
    """
    if image_id:
        return image_id
    if not team_name:
        return None

    raw = str(team_name).lower().strip()
    clean = re.sub(r'[^a-z0-9 ]+', '', raw).strip()
    slug = re.sub(r'[^a-z0-9]+', '-', raw).strip('-')

    # 1. Exact match
    res = (
        KNOWN_TEAM_IMAGE_IDS.get(raw) or
        KNOWN_TEAM_IMAGE_IDS.get(clean) or
        KNOWN_TEAM_IMAGE_IDS.get(slug)
    )
    if res:
        return res

    # 2. Substring match (e.g. "Pakistan Women", "Team India", "Australia XI")
    for key, val in KNOWN_TEAM_IMAGE_IDS.items():
        if len(key) >= 4 and key in raw:
            return val

    return None


def get_team_logo_url(team_name, image_id=None):
    """
    Generate Cricbuzz official static CDN team logo URL.
    Format: https://static.cricbuzz.com/a/img/v1/0x0/i1/c{imageId}/{slug}.jpg
    Reference: https://static.cricbuzz.com/a/img/v1/0x0/i1/c776333/new-zealand.jpg
    """
    img_id = resolve_team_image_id(team_name, image_id)
    if not img_id:
        return None
    slug = re.sub(r'[^a-z0-9]+', '-', (team_name or 'team').lower()).strip('-') or 'team'
    return f"https://static.cricbuzz.com/a/img/v1/0x0/i1/c{img_id}/{slug}.jpg"


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_team_logo_bytes(team_name, image_id=None, api_key=None):
    """
    Fetch team logo image bytes directly from Cricbuzz's official static CDN,
    with fallback to RapidAPI image endpoint.
    Reference: https://static.cricbuzz.com/a/img/v1/0x0/i1/c776333/new-zealand.jpg
    """
    url = get_team_logo_url(team_name, image_id)
    if url:
        browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        try:
            resp = requests.get(url, headers=browser_headers, timeout=6)
            if resp.status_code == 200 and len(resp.content) > 100:
                return resp.content
        except Exception:
            pass

    # Fallback to RapidAPI image endpoint if image_id is available
    img_id = resolve_team_image_id(team_name, image_id)
    if img_id:
        headers = get_headers(api_key)
        try:
            rapid_url = f"https://cricbuzz-cricket.p.rapidapi.com/img/v1/i1/c{img_id}/i.jpg"
            resp = requests.get(rapid_url, headers=headers, timeout=5)
            if resp.status_code == 200 and len(resp.content) > 100:
                return resp.content
        except Exception:
            pass

    return None


# ==============================================================================
# PLAYER STATS API
# ==============================================================================

def get_player_image_url(name, face_image_id):
    """
    Generate Cricbuzz official static CDN image URL.
    Format: https://static.cricbuzz.com/a/img/v1/i1/c{faceImageId}/{slug}.jpg?d=low&p=gthumb
    """
    if not face_image_id:
        return None
    slug = re.sub(r'[^a-z0-9]+', '-', (name or 'player').lower()).strip('-') or 'player'
    return f"https://static.cricbuzz.com/a/img/v1/i1/c{face_image_id}/{slug}.jpg?d=low&p=gthumb"


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_player_image_bytes(name, face_image_id, player_id=None, api_key=None):
    """
    Fetch player headshot image bytes directly from Cricbuzz's official static CDN,
    with fallback to RapidAPI image endpoint.
    """
    # 1. Primary: Cricbuzz official static CDN
    if face_image_id:
        url = get_player_image_url(name, face_image_id)
        browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        try:
            resp = requests.get(url, headers=browser_headers, timeout=6)
            if resp.status_code == 200 and len(resp.content) > 100:
                return resp.content
        except Exception:
            pass

    # 2. Fallback: RapidAPI image endpoint
    headers = get_headers(api_key)
    candidates = [c for c in [face_image_id, player_id] if c]
    for cid in candidates:
        try:
            rapid_url = f"https://cricbuzz-cricket.p.rapidapi.com/img/v1/i1/c{cid}/i.jpg"
            resp = requests.get(rapid_url, headers=headers, timeout=5)
            if resp.status_code == 200 and len(resp.content) > 100:
                return resp.content
        except Exception:
            continue

    return None


@st.cache_data(ttl=300, show_spinner=False)
def search_player_data(name, api_key=None):
    """Search players by name keyword"""
    if not name or not name.strip():
        return pd.DataFrame()
    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search"
    headers = get_headers(api_key)
    try:
        response = requests.get(url, headers=headers, params={"plrN": name.strip()}, timeout=10)
        if response.status_code != 200:
            return pd.DataFrame()
        data = response.json()
        players = []
        for p in data.get("player", []):
            players.append({
                "id": str(p.get("id")),
                "name": p.get("name", "Unknown"),
                "teamName": p.get("teamName", ""),
                "faceImageId": p.get("faceImageId"),
                "dob": p.get("dob", "")
            })
        return pd.DataFrame(players)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_player_info(player_id, api_key=None):
    """Fetch personal details, rankings, bio, recent form for player"""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"
    headers = get_headers(api_key)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {}
        return response.json()
    except Exception:
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def fetch_player_batting_stats(player_id, api_key=None):
    """Fetch structured career batting statistics across Test, ODI, T20, and IPL"""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/batting"
    headers = get_headers(api_key)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return pd.DataFrame()
        data = response.json()
        rows = []
        for mv in data.get("values", []):
            vals = mv.get("values", [])
            if len(vals) >= 5:
                rows.append([vals[0], vals[1], vals[2], vals[3], vals[4]])
        df = pd.DataFrame(rows, columns=["Metric", "Test", "ODI", "T20", "IPL"])
        return df.set_index("Metric")
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_player_bowling_stats(player_id, api_key=None):
    """Fetch structured career bowling statistics across Test, ODI, T20, and IPL"""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/bowling"
    headers = get_headers(api_key)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return pd.DataFrame()
        data = response.json()
        rows = []
        for mv in data.get("values", []):
            vals = mv.get("values", [])
            if len(vals) >= 5:
                rows.append([vals[0], vals[1], vals[2], vals[3], vals[4]])
        df = pd.DataFrame(rows, columns=["Metric", "Test", "ODI", "T20", "IPL"])
        return df.set_index("Metric")
    except Exception:
        return pd.DataFrame()
