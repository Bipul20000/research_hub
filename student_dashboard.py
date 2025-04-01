import streamlit as st
from db_connection import get_db_connection, update_user_profile, send_collaboration_request, get_active_collaborations
import research_matching


def show():
    st.title("🎓 Student Dashboard")

    user = st.session_state.get("user")
    if not user:
        st.error("Unauthorized access. Please log in.")
        return

    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Profile",
        "🔍 Find Professors",
        "👥 Research Partners",
        "🤝 My Collaborations"
    ])

    # Profile Section
    with tab1:
        if not user.get("department") or not user.get("research_interests"):
            st.warning("⚠️ Your profile is incomplete! Please fill in the required details.")

            department = st.text_input("Department", value=user.get("department", ""))
            research_interests = st.text_area("Research Interests", value=user.get("research_interests", ""))

            # ✅ Fix for "None is not in list" error
            experience_level = user.get("experience_level", "beginner")  # Default to beginner
            if experience_level not in ["beginner", "intermediate", "advanced"]:
                experience_level = "beginner"

            experience_level = st.selectbox(
                "Experience Level", ["beginner", "intermediate", "advanced"],
                index=["beginner", "intermediate", "advanced"].index(experience_level)
            )

            if st.button("Save Profile"):
                success = update_user_profile(user["user_id"], department, research_interests, experience_level)
                if success:
                    # ✅ Update session state
                    st.session_state["user"].update({
                        "department": department,
                        "research_interests": research_interests,
                        "experience_level": experience_level
                    })
                    st.success("✅ Profile updated successfully!")
                    st.rerun()  # ✅ Updated rerun method
        else:
            st.write(f"📚 **Department:** {user['department']}")
            st.write(f"🔬 **Research Interests:** {user['research_interests']}")
            st.write(f"📈 **Experience Level:** {user['experience_level'].capitalize()}")

            if st.button("Edit Profile", key="edit_profile"):
                # Reset profile completion flags to allow editing
                st.session_state["user"].update({
                    "department": "",
                    "research_interests": "",
                    "experience_level": "beginner"
                })
                st.rerun()

    # Search Professors Section
    with tab2:
        # Show professor recommendations
        research_matching.show_professor_recommendations()

        st.divider()

        # Manual search
        st.subheader("🔍 Search for Professors")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        search_query = st.text_input("Enter Research Field or Professor Name")
        if search_query:
            cursor.execute(
                "SELECT * FROM users WHERE role='professor' AND (name LIKE %s OR research_interests LIKE %s)",
                ('%' + search_query + '%', '%' + search_query + '%')
            )
            professors = cursor.fetchall()

            if professors:
                for prof in professors:
                    with st.container():
                        st.markdown(f"### 👨‍🏫 {prof['name']}")
                        st.write(f"🏛️ **Department:** {prof['department']}")
                        st.write(f"🔬 **Research Interests:** {prof['research_interests']}")

                        if st.button(f"Request Collaboration with {prof['name']}", key=f"req_{prof['user_id']}"):
                            success = send_collaboration_request(user["user_id"], prof['user_id'])
                            if success:
                                st.success(f"✅ Collaboration request sent to {prof['name']}!")
                            else:
                                st.info("You've already sent a request to this professor.")
            else:
                st.warning("⚠️ No matching professors found.")

        cursor.close()  # ✅ Close cursor
        conn.close()  # ✅ Close DB connection

    # Find Research Partners Tab
    with tab3:
        research_matching.show_research_partners()

    # My Collaborations Tab
    with tab4:
        st.subheader("🤝 My Active Collaborations")
        collaborations = get_active_collaborations(user["user_id"], "student")

        if not collaborations:
            st.info(
                "You don't have any active collaborations yet. Use the 'Find Professors' tab to connect with professors.")
        else:
            for collab in collaborations:
                with st.container():
                    st.markdown(f"### 👨‍🏫 Collaborating with: {collab['name']}")
                    st.write(f"🏛️ **Department:** {collab['department']}")
                    st.write(f"🔬 **Research Interests:** {collab['research_interests']}")
                    st.divider()

        # Pending Requests
        st.subheader("⏳ Pending Collaboration Requests")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT cr.request_id, u.name, u.department, u.research_interests 
            FROM collaboration_requests cr 
            JOIN users u ON cr.professor_id = u.user_id 
            WHERE cr.student_id = %s AND cr.status = 'pending'
        """, (user["user_id"],))

        pending = cursor.fetchall()

        if not pending:
            st.info("You don't have any pending collaboration requests.")
        else:
            for req in pending:
                with st.container():
                    st.markdown(f"### ⏳ Request to: {req['name']}")
                    st.write(f"🏛️ **Department:** {req['department']}")
                    st.write(f"🔬 **Research Interests:** {req['research_interests']}")
                    st.write("**Status:** Pending")
                    st.divider()

        conn.close()

    # Logout Button (at the bottom of the dashboard)
    if st.button("🚪 Logout", key="logout_button"):
        st.session_state["user"] = None
        st.rerun()
