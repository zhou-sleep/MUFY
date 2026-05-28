import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import hashlib
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Sunway Club Hub Ultimate",
    page_icon="🏆",
    layout="wide"
)

# =========================
# FOLDER FOR UPLOADS
# =========================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("sunway_club_ultimate.db", check_same_thread=False)
c = conn.cursor()

# USERS
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    avatar TEXT
)
''')

# CLUBS (15 clubs)
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

# POSTS
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
# INIT 15 CLUBS (auto insert once)
# =========================
def init_clubs():
    c.execute("SELECT COUNT(*) FROM clubs")
    if c.fetchone()[0] == 0:
        clubs = [
            ("Basketball", "Sports", "Team coordination and fitness"),
            ("Badminton", "Sports", "Speed and reflex training"),
            ("Football", "Sports", "11v11 competitive matches"),
            ("Volleyball", "Sports", "Team strategy and spikes"),
            ("Table Tennis", "Sports", "Fast reaction sport"),
            ("Swimming", "Sports", "Endurance and technique"),

            ("Robotics", "Tech", "AI and engineering projects"),
            ("Coding Club", "Tech", "Python, Java, projects"),
            ("Cyber Security", "Tech", "Ethical hacking basics"),
            ("AI Society", "Tech", "Machine learning projects"),

            ("Debate Club", "Academic", "Public speaking skills"),
            ("Entrepreneur Club", "Business", "Startup and business pitching"),

            ("Music Club", "Arts", "Band and performance"),
            ("Photography", "Arts", "Photo editing and shooting"),
            ("Drama Club", "Arts", "Acting and stage performance")
        ]
        c.executemany("INSERT INTO clubs (name, category, description) VALUES (?, ?, ?)", clubs)
        conn.commit()

init_clubs()

# =========================
# SECURITY
# =========================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# =========================
# SESSION
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# AUTH
# =========================
def register_user(u, p):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (u, hash_password(p)))
        conn.commit()
        return True
    except:
        return False

def login_user(u, p):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (u, hash_password(p)))
    return c.fetchone()

# =========================
# LOGIN
# =========================
if not st.session_state.logged_in:
    st.title("🏆 Sunway Club Hub Ultimate")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(u, p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Wrong credentials")

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

    # avatar upload
    avatar = st.sidebar.file_uploader("Upload Profile Picture", type=["png","jpg","jpeg"])

    if avatar:
        path = os.path.join(UPLOAD_FOLDER, f"{st.session_state.user}.png")
        with open(path, "wb") as f:
            f.write(avatar.read())
        c.execute("UPDATE users SET avatar=? WHERE username=?", (path, st.session_state.user))
        conn.commit()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Clubs", "Trials", "Tournaments", "Matchmaking", "Profile"]
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

        col1.metric("Trials", int(trials['c'][0]))
        col2.metric("Posts", int(posts['c'][0]))
        col3.metric("Clubs", "15+")

    # =========================
    # CLUBS (15 clubs + images)
    # =========================
    elif page == "Clubs":
        st.title("📚 15 Clubs Explorer")

        df = pd.read_sql_query("SELECT * FROM clubs", conn)

        for _, row in df.iterrows():
            with st.container():
                st.subheader(f"{row['name']} ({row['category']})")
                st.write(row['description'])

                col1, col2 = st.columns(2)

                if col1.button(f"Join Trial - {row['name']}"):
                    c.execute("INSERT INTO trials (username, club, created_at) VALUES (?, ?, ?)",
                              (st.session_state.user, row['name'], str(datetime.now())))
                    conn.commit()
                    st.success("Trial joined")

                if col2.button(f"More Info - {row['name']}"):
                    st.info("This club is active and open for recruitment 🎯")

    # =========================
    # TRIALS
    # =========================
    elif page == "Trials":
        st.title("📝 My Trials")

        df = pd.read_sql_query("SELECT * FROM trials WHERE username=? ORDER BY id DESC",
                               conn, params=(st.session_state.user,))
        st.dataframe(df)

    # =========================
    # TOURNAMENTS
    # =========================
    elif page == "Tournaments":
        st.title("🏆 Tournaments")

        st.info("Upcoming competitions will be updated weekly 🔥")

        tournaments = ["Basketball 3v3", "Badminton Cup", "E-Sports Valorant"]

        for t in tournaments:
            st.subheader(t)
            st.button(f"Join {t}")

    # =========================
    # MATCHMAKING
    # =========================
    elif page == "Matchmaking":
        st.title("🤝 Find Teammates")

        sport = st.selectbox("Sport", ["Basketball","Badminton","Football","Gaming","Music"])
        msg = st.text_area("Looking for teammates")

        if st.button("Post"):
            c.execute("INSERT INTO posts (username, sport, message, created_at) VALUES (?, ?, ?, ?)",
                      (st.session_state.user, sport, msg, str(datetime.now())))
            conn.commit()
            st.success("Posted!")

        st.subheader("Community Feed")

        posts = pd.read_sql_query("SELECT * FROM posts ORDER BY id DESC", conn)

        for _, r in posts.iterrows():
            st.markdown("---")
            st.write(f"👤 {r['username']} | 🏅 {r['sport']}")
            st.write(r['message'])
            st.caption(r['created_at'])

    # =========================
    # PROFILE (with avatar)
    # =========================
    elif page == "Profile":
        st.title("👤 Profile")

        user = pd.read_sql_query("SELECT * FROM users WHERE username=?",
                                 conn, params=(st.session_state.user,))

        if not user.empty and user['avatar'][0]:
            st.image(user['avatar'][0], width=150)

        st.write(f"Username: {st.session_state.user}")

        trial_count = pd.read_sql_query("SELECT COUNT(*) as c FROM trials WHERE username=?",
                                        conn, params=(st.session_state.user,))
        st.metric("Trials", int(trial_count['c'][0]))

st.markdown("---")
st.caption("Sunway Club Hub Ultimate 🚀 - Advanced Student Platform with Profiles, Uploads & 15 Clubs")