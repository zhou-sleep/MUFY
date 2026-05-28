import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import hashlib

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Sunway Club Hub Pro",
    page_icon="🏆",
    layout="wide"
)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("sunway_club_pro.db", check_same_thread=False)
c = conn.cursor()

# USERS (hashed password + role)
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'student'
)
''')

# CLUBS
c.execute('''
CREATE TABLE IF NOT EXISTS clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    category TEXT
)
''')

# TRIALS
c.execute('''
CREATE TABLE IF NOT EXISTS trials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    club TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT
)
''')

# POSTS / MATCHING
c.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    sport TEXT,
    message TEXT,
    created_at TEXT
)
''')

conn.commit()

# =========================
# SECURITY
# =========================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# AUTH
# =========================

def register_user(username, password):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, hash_password(password)))
        conn.commit()
        return True
    except:
        return False


def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()

# =========================
# LOGIN PAGE
# =========================
if not st.session_state.logged_in:
    st.title("🏆 Sunway Club Hub Pro")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(u, p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.success("Welcome back!")
                st.rerun()
            else:
                st.error("Invalid login")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if register_user(u, p):
                st.success("Account created")
            else:
                st.error("Username exists")

# =========================
# MAIN APP
# =========================
else:
    st.sidebar.title(f"👤 {st.session_state.user}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Clubs", "Trials", "Tournaments", "Matchmaking", "Analytics"]
    )

    # =========================
    # DASHBOARD
    # =========================
    if page == "Dashboard":
        st.title("📊 Dashboard")

        col1, col2, col3 = st.columns(3)

        trials = pd.read_sql_query("SELECT COUNT(*) as c FROM trials WHERE username=?",
                                   conn, params=(st.session_state.user,))
        posts = pd.read_sql_query("SELECT COUNT(*) as c FROM posts WHERE username=?",
                                  conn, params=(st.session_state.user,))

        col1.metric("Trials Joined", int(trials['c'][0]))
        col2.metric("Posts", int(posts['c'][0]))
        col3.metric("Active Clubs", "5+")

    # =========================
    # CLUBS (ADVANCED)
    # =========================
    elif page == "Clubs":
        st.title("📚 Clubs Explorer")

        clubs = [
            ("Basketball", "Sports", "Team coordination + fitness"),
            ("Badminton", "Sports", "Speed + reflex training"),
            ("Robotics", "Tech", "AI + engineering projects"),
            ("Debate", "Academic", "Critical thinking + speaking"),
            ("Music", "Arts", "Performance + creativity")
        ]

        for name, cat, desc in clubs:
            with st.expander(f"{name} ({cat})"):
                st.write(desc)

                col1, col2 = st.columns(2)

                if col1.button(f"Join Trial - {name}"):
                    c.execute("INSERT INTO trials (username, club, created_at) VALUES (?, ?, ?)",
                              (st.session_state.user, name, str(datetime.now())))
                    conn.commit()
                    st.success("Trial booked")

                if col2.button(f"View Stats - {name}"):
                    st.info("Popularity: High 🔥 | Difficulty: Medium")

    # =========================
    # TRIALS
    # =========================
    elif page == "Trials":
        st.title("📝 My Trials")

        df = pd.read_sql_query(
            "SELECT club, status, created_at FROM trials WHERE username=? ORDER BY id DESC",
            conn, params=(st.session_state.user,)
        )

        st.dataframe(df, use_container_width=True)

    # =========================
    # TOURNAMENTS
    # =========================
    elif page == "Tournaments":
        st.title("🏆 Tournament Hub")

        tournaments = [
            {"name": "Basketball 3v3", "status": "Open"},
            {"name": "Badminton Cup", "status": "Ongoing"},
            {"name": "Valorant Clash", "status": "Upcoming"}
        ]

        for t in tournaments:
            with st.container():
                st.subheader(t["name"])
                st.caption(f"Status: {t['status']}")
                st.button(f"Join {t['name']}")

    # =========================
    # MATCHMAKING (ADVANCED)
    # =========================
    elif page == "Matchmaking":
        st.title("🤝 Smart Matchmaking")

        sport = st.selectbox("Choose Sport", ["Basketball", "Badminton", "Football", "Gaming"])
        level = st.selectbox("Skill Level", ["Beginner", "Intermediate", "Advanced"])
        msg = st.text_area("Looking for...")

        if st.button("Post Match Request"):
            c.execute(
                "INSERT INTO posts (username, sport, message, created_at) VALUES (?, ?, ?, ?)",
                (st.session_state.user, sport, msg, str(datetime.now())))
            conn.commit()
            st.success("Posted!")

        st.subheader("Live Feed")

        posts = pd.read_sql_query("SELECT * FROM posts ORDER BY id DESC", conn)

        for _, r in posts.iterrows():
            score = "🔥 High Match" if r['sport'] == sport else "🙂 Possible Match"

            st.markdown("---")
            st.write(f"👤 {r['username']} | 🏅 {r['sport']} | {score}")
            st.write(r['message'])

    # =========================
    # ANALYTICS
    # =========================
    elif page == "Analytics":
        st.title("📊 Analytics")

        df = pd.read_sql_query("SELECT club FROM trials", conn)

        if not df.empty:
            st.bar_chart(df.value_counts())
        else:
            st.info("No data yet")

st.markdown("---")
st.caption("Sunway Club Hub Pro - Advanced Student Platform 🚀")