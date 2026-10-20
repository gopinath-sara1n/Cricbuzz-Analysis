"""
Cricbuzz LiveStats Pro - Modern Cricket Analytics Dashboard
Streamlit Main Application Entrypoint
"""

import streamlit as st
import Pg1_Live_Matches
import Pg2_Player_Stats
from cricbuzz_api import DEFAULT_API_KEY

# Set global page configuration (must be called only once at the top of the main file)
st.set_page_config(
    page_title="Cricbuzz LiveStats Pro",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling & prominent tabs
st.markdown("""
<style>
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    
    /* Main Top Tabs styling */
    div[data-testid="stTabs"] > div > div[data-baseweb="tab-list"] {
        gap: 12px;
        margin-top: 10px;
        margin-bottom: 25px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }
    div[data-testid="stTabs"] > div > div[data-baseweb="tab-list"] button[data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px;
        padding: 12px 28px;
        font-weight: 700;
        font-size: 1.15rem;
    }
    
    /* Sidebar header */
    .sidebar-header {
        text-align: center;
        padding-bottom: 15px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    
    /* Info banners */
    .feature-card {
        background-color: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px;
        margin-top: 15px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize API Key in Session State
if "rapidapi_key" not in st.session_state:
    st.session_state["rapidapi_key"] = DEFAULT_API_KEY

# ==============================================================================
# SIDEBAR SETTINGS & INFO
# ==============================================================================

with st.sidebar:
    st.markdown("""
        <div class="sidebar-header">
            <h2 style="margin: 0; color: #4CAF50;">🏏 Cricbuzz LiveStats</h2>
            <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #888;">Real-Time Cricket Intelligence</p>
        </div>
    """, unsafe_allow_html=True)

    # API Settings Expander
    with st.expander("⚙️ API Configuration", expanded=False):
        custom_key = st.text_input(
            "RapidAPI Key",
            value=st.session_state["rapidapi_key"],
            type="password",
            help="Default key is pre-loaded. If rate limits are exceeded, enter your own Cricbuzz RapidAPI key."
        )
        if custom_key != st.session_state["rapidapi_key"]:
            st.session_state["rapidapi_key"] = custom_key
            st.success("API Key updated!")
            st.cache_data.clear()

        if st.button("🧹 Clear App Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache cleared successfully!")
            st.rerun()

    # Features Banner
    st.markdown("""
        <div class="feature-card">
            <b>✨ Key Features:</b>
            <ul style="margin: 6px 0 0 0; padding-left: 20px;">
                <li><b>4-Innings Test Architecture:</b> Full support for Test matches across all 4 innings</li>
                <li><b>Live, Recent & Upcoming:</b> Real-time scores and completed scorecards</li>
                <li><b>Interactive Scorecards:</b> Batsmen, Bowlers, Fall of Wickets & Partnerships</li>
                <li><b>Player Career Analytics:</b> Batting & Bowling stats across Test, ODI, T20, IPL</li>
                <li><b>Head-to-Head Comparison:</b> Compare any two cricket icons</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Powered by Cricbuzz RapidAPI & Streamlit")


# ==============================================================================
# TOP TITLE & MAIN TAB NAVIGATION
# ==============================================================================

st.markdown("""
    <div style="margin-bottom: 10px;">
        <h1 style="margin: 0; padding: 0;">🏏 Cricbuzz LiveStats Pro</h1>
        <p style="color: #888; font-size: 1.05rem; margin-top: 4px;">
            Real-Time Cricket Intelligence, 4-Innings Test Match Analytics & Player Statistics
        </p>
    </div>
""", unsafe_allow_html=True)

tab_live_matches, tab_player_stats = st.tabs([
    "📡 Live Matches",
    "👤 Player Stats"
])

with tab_live_matches:
    Pg1_Live_Matches.app()

with tab_player_stats:
    Pg2_Player_Stats.app()
