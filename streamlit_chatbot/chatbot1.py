import streamlit as st

import pandas as pd
import sqlite3
from datetime import datetime
# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Sunway Club Hub",
    page_icon="🏆",
    layout="wide"
)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("sunway_club.db", check_same_thread=False)
c = conn.cursor()

# Create tables
c.execute('''
CREATE TABLE IF NOT EXISTS trial_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    student_id TEXT,
    club TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS teammate_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    sport TEXT,
    message TEXT
)
''')

conn.commit()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🏫 Sunway Club Hub")
page = st.sidebar.radio(
    "Navigate",
    [
        "Home",
        "Club Information",
        "Trial Registration",
        "Sunway Tournament",
        "Find Teammates"
    ]
)

# =========================
# HOME PAGE
# =========================
if page == "Home":
    st.title("🏆 Sunway Club Hub")

    st.markdown("""
    Welcome to the **Sunway Club Hub** 🎉

    This platform helps Sunway students:
    - Explore different clubs
    - Register for club trials
    - Join tournaments
    - Find teammates and make new friends
    - Connect with other students through sports and activities
    """)

    st.image(
        "https://images.unsplash.com/photo-1529156069898-49953e39b3ac",
        use_container_width=True
    )

    st.subheader("✨ Features")

    col1, col2 = st.columns(2)

    with col1:
        st.info("📚 Club Information")
        st.info("📝 Trial Registration")

    with col2:
        st.info("🏆 Sunway Tournament")
        st.info("🤝 Find Teammates")

# =========================
# CLUB INFORMATION
# =========================
elif page == "Club Information":
    st.title("📚 Club Information")

    clubs = {
        "Basketball Club": {
            "Description": "Weekly basketball training for beginners and advanced players.",
            "Training": "Wednesday & Friday",
            "Location": "Sunway Sports Hall"
        },
        "Badminton Club": {
            "Description": "Competitive and casual badminton sessions.",
            "Training": "Tuesday & Thursday",
            "Location": "Sunway Indoor Court"
        },
        "Robotics Club": {
            "Description": "Learn robotics, coding and engineering projects.",
            "Training": "Saturday",
            "Location": "Engineering Lab"
        },
        "Debate Club": {
            "Description": "Improve public speaking and debate skills.",
            "Training": "Monday",
            "Location": "Lecture Hall 3"
        },
        "Music Club": {
            "Description": "Jam sessions, performances and music practice.",
            "Training": "Friday Evening",
            "Location": "Music Room"
        }
    }

    for club, info in clubs.items():
        with st.expander(f"{club}"):
            st.write(f"**Description:** {info['Description']}")
            st.write(f"**Training Days:** {info['Training']}")
            st.write(f"**Location:** {info['Location']}")

# =========================
# TRIAL REGISTRATION
# =========================
elif page == "Trial Registration":
    st.title("📝 Club Trial Registration")

    with st.form("trial_form"):
        name = st.text_input("Student Name")
        student_id = st.text_input("Student ID")

        club = st.selectbox(
            "Choose Club",
            [
                "Basketball Club",
                "Badminton Club",
                "Robotics Club",
                "Debate Club",
                "Music Club"
            ]
        )

        submitted = st.form_submit_button("Register")

        if submitted:
            c.execute(
                "INSERT INTO trial_registrations (name, student_id, club) VALUES (?, ?, ?)",
                (name, student_id, club)
            )
            conn.commit()

            st.success(f"✅ {name} successfully registered for {club}!")

    st.subheader("📋 Registered Students")

    registrations = pd.read_sql_query(
        "SELECT name, student_id, club FROM trial_registrations",
        conn
    )

    st.dataframe(registrations, use_container_width=True)

# =========================
# TOURNAMENT PAGE
# =========================
elif page == "Sunway Tournament":
    st.title("🏆 Sunway Tournament")

    tournaments = [
        {
            "Tournament": "Basketball 3v3",
            "Date": "15 June 2026",
            "Location": "Sunway Sports Hall"
        },
        {
            "Tournament": "Badminton Championship",
            "Date": "20 June 2026",
            "Location": "Indoor Court"
        },
        {
            "Tournament": "Valorant Tournament",
            "Date": "28 June 2026",
            "Location": "E-Sports Room"
        }
    ]

    for tournament in tournaments:
        st.card = st.container()

        with st.card:
            st.subheader(tournament["Tournament"])
            st.write(f"📅 Date: {tournament['Date']}")
            st.write(f"📍 Location: {tournament['Location']}")
            st.button(f"Join {tournament['Tournament']}")

# =========================
# FIND TEAMMATES
# =========================
elif page == "Find Teammates":
    st.title("🤝 Find Teammates & Make Friends")

    st.write("Find other students who enjoy the same sports and activities.")

    with st.form("teammate_form"):
        name = st.text_input("Your Name")

        sport = st.selectbox(
            "Sport / Activity",
            [
                "Basketball",
                "Badminton",
                "Volleyball",
                "Football",
                "Gaming",
                "Music"
            ]
        )

        message = st.text_area(
            "Message",
            placeholder="Example: Looking for basketball teammates for weekend games!"
        )

        post_button = st.form_submit_button("Post")

        if post_button:
            c.execute(
                "INSERT INTO teammate_posts (name, sport, message) VALUES (?, ?, ?)",
                (name, sport, message)
            )
            conn.commit()

            st.success("✅ Your post has been uploaded!")

    st.subheader("📢 Community Posts")

    posts = pd.read_sql_query(
        "SELECT name, sport, message FROM teammate_posts",
        conn
    )

    if not posts.empty:
        for index, row in posts.iterrows():
            st.markdown("---")
            st.write(f"👤 **{row['name']}**")
            st.write(f"🏅 Sport: {row['sport']}")
            st.write(f"💬 {row['message']}")
    else:
        st.info("No posts yet.")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Developed using Python & Streamlit 💻")