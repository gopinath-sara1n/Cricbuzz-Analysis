import streamlit as st
import pandas as pd
import pymysql
import json

st.set_page_config(page_title="CRUD Operations", page_icon="🛠️", layout="wide")
# MySQL connection function
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Qwerty@123",
        database="cricbuzz_db"
    )

# CREATE, INSERT, DELETE QUERY
def run_cid(query, value = None):
    conn = get_connection()
    cursor = conn.cursor()
    if value:
          cursor.execute(query, value)
    else:
          cursor.execute(query)
    conn.commit()
    conn.close()

# SELECT QUERY
def run_select(query):
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
    
def app():    
        #Title
        st.title("CRUD Operaton")

        #Options
        pg4_queries = ["🆕 Create | Add new data",
                    "📖 Read | Retrieve/view data",
                    "✏️ Update | Modify existing data",
                    "🗑️ Delete | Remove data"]

        #Selectbox
        select_Query = st.selectbox(
            "Select a Query:",
            pg4_queries)

        #==============================
        # 🆕 Create | Add new data
        #==============================

        if select_Query == pg4_queries[0]:
                st.subheader("🆕 Create Record")
                id = st.number_input("🆔 Player ID: ", step=1)
                pname = st.text_input("🏏 Player Name: ")
                matches = st.number_input("🎯 Matches: ", step=25)
                innings = st.number_input("📝 Innings: ", step=30)
                runs = st.number_input("🔥 Runs: ", step=500)
                average = st.number_input("📊 Average: ", step=10.11, format="%.2f")
                if st.button("✅ Submit"):
                    try: 
                        query = """INSERT INTO cricbuzz_db.for_crud (ID, Name, Matches, Innings, Runs, Average)
                                    VALUES (%s, %s, %s, %s, %s, %s);"""
                        value = (id, pname, matches, innings, runs, average)
                        run_cid(query, value)
                        st.write(f"✅ Added {pname} Successfully")
                    except:
                        st.warning("⚠️ Player ID Needs to be Unique Extry")
                        st.stop()

        #==============================
        # 📖 Read | Retrieve/view data
        #==============================

        if select_Query == pg4_queries[1]:
                st.subheader("📖 Read Record")
                if st.button("Run Query"):
                    df = run_select("SELECT * FROM for_crud;")
                    st.table(df)

        #==============================
        # ✏️ Update | Modify existing data
        #==============================

        if select_Query == pg4_queries[2]:
                st.subheader("✏️ Update Record")
                p_list = run_select("SELECT * FROM for_crud;")
                if p_list.empty:
                    st.warning("⚠️ No records found to update.")
                else:
                    ID = st.selectbox("Select Player ID to Update", p_list, index=None)
                    if ID:
                        pname = st.text_input("🏏 Player Name: ")
                        matches = st.number_input("🎯 Matches: ", step=25)
                        innings = st.number_input("📝 Innings: ", step=30)
                        runs = st.number_input("🔥 Runs: ", step=500)
                        average = st.number_input("📊 Average: ", step=10.11, format="%.2f")
                        if st.button("✅ Update"):
                                query = """UPDATE cricbuzz_db.for_crud 
                                            SET Name = %s, Matches = %s, Innings = %s, Runs = %s, Average = %s 
                                            WHERE ID = %s;"""
                                value = (pname, matches, innings, runs, average, ID)
                                run_cid(query, value)
                                st.write(f"✅ Updated ID: {ID} as {pname} Successfully")
                

        #=========================
        # 🗑️ Delete | Remove data
        #=========================

        if select_Query == pg4_queries[3]:
                st.subheader("🗑️ Delete Record")
                p_list = run_select("SELECT * FROM for_crud;")
                if p_list.empty:
                    st.warning("⚠️ No records found to update.")
                else:
                    ID = st.selectbox("Select Player ID to Delete", p_list, index=None)
                    if ID:
                        st.warning(f"⚠️ You are about to delete ID: {ID} Records from the table")
                        if st.button("✅ Delete"):
                            query = """DELETE FROM cricbuzz_db.for_crud 
                                        WHERE ID = %s;"""
                            value = (ID)
                            run_cid(query, value)
                            st.write(f"✅ Deleted  ID: {ID} Successfully")        

