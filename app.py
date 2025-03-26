import streamlit as st
import pandas as pd
from auth import login, signup, is_authenticated, logout
from profile import display_profile, edit_profile
from search import search_page
from forum import forum_page
from research import research_highlights
from admin import admin_dashboard
from collaboration import collaboration_requests
from database import init_connection

# Page configuration
st.set_page_config(
    page_title="Research Connect",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database connection
conn = init_connection()

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Sidebar navigation
def sidebar():
    st.sidebar.title("Research Connect")
    
    if not st.session_state.authenticated:
        st.sidebar.subheader("Login")
        auth_status = st.sidebar.radio("", ["Login", "Sign Up"])
        
        if auth_status == "Login":
            login()
        else:
            signup()
    else:
        st.sidebar.success(f"Logged in as: {st.session_state.username}")
        st.sidebar.button("Logout", on_click=logout)
        
        st.sidebar.header("Navigation")
        navigation = st.sidebar.selectbox(
            "Go to",
            ["Home", "My Profile", "Search", "Collaboration Requests", "Forum", "Research Highlights"] +
            (["Admin Dashboard"] if st.session_state.role == "admin" else [])
        )
        
        return navigation
    
    return "Home"

# Main app logic
def main():
    page = sidebar()
    
    if not st.session_state.authenticated and page != "Home":
        st.warning("Please login to access this feature.")
        page = "Home"
    
    if page == "Home":
        display_home()
    elif page == "My Profile":
        display_profile() if not st.sidebar.button("Edit Profile") else edit_profile()
    elif page == "Search":
        search_page()
    elif page == "Collaboration Requests":
        collaboration_requests()
    elif page == "Forum":
        forum_page()
    elif page == "Research Highlights":
        research_highlights()
    elif page == "Admin Dashboard" and st.session_state.role == "admin":
        admin_dashboard()

# Home page display
def display_home():
    st.title("Welcome to Research Connect")
    
    st.markdown("""
    ### Connect with the right research collaborators in your college
    
    Research Connect helps students and professors find the perfect research partners based on shared interests and complementary skills.
    
    **Key Features:**
    - 🔍 Find professors and students with matching research interests
    - 🤝 Send collaboration requests with just one click
    - 💬 Participate in research discussions in our community forum
    - 📊 Discover the latest research highlights from your college
    
    Get started by creating an account or logging in!
    """)
    
    # Display featured research highlights on homepage
    if st.session_state.authenticated:
        st.subheader("Featured Research Highlights")
        research_highlights(featured_only=True)

if __name__ == "__main__":
    main()
