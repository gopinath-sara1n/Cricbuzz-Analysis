import pymysql
import pandas as pd
import streamlit as st

st.set_page_config(page_title="SQL Queries", page_icon="📊", layout="wide")
# MySQL connection function
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Qwerty@123",
        database="cricbuzz_db"
    )

# Function to run query and return DataFrame
def mydb_query(query):
    conn = get_connection()  # Call the function
    df = pd.read_sql(query, conn)  # Read query into DataFrame
    conn.close()  # Close connection
    return df

def app():
        st.title("SQL Queries Dashboard")

        #Qn list
        pg3_queries = ["Qn1: Find all players who represent India",
                    "Qn2: Show all cricket matches that were played in the last 30 days",
                    "Qn3: List the top 10 highest run scorers in Test cricket",
                    "Qn4: Display all cricket venues that have a seating capacity of more than 40,000 spectators",
                    "Qn5: Calculate how many matches each team has won in ICC Womens T20 World Cup Africa Region Division One Qualifier 2025",
                    "Qn6: Count how many players belong to each playing role (like Batsman, Bowler, All-rounder, Wicket-keeper)",
                    "Qn7: Find the highest individual batting score achieved in cricket format Test",
                    "Qn8: Show all cricket series that started in the year 2025",
                    "Qn9: Find all-rounder players who have scored more than 1000 runs AND taken more than 50 wickets in their career",
                    "Qn10: 20 completed matches. Basic Infos",
                    "Qn11: Compare each player's performance across different cricket formats",
                    "Qn12: Analyze each international team's performance when playing at home versus playing away",
                    "Qn13: Batting partnerships where two batsmen scored a combined total of 100 or more runs ",
                    "Qn14: bowling performance at different venues (at least 3 matches played and 4 overs bowled per match)",
                    "Qn15: Close Matches, A close match is defined as one decided by less than 50 runs OR less than 5 wickets",
                    "Qn16: Best strike rate among bowlers with more than 85 wickets",
                    "Qn17: Investigate whether winning the toss gives teams an advantage in winning matches",
                    "Qn18: Find the most economical bowlers in limited-overs cricket (T20)",
                    "Qn19: Which batsmen are most consistent in their scoring (Using AVG & SD)",
                    "Qn20: Matches played across formats and batting average (min 20 combined)",
                    "Qn21: Comprehensive performance ranking system for players",
                    "Qn22: Head-to-head match prediction analysis between teams",
                    "Qn23: Analyze recent player form and momentum. For each player's last 10 batting performances",
                    "Qn24: Study successful batting partnerships to identify the best player combinations",
                    "Qn25: Perform a time-series analysis of player performance evolution"                                           
                    ]

        #Selectbox
        select_Query = st.selectbox(
            "Select a Query:",
            pg3_queries)

        #Qn1: Find all players who represent India
        if select_Query == pg3_queries[0]:
            if st.button("Run Query"):
                df = mydb_query("SELECT * FROM players_represent_india;")
                st.table(df)

        #Qn2: Show all cricket matches that were played in the last 30 days
        if select_Query == pg3_queries[1]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select match_Desc, team1_Name, team2_Name, ground, city, start_Date   
                                from recent_matches
                                order by start_Date desc;
                                """)
                st.table(df)

        #Qn3: List the top 10 highest run scorers in Test cricket 
        if select_Query == pg3_queries[2]:
            if st.button("Run Query"):
                df = mydb_query("SELECT * FROM Highest_Test_Scorer;")
                st.table(df)

        #Qn4: Display all cricket venues that have a seating capacity of more than 40,000 spectators
        if select_Query == pg3_queries[3]:
            if st.button("Run Query"):
                df = mydb_query("select * from venue_info where capacity > 40000;")
                st.table(df)

        #Qn5: Calculate how many matches each team has won
        if select_Query == pg3_queries[4]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select team, count(*) as wins
                                from(
                                    select
                                        case
                                            when status like concat (team1_Name, '%') then team1_Name
                                            when status like concat (team2_Name, '%') then team2_Name
                                        end as team
                                    from recent_matches
                                    where series_name = 'ICC Womens T20 World Cup Africa Region Division One Qualifier 2025' 
                                )as winners
                                where team is not null
                                group by team
                                order by wins desc
                                """)
                st.table(df)

        # Qn6: Count how many players belong to each playing role (like Batsman, Bowler, All-rounder, Wicket-keeper)
        if select_Query == pg3_queries[5]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select Role, count(*) as Player_count
                                from players_represent_india
                                group by Role
                                order by Player_count;
                                """)
                st.table(df)

        #Qn7: Find the highest individual batting score achieved in cricket format Test
        if select_Query == pg3_queries[6]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select * from highest_test_score
                                order by High_Score desc
                                limit 1;
                                """)
                st.table(df)

        #Qn8: Show all cricket series that started in the year 2025
        if select_Query == pg3_queries[7]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select 
                                    series_name,
                                    match_Format,
                                    min(start_Date) as start_date,
                                    count(*) as matches_played
                                from recent_matches
                                group by series_name, match_Format
                                order by start_date desc;
                                """)
                st.table(df)

        # Qn9: Find all-rounder players who have scored more than 1000 runs AND taken more than 50 wickets in their career"
        if select_Query == pg3_queries[8]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select  * 
                                from all_rounder
                                order by Span desc;
                                """)
                st.table(df)


        # Qn10: 20 completed matches. Show match description, both team names, winning team, victory margin, victory type (runs/wickets), and venue name
        if select_Query == pg3_queries[9]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select
                                    match_Desc,
                                    team1_Name,
                                    team2_Name,
                                    
                                    CASE
                                        WHEN status LIKE CONCAT(team1_name, '%') THEN team1_name
                                        WHEN status LIKE CONCAT(team2_name, '%') THEN team2_name
                                        ELSE NULL
                                    END AS winning_team, 
                                    
                                    REGEXP_SUBSTR (STATUS, 'runs|wkts') as win_type,
                                    
                                    REGEXP_SUBSTR (STATUS, '[0-9]+') as margin,
                                    ground,
                                    start_Date
                                    
                                from recent_matches
                                where status like '%won by%'
                                order by start_Date desc
                                limit 20;
                                """)
                st.table(df)

        #Qn11: Compare each player's performance across different cricket formats
        if select_Query == pg3_queries[10]:
            if st.button("Run Query"):
                df = mydb_query("""
                                    select 
                                    i.Name,
                                    s.Test_Runs,
                                    s.Test_Avg,
                                    s.ODI_Runs,
                                    s.ODI_Avg,
                                    s.T20_Runs,
                                    s.T20_Avg,
                                    ROUND(
                                        (s.Test_Avg + s.ODI_Avg + s.T20_Avg) / NULLIF(
                                            (CASE WHEN s.Test_Avg > 0 THEN 1 ELSE 0 END) +
                                            (CASE WHEN s.ODI_Avg > 0 THEN 1 ELSE 0 END) +
                                            (CASE WHEN s.T20_Avg > 0 THEN 1 ELSE 0 END),
                                        0),
                                        2
                                    ) AS Overall_Avg
                                    from ind_plyr_id as i
                                    inner join ind_plyr_id_stat as s
                                    on i.id = s.player_id
                                    where (
                                        (case when s.Test_Runs > 0 then 1 else 0 end) +
                                        (case when s.ODI_Runs > 0 then 1 else 0 end) +  
                                        (case when s.T20_Runs > 0 then 1 else 0 end) 
                                    ) >= 2;
                                """)
                st.table(df)


        # Qn12: Analyze each international team's performance when playing at home versus playing away
        if select_Query == pg3_queries[11]:
            if st.button("Run Query"):
                df = mydb_query("""
                                With match_result as (
                                    select distinct
                                        r.team1_Name,
                                        r.team2_Name,
                                        r.status,
                                        v.country,
                                        
                                        case
                                            when r.team1_Name = v.country then r.team1_Name
                                            when r.team2_Name = v.country then r.team2_Name
                                            else null
                                        end as home_team,
                                        
                                        case
                                            when r.team1_Name = v.country then r.team2_Name
                                            when r.team2_Name = v.country then r.team1_Name
                                            else null
                                        end as away_team,
                                        
                                        case
                                            when r.status like concat (r.team1_Name, "%") then r.team1_Name
                                            when r.status like concat (r.team2_Name, "%") then r.team2_Name
                                            else null
                                        end as winner
                                        from recent_matches as r inner join venue_info as v
                                        on r.city = v.city
                                )    
                                select 
                                    country,
                                    count(*) as total_matches,
                                    sum(case when winner = home_team then 1 else 0 end) as home_wins,
                                    sum(case when winner = away_team then 1 else 0 end) as away_wins
                                from match_result where home_team is not null
                                group by country
                                order by country asc;
                                """)
                st.table(df)

        # Qn13: batting partnerships where two batsmen scored a combined total of 100 or more runs 
        if select_Query == pg3_queries[12]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select * from partnership_stat
                                where totalruns > 100;
                                """)
                st.table(df)

        # Qn14: bowling performance at different venues (at least 3 matches played and 4 overs bowled per match)
        if select_Query == pg3_queries[13]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select 
                                name,
                                count(*) as matches_played,
                                sum(overs) as total_overs,
                                round(avg(economy), 2) as avg_eco,
                                sum(wickets) as total_wkts
                                from gt_bowl_ahmd
                                where overs >= 4
                                group by name
                                having matches_played >=3
                                order by total_wkts desc;
                                """)
                st.table(df)

        # Qn15: Close Matches, A close match is defined as one decided by less than 50 runs OR less than 5 wickets
        if select_Query == pg3_queries[14]:
            if st.button("Run Query"):
                df = mydb_query("""
                                SELECT *
                                FROM (
                                    SELECT
                                        match_Desc,
                                        team1_Name,
                                        team2_Name,
                                        
                                        CASE
                                            WHEN status LIKE CONCAT(team1_name, '%') THEN team1_name
                                            WHEN status LIKE CONCAT(team2_name, '%') THEN team2_name
                                            ELSE NULL
                                        END AS winning_team, 
                                        
                                        REGEXP_SUBSTR(status, 'runs|wkts') AS win_type,
                                        CAST(REGEXP_SUBSTR(status, '[0-9]+') AS UNSIGNED) AS margin
                                        
                                    FROM recent_matches
                                    WHERE status LIKE '%won by%'
                                ) AS sub
                                WHERE 
                                    (win_type = 'runs' AND margin < 50)
                                OR (win_type = 'wkts' AND margin < 5);
                                """)
                st.table(df)

        #Qn16: Best strike rate among bowlers with more than 85 wickets
        if select_Query == pg3_queries[15]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select * from bowler_stat 
                                where Wkts > 85
                                order by SR asc;
                                """)
                st.table(df)


        # Qn17: Investigate whether winning the toss gives teams an advantage in winning matches
        if select_Query == pg3_queries[16]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select
                                    decision,
                                    count(*) as total_matches,
                                    sum(case when toss_winner = match_winner then 1 else 0 end) as winning,
                                    round(100 * sum(case when toss_winner = match_winner then 1 else 0 end) / count(*), 2) as winning_percentage
                                from(

                                    select 
                                    case 
                                        when t.toss like concat (m.team1_Name, "%") then m.team1_Name
                                        when t.toss like concat (m.team2_Name, "%") then m.team2_Name
                                    end as toss_winner, 

                                    case
                                        when t.toss like "%bowl%" then "bowl_first"
                                        when t.toss like "%bat%" then "bat"
                                        else "unknown"
                                    end as decision,

                                    case 
                                        when m.status like concat (m.team1_Name, "%") then m.team1_Name
                                        when m.status like concat (m.team2_Name, "%") then m.team2_Name
                                    end as match_winner
                                    from recent_matches as m inner join recent_match_toss as t
                                    on m.match_Id = t.match_Id where state ="Complete") as sub
                                group by decision;
                                """)
                st.table(df)


        # Qn18: Find the most economical bowlers in limited-overs cricket (T20)
        if select_Query == pg3_queries[17]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select * from bowler_stat
                                order by Econ asc
                                limit 20;
                                """)
                st.table(df)

        # Qn19: Which batsmen are most consistent in their scoring (Using AVG & SD)
        if select_Query == pg3_queries[18]:
            if st.button("Run Query"):
                df = mydb_query("""
                                SELECT 
                                    name,
                                    round(AVG(score), 2) AS avg_runs,
                                    round(STDDEV_POP(score), 2) AS gt_run_sd
                                FROM (
                                    SELECT id, name, match1 AS score FROM gt_run_sd
                                    UNION ALL SELECT id, name, match2 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match3 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match4 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match5 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match6 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match7 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match8 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match9 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match10 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match11 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match12 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match13 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match14 FROM gt_run_sd
                                    UNION ALL SELECT id, name, match15 FROM gt_run_sd
                                ) t
                                WHERE score > 5
                                GROUP BY name
                                HAVING COUNT(score) > 10
                                ORDER BY gt_run_sd ASC;
                                """)
                st.table(df)


        # Qn20: Matches played across formats and batting average (min 20 combined)
        if select_Query == pg3_queries[19]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select  
                                    i.Name,
                                    m.Test_Matches,
                                    m.Test_Avg,
                                    m.ODI_Matches,
                                    m.ODI_Avg,
                                    m.T20_Matches,
                                    m.T20_Avg
                                from 
                                    all_player_match_stat as m 
                                    inner join
                                    ind_plyr_id as i on m.player_id  = i.id
                                where (m.Test_Matches + m.ODI_Matches + m.T20_Matches) > 20;
                                """)
                st.table(df)



        # Qn21: Comprehensive performance ranking system for players
        if select_Query == pg3_queries[20]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select
                                name,
                                country,
                                runs,
                                strike_rate,
                                wickets,
                                economy,
                                round((runs * 0.01) + (strike_rate * 0.3), 1) as Batting_points,
                                round(
                                    case
                                        when wickets = 0 and economy =0 then 0
                                        else (wickets * 2) +  ((12 - economy) * 2)
                                    end
                                , 1) as Bowling_points,
                                round((runs * 0.01) + (strike_rate * 0.3) + 
                                        case
                                            when wickets = 0 and economy =0 then 0
                                            else (wickets * 2) +  ((12 - economy) * 2)
                                        end
                                , 1)as Total_points
                                from performance_ranking
                                order by Total_points desc;
                                """)
                st.table(df)


        # Qn22: head-to-head match prediction analysis between teams 
        if select_Query == pg3_queries[21]:
            if st.button("Run Query"):
                df = mydb_query("""
                                    WITH match_results AS (
                                        SELECT 
                                            LEAST(team1_short, team2_short) AS team_a,
                                            GREATEST(team1_short, team2_short) AS team_b,
                                            CASE
                                                WHEN status LIKE CONCAT(team1, ' won%') THEN team1_short
                                                WHEN status LIKE CONCAT(team2, ' won%') THEN team2_short
                                                ELSE NULL
                                            END AS winner,
                                            CASE
                                                WHEN status LIKE '%won by% run%' 
                                                THEN CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(status, ' run', 1), 'won by ', -1) AS UNSIGNED)
                                                ELSE NULL
                                            END AS run_margin,
                                            CASE
                                                WHEN status LIKE '%won by% wkt%' 
                                                THEN CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(status, ' wkt', 1), 'won by ', -1) AS UNSIGNED)
                                                ELSE NULL
                                            END AS wkt_margin
                                        FROM ipl25
                                        WHERE status LIKE '%won by%'
                                    ),
                                    agg AS (
                                        SELECT 
                                            team_a, team_b,
                                            COUNT(*) AS total_matches,
                                            SUM(CASE WHEN winner = team_a THEN 1 ELSE 0 END) AS wins_team_a,
                                            SUM(CASE WHEN winner = team_b THEN 1 ELSE 0 END) AS wins_team_b,
                                            AVG(CASE WHEN winner = team_a THEN run_margin END) AS avg_run_margin_a,
                                            AVG(CASE WHEN winner = team_b THEN run_margin END) AS avg_run_margin_b,
                                            AVG(CASE WHEN winner = team_a THEN wkt_margin END) AS avg_wkt_margin_a,
                                            AVG(CASE WHEN winner = team_b THEN wkt_margin END) AS avg_wkt_margin_b
                                        FROM match_results
                                        GROUP BY team_a, team_b
                                    )
                                    SELECT *,
                                        ROUND(100.0 * wins_team_a / total_matches, 2) AS win_pct_team_a,
                                        ROUND(100.0 * wins_team_b / total_matches, 2) AS win_pct_team_b
                                    FROM agg
                                    WHERE total_matches >= 2
                                    ORDER BY total_matches DESC;
                                """)
                st.table(df)
                
        # Qn23: Analyze recent player form and momentum. For each player's last 10 batting performances 
        if select_Query == pg3_queries[22]:
            if st.button("Run Query"):
                df = mydb_query("""
                                select * from gt_bat_momentum;
                                """)
                st.table(df)

        # Qn24: Study successful batting partnerships to identify the best player combinations
        if select_Query == pg3_queries[23]:
            if st.button("Run Query"):
                df = mydb_query("""
                                SELECT 
                                    LEAST(bat1name, bat2name) AS player1,
                                    GREATEST(bat1name, bat2name) AS player2,
                                    COUNT(*) AS total_partnerships,
                                    SUM(totalruns) as total_runs,
                                    ROUND(AVG(totalruns), 2) AS avg_runs,
                                    SUM(CASE WHEN totalruns >= 50 THEN 1 ELSE 0 END) AS fifty_plus_count,
                                    MAX(totalruns) AS highest_score,
                                    ROUND(100.0 * SUM(CASE WHEN totalruns >= 50 THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate
                                FROM gt_bat_partnership
                                GROUP BY 
                                    LEAST(bat1name, bat2name), 
                                    GREATEST(bat1name, bat2name)
                                HAVING COUNT(*) >= 5
                                ORDER BY success_rate DESC, avg_runs DESC;
                                """)
                st.table(df)


        # Qn25: Perform a time-series analysis of player performance evolution
        if select_Query == pg3_queries[24]:
            if st.button("Run Query"):
                df = mydb_query("""
                                WITH table_1 AS (
                                    -- Step 1: Assign quarters (every 3 matches)
                                    SELECT
                                        id,
                                        name,
                                        runs,
                                        strkRate,
                                        match_no,
                                        CEIL(match_no/3.0) AS qtr
                                    FROM gt_bat_25q
                                ),

                                qtr_summary AS (
                                    -- Step 2: Calculate quarterly averages
                                    SELECT
                                        id,
                                        qtr,
                                        COUNT(*) AS matches_in_qtr,
                                        AVG(runs) AS avg_runs,
                                        AVG(strkRate) AS avg_strkRate
                                    FROM table_1
                                    GROUP BY id, qtr
                                ),

                                player_valid AS (
                                    -- Step 3: Keep only players with >=4 quarters and >=3 matches per quarter
                                    SELECT id
                                    FROM qtr_summary
                                    where avg_runs > 0
                                    GROUP BY id
                                    HAVING COUNT(*) >= 5
                                    AND min(matches_in_qtr) >= 3
                                ),

                                quarter_trends AS (
                                    -- Step 4: Calculate quarter-to-quarter changes and trends
                                    SELECT
                                        q.id,
                                        q.qtr,
                                        q.avg_runs,
                                        q.avg_strkRate,
                                        q.avg_runs - LAG(q.avg_runs) OVER (PARTITION BY q.id ORDER BY q.qtr) AS runs_change,
                                        q.avg_strkRate - LAG(q.avg_strkRate) OVER (PARTITION BY q.id ORDER BY q.qtr) AS strkRate_change,
                                        CASE  
                                            WHEN (q.avg_runs - LAG(q.avg_runs) OVER (PARTITION BY q.id ORDER BY q.qtr)) > 5 THEN 'Improving'
                                            WHEN (q.avg_runs - LAG(q.avg_runs) OVER (PARTITION BY q.id ORDER BY q.qtr)) < -5 THEN 'Declining'
                                            ELSE 'Stable'
                                        END AS runs_trend,
                                        CASE  
                                            WHEN (q.avg_strkRate - LAG(q.avg_strkRate) OVER (PARTITION BY q.id ORDER BY q.qtr)) > 5 THEN 'Improving'
                                            WHEN (q.avg_strkRate - LAG(q.avg_strkRate) OVER (PARTITION BY q.id ORDER BY q.qtr)) < -5 THEN 'Declining'
                                            ELSE 'Stable'
                                        END AS strkRate_trend
                                    FROM qtr_summary q
                                    JOIN player_valid p
                                    ON q.id = p.id
                                ),

                                career_phase AS (
                                    -- Step 5: Determine overall career trajectory
                                    SELECT
                                        id,
                                        SUM(CASE WHEN runs_trend='Improving' THEN 1 ELSE 0 END) AS improving_qtrs,
                                        SUM(CASE WHEN runs_trend='Declining' THEN 1 ELSE 0 END) AS declining_qtrs
                                    FROM quarter_trends
                                    GROUP BY id
                                ),

                                -- Final output: quarterly trends + overall career phase
                                final as (SELECT
                                    qt.id,
                                    qt.qtr,
                                    qt.avg_runs,
                                    qt.avg_strkRate,
                                    qt.runs_change,
                                    qt.strkRate_change,
                                    qt.runs_trend,
                                    qt.strkRate_trend,
                                    CASE
                                        WHEN cp.improving_qtrs > cp.declining_qtrs THEN 'Career Ascending'
                                        WHEN cp.declining_qtrs > cp.improving_qtrs THEN 'Career Declining'
                                        ELSE 'Career Stable'
                                    END AS career_phase
                                FROM quarter_trends qt
                                JOIN career_phase cp
                                ON qt.id = cp.id
                                ORDER BY qt.id, qt.qtr)

                                select distinct
                                    qt.id,
                                    p.name,
                                    qt.qtr,
                                    qt.avg_runs,
                                    qt.avg_strkRate,
                                    qt.runs_change,
                                    qt.strkRate_change,
                                    qt.runs_trend,
                                    qt.strkRate_trend,
                                    qt.career_phase
                                from final qt
                                JOIN table_1 p
                                ON qt.id = p.id;
                                """)
                st.table(df)




