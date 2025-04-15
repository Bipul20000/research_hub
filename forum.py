import streamlit as st
from db_connection import get_db_connection, get_forum_posts, get_forum_posts_by_category, create_forum_post


def show():
    st.title(" Community Forum")

    user = st.session_state.get("user")
    if not user:
        st.error("Unauthorized access. Please log in.")
        return

    # Display tabs for posting and viewing
    tab1, tab2 = st.tabs(["Browse Discussions", "Start a Discussion"])

    with tab1:
        st.subheader("Browse Discussions")

        # Filter by category
        categories = ["All", "General Research", "Funding", "Publication Help", "Research Groups"]
        selected_category = st.selectbox("Filter by Category", categories)

        if selected_category == "All":
            posts = get_forum_posts()
        else:
            posts = get_forum_posts_by_category(selected_category)

        if not posts:
            st.info("No discussions available in this category yet. Be the first to start one!")

        # Display posts
        for post in posts:
            with st.expander(f"📝 {post['title']} - by {post['author_name']} ({post['author_role']})"):
                st.write(f"**Category:** {post['category']}")
                st.write(f"**Posted on:** {post['created_at'].strftime('%d %B %Y, %H:%M')}")
                st.markdown("---")
                st.write(post['content'])

    with tab2:
        st.subheader("Start a New Discussion")

        # Form for creating a new post
        title = st.text_input("Title")
        category = st.selectbox(
            "Category",
            ["General Research", "Funding", "Publication Help", "Research Groups"]
        )
        content = st.text_area("Content", height=200)

        if st.button("Post Discussion"):
            if title and content:
                success = create_forum_post(title, content, user["user_id"], category)
                if success:
                    st.success("Your discussion has been posted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to post discussion. Please try again.")
            else:
                st.warning("Please fill out both title and content.")
