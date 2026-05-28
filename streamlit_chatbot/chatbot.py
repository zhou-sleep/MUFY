import streamlit as st
import pandas as pd
st.title("Sunway Club Activities Portal")

# Sample activities
activities = [
    "Basketball Training",
    "Robotics Workshop",
    "Coding Bootcamp",
    "Photography Club",
    "Debate Competition"
]

# Session state to store registrations
if "registered" not in st.session_state:
    st.session_state.registered = []

st.header("Available Activities")

# Show activities with buttons
for activity in activities:
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(activity)

    with col2:
        if st.button(f"Join {activity}"):
            if activity not in st.session_state.registered:
                st.session_state.registered.append(activity)
                st.success(f"You joined {activity}")
            else:
                st.warning("Already registered!")

st.divider()

st.header("Your Registered Activities")

if st.session_state.registered:
    for item in st.session_state.registered:
        st.write("✅", item)
else:
    st.info("No activities registered yet.")

# ---------------------------
# Session State Setup
# ---------------------------
if "posts" not in st.session_state:
    st.session_state.posts = []

if "registrations" not in st.session_state:
    st.session_state.registrations = {}

# ---------------------------
# CREATE NEW POST
# ---------------------------
st.header("📌 Create a New Post")

with st.form("post_form"):
    title = st.text_input("Event Title")
    category = st.selectbox("Category", ["Activity", "Tournament", "Workshop", "Other"])
    description = st.text_area("Description")
    date = st.date_input("Event Date")

    submitted = st.form_submit_button("Post Event")

    if submitted:
        if title:
            post = {
                "title": title,
                "category": category,
                "description": description,
                "date": str(date),
                "created_at": str(datetime.now())
            }
            st.session_state.posts.append(post)
            st.success("Event posted successfully!")
        else:
            st.error("Title is required!")

# ---------------------------
# VIEW POSTS
# ---------------------------
st.divider()
st.header("📋 All Club Events")

if not st.session_state.posts:
    st.info("No events posted yet.")
else:
    for i, post in enumerate(st.session_state.posts):
        st.subheader(f"{post['title']} ({post['category']})")
        st.write("📅 Date:", post["date"])
        st.write(post["description"])

        # Register button
        if st.button(f"Register for {post['title']}", key=f"reg_{i}"):
            if post["title"] not in st.session_state.registrations:
                st.session_state.registrations[post["title"]] = True
                st.success(f"Registered for {post['title']}")
            else:
                st.warning("Already registered!")

        st.divider()

# ---------------------------
# USER REGISTRATIONS
# ---------------------------
st.header("📝 My Registrations")

if not st.session_state.registrations:
    st.info("You haven't registered for any events yet.")
else:
    for event in st.session_state.registrations:
        st.write("✅", event)
import streamlit as st
from datetime import datetime

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Sunway Club Hub", page_icon="🎓", layout="wide")

st.title("🎓 Sunway Club Hub")
st.caption("Activities • Tournaments • Workshops • Community Board")

# ---------------------------
# SESSION STATE
# ---------------------------
if "posts" not in st.session_state:
    st.session_state.posts = []

if "registrations" not in st.session_state:
    st.session_state.registrations = set()

# ---------------------------
# CREATE POST (SIDEBAR)
# ---------------------------
st.sidebar.header("📌 Create Event")

with st.sidebar.form("create_event_form"):  # ✅ FIXED KEY
    title = st.text_input("Event Title")
    category = st.selectbox(
        "Category",
        ["🎯 Activity", "🏆 Tournament", "📚 Workshop", "✨ Other"]
    )
    description = st.text_area("Description")
    date = st.date_input("Event Date")

    submitted = st.form_submit_button("Post Event")

    if submitted:
        if title:
            st.session_state.posts.append({
                "title": title,
                "category": category,
                "description": description,
                "date": str(date),
                "created_at": str(datetime.now())
            })
            st.success("Event posted!")
        else:
            st.error("Title is required!")

# ---------------------------
# EVENTS DISPLAY
# ---------------------------
st.subheader("📋 Upcoming Events")

if not st.session_state.posts:
    st.info("No events yet. Create one from the sidebar 👈")
else:
    for i, post in enumerate(reversed(st.session_state.posts)):
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### {post['category']} {post['title']}")
                st.write(f"📅 **Date:** {post['date']}")
                st.write(post["description"])

            with col2:
                if post["title"] in st.session_state.registrations:
                    st.success("✅ Registered")
                else:
                    if st.button("Register", key=f"reg_{i}"):
                        st.session_state.registrations.add(post["title"])
                        st.rerun()

        st.markdown("---")

# ---------------------------
# REGISTRATIONS
# ---------------------------
st.subheader("📝 My Registrations")

if not st.session_state.registrations:
    st.info("No registrations yet.")
else:
    for event in st.session_state.registrations:
        st.markdown(f"- 🎟️ {event}")