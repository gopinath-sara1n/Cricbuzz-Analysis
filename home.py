import streamlit as st
import Pg1_Live_Matches, Pg2_Player_Stats, Pg3_SQL_Queries, Pg4_CRUD_Operations


# Page Config
st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide"
)


st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["📡 Live Matches", "👤 Player Stats", "📊 SQL Queries & Analytics", "🛠️ CRUD Operations"])

# Page router
if page == "📡 Live Matches":
    Pg1_Live_Matches.app()

elif page == "👤 Player Stats":
    Pg2_Player_Stats.app()

elif page == "📊 SQL Queries & Analytics":
    Pg3_SQL_Queries.app()

elif page == "🛠️ CRUD Operations":
    Pg4_CRUD_Operations.app()

# Title
st.title("🏏 Cricbuzz LiveStats: Real-Time Cricket Insights")
st.markdown("""
Welcome to the **Cricket Analytics Dashboard**!  
Use the **sidebar** to explore:

---
Built with **Python, Streamlit, SQL, and Cricbuzz API**.
""")

