import streamlit as st
import pandas as pd
from database import search_users, get_all_departments, create_collaboration_request

# Search page
def search_page():
    st.title("Research Connect Search")
    
    # Get all departments for filter
    departments = get_all_departments()
    
    # Search filters
    st.subheader("Search Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_role = st.selectbox(
            "I'm looking for", 
            ["All", "Professors", "Students"],
            index=0
        )
    
    with col2:
        selected_department = st.selectbox(
            "Department",
            ["All"] + departments,
            index=0
        )
    
    with col3:
        keywords = st.text_input("Research Keywords")
    
    # Convert UI selections to database query parameters
    role_param = None
    if search_role == "Professors":
        role_param = "professor"
    elif search_role == "Students":
        role_param = "student"
    
    dept_param = None if selected_department == "All" else selected_department
    
    # Execute search when button is clicked
    if st.button("Search"):
        results = search_users(
            role=role_param,
            keywords=keywords,
            department=dept_param
        )
        
        display_search_results(results)
    
    # Tips for effective searching
    with st.expander("Search Tips"):
        st.markdown("""
        ### Tips for Finding the Right Research Match
        
        - **Be specific with keywords**: Use specific research terms rather than broad areas
        - **Try different departments**: Some research areas are interdisciplinary
        - **Look at profiles**: Click on interesting matches to see their full research profile
        - **Send a personalized message**: When requesting collaboration, mention specific interests
        """)

# Display search results
def display_search_results(results):
    if not results:
        st.info("No results found matching your criteria. Try adjusting your search filters.")
        return
    
    st.subheader(f"Found {len(results)} potential research matches")
    
    # Group results by role for better organization
    df = pd.DataFrame(results)
    
    # If there are professors in results, show them first
    professors = df[df['role'] == 'professor']
    if not professors.empty:
        st.markdown("### Professors")
        display_user_cards(professors)
    
    # Then show students
    students = df[df['role'] == 'student']
    if not students.empty:
        st.markdown("### Students")
        display_user_cards(students)
    
    # Show admins last (if any)
    admins = df[df['role'] == 'admin']
    if not admins.empty:
        st.markdown("### Administrators")
        display_user_cards(admins)

# Display user cards in a grid
def display_user_cards(users_df):
    # Display in rows of 3
    for i in range(0, len(users_df), 3):
        cols = st.columns(3)
        
        # Get chunk of 3 users (or fewer for the last row)
        chunk = users_df.iloc[i:min(i+3, len(users_df))]
        
        for j, (_, user) in enumerate(chunk.iterrows()):
            with cols[j]:
                with st.container():
                    st.subheader(user['name'])
                    st.write(f"**Department:** {user['department']}")
                    
                    # Show truncated research interests
                    interests = user['research_interests']
                    if interests and len(interests) > 100:
                        interests_display = interests[:100] + "..."
                    else:
                        interests_display = interests or "No interests specified"
                    
                    st.write(f"**Research Interests:** {interests_display}")
                    
                    # View profile button
                    if st.button("View Full Profile", key=f"view_{user['id']}"):
                        st.session_state.view_profile_id = user['id']
                        st.rerun()
                    
                    # Request collaboration button (don't show for own profile)
                    if (user['id'] != st.session_state.user_id and 
                        ((st.session_state.role == 'professor' and user['role'] == 'student') or
                         (st.session_state.role == 'student' and user['role'] == 'professor'))):
                        if st.button("Request Collaboration", key=f"collab_{user['id']}"):
                            st.session_state.request_collab_id = user['id']
                            st.session_state.request_collab_name = user['name']
                            st.rerun()
    
    # Handle viewing a full profile
    if 'view_profile_id' in st.session_state:
        display_full_profile(st.session_state.view_profile_id)
    
    # Handle collaboration request
    if 'request_collab_id' in st.session_state:
        request_collaboration(st.session_state.request_collab_id, st.session_state.request_collab_name)

# Display full profile of a user
def display_full_profile(user_id):
    # Get user details from the selected ID
    user = next((u for u in search_users() if u['id'] == user_id), None)
    
    if not user:
        st.error("User profile not found")
        del st.session_state.view_profile_id
        return
    
    st.subheader(f"{user['name']}'s Profile")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write(f"**Role:** {user['role'].capitalize()}")
        st.write(f"**Department:** {user['department']}")
    
    with col2:
        st.write("**Research Interests:**")
        interests = user['research_interests'].split(',') if user['research_interests'] else []
        if interests:
            for interest in interests:
                st.write(f"• {interest.strip()}")
        else:
            st.write("No research interests specified.")
    
    st.write("**Bio:**")
    st.write(user['bio'] if user['bio'] else "No bio provided.")
    
    # Close profile button
    if st.button("Close Profile"):
        del st.session_state.view_profile_id
        st.rerun()
    
    # Request collaboration button (don't show for own profile)
    if (user['id'] != st.session_state.user_id and 
        ((st.session_state.role == 'professor' and user['role'] == 'student') or
         (st.session_state.role == 'student' and user['role'] == 'professor'))):
        if st.button("Request Collaboration"):
            st.session_state.request_collab_id = user['id']
            st.session_state.request_collab_name = user['name']
            st.rerun()

# Request collaboration with a user
def request_collaboration(user_id, user_name):
    st.subheader(f"Request Collaboration with {user_name}")
    
    with st.form("collaboration_request_form"):
        message = st.text_area("Collaboration Message (optional)", 
                              placeholder="Describe why you're interested in collaborating...")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Send Request")
        with col2:
            cancel = st.form_submit_button("Cancel")
        
        if submit:
            # Determine professor and student IDs based on roles
            if st.session_state.role == 'professor':
                professor_id = st.session_state.user_id
                student_id = user_id
            else:
                professor_id = user_id
                student_id = st.session_state.user_id
            
            # Create the collaboration request
            if create_collaboration_request(professor_id, student_id, message):
                st.success(f"Collaboration request sent to {user_name}!")
                # Clear the session variables
                del st.session_state.request_collab_id
                del st.session_state.request_collab_name
                st.rerun()
            else:
                st.error("Failed to send collaboration request. Please try again.")
        
        if cancel:
            # Clear the session variables
            del st.session_state.request_collab_id
            del st.session_state.request_collab_name
            st.rerun()
