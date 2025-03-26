import streamlit as st
from database import get_research_updates

# Display research highlights
def research_highlights(featured_only=False):
    if not featured_only:
        st.title("College Research Highlights")
    
    # Get research updates
    updates = get_research_updates(featured_only=featured_only)
    
    if not updates:
        st.info("No research highlights available at this time.")
        return
    
    # Display each research update
    for i, update in enumerate(updates):
        with st.container():
            # Add a horizontal rule between items (except before the first one)
            if i > 0:
                st.markdown("---")
            
            st.subheader(update['title'])
            
            # Show featured badge if applicable
            if update['featured']:
                st.markdown("🌟 **Featured Research**")
            
            st.write(update['summary'])
            
            # Display contributors and posted info
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Contributors:** {update['contributors']}")
            with col2:
                st.write(f"**Posted by:** {update['posted_by_name']} on {update['date_posted'].strftime('%b %d, %Y')}")
            
            # Add some spacing
            st.write("")
    
    # If on the main research highlights page (not the homepage featured section)
    if not featured_only:
        # Research submission guidelines
        with st.expander("How to Submit Your Research for Highlights"):
            st.markdown("""
            ### Submitting Your Research for College Highlights
            
            1. **Eligibility**: Your research must be affiliated with our college
            2. **Process**: Contact the research administrator or department head
            3. **Requirements**: 
               - Research title
               - Brief summary (200-300 words)
               - List of contributors
               - Any relevant publications or presentations
            
            Featured research is selected by the administration based on impact, innovation, and relevance.
            """)
