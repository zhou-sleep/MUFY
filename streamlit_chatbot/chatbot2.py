import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('sunway_club.db')
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, pfp TEXT, watchlist TEXT, circles TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS trial_forms 
                 (username TEXT, club TEXT, experience TEXT, notes TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS matchmaking 
                 (username TEXT, sport TEXT, time TEXT, location TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS marketplace 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, seller TEXT, item TEXT, price TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS reviews 
                 (club TEXT, username TEXT, rating INTEGER, comment TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# --- HARDCODED CLUB DATA & HISTORY ---
CLUBS_DATA = {
    "Basketball Club": {
        "created_by": "Alex Wong", "year": "2015",
        "why": "To foster teamwork and dominate the local university leagues.",
        "popularity": 95, "emoji": "🏀",
        "history": "🏆 Won the State Competitive Championship on May 25, 2025."
    },
    "Volleyball Club": {
        "created_by": "Sarah Lee", "year": "2017",
        "why": "To build lightning-fast reflexes and great court chemistry.",
        "popularity": 88, "emoji": "🏐",
        "history": "🥈 Runners-up in the National Inter-Varsity Games 2025."
    },
    "Badminton Club": {
        "created_by": "Dato Justin", "year": "2012",
        "why": "To carry on the Malaysian legacy of badminton excellence.",
        "popularity": 98, "emoji": "🏸",
        "history": "🏆 Clean sweep gold medals in MAPCU 2024."
    },
    "Football Club": {
        "created_by": "Coach Amran", "year": "2010",
        "why": "The ultimate beautiful game to unite students across campuses.",
        "popularity": 92, "emoji": "⚽",
        "history": "🏆 Sunway-Monash Derby Champions 2025."
    },
    "Esports Club": {
        "created_by": "Kevin 'Pro' Tan", "year": "2019",
        "why": "To provide a structured platform for competitive gaming and strategy.",
        "popularity": 96, "emoji": "🎮",
        "history": "🏆 Mobile Legends Campus Championship Winners 2025."
    },
    "Dev & Programming": {
        "created_by": "Dr. Lim", "year": "2018",
        "why": "To build real-world software solutions and ace hackathons.",
        "popularity": 90, "emoji": "💻",
        "history": "🏆 1st Place in Varsity Hackathon 2025."
    },
    "Startup & Business": {
        "created_by": "Chloe Siew", "year": "2016",
        "why": "Nurturing the next generation of Sunway unicorns and entrepreneurs.",
        "popularity": 85, "emoji": "🚀",
        "history": "💡 Secured RM50,000 seed funding for student projects in 2024."
    },
    "Finance Innovation": {
        "created_by": "Ryan Teoh", "year": "2021",
        "why": "Demystifying Web3, Trading, and Personal Wealth Management.",
        "popularity": 82, "emoji": "📈",
        "history": "🏆 National Bloomberg Trading Challenge Top 3 (2025)."
    },
    "Logic & Math Club": {
        "created_by": "Prof. Raman", "year": "2014",
        "why": "For minds that love breaking down complex riddles and theories.",
        "popularity": 74, "emoji": "🧮",
        "history": "🥇 Perfect scores in the International Youth Math Challenge 2025."
    },
    "Applied Science": {
        "created_by": "Dr. Farah", "year": "2015",
        "why": "Bridging laboratory research with real-world environmental impacts.",
        "popularity": 79, "emoji": "🧪",
        "history": "🌿 Received the National Green Campus Innovation Award 2025."
    }
}

# --- TOURNAMENTS DATA ---
TOURNAMENTS = [
    {"event": "Sunway Mega Inter-Club Games", "time": "June 15, 2026", "loc": "Sunway Sports Complex", "slots": "200 Participants Left"},
    {"event": "E-Sports Varsity Clash", "time": "July 02, 2026", "loc": "Jeffrey Cheah Hall", "slots": "64 Teams Max"},
    {"event": "Hackathon 2026", "time": "August 20, 2026", "loc": "Sunway Innovation Labs", "slots": "40 Teams Max"}
]

# --- STREAMLIT UI ---
st.set_page_config(page_title="Sunway Club Hub", page_icon="🏫", layout="wide")
st.title("🏫 Sunway Club & Sports Hub")

# Session State Management
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.pfp = "👤"

# --- SIDEBAR: AUTH & PROFILE ---
st.sidebar.header("👤 Account & Navigation")
if not st.session_state.logged_in:
    auth_mode = st.sidebar.radio("Action", ["Login", "Register"])
    user_input = st.sidebar.text_input("Username")
    pass_input = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button(auth_mode):
        conn = sqlite3.connect('sunway_club.db')
        c = conn.cursor()
        if auth_mode == "Register":
            try:
                c.execute("INSERT INTO users VALUES (?, ?, '👤', '', '')", (user_input, pass_input))
                conn.commit()
                st.sidebar.success("Registered successfully! Please login.")
            except:
                st.sidebar.error("Username already exists.")
        else:
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user_input, pass_input))
            if c.fetchone():
                st.session_state.logged_in = True
                st.session_state.username = user_input
                st.rerun()
            else:
                st.sidebar.error("Invalid Credentials.")
        conn.close()
else:
    st.sidebar.success(f"Logged in as: {st.session_state.username}")
    pfp_choice = st.sidebar.selectbox("Choose Profile Avatar", ["👤", "🦁", "⚽", "💻", "🚀"])
    if pfp_choice != st.session_state.pfp:
        st.session_state.pfp = pfp_choice
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- MAIN NAVIGATION TABS ---
tabs = st.tabs([
    "🗂️ Clubs Directory", "🧪 First Try (Trials)", "🏆 Tournaments & Leagues", 
    "🤝 Matchmaking", "🛍️ Marketplace & AI Chat", "🏅 Popularity & Watchlist"
])

# 1. CLUBS DIRECTORY
with tabs[0]:
    st.header("Explore Sunway Clubs")
    selected_club = st.selectbox("Select a Club to View", list(CLUBS_DATA.keys()))
    
    club_info = CLUBS_DATA[selected_club]
    
    col1, col2 = st.columns([1, 2])
    with col1:
        # Placeholder for dynamic picture representation
        st.subheader(f"{club_info['emoji']} {selected_club}")
        st.info(f"**Founded:** {club_info['year']}\n\n**Founder:** {club_info['created_by']}")
    
    with col2:
        st.markdown(f"### ❓ Why You Should Join\n>{club_info.get('why', '')}")
        st.markdown(f"### 📜 Club Honors & History\n{club_info['history']}")
        
        # Action Buttons
        if st.session_state.logged_in:
            if st.button(f"❤️ Add {selected_club} to Watchlist"):
                st.success(f"Added {selected_club} to your Watchlist!")
            if st.button(f"➕ Join {selected_club} Circle"):
                st.success(f"You are now a member of {selected_club}'s Student Circle!")
        else:
            st.warning("🔒 Please login to add to watchlist or join circles.")

    # Reviews Section
    st.write("---")
    st.subheader(f"💬 Student Reviews for {selected_club}")
    
    conn = sqlite3.connect('sunway_club.db')
    c = conn.cursor()
    
    if st.session_state.logged_in:
        with st.form(f"review_{selected_club}"):
            rating = st.slider("Rating", 1, 5, 5)
            comment = st.text_area("Write your club review...")
            if st.form_submit_button("Submit Review"):
                c.execute("INSERT INTO reviews VALUES (?, ?, ?, ?)", (selected_club, st.session_state.username, rating, comment))
                conn.commit()
                st.success("Review submitted!")
    
    # Display existing reviews
    reviews_df = pd.read_sql_query("SELECT username, rating, comment FROM reviews WHERE club=?", conn, params=(selected_club,))
    conn.close()
    
    if not reviews_df.empty:
        for idx, row in reviews_df.iterrows():
            st.markdown(f"**{row['username']}** ({'⭐'*row['rating']}): {row['comment']}")
    else:
        st.caption("No reviews yet. Be the first to review!")

# 2. FIRST TRY (TRIALS)
with tabs[1]:
    st.header("🏃 First Try: Join a Club Trial Session")
    st.write("Want to give a sport or club a test run? Fill out this quick form, and we'll instantly pitch it to the club managers.")
    
    if st.session_state.logged_in:
        with st.form("trial_form"):
            target_club = st.selectbox("Club to Try", list(CLUBS_DATA.keys()))
            experience = st.selectbox("Your Experience Level", ["Complete Beginner", "Intermediate", "Advanced/State Player"])
            notes = st.text_area("Any specific goals? (e.g., 'Looking to join the running trials to improve cardio')")
            
            if st.form_submit_button("Submit Application"):
                conn = sqlite3.connect('sunway_club.db')
                c = conn.cursor()
                c.execute("INSERT INTO trial_forms VALUES (?, ?, ?, ?)", (st.session_state.username, target_club, experience, notes))
                conn.commit()
                conn.close()
                st.success(f"🎯 Application sent to {target_club} managers! Keep an eye on your student email.")
    else:
        st.warning("🔒 Please log in to request a trial session.")

# 3. TOURNAMENTS & LEAGUES
with tabs[2]:
    st.header("🏆 Live Tournaments & Active Leagues")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🗓️ Upcoming Competitions")
        for t in TOURNAMENTS:
            with st.expander(t["event"]):
                st.write(f"📅 **Time:** {t['time']}")
                st.write(f"📍 **Location:** {t['loc']}")
                st.write(f"👥 **Capacity:** {t['slots']}")
                if st.button("Register Team", key=t["event"]):
                    st.success("Registration registered! Check 'My Schedule'.")

    with col2:
        st.subheader("🏛️ Leagues History & Hall of Fame")
        st.write("Tracking Sunway University's elite competitive history:")
        for club, details in CLUBS_DATA.items():
            st.markdown(f"**{club}**: {details['history']}")

# 4. MATCHMAKING
with tabs[3]:
    st.header("🤝 Peer Sports Matchmaking")
    st.write("Looking for a player to fill up a court session or a casual spar?")
    
    if st.session_state.logged_in:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Post a Match Session")
            m_sport = st.selectbox("Sport/Activity", ["Basketball", "Volleyball", "Badminton", "Football", "Gaming/Esports"])
            m_time = st.text_input("When? (e.g., Today 5 PM)")
            m_loc = st.text_input("Where? (e.g., Sunway College Roof Court)")
            
            if st.button("Broadcast Request"):
                conn = sqlite3.connect('sunway_club.db')
                c = conn.cursor()
                c.execute("INSERT INTO matchmaking VALUES (?, ?, ?, ?)", (st.session_state.username, m_sport, m_time, m_loc))
                conn.commit()
                conn.close()
                st.success("Broadcasted! Other students can now see your request below.")
        
        with col2:
            st.subheader("Available Matches Nearby")
            conn = sqlite3.connect('sunway_club.db')
            match_df = pd.read_sql_query("SELECT * FROM matchmaking", conn)
            conn.close()
            
            if not match_df.empty:
                for idx, row in match_df.iterrows():
                    st.warning(f"🏃 **{row['username']}** wants to play **{row['sport']}**!\n\n📅 {row['time']} | 📍 {row['location']}")
                    if st.button(f"Join Match with {row['username']}", key=f"match_{idx}"):
                        st.balloons()
                        st.success(f"Matched! Contacting {row['username']} for coordination.")
            else:
                st.caption("No active sports matching requests currently open.")
    else:
        st.warning("🔒 Please login to find sports peers.")

# 5. PEER MARKETPLACE & AI CHAT
with tabs[4]:
    st.header("🛒 Student Peer Marketplace")
    st.caption("Buy or sell sports jerseys, gear, textbooks, or tech items from fellow Sunwayians.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Items For Sale")
        conn = sqlite3.connect('sunway_club.db')
        if st.session_state.logged_in:
            with st.form("sell_item"):
                item_name = st.text_input("Item Name")
                price = st.text_input("Price (RM)")
                if st.form_submit_button("Post Listing"):
                    c = conn.cursor()
                    c.execute("INSERT INTO marketplace (seller, item, price) VALUES (?, ?, ?)", (st.session_state.username, item_name, price))
                    conn.commit()
                    st.success("Item Listed!")
        
        market_df = pd.read_sql_query("SELECT * FROM marketplace", conn)
        conn.close()
        
        if not market_df.empty:
            for idx, row in market_df.iterrows():
                st.write(f"📦 **{row['item']}** — **RM{row['price']}** (Seller: {row['seller']})")
        else:
            st.caption("No listings yet.")
            
    with col2:
        st.subheader("🤖 Ask Sunny (Your AI Club Guide)")
        ai_prompt = st.text_input("Ask anything (e.g., 'Which club won the state in 2025?')")
        if ai_prompt:
            # Rule-based AI Mock responding logically to inputs
            prompt_lower = ai_prompt.lower()
            if "basketball" in prompt_lower or "2025" in prompt_lower:
                st.write("🤖 **Sunny:** The Sunway Basketball Club proudly brought home the State Competitive Championship title on May 25, 2025!")
            elif "programming" in prompt_lower or "dev" in prompt_lower:
                st.write("🤖 **Sunny:** The Dev & Programming club was started by Dr. Lim in 2018 to win Hackathons!")
            else:
                st.write("🤖 **Sunny:** I recommend checking out the 'Clubs Directory' or joining the Basketball Club if you are looking for high energy!")

# 6. STANDINGS & COMMON ROOMS
with tabs[5]:
    st.header("📊 Popularity Standings & Common Area")
    
    # Standings Data Chart
    standings = [{"Club": k, "Popularity Score 🔥": v["popularity"]} for k, v in CLUBS_DATA.items()]
    df_standings = pd.DataFrame(standings).sort_values(by="Popularity Score 🔥", ascending=False)
    
    st.dataframe(df_standings, use_container_width=True, hide_index=True)
    
    st.write("---")
    st.subheader("🏢 Set Common Room Status")
    st.write("See how busy the club common lounge room is right now.")
    room_status = st.select_slider("Lounge Congestion Level", options=["Empty 🍃", "Chilled ☕", "Buzzing 🗣️", "Packed 💥"])
    st.info(f"Current Common Room Setting: **{room_status}**")