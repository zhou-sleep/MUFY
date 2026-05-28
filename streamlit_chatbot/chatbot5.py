import streamlit as st
import pandas as pd
import sqlite3
import hashlib

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Sunway Club App",
    page_icon="🔥",
    layout="wide"
)

# =========================
# DB (safe for cloud)
# =========================
conn = sqlite3.connect("app.db", check_same_thread=False)
c = conn.cursor()

# USERS
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

# CLUBS
c.execute("""
CREATE TABLE IF NOT EXISTS clubs (
    name TEXT,
    category TEXT,
    description TEXT
)
""")

# INIT CLUBS (only once)
c.execute("SELECT COUNT(*) FROM clubs")
if c.fetchone()[0] == 0:
    clubs = [
        ("Basketball", "Sports", "Fast-paced team sport"),
        ("Badminton", "Sports", "Speed & reflex game"),
        ("Football", "Sports", "Team coordination"),
        ("Volleyball", "Sports", "Spike and teamwork"),
        ("Swimming", "Sports", "Water endurance"),
        ("Tennis", "Sports", "Precision sport"),
        ("Robotics", "Tech", "Build intelligent robots"),
        ("Coding Club", "Tech", "Python & projects"),
        ("AI Society", "Tech", "Machine learning"),
        ("Cyber Security", "Tech", "Ethical hacking"),
        ("Music Club", "Arts", "Band & performance"),
        ("Photography", "Arts", "Capture moments"),
        ("Drama Club", "Arts", "Acting & stage"),
        ("Debate Club", "Academic", "Public speaking"),
        ("Entrepreneur", "Business", "Startup ideas")
    ]
    c.executemany("INSERT INTO clubs VALUES (?,?,?)", clubs)
    conn.commit()

# =========================
# AUTH
# =========================
def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def register(u, p):
    try:
        c.execute("INSERT INTO users VALUES (?,?)", (u, hash_pw(p)))
        conn.commit()
        return True
    except:
        return False

def login(u, p):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (u, hash_pw(p)))
    return c.fetchone()

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# LOGIN PAGE
# =========================
if not st.session_state.user:

    st.title("🔥 Sunway Club App")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Wrong login")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if register(u, p):
                st.success("Account created")
            else:
                st.error("User exists")

# =========================
# MAIN APP (Instagram style)
# =========================
else:
    st.sidebar.title(f"👤 {st.session_state.user}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    st.title("🔥 Explore Clubs")

    search = st.text_input("🔍 Search clubs")

    df = pd.read_sql_query("SELECT * FROM clubs", conn)

    if search:
        df = df[df["name"].str.lower().str.contains(search.lower())]

    # FEED
    for _, row in df.iterrows():

        st.markdown("---")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(
                f"https://source.unsplash.com/400x300/?{row['name']}",
                use_container_width=True
            )

        with col2:
            st.subheader(row["name"])
            st.caption(row["category"])
            st.write(row["description"])

            if st.button(f"❤️ Join {row['name']}", key=row["name"]):
                st.success("Joined successfully!")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Sunway Club App 🚀 - Simple but clean MVP")