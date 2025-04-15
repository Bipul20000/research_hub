import streamlit as st
from db_connection import (
    get_db_connection, update_user_profile, send_collaboration_request,
    get_active_collaborations, get_user_projects, add_new_project,
    delete_collaboration, update_project, get_project_by_id
)
import research_matching


def show():
    st.title("🎓 Student Dashboard")

    user = st.session_state.get("user")
    if not user:
        st.error("Unauthorized access. Please log in.")
        return


    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 Profile",
        "🔍 Find Professors",
        "👥 Research Partners",
        "🤝 My Collaborations",
        "📊 My Projects"
    ])

    # Profile Section
    with tab1:
        col1, col2 = st.columns([1, 3])

        with col1:
            # Display profile photo if it exists
            if user.get("profile_photo"):
                st.image(user["profile_photo"], width=150)
            else:
                # Show placeholder
                st.markdown("### 👤")
                st.write("No photo")

        with col2:
            if not user.get("department") or not user.get("research_interests"):
                st.warning("⚠️ Your profile is incomplete! Please fill in the required details.")

                department = st.text_input("Department", value=user.get("department", ""))
                research_interests = st.text_area("Research Interests", value=user.get("research_interests", ""))

                #  Fix for "None is not in list" error
                experience_level = user.get("experience_level", "beginner")  # Default to beginner
                if experience_level not in ["beginner", "intermediate", "advanced"]:
                    experience_level = "beginner"

                experience_level = st.selectbox(
                    "Experience Level", ["beginner", "intermediate", "advanced"],
                    index=["beginner", "intermediate", "advanced"].index(experience_level)
                )

                # Add photo upload
                profile_photo = st.file_uploader("Profile Photo", type=["jpg", "jpeg", "png"])

                if st.button("Save Profile"):
                    # Handle photo upload
                    photo_data = None
                    if profile_photo is not None:
                        # Convert the file to bytes for storage
                        photo_data = profile_photo.getvalue()

                    success = update_user_profile(
                        user["user_id"],
                        department,
                        research_interests,
                        experience_level,
                        photo_data
                    )

                    if success:
                        #  Update session state
                        st.session_state["user"].update({
                            "department": department,
                            "research_interests": research_interests,
                            "experience_level": experience_level,
                            "profile_photo": photo_data
                        })
                        st.success("✅ Profile updated successfully!")
                        st.rerun()  #  Updated rerun method
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
                        # Don't reset profile_photo here to maintain it during editing
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

                        # Check if there's already an active collaboration
                        cursor.execute(
                            "SELECT * FROM collaboration_requests WHERE student_id = %s AND professor_id = %s AND status = 'accepted'",
                            (user["user_id"], prof['user_id'])
                        )
                        existing_collab = cursor.fetchone()

                        if existing_collab:
                            st.info("You're already collaborating with this professor.")
                        else:
                            if st.button(f"Request Collaboration with {prof['name']}", key=f"req_{prof['user_id']}"):
                                success = send_collaboration_request(user["user_id"], prof['user_id'])
                                if success:
                                    st.success(f"✅ Collaboration request sent to {prof['name']}!")
                                else:
                                    st.info("You've already sent a request to this professor.")
            else:
                st.warning("⚠️ No matching professors found.")

        cursor.close()
        conn.close()  #  Close DB connection after fetching

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
                    st.markdown(f"###  Collaborating with: {collab['name']}")
                    st.write(f" **Department:** {collab['department']}")
                    st.write(f"🔬 **Research Interests:** {collab['research_interests']}")

                    # Add delete collaboration button
                    if st.button(f"End Collaboration with {collab['name']}", key=f"end_collab_{collab['request_id']}"):
                        if delete_collaboration(collab['request_id']):
                            st.success(f"Collaboration with {collab['name']} has been ended.")
                            st.rerun()

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
                    st.markdown(f"###  Request to: {req['name']}")
                    st.write(f"🏛️ **Department:** {req['department']}")
                    st.write(f"🔬 **Research Interests:** {req['research_interests']}")
                    st.write("**Status:** Pending")
                    st.divider()

        cursor.close()  # Close cursor after fetching
        conn.close()  #  Close DB connection after fetching

    # Projects Tab
    with tab5:
        st.subheader(" My Research Projects")

        # State for editing project
        if "editing_project" not in st.session_state:
            st.session_state.editing_project = None

        # Fetch user projects
        user_projects = get_user_projects(user["user_id"])

        if user_projects:
            for proj in user_projects:
                with st.container():
                    st.markdown(f"###  {proj['title']}")
                    st.write(proj['description'])
                    st.write(f"**Status:** {proj['status'].capitalize()}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Edit Project", key=f"edit_proj_{proj['project_id']}"):
                            st.session_state.editing_project = proj['project_id']
                            st.rerun()

                    st.divider()
        else:
            st.info("You haven't added any projects yet.")

        # Edit project form
        if st.session_state.editing_project:
            project = get_project_by_id(st.session_state.editing_project)
            if project:
                st.markdown("## ✏️ Edit Project")
                with st.form("edit_project_form"):
                    title = st.text_input("Project Title", value=project['title'])
                    description = st.text_area("Project Description", value=project['description'])
                    status = st.selectbox("Status", ["ongoing", "completed"],
                                          index=0 if project['status'] == 'ongoing' else 1)

                    col1, col2 = st.columns(2)
                    with col1:
                        submit_button = st.form_submit_button("Save Changes")
                    with col2:
                        cancel_button = st.form_submit_button("Cancel")

                    if submit_button:
                        if title.strip() == "":
                            st.warning("Please enter a valid project title.")
                        else:
                            update_project(st.session_state.editing_project, title, description, status)
                            st.success("✅ Project updated successfully!")
                            st.session_state.editing_project = None
                            st.rerun()

                    if cancel_button:
                        st.session_state.editing_project = None
                        st.rerun()

        # Add new project form (only show if not editing)
        if not st.session_state.editing_project:
            st.markdown("## ➕ Add New Project")
            with st.form("add_project_form"):
                title = st.text_input("Project Title")
                description = st.text_area("Project Description")
                status = st.selectbox("Status", ["ongoing", "completed"])

                submitted = st.form_submit_button("Add Project")
                if submitted:
                    if title.strip() == "":
                        st.warning("Please enter a valid project title.")
                    else:
                        add_new_project(title, description, status, user["user_id"])
                        st.success("✅ Project added successfully!")
                        st.rerun()

    # Logout Button (at the bottom of the dashboard)
    if st.button("🚪 Logout", key="logout_button"):
        st.session_state["user"] = None
        st.rerun()


# import streamlit as st
# from db_connection import get_db_connection, update_user_profile, send_collaboration_request, get_active_collaborations,get_user_projects, add_new_project
# import research_matching
#
#
# def show():
#     st.title("🎓 Student Dashboard")
#
#     user = st.session_state.get("user")
#     if not user:
#         st.error("Unauthorized access. Please log in.")
#         return
#
#     # Create tabs for different sections
#     tab1, tab2, tab3, tab4,tab5 = st.tabs([
#         "👤 Profile",
#         "🔍 Find Professors",
#         "👥 Research Partners",
#         "🤝 My Collaborations",
#         "My Projects"
#     ])
#
#     # Profile Section
#     with tab1:
#         col1, col2 = st.columns([1, 3])
#
#         with col1:
#             # Display profile photo if it exists
#             if user.get("profile_photo"):
#                 st.image(user["profile_photo"], width=150)
#             else:
#                 # Show placeholder
#                 st.markdown("### 👤")
#                 st.write("No photo")
#
#         with col2:
#             if not user.get("department") or not user.get("research_interests"):
#                 st.warning("⚠️ Your profile is incomplete! Please fill in the required details.")
#
#                 department = st.text_input("Department", value=user.get("department", ""))
#                 research_interests = st.text_area("Research Interests", value=user.get("research_interests", ""))
#
#                 # ✅ Fix for "None is not in list" error
#                 experience_level = user.get("experience_level", "beginner")  # Default to beginner
#                 if experience_level not in ["beginner", "intermediate", "advanced"]:
#                     experience_level = "beginner"
#
#                 experience_level = st.selectbox(
#                     "Experience Level", ["beginner", "intermediate", "advanced"],
#                     index=["beginner", "intermediate", "advanced"].index(experience_level)
#                 )
#
#                 # Add photo upload
#                 profile_photo = st.file_uploader("Profile Photo", type=["jpg", "jpeg", "png"])
#
#                 if st.button("Save Profile"):
#                     # Handle photo upload
#                     photo_data = None
#                     if profile_photo is not None:
#                         # Convert the file to bytes for storage
#                         photo_data = profile_photo.getvalue()
#
#                     success = update_user_profile(
#                         user["user_id"],
#                         department,
#                         research_interests,
#                         experience_level,
#                         photo_data
#                     )
#
#                     if success:
#                         # ✅ Update session state
#                         st.session_state["user"].update({
#                             "department": department,
#                             "research_interests": research_interests,
#                             "experience_level": experience_level,
#                             "profile_photo": photo_data
#                         })
#                         st.success("✅ Profile updated successfully!")
#                         st.rerun()  # ✅ Updated rerun method
#             else:
#                 st.write(f"📚 **Department:** {user['department']}")
#                 st.write(f"🔬 **Research Interests:** {user['research_interests']}")
#                 st.write(f"📈 **Experience Level:** {user['experience_level'].capitalize()}")
#
#                 if st.button("Edit Profile", key="edit_profile"):
#                     # Reset profile completion flags to allow editing
#                     st.session_state["user"].update({
#                         "department": "",
#                         "research_interests": "",
#                         "experience_level": "beginner"
#                         # Don't reset profile_photo here to maintain it during editing
#                     })
#                     st.rerun()
#
#     # Search Professors Section
#     with tab2:
#         # Show professor recommendations
#         research_matching.show_professor_recommendations()
#
#         st.divider()
#
#         # Manual search
#         st.subheader("🔍 Search for Professors")
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#
#         search_query = st.text_input("Enter Research Field or Professor Name")
#         if search_query:
#             cursor.execute(
#                 "SELECT * FROM users WHERE role='professor' AND (name LIKE %s OR research_interests LIKE %s)",
#                 ('%' + search_query + '%', '%' + search_query + '%')
#             )
#             professors = cursor.fetchall()
#
#             if professors:
#                 for prof in professors:
#                     with st.container():
#                         st.markdown(f"### 👨‍🏫 {prof['name']}")
#                         st.write(f"🏛️ **Department:** {prof['department']}")
#                         st.write(f"🔬 **Research Interests:** {prof['research_interests']}")
#
#                         if st.button(f"Request Collaboration with {prof['name']}", key=f"req_{prof['user_id']}"):
#                             success = send_collaboration_request(user["user_id"], prof['user_id'])
#                             if success:
#                                 st.success(f"✅ Collaboration request sent to {prof['name']}!")
#                             else:
#                                 st.info("You've already sent a request to this professor.")
#             else:
#                 st.warning("⚠️ No matching professors found.")
#
#         cursor.close()  # ✅ Close cursor
#         conn.close()  # ✅ Close DB connection
#
#     # Find Research Partners Tab
#     with tab3:
#         research_matching.show_research_partners()
#
#     # My Collaborations Tab
#     with tab4:
#         st.subheader("🤝 My Active Collaborations")
#         collaborations = get_active_collaborations(user["user_id"], "student")
#
#         if not collaborations:
#             st.info(
#                 "You don't have any active collaborations yet. Use the 'Find Professors' tab to connect with professors.")
#         else:
#             for collab in collaborations:
#                 with st.container():
#                     st.markdown(f"### 👨‍🏫 Collaborating with: {collab['name']}")
#                     st.write(f"🏛️ **Department:** {collab['department']}")
#                     st.write(f"🔬 **Research Interests:** {collab['research_interests']}")
#                     st.divider()
#
#         # Pending Requests
#         st.subheader("⏳ Pending Collaboration Requests")
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#
#         cursor.execute("""
#             SELECT cr.request_id, u.name, u.department, u.research_interests
#             FROM collaboration_requests cr
#             JOIN users u ON cr.professor_id = u.user_id
#             WHERE cr.student_id = %s AND cr.status = 'pending'
#         """, (user["user_id"],))
#
#         pending = cursor.fetchall()
#
#         if not pending:
#             st.info("You don't have any pending collaboration requests.")
#         else:
#             for req in pending:
#                 with st.container():
#                     st.markdown(f"### ⏳ Request to: {req['name']}")
#                     st.write(f"🏛️ **Department:** {req['department']}")
#                     st.write(f"🔬 **Research Interests:** {req['research_interests']}")
#                     st.write("**Status:** Pending")
#                     st.divider()
#
#         conn.close()
#
#
#     with tab5:
#         st.subheader("📁 My Research Projects")
#
#         # Fetch user projects
#         user_projects = get_user_projects(user["user_id"])
#
#         if user_projects:
#             for proj in user_projects:
#                 with st.container():
#                     st.markdown(f"### 🧪 {proj['title']}")
#                     st.write(proj['description'])
#                     st.write(f"**Status:** {proj['status'].capitalize()}")
#                     st.divider()
#         else:
#             st.info("You haven't added any projects yet.")
#
#         # Add new project form
#         st.markdown("## ➕ Add New Project")
#         with st.form("add_project_form"):
#             title = st.text_input("Project Title")
#             description = st.text_area("Project Description")
#             status = st.selectbox("Status", ["ongoing", "completed"])
#
#             submitted = st.form_submit_button("Add Project")
#             if submitted:
#                 if title.strip() == "":
#                     st.warning("Please enter a valid project title.")
#                 else:
#                     add_new_project(title, description, status, user["user_id"])
#                     st.success("✅ Project added successfully!")
#                     st.rerun()
#
#     # Logout Button (at the bottom of the dashboard)
#     if st.button("🚪 Logout", key="logout_button"):
#         st.session_state["user"] = None
#         st.rerun()
