import streamlit as st
from database import get_user_by_id, update_user, get_projects_by_user, create_project, update_project

# Display user profile
def display_profile():
    st.title("My Profile")
    
    if not st.session_state.user_id:
        st.warning("Please login to view your profile")
        return
    
    user = get_user_by_id(st.session_state.user_id)
    if not user:
        st.error("User profile not found")
        return
    
    # Display user info
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Profile Information")
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Role:** {user['role'].capitalize()}")
        st.write(f"**Department:** {user['department']}")
        st.write(f"**Email:** {user['email']}")
    
    with col2:
        st.subheader("Research Interests")
        interests = user['research_interests'].split(',') if user['research_interests'] else []
        if interests:
            for interest in interests:
                st.write(f"• {interest.strip()}")
        else:
            st.write("No research interests specified.")
        
        st.subheader("Bio")
        st.write(user['bio'] if user['bio'] else "No bio provided.")
    
    # Display user's projects
    st.header("My Research Projects")
    projects = get_projects_by_user(st.session_state.user_id)
    
    if not projects:
        st.info("You haven't created any research projects yet.")
    else:
        for project in projects:
            with st.expander(f"{project['title']} ({project['status']})"):
                st.write(f"**Description:** {project['description']}")
                st.write(f"**Created:** {project['created_at']}")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Edit", key=f"edit_{project['id']}"):
                        st.session_state.edit_project_id = project['id']
                        st.session_state.edit_project_title = project['title']
                        st.session_state.edit_project_desc = project['description']
                        st.session_state.edit_project_status = project['status']
                        st.rerun()
    
    # New project button
    if st.button("Add New Project"):
        st.session_state.add_new_project = True
        st.rerun()
    
    # Edit project form
    if 'edit_project_id' in st.session_state:
        st.subheader("Edit Project")
        with st.form("edit_project_form"):
            title = st.text_input("Project Title", value=st.session_state.edit_project_title)
            description = st.text_area("Project Description", value=st.session_state.edit_project_desc)
            status = st.selectbox("Status", ["Active", "Completed", "On Hold"], 
                                 index=["Active", "Completed", "On Hold"].index(st.session_state.edit_project_status))
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit = st.form_submit_button("Update Project")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if submit:
                if update_project(st.session_state.edit_project_id, title, description, status):
                    st.success("Project updated successfully!")
                    # Clear session variables
                    del st.session_state.edit_project_id
                    del st.session_state.edit_project_title
                    del st.session_state.edit_project_desc
                    del st.session_state.edit_project_status
                    st.rerun()
                else:
                    st.error("Failed to update project.")
            
            if cancel:
                # Clear session variables
                del st.session_state.edit_project_id
                del st.session_state.edit_project_title
                del st.session_state.edit_project_desc
                del st.session_state.edit_project_status
                st.rerun()
    
    # New project form
    if st.session_state.get('add_new_project', False):
        st.subheader("Add New Project")
        with st.form("new_project_form"):
            title = st.text_input("Project Title")
            description = st.text_area("Project Description")
            status = st.selectbox("Status", ["Active", "Completed", "On Hold"])
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit = st.form_submit_button("Add Project")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if submit:
                if title and description:
                    if create_project(title, description, st.session_state.user_id, status):
                        st.success("Project added successfully!")
                        st.session_state.add_new_project = False
                        st.rerun()
                    else:
                        st.error("Failed to add project.")
                else:
                    st.warning("Please provide both title and description.")
            
            if cancel:
                st.session_state.add_new_project = False
                st.rerun()

# Edit user profile
def edit_profile():
    st.title("Edit Profile")
    
    if not st.session_state.user_id:
        st.warning("Please login to edit your profile")
        return
    
    user = get_user_by_id(st.session_state.user_id)
    if not user:
        st.error("User profile not found")
        return
    
    with st.form("edit_profile_form"):
        name = st.text_input("Full Name", value=user['name'])
        department = st.text_input("Department", value=user['department'])
        
        research_interests = st.text_area("Research Interests (comma separated)", 
                                        value=user['research_interests'])
        
        bio = st.text_area("Bio", value=user['bio'] if user['bio'] else "")
        
        submit = st.form_submit_button("Update Profile")
        
        if submit:
            if not name or not department:
                st.error("Name and department are required.")
                return
            
            if update_user(st.session_state.user_id, name, department, research_interests, bio):
                st.success("Profile updated successfully!")
                st.session_state.username = name  # Update the session name if changed
            else:
                st.error("Failed to update profile.")
