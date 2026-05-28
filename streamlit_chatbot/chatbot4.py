import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import hashlib
import os
import random

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Sunway Club Hub Ultimate+",
    page_icon="🏆",
    layout="wide"
)

# =========================
# DB
# =========================
conn = sqlite3.connect("sunway_ultimate_plus.db", check_same_thread=False)
c = conn.cursor()

# USERS
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
''')

# CLUBS
c.execute('''
CREATE TABLE IF NOT EXISTS clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    description TEXT
)
''')

# TRIALS
c.execute('''
CREATE TABLE IF NOT EXISTS trials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    club TEXT,
    created_at TEXT
)
''')

# POSTS (MATCH + CHAT)
c.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    category TEXT,
    message TEXT,
    created_at TEXT
)
''')

# CHAT SYSTEM
c.execute('''
CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    message TEXT,
    created_at TEXT
)
''')

conn.commit()

# =========================
# INIT CLUBS
# =========================
def init_clubs():
    c.execute("SELECT COUNT(*) FROM clubs")
    if c.fetchone()[0] == 0:
        clubs = [
            ("Basketball", "Sports", "Team sport training"),
            ("Badminton", "Sports", "Speed and reflex"),
            ("Football", "Sports", "Team coordination"),
            ("Volleyball", "Sports", "Spiking and teamwork"),
            ("Swimming", "Sports", "Endurance"),
            ("Table Tennis", "Sports", "Fast reaction"),
            ("Robotics", "Tech", "AI + engineering"),
            ("Coding Club", "Tech", "Python & projects"),
            ("Cyber Security", "Tech", "Hacking basics"),
            ("AI Society", "Tech", "Machine learning"),
            ("Debate", "Academic", "Speaking skills"),
            ("Entrepreneur", "Business", "Startup pitching"),
            ("Music", "Arts", "Band performance"),
            ("Photography", "Arts", "Photo skills"),
            ("Drama", "Arts", "Acting")
        ]
        c.executemany("INSERT INTO clubs (name, category, description) VALUES (?, ?, ?)", clubs)
        conn.commit()

init_clubs()

# =========================
# AUTH
# =========================
def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def register(u,p):
    try:
        c.execute("INSERT INTO users VALUES (NULL,?,?)", (u,hash_pw(p)))
        conn.commit()
        return True
    except:
        return False

def login(u,p):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,hash_pw(p)))
    return c.fetchone()

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# LOGIN
# =========================
if not st.session_state.user:
    st.title("🏆 Sunway Ultimate+ Login")

    tab1, tab2 = st.tabs(["Login","Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if login(u,p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Wrong login")

    with tab2:
        u = st.text_input("New user")
        p = st.text_input("New pass", type="password")
        if st.button("Create"):
            if register(u,p):
                st.success("Created")
            else:
                st.error("Exists")

# =========================
# APP
# =========================
else:
    st.sidebar.title(f"👤 {st.session_state.user}")

    page = st.sidebar.radio("Menu", ["Dashboard","Clubs","Trials","Matchmaking","Chat","AI Match","Tournaments","Profile"])

    # ---------------- DASHBOARD ----------------
    if page == "Dashboard":
        st.title("📊 Dashboard")

        t = pd.read_sql_query("SELECT COUNT(*) c FROM trials WHERE username=?", conn, params=(st.session_state.user,))
        p = pd.read_sql_query("SELECT COUNT(*) c FROM posts WHERE username=?", conn, params=(st.session_state.user,))

        col1,col2,col3 = st.columns(3)
        col1.metric("Trials", int(t['c'][0]))
        col2.metric("Posts", int(p['c'][0]))
        col3.metric("Clubs", "15+")

    # ---------------- CLUBS ----------------
    elif page == "Clubs":
        st.title("📚 Clubs")
        df = pd.read_sql_query("SELECT * FROM clubs", conn)

        for _,r in df.iterrows():
            with st.expander(f"{r['name']} ({r['category']})"):
                st.write(r['description'])

                if st.button(f"Join {r['name']}"):
                    c.execute("INSERT INTO trials VALUES (NULL,?,?,?)",
                              (st.session_state.user,r['name'],str(datetime.now())))
                    conn.commit()
                    st.success("Joined")

    # ---------------- MATCHMAKING ----------------
    elif page == "Matchmaking":
        st.title("🤝 Find Teammates")

        cat = st.selectbox("Category", ["Basketball","Badminton","Football","Gaming","Music"])
        msg = st.text_area("Message")

        if st.button("Post"):
            c.execute("INSERT INTO posts VALUES (NULL,?,?,?,?)",
                      (st.session_state.user,cat,msg,str(datetime.now())))
            conn.commit()
            st.success("Posted")

        df = pd.read_sql_query("SELECT * FROM posts ORDER BY id DESC", conn)

        for _,r in df.iterrows():
            st.markdown("---")
            st.write(f"👤 {r['username']} | 🏷️ {r['category']}")
            st.write(r['message'])

    # ---------------- CHAT ----------------
    elif page == "Chat":
        st.title("💬 Chat System")

        users = pd.read_sql_query("SELECT username FROM users", conn)
        receiver = st.selectbox("Chat with", users['username'].tolist())

        msg = st.text_input("Message")

        if st.button("Send"):
            c.execute("INSERT INTO chat VALUES (NULL,?,?,?,?)",
                      (st.session_state.user,receiver,msg,str(datetime.now())))
            conn.commit()

        st.subheader("Messages")
        chat = pd.read_sql_query("SELECT * FROM chat ORDER BY id DESC", conn)

        for _,r in chat.iterrows():
            if r['sender']==st.session_state.user or r['receiver']==st.session_state.user:
                st.write(f"{r['sender']} → {r['receiver']}: {r['message']}")

    # ---------------- AI MATCH ----------------
    elif page == "AI Match":
        st.title("🧠 AI Match System")

        df = pd.read_sql_query("SELECT * FROM posts", conn)

        if df.empty:
            st.info("No data")
        else:
            pick = df.sample(min(3,len(df)))

            for _,r in pick.iterrows():
                score = random.randint(70,99)
                st.success(f"Match Score: {score}% with {r['username']}")
                st.write(r['message'])

    # ---------------- TOURNAMENTS ----------------
    elif page == "Tournaments":
        st.title("🏆 Tournament Bracket")

        teams = ["Team A","Team B","Team C","Team D"]

        st.write("Semi Finals")
        st.write(f"{teams[0]} vs {teams[1]}")
        st.write(f"{teams[2]} vs {teams[3]}")

        st.write("Final")
        st.write("Winner TBD")

    # ---------------- PROFILE ----------------
    elif page == "Profile":
        st.title("👤 Profile")

        st.write("User:", st.session_state.user)

        t = pd.read_sql_query("SELECT COUNT(*) c FROM trials WHERE username=?", conn, params=(st.session_state.user,))
        st.metric("Trials", int(t['c'][0]))

        p = pd.read_sql_query("SELECT COUNT(*) c FROM posts WHERE username=?", conn, params=(st.session_state.user,))
        st.metric("Posts", int(p['c'][0]))

st.markdown("---")
st.caption("Sunway Ultimate+ 🚀 AI + Chat + Clubs + Matching System")