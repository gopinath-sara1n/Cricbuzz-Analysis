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

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
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
# SIDEBAR NAVIGATION & SETTINGS
# ==============================================================================

with st.sidebar:
    st.markdown("""
        <div class="sidebar-header">
            <h2 style="margin: 0; color: #4CAF50;">🏏 Cricbuzz LiveStats</h2>
            <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #888;">Real-Time Cricket Intelligence</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🧭 Navigation")
    page = st.radio(
        "Select View",
        [
            "📡 Live & Recent Matches",
            "👤 Player Stats & Profiles"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")

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
# PAGE ROUTING
# ==============================================================================

if page == "📡 Live & Recent Matches":
    Pg1_Live_Matches.app()
elif page == "👤 Player Stats & Profiles":
    Pg2_Player_Stats.app()
