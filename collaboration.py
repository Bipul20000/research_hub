import streamlit as st
from database import get_collaboration_requests, update_collaboration_status

# Collaboration requests page
def collaboration_requests():
    st.title("Collaboration Requests")
    
    # Get collaboration requests for the user
    requests = get_collaboration_requests(st.session_state.user_id, st.session_state.role)
    
    # Tabs for incoming and outgoing requests
    tab1, tab2 = st.tabs(["Incoming Requests", "Outgoing Requests"])
    
    with tab1:
        display_incoming_requests(requests)
    
    with tab2:
        display_outgoing_requests(requests)
    
    # Guidelines for successful collaborations
    with st.expander("Tips for Successful Research Collaborations"):
        st.markdown("""
        ### Making the Most of Research Collaborations
        
        1. **Clear expectations**: Discuss goals, timelines, and responsibilities early
        2. **Regular communication**: Schedule check-ins to discuss progress
        3. **Documentation**: Keep detailed notes on research findings
        4. **Credit sharing**: Agree on authorship guidelines from the start
        5. **Feedback loop**: Provide constructive feedback to improve collaboration
        
        Successful collaborations lead to better research outcomes and future opportunities!
        """)

# Display incoming collaboration requests
def display_incoming_requests(requests):
    # Filter requests based on role
    if st.session_state.role == 'professor':
        incoming = [r for r in requests if r['status'] == 'Pending']
    else:  # student
        incoming = [r for r in requests if r['status'] == 'Pending']
    
    if not incoming:
        st.info("You have no pending incoming collaboration requests.")
        return
    
    st.subheader(f"You have {len(incoming)} pending request(s)")
    
    # Display each request
    for req in incoming:
        with st.container():
            if st.session_state.role == 'professor':
                name = req['student_name']
                department = req['student_department']
            else:
                name = req['professor_name']
                department = req['professor_department']
            
            st.markdown(f"### Request from {name}")
            st.write(f"**Department:** {department}")
            st.write(f"**Request Date:** {req['request_date']}")
            
            if req['message']:
                st.write("**Message:**")
                st.write(req['message'])
            
            # Accept/Decline buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Accept", key=f"accept_{req['id']}"):
                    if update_collaboration_status(req['id'], 'Accepted'):
                        st.success(f"You've accepted the collaboration request from {name}!")
                        st.rerun()
            
            with col2:
                if st.button("Decline", key=f"decline_{req['id']}"):
                    if update_collaboration_status(req['id'], 'Declined'):
                        st.success(f"You've declined the collaboration request from {name}.")
                        st.rerun()
            
            st.markdown("---")

# Display outgoing collaboration requests
def display_outgoing_requests(requests):
    # All requests for the user (will show status)
    if not requests:
        st.info("You haven't sent any collaboration requests yet.")
        return
    
    # Group requests by status
    pending = [r for r in requests if r['status'] == 'Pending']
    accepted = [r for r in requests if r['status'] == 'Accepted']
    declined = [r for r in requests if r['status'] == 'Declined']
    
    # Display pending requests
    if pending:
        st.subheader("Pending Requests")
        display_request_group(pending)
    
    # Display accepted requests
    if accepted:
        st.subheader("Accepted Requests")
        display_request_group(accepted)
    
    # Display declined requests
    if declined:
        st.subheader("Declined Requests")
        display_request_group(declined)

# Helper to display a group of requests
def display_request_group(requests):
    for req in requests:
        with st.container():
            if st.session_state.role == 'professor':
                name = req['student_name']
                department = req['student_department']
            else:
                name = req['professor_name']
                department = req['professor_department']
            
            st.write(f"**Request to:** {name} ({department})")
            st.write(f"**Sent on:** {req['request_date']}")
            
            if req['message']:
                with st.expander("View Message"):
                    st.write(req['message'])
            
            # Cancel button for pending requests
            if req['status'] == 'Pending':
                if st.button("Cancel Request", key=f"cancel_{req['id']}"):
                    if update_collaboration_status(req['id'], 'Cancelled'):
                        st.success("Request cancelled successfully.")
                        st.rerun()
            
            st.markdown("---")
