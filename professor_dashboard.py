import streamlit as st
from db_connection import (
    get_db_connection, update_user_profile, update_request_status,
    get_active_collaborations, delete_collaboration
)


def show():
    st.title("👨‍🏫 Professor Dashboard")

    user = st.session_state.get("user")
    if not user:
        st.error("Unauthorized access. Please log in.")
        return

    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs([
        "👤 Profile",
        "📩 Collaboration Requests",
        "🤝 Active Collaborations"
    ])

    # Profile Section
    with tab1:
        if not user.get("department") or not user.get("research_interests"):
            st.warning("⚠️ Your profile is incomplete! Please fill in the required details.")
            department = st.text_input("Department", value=user.get("department", ""))
            research_interests = st.text_area("Research Interests", value=user.get("research_interests", ""))

            if st.button("Save Profile"):
                success = update_user_profile(user["user_id"], department, research_interests)
                if success:
                    st.session_state["user"].update({
                        "department": department,
                        "research_interests": research_interests
                    })
                    st.success("Profile updated successfully!")
                    st.rerun()
        else:
            st.write(f"📚 **Department:** {user['department']}")
            st.write(f"🔬 **Research Interests:** {user['research_interests']}")

            if st.button("Edit Profile", key="edit_profile"):
                # Reset profile completion flags to allow editing
                st.session_state["user"].update({
                    "department": "",
                    "research_interests": ""
                })
                st.rerun()

    # Collaboration Requests Section
    with tab2:
        st.subheader("📩 Pending Collaboration Requests")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT r.request_id, u.user_id AS student_id, u.name AS student_name, 
                   u.research_interests, u.department, u.experience_level
            FROM collaboration_requests r 
            JOIN users u ON r.student_id = u.user_id 
            WHERE r.professor_id = %s AND r.status = 'pending'
        """, (user["user_id"],))

        requests = cursor.fetchall()

        if requests:
            for req in requests:
                st.markdown(f"### 🎓 Request from: {req['student_name']}")
                st.write(f"🏛️ **Department:** {req['department']}")
                st.write(f"🔬 **Research Interests:** {req['research_interests']}")
                st.write(
                    f"📈 **Experience Level:** {req['experience_level'].capitalize() if req['experience_level'] else 'Not specified'}")

                col1, col2 = st.columns(2)
                if col1.button("✅ Accept", key=f"accept_{req['request_id']}"):
                    success = update_request_status(req['request_id'], 'accepted')
                    if success:
                        st.success("Collaboration Accepted!")
                    else:
                        st.error("Failed to accept collaboration.")
                    st.rerun()

                if col2.button("❌ Reject", key=f"reject_{req['request_id']}"):
                    success = update_request_status(req['request_id'], 'rejected')
                    if success:
                        st.error("Collaboration Rejected!")
                    else:
                        st.error("Failed to reject collaboration.")
                    st.rerun()

                st.divider()
        else:
            st.info("No pending requests.")

        # Search for students who haven't sent requests yet
        st.subheader("🔍 Browse Students by Research Interest")
        search_term = st.text_input("Enter Research Interest Keyword")

        if search_term:
            # Get all students with matching research interests who haven't sent requests
            cursor.execute("""
                SELECT u.user_id, u.name, u.department, u.research_interests, u.experience_level
                FROM users u
                LEFT JOIN collaboration_requests cr ON cr.student_id = u.user_id AND cr.professor_id = %s
                WHERE u.role = 'student' AND u.research_interests LIKE %s AND cr.request_id IS NULL
                ORDER BY u.name
            """, (user["user_id"], f'%{search_term}%'))

            students = cursor.fetchall()

            if students:
                for student in students:
                    st.markdown(f"### 🎓 {student['name']}")
                    st.write(f"🏛️ **Department:** {student['department']}")
                    st.write(f"🔬 **Research Interests:** {student['research_interests']}")
                    st.write(
                        f"📈 **Experience Level:** {student['experience_level'].capitalize() if student['experience_level'] else 'Not specified'}")
                    st.divider()
            else:
                st.info(f"No students found with research interests matching '{search_term}'.")

        conn.close()

    # Active Collaborations Section
    with tab3:
        st.subheader("🤝 Active Collaborations")
        collaborations = get_active_collaborations(user["user_id"], "professor")

        if not collaborations:
            st.info("You don't have any active collaborations yet.")
        else:
            for collab in collaborations:
                with st.container():
                    st.markdown(f"### 🎓 Collaborating with: {collab['name']}")
                    st.write(f"🏛️ **Department:** {collab['department']}")
                    st.write(f"🔬 **Research Interests:** {collab['research_interests']}")
                    st.write(
                        f"📈 **Experience Level:** {collab['experience_level'].capitalize() if collab['experience_level'] else 'Not specified'}")

                    # Add delete collaboration button
                    if st.button(f"End Collaboration with {collab['name']}", key=f"end_collab_{collab['request_id']}"):
                        if delete_collaboration(collab['request_id']):
                            st.success(f"Collaboration with {collab['name']} has been ended.")
                            st.rerun()

                    st.divider()

    # Logout Button (at the bottom of the dashboard)
    if st.button("🚪 Logout", key="logout_button"):
        st.session_state["user"] = None
        st.rerun()


# import streamlit as st
# from db_connection import get_db_connection, update_user_profile, update_request_status, get_active_collaborations
#
#
# def show():
#     st.title("👨‍🏫 Professor Dashboard")
#
#     user = st.session_state.get("user")
#     if not user:
#         st.error("Unauthorized access. Please log in.")
#         return
#
#     # Create tabs for different sections
#     tab1, tab2, tab3 = st.tabs([
#         "👤 Profile",
#         "📩 Collaboration Requests",
#         "🤝 Active Collaborations"
#     ])
#
#     # Profile Section
#     with tab1:
#         if not user.get("department") or not user.get("research_interests"):
#             st.warning("⚠️ Your profile is incomplete! Please fill in the required details.")
#             department = st.text_input("Department", value=user.get("department", ""))
#             research_interests = st.text_area("Research Interests", value=user.get("research_interests", ""))
#
#             if st.button("Save Profile"):
#                 success = update_user_profile(user["user_id"], department, research_interests)
#                 if success:
#                     st.session_state["user"].update({
#                         "department": department,
#                         "research_interests": research_interests
#                     })
#                     st.success("Profile updated successfully!")
#                     st.rerun()
#         else:
#             st.write(f"📚 **Department:** {user['department']}")
#             st.write(f"🔬 **Research Interests:** {user['research_interests']}")
#
#             if st.button("Edit Profile", key="edit_profile"):
#                 # Reset profile completion flags to allow editing
#                 st.session_state["user"].update({
#                     "department": "",
#                     "research_interests": ""
#                 })
#                 st.rerun()
#
#     # Collaboration Requests Section
#     with tab2:
#         st.subheader("📩 Pending Collaboration Requests")
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#
#         cursor.execute("""
#             SELECT r.request_id, u.user_id AS student_id, u.name AS student_name,
#                    u.research_interests, u.department, u.experience_level
#             FROM collaboration_requests r
#             JOIN users u ON r.student_id = u.user_id
#             WHERE r.professor_id = %s AND r.status = 'pending'
#         """, (user["user_id"],))
#
#         requests = cursor.fetchall()
#
#         if requests:
#             for req in requests:
#                 st.markdown(f"### 🎓 Request from: {req['student_name']}")
#                 st.write(f"🏛️ **Department:** {req['department']}")
#                 st.write(f"🔬 **Research Interests:** {req['research_interests']}")
#                 st.write(
#                     f"📈 **Experience Level:** {req['experience_level'].capitalize() if req['experience_level'] else 'Not specified'}")
#
#                 col1, col2 = st.columns(2)
#                 if col1.button("✅ Accept", key=f"accept_{req['request_id']}"):
#                     update_request_status(req['request_id'], 'accepted')
#                     st.success("Collaboration Accepted!")
#                     st.rerun()
#
#                 if col2.button("❌ Reject", key=f"reject_{req['request_id']}"):
#                     update_request_status(req['request_id'], 'rejected')
#                     st.error("Collaboration Rejected!")
#                     st.rerun()
#
#                 st.divider()
#         else:
#             st.info("No pending requests.")
#
#         # Search for students who haven't sent requests yet
#         st.subheader("🔍 Browse Students by Research Interest")
#         search_term = st.text_input("Enter Research Interest Keyword")
#
#         if search_term:
#             # Get all students with matching research interests who haven't sent requests
#             cursor.execute("""
#                 SELECT u.user_id, u.name, u.department, u.research_interests, u.experience_level
#                 FROM users u
#                 LEFT JOIN collaboration_requests cr ON cr.student_id = u.user_id AND cr.professor_id = %s
#                 WHERE u.role = 'student' AND u.research_interests LIKE %s AND cr.request_id IS NULL
#                 ORDER BY u.name
#             """, (user["user_id"], f'%{search_term}%'))
#
#             students = cursor.fetchall()
#
#             if students:
#                 for student in students:
#                     st.markdown(f"### 🎓 {student['name']}")
#                     st.write(f"🏛️ **Department:** {student['department']}")
#                     st.write(f"🔬 **Research Interests:** {student['research_interests']}")
#                     st.write(
#                         f"📈 **Experience Level:** {student['experience_level'].capitalize() if student['experience_level'] else 'Not specified'}")
#                     st.divider()
#             else:
#                 st.info(f"No students found with research interests matching '{search_term}'.")
#
#         conn.close()
#
#     # Active Collaborations Section
#     with tab3:
#         st.subheader("🤝 Active Collaborations")
#         collaborations = get_active_collaborations(user["user_id"], "professor")
#
#         if not collaborations:
#             st.info("You don't have any active collaborations yet.")
#         else:
#             for collab in collaborations:
#                 with st.container():
#                     st.markdown(f"### 🎓 Collaborating with: {collab['name']}")
#                     st.write(f"🏛️ **Department:** {collab['department']}")
#                     st.write(f"🔬 **Research Interests:** {collab['research_interests']}")
#                     st.write(
#                         f"📈 **Experience Level:** {collab['experience_level'].capitalize() if collab['experience_level'] else 'Not specified'}")
#                     st.divider()
#
#     # Logout Button (at the bottom of the dashboard)
#     if st.button("🚪 Logout", key="logout_button"):
#         st.session_state["user"] = None
#         st.rerun()
