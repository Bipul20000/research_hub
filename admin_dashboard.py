import streamlit as st
from db_connection import get_db_connection

def show():
    st.title("🛠️ Admin Dashboard")

    user = st.session_state.get("user")
    if not user:
        st.error("Unauthorized access. Please log in.")
        return

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Add Research Highlights
    st.subheader("📌 Add Research Highlight")
    title = st.text_input("Research Title")
    summary = st.text_area("Summary")
    contributors = st.text_input("Contributors (comma-separated)")

    if st.button("Post Highlight"):
        cursor.execute("INSERT INTO research_highlights (title, summary, contributors, posted_by) VALUES (%s, %s, %s, %s)",
                       (title, summary, contributors, user["user_id"]))
        conn.commit()
        st.success("✅ Research Highlight Posted!")
        st.rerun()

    # Show Existing Highlights
    st.subheader("📜 College Research Highlights")
    cursor.execute("SELECT * FROM research_highlights ORDER BY date_posted DESC")
    highlights = cursor.fetchall()

    for highlight in highlights:
        st.markdown(f"### {highlight['title']}")
        st.write(f"📄 {highlight['summary']}")
        st.write(f"👥 Contributors: {highlight['contributors']}")
        st.write("---")

    conn.close()

    # Logout
    if st.button("🚪 Logout", key="logout_button"):
        st.session_state["user"] = None
        st.rerun()
