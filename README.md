# 🏏 Cricbuzz LiveStats Pro

A modern, high-performance cricket analytics dashboard and match center built with **Python**, **Streamlit**, **Plotly**, and the **Cricbuzz RapidAPI**.

---

## 🌐 Live Application

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cricbuzz-analysis-fuzeeeljckfpfmhpa4zv2m.streamlit.app/)

> 🔗 **Live App Link:** [Lie App]((https://cricbuzz-analysis-u5ryqnrknqvfraczr9btpb.streamlit.app/))

---

## 🌟 Key Features & Improvements

### 1. 🏏 Tailored 4-Innings Test Match Architecture
- **Full 4-Innings Support**: Built specifically to handle multi-innings Test matches cleanly (Innings 1, 2, 3, and 4).
- **Multi-Innings Scoreline Display**: Tracks both `1st Innings` and `2nd Innings` for both teams simultaneously (e.g. `Bihar: 166/10 & 251/10` vs `Baroda: 416/10 & 4/0`), avoiding truncation or loss of second innings data.
- **Dynamic Innings Tabs**: Automatically generates dedicated tabs for every completed and in-progress innings in a Test match, displaying:
  - Innings summary metrics (Score, Wickets, Overs, Run Rate, Extras)
  - Special match conditions (Declarations `d`, Follow-on `f/o`)
  - Full Batting Scorecard (Runs, Balls, 4s, 6s, Strike Rate, Dismissal status, with 50s ⭐ and 100s 💯 highlights)
  - Bowling Figures (Overs, Maidens, Runs, Wickets, Economy, Dots)
  - Extras Breakdown (Byes, Leg-byes, Wides, No-balls, Penalty)
  - Fall of Wickets (FOW) timeline
  - Batting Partnerships breakdown
  - Interactive Plotly charts for batting contributions and bowling spells

### 2. 📡 Live, Recent & Upcoming Match Explorer
- **Three Match Categories**: Easily switch between **🔴 Live Matches**, **🏁 Recent (Completed) Matches**, and **📅 Upcoming Fixtures**.
- **Format Filtering**: Filter matches instantly by format: `TEST`, `ODI`, `T20`, or view `All Formats`.
- **Search & Filter**: Search matches by team names, venues, or tournament series (e.g. Ranji Trophy, Ashes, World Cup).
- **One-Click Refresh**: Clear cache and refresh live data with a single button.

### 3. 👤 Comprehensive Player Profiles & Career Analytics
- **Instant Search & Quick Picks**: Quick-select popular global stars (Virat Kohli, Joe Root, Steve Smith, Rohit Sharma, Jasprit Bumrah, Pat Cummins, Babar Azam, Kane Williamson, Rashid Khan) or search any cricketer by name.
- **Player Details**: Official headshot, national team, playing role, batting/bowling style, date of birth, age, birth place, and teams represented.
- **ICC Rankings**: Test, ODI, and T20 official rankings for batting and bowling.
- **Format-by-Format Career Tables**: Comprehensive career stats across **Test**, **ODI**, **T20**, and **IPL**.
- **Interactive Visualizations**: Total runs by format, centuries vs half-centuries, total wickets, and economy trends rendered using Plotly.
- **Recent Form Tracker**: Real-time log of the player's most recent batting scores and bowling figures.
- **Player Bio**: Formatted biographical narrative and career journey.

### 4. ⚔️ Head-to-Head Player Comparison
- Compare any two cricketers directly across **Test**, **ODI**, **T20**, or **IPL**.
- Side-by-side key metrics: Runs, Averages, Strike Rates, Hundreds, Fifties, Highest Score, Wickets, and Economy.
- Interactive grouped bar chart comparing performance in the chosen format.

### 5. ⚡ Streamlined, Zero-Database Setup
- **No Local Database Required**: Removed legacy MySQL SQL queries and CRUD dependencies (Pages 3 & 4) for an instant, out-of-the-box experience.
- **API Key Management**: Works out of the box with the default RapidAPI key, and includes a sidebar configuration expander where users can plug in their personal RapidAPI key anytime.

---

## 📁 Project Structure

```text
Cricbuzz-Analysis/
├── app.py                # Main application entrypoint with top-level tabs navigation ("📡 Live Matches", "👤 Player Stats")
├── Pg1_Live_Matches.py   # Live, Recent & Upcoming match center with 4-innings Test support
├── Pg2_Player_Stats.py   # Player profiles, career stats, recent form & H2H comparison
├── cricbuzz_api.py       # Cricbuzz RapidAPI client, caching, and data parsers
├── requirements.txt      # Python package dependencies
└── README.md             # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/gopinath-sara1n/Cricbuzz-Analysis.git
cd Cricbuzz-Analysis
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🔑 RapidAPI Configuration

The dashboard uses the [Cricbuzz Cricket API on RapidAPI](https://rapidapi.com/crmMatches/api/cricbuzz-cricket).  
A working key is included by default. If you reach the RapidAPI free tier rate limit:
1. Open the sidebar in the app.
2. Expand **⚙️ API Configuration**.
3. Paste your own free RapidAPI Key.
4. Click **🧹 Clear App Cache**.
