import streamlit as st
import hashlib
from database import get_user_by_email, create_user

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login function
def login():
    email = st.sidebar.text_input("Email", key="login_email")
    password = st.sidebar.text_input("Password", type="password", key="login_password")
    
    if st.sidebar.button("Login"):
        if not email or not password:
            st.sidebar.error("Please enter both email and password.")
            return
        
        user = get_user_by_email(email)
        if user and user['password'] == hash_password(password):
            st.session_state.user_id = user['id']
            st.session_state.username = user['name']
            st.session_state.role = user['role']
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.sidebar.error("Invalid email or password.")

# Signup function
def signup():
    with st.sidebar.form("signup_form"):
        st.subheader("Create Account")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        role = st.selectbox("Role", ["student", "professor", "admin"])
        department = st.text_input("Department")
        research_interests = st.text_area("Research Interests (comma separated)")
        
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not name or not email or not password or not role or not department:
                st.error("All fields are required except research interests.")
                return
                
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
                
            existing_user = get_user_by_email(email)
            if existing_user:
                st.error("Email already registered. Please login instead.")
                return
                
            # Create user
            hashed_password = hash_password(password)
            user_id = create_user(name, email, hashed_password, role, department, research_interests)
            
            if user_id:
                st.success("Account created successfully! Please login.")
            else:
                st.error("Error creating account. Please try again.")

# Check if user is authenticated
def is_authenticated():
    return st.session_state.get('authenticated', False)

# Logout function
def logout():
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.authenticated = False
    st.rerun()
