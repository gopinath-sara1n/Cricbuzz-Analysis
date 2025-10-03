import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Player Stats", page_icon="👤", layout="wide")
KEY_2nd_PAGE = "cd436a9136msh7134d9e6d53e7a4p1ee911jsn476d453f0ea8"

#Player Search Function
@st.cache_data
def pname(name):
    import requests

    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search"

    querystring = {"plrN":f"{name}"}

    headers = {
        "x-rapidapi-key": KEY_2nd_PAGE,
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()
        
    players = []

    for player in data.get('player', []):

        id = player.get('id')
        name = player.get('name')
        teamName = player.get('teamName')
        faceImageId = player.get('faceImageId')
        dob= player.get('dob')

        players.append({
        "id" : id,
        "name" : name,
        "teamName" : teamName,
        "faceImageId" : faceImageId,
        "dob" : dob
        })   
    return pd.DataFrame(players)


#personal info
@st.cache_data
def pinfo(id):
	qw =[]

	url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{id}"

	headers = {
		"x-rapidapi-key": KEY_2nd_PAGE,
		"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
	}

	response = requests.get(url, headers=headers)

	data = response.json()
	qw.append({
				"id" : data.get("id", "No Data"),
				"name" : data.get("name", "No Data"),
				"role" : data.get("role", "No Data"),
				"bat" : data.get("bat", "No Data"),
				"bowl" : data.get("bowl", "No Data"), 
				"intlTeam" : data.get("intlTeam", "No Data"),
				"DoB" : data.get("DoB", "No Data"),
				"birthPlace" : data.get("birthPlace", "No Data"),
				"height" : data.get("height", "No Data"),
				"teams" : data.get("teams", "No Data")
	})

	df = pd.DataFrame(qw)
	
	return df

#Batting Stats Function
@st.cache_data
def bat_stats(id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{id}/batting"

    headers = {
      "x-rapidapi-key": KEY_2nd_PAGE,
      "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    data = response.json()
    qw =[]
    for main_value in data.get('values', []):
        sub_value = main_value['values']
        ROWHEADER = sub_value[0]
        Test = sub_value[1]
        ODI = sub_value[2]
        T20 = sub_value[3]
        IPL = sub_value[4]
        qw.append([ROWHEADER, Test, ODI, T20, IPL])
    df_bat_stat = pd.DataFrame(qw, columns=['ROWHEADER', 'Test', 'ODI', 'T20', 'IPL'])
    df_bat_stat = df_bat_stat.set_index("ROWHEADER")
    return df_bat_stat

#Bowling Stats Function
@st.cache_data
def bowl_stats(id):
    import requests

    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{id}/bowling"

    headers = {
      "x-rapidapi-key": KEY_2nd_PAGE,
      "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    data = response.json()
    bowl_stat = []
    for description in data.get("values", []):
      values = description.get("values")
      ROWHEADER = values[0]
      Test = values[1]
      ODI = values[2]
      T20 = values[3]
      IPL = values[4]
      bowl_stat.append([ROWHEADER, Test, ODI, T20, IPL])
    df_bowl_stat = pd.DataFrame(bowl_stat, columns=['ROWHEADER', 'Test', 'ODI', 'T20', 'IPL'])
    df_bowl_stat = df_bowl_stat.set_index('ROWHEADER')
    
    return df_bowl_stat

#Stramlit

def app():
        #Page Title
        st.title("Player Stats")

        #player name Input
        Player_Name = st.text_input("Enter Player Name: ")
        df1 = pname(Player_Name)

        #If no player found
        if df1.empty:
            st.warning("No players found. Try another name.")
            st.stop()

        #Related Player Name Selectbox
        player_index = st.selectbox("select the player", 
                                df1.index, 
                                format_func= lambda i : f"{df1.loc[i, 'name']} | {df1.loc[i, 'teamName']}")
        selected_player = df1.loc[player_index]

        #for connecting Personal info fn, batting stat fn, bowling stat fn
        m_id = selected_player['id']

        #Selected Player Primary Info
        st.subheader(f"{selected_player['name']} - Player Profile")
        #st.write(f"**Player id:** {selected_player['id']}")

        tabs_21 = st.tabs(["Profile", "Batting Stats", "Bowling Stats"])

        with tabs_21[0]:
            #calling Personal Info function
            player_info = pinfo(m_id).iloc[0]

            col_21, col_22, col_23 = st.columns(3)

            with col_21:
                st.subheader("Cricket details")
                st.write(f"**Role:** {player_info['role']}")
                st.write(f"**Batting:** {player_info['bat']}")
                st.write(f"**Bowling:** {player_info['bowl']}")
                st.write(f"**International Team:** {player_info['intlTeam']}")

            with col_22:
                st.subheader("Personal details")
                st.write(f"**Date of Birth:** {player_info['DoB']}")
                st.write(f"**Birth Place:** {player_info['birthPlace']}")
                st.write(f"**Height:** {player_info['height']}")

            with col_23:
                st.subheader("Teams Played")
                Teams = player_info['teams']
                team_list = [team.strip() for team in Teams.split(",")]
                for team in team_list:
                    st.markdown(f"- {team}")

        with tabs_21[1]:
            #calling Batting Stat Function
            player_bat_stats = bat_stats(m_id)

            st.subheader("Detailed Batting Statistics")
            st.table(player_bat_stats)

        with tabs_21[2]:
            #calling Bowling Stat function
            player_bowl_stats = bowl_stats(m_id)

            st.subheader("Detailed Bowling Statistics")
            st.table(player_bowl_stats)







