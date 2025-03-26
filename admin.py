import streamlit as st
from database import create_research_update, get_research_updates, update_research_featured_status

# Admin dashboard
def admin_dashboard():
    st.title("Admin Dashboard")
    
    # Check if user is admin
    if st.session_state.role != "admin":
        st.error("You do not have permission to access this page.")
        return
    
    # Admin tabs
    tab1, tab2 = st.tabs(["Manage Research Highlights", "System Stats"])
    
    with tab1:
        manage_research_highlights()
    
    with tab2:
        system_statistics()

# Manage research highlights section
def manage_research_highlights():
    st.subheader("Research Highlights Management")
    
    # Current research highlights
    st.markdown("### Current Research Highlights")
    updates = get_research_updates(featured_only=False)
    
    if not updates:
        st.info("No research highlights available.")
    else:
        for update in updates:
            with st.expander(f"{update['title']} - Posted on {update['date_posted'].strftime('%b %d, %Y')}"):
                st.write(f"**Summary:** {update['summary']}")
                st.write(f"**Contributors:** {update['contributors']}")
                
                # Feature/unfeature toggle
                featured = update['featured'] == 1
                
                if featured:
                    if st.button(f"Unfeature", key=f"unfeature_{update['id']}"):
                        if update_research_featured_status(update['id'], 0):
                            st.success("Research update unfeatured!")
                            st.rerun()
                else:
                    if st.button(f"Feature", key=f"feature_{update['id']}"):
                        if update_research_featured_status(update['id'], 1):
                            st.success("Research update featured!")
                            st.rerun()
    
    # Add new research highlight
    st.markdown("### Add New Research Highlight")
    
    with st.form("new_research_form"):
        title = st.text_input("Research Title")
        summary = st.text_area("Research Summary")
        contributors = st.text_input("Contributors (comma separated)")
        featured = st.checkbox("Feature on Homepage")
        
        submit = st.form_submit_button("Add Research Highlight")
        
        if submit:
            if not title or not summary or not contributors:
                st.error("Please fill in all required fields.")
                return
            
            if create_research_update(title, summary, contributors, st.session_state.user_id, featured):
                st.success("Research highlight added successfully!")
                st.rerun()
            else:
                st.error("Failed to add research highlight. Please try again.")

# System statistics section
def system_statistics():
    st.subheader("System Statistics")
    
    # This would normally pull data from the database
    # For now, we'll use placeholder data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Users", "120")
        st.metric("Active Research Projects", "45")
        st.metric("Forum Posts", "256")
    
    with col2:
        st.metric("Collaboration Requests", "78")
        st.metric("Successful Matches", "32")
        st.metric("Research Highlights", "15")
    
    # User activity chart
    st.subheader("User Activity (Last 30 Days)")
    
    # In a real implementation, this would use actual data
    # For now, let's create a placeholder chart using Streamlit
    
    import pandas as pd
    import plotly.express as px
    
    # Sample activity data
    data = {
        'Date': pd.date_range(start='2023-01-01', periods=30),
        'Logins': [10, 15, 12, 8, 20, 22, 18, 15, 25, 30, 28, 22, 20, 18, 15,
                  17, 19, 22, 25, 28, 30, 32, 35, 30, 28, 25, 22, 20, 18, 15],
        'New Users': [2, 3, 1, 0, 4, 2, 1, 0, 3, 4, 2, 1, 0, 1, 2, 
                     3, 1, 2, 3, 2, 1, 4, 5, 2, 1, 0, 1, 2, 1, 0]
    }
    
    df = pd.DataFrame(data)
    fig = px.line(df, x='Date', y=['Logins', 'New Users'], title='User Activity')
    st.plotly_chart(fig)
    
    # Most active departments
    st.subheader("Most Active Departments")
    
    dept_data = {
        'Department': ['Computer Science', 'Electrical Engineering', 'Biology', 'Chemistry', 'Physics'],
        'Users': [35, 28, 22, 18, 17],
        'Projects': [12, 10, 8, 7, 6],
    }
    
    dept_df = pd.DataFrame(dept_data)
    fig2 = px.bar(dept_df, x='Department', y=['Users', 'Projects'], 
                 title='Department Activity', barmode='group')
    st.plotly_chart(fig2)
