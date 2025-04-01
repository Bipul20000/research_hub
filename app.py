import streamlit as st
from db_connection import get_user, register_user, get_research_highlights, search_research_highlights

st.set_page_config(page_title="Collaborative Research Hub", layout="wide")

# ✅ Initialize session state variables safely
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"
if "user" not in st.session_state:
    st.session_state["user"] = "logged_out"  # Avoids resetting issues


# ✅ Navigation Function
def navigate_to(page):
    if st.session_state["current_page"] != page:
        st.session_state["current_page"] = page
        st.rerun()


# ✅ Top Navigation Bar
st.markdown(
    """
    <style>
    .stApp {
        background: url('https://t4.ftcdn.net/jpg/01/16/88/37/360_F_116883786_wuckft1sNw1ouQfJ6FuquZnxea3qBlxy.jpg') no-repeat center center fixed;
        background-size: cover;
    }

    /* Top Navigation Bar */
        .topnav {
            background-color: #4A90E2;  /* Changed to a deeper blue for better contrast */
            overflow: hidden;
            padding: 12px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 8px;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        }

        .topnav a {
            color: #ffffff;
            text-decoration: none;
            padding: 10px 18px;
            font-size: 18px;
            font-weight: bold;
            transition: background 0.3s ease, color 0.3s ease;
            border-radius: 6px;
        }

        .topnav a:hover {
            background-color: #2B6CB0;
            color: #ffffff;
        }

        /* Centered Main Heading */
        .center-content {
            text-align: center;
            margin-top: 20px;
        }

        .center-content h1 {
            font-size: 36px;
            font-weight: bold;
            color: #ffffff;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.2);
        }

        /* Research Highlight Cards */
        .highlight-card {
            background-color: #E3F2FD;  
            padding: 20px;
            color: #000000;
            border-radius: 12px;
            box-shadow: 3px 3px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            transition: transform 0.2s ease-in-out;
        }

        .highlight-card:hover {
            transform: scale(1.02);
            box-shadow: 3px 3px 20px rgba(0, 0, 0, 0.2);
        }

        .highlight-card h3 {
            font-size: 22px;
            font-weight: bold;
            color: #062842;
        }

        .highlight-card p {
            font-size: 16px;
            margin: 5px 0;
        }

        /* Styled Login/Register Button */
        .login-btn {
            background-color: #2B6CB0;
            color: white;
            padding: 12px 20px;
            font-size: 18px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.3s ease;
        }

        .login-btn:hover {
            background-color: #1A4D8F;
        }
    </style>

    <div class="topnav">
        <a href="?page=home">Home</a>
        <a href="?page=form">Login/Register</a>
        <a href="?page=about">ℹ️ About</a>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="center-content"><h1>Collaborative Research Hub</h1></div>', unsafe_allow_html=True)

# ✅ Handle Page Navigation
current_page = st.session_state.get("current_page", "home")

# ✅ Home Page
if current_page == "home":
    # Search bar for research works
    st.subheader("🔍 Search Research Works")
    search_term = st.text_input("Enter keywords to search for research")

    # Show research highlights (filtered if search term is provided)
    st.subheader("📢 Research Highlights")

    if search_term:
        highlights = search_research_highlights(search_term)
        if not highlights:
            st.info(f"No research highlights found for '{search_term}'.")
    else:
        highlights = get_research_highlights()

    if highlights:
        for highlight in highlights:
            st.markdown(
                f"""
                <div class="highlight-card">
                    <h3>{highlight['title']}</h3>
                    <p>{highlight['summary']}</p>
                    <p><strong>👨‍🏫 Contributors:</strong> {highlight['contributors']}</p>
                    <p><strong>📝 Posted by:</strong> {highlight['posted_by']} | 📅 {highlight['date_posted'].strftime('%d %B %Y')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No research highlights available yet. Stay tuned!")

    # Call to action for users to join
    st.markdown("### 🚀 Join our Research Community!")
    st.write("Connect with professors and students for collaborative research opportunities.")

    if st.button("Go to Login/Register"):
        navigate_to("form")

# ✅ Login/Register Page
elif current_page == "form":
    st.subheader("🔐 Login or Register")
    option = st.radio("Select an option", ["Login", "Register"])

    if option == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            user = get_user(email, password)
            if user:
                st.session_state["user"] = user  # ✅ Store logged-in user details
                st.success(f"Welcome, {user['name']}! 🎉")

                # Navigate to respective dashboard
                if user["role"] == "student":
                    navigate_to("student_dashboard")
                elif user["role"] == "professor":
                    navigate_to("professor_dashboard")
                elif user["role"] == "admin":
                    navigate_to("admin_dashboard")
            else:
                st.error("Invalid email or password. Please try again.")

    elif option == "Register":
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Register as", ["student", "professor", "admin"])

        if st.button("Sign Up"):
            success = register_user(name, email, password, role)
            if success:
                st.success("✅ Registration successful! You can now log in.")
                navigate_to("form")
            else:
                st.error("⚠️ Registration failed. Email may already exist.")

    if st.button("Back to Home"):
        navigate_to("home")

# ✅ Student Dashboard
elif current_page == "student_dashboard":
    import student_dashboard

    student_dashboard.show()

# ✅ Professor Dashboard
elif current_page == "professor_dashboard":
    import professor_dashboard

    professor_dashboard.show()

# ✅ Admin Dashboard
elif current_page == "admin_dashboard":
    import admin_dashboard

    admin_dashboard.show()

# ✅ Community Forum
elif current_page == "forum":
    import forum

    forum.show()

    if st.button("Back to Dashboard"):
        user = st.session_state.get("user")
        if user:
            if user["role"] == "student":
                navigate_to("student_dashboard")
            elif user["role"] == "professor":
                navigate_to("professor_dashboard")
            elif user["role"] == "admin":
                navigate_to("admin_dashboard")
        else:
            navigate_to("home")

# Add navigation to forum from dashboards
if st.session_state.get("user") and st.session_state.get("user") != "logged_out":
    if current_page in ["student_dashboard", "professor_dashboard", "admin_dashboard"]:
        st.sidebar.title("Navigation")
        if st.sidebar.button("🗣️ Community Forum"):
            navigate_to("forum")
