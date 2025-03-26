import streamlit as st
import pandas as pd
from database import get_forum_posts, create_forum_post, vote_post

# Forum page
def forum_page():
    st.title("Research Community Forum")
    
    # Forum categories
    categories = ["General Research", "Funding Opportunities", "Publication Help", "Research Groups", "All Categories"]
    
    # Tabs for different forum sections
    tab1, tab2 = st.tabs(["Browse Discussions", "Start New Discussion"])
    
    with tab1:
        selected_category = st.selectbox(
            "Filter by Category",
            categories,
            index=4  # Default to "All Categories"
        )
        
        # Convert UI selection to database parameter
        category_param = None if selected_category == "All Categories" else selected_category
        
        # Get forum posts
        posts = get_forum_posts(category=category_param)
        display_forum_posts(posts)
    
    with tab2:
        create_new_post()

# Display forum posts
def display_forum_posts(posts):
    if not posts:
        st.info("No discussions found. Be the first to start a discussion!")
        return
    
    # Convert to dataframe for easier sorting
    posts_df = pd.DataFrame(posts)
    
    # Add a column for net votes
    posts_df['net_votes'] = posts_df['upvotes'] - posts_df['downvotes']
    
    # Sort options
    sort_option = st.radio(
        "Sort by",
        ["Latest", "Most Popular"],
        horizontal=True
    )
    
    if sort_option == "Latest":
        posts_df = posts_df.sort_values('created_at', ascending=False)
    else:  # Most Popular
        posts_df = posts_df.sort_values('net_votes', ascending=False)
    
    # Display each post
    for _, post in posts_df.iterrows():
        with st.expander(f"{post['title']} - by {post['author_name']} ({post['category']})"):
            # Post content
            st.write(post['content'])
            st.caption(f"Posted on: {post['created_at']}")
            
            # Vote buttons
            col1, col2, col3 = st.columns([1, 1, 8])
            
            with col1:
                if st.button("👍", key=f"up_{post['id']}"):
                    if vote_post(post['id'], st.session_state.user_id, 'upvote'):
                        st.success("Vote recorded!")
                        st.rerun()
            
            with col2:
                if st.button("👎", key=f"down_{post['id']}"):
                    if vote_post(post['id'], st.session_state.user_id, 'downvote'):
                        st.success("Vote recorded!")
                        st.rerun()
            
            with col3:
                st.write(f"**Score: {post['upvotes'] - post['downvotes']}** ({post['upvotes']} upvotes, {post['downvotes']} downvotes)")

# Create new forum post
def create_new_post():
    st.subheader("Start a New Discussion")
    
    categories = ["General Research", "Funding Opportunities", "Publication Help", "Research Groups"]
    
    with st.form("new_post_form"):
        title = st.text_input("Title", placeholder="What's your discussion about?")
        category = st.selectbox("Category", categories)
        content = st.text_area("Content", placeholder="Provide details, questions, or information...")
        
        submit = st.form_submit_button("Post Discussion")
        
        if submit:
            if not title or not content:
                st.error("Please provide both a title and content for your post.")
                return
            
            if create_forum_post(title, content, st.session_state.user_id, category):
                st.success("Your discussion has been posted!")
                st.rerun()
            else:
                st.error("Failed to post discussion. Please try again.")
    
    # Guidelines for effective discussions
    with st.expander("Discussion Guidelines"):
        st.markdown("""
        ### Guidelines for Effective Discussions
        
        - **Be specific**: Clearly state your question or point
        - **Add context**: Include relevant background information 
        - **Use descriptive titles**: Help others find your discussion
        - **Be respectful**: Maintain a positive, constructive tone
        - **Follow up**: If someone answers your question, acknowledge it
        """)
