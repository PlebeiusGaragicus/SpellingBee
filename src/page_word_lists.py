import streamlit as st
from datetime import datetime
import time

from src.database import get_db
from src.login import login
from src.schema import WordList, SpellingWord

import src.sites as sites

def show_progress_report():
    db = get_db()
    user_attempts = list(db["attempts"].find({"user_id": st.session_state.user_id_str}))

    with st.container(border=True):
        st.subheader("📈 :green[Your Progress]", divider="rainbow")
        
        attempts_in_last_2_days = [attempt for attempt in user_attempts if attempt['attempt_date'].timestamp() > time.time() - 2 * 24 * 60 * 60]
        attempts_in_last_6_hours = [attempt for attempt in user_attempts if attempt['attempt_date'].timestamp() > time.time() - 6 * 60 * 60]
        correct_attempts = [attempt for attempt in user_attempts if attempt['was_correct']]

        cols = st.columns(3)
        with cols[0]:
            st.metric("Last 2 Days", f"{len(attempts_in_last_2_days)} attempts")
        with cols[1]:
            st.metric("Last 6 Hours", f"{len(attempts_in_last_6_hours)} attempts")
        with cols[2]:
            accuracy = len(correct_attempts) / len(user_attempts) if user_attempts else 0
            st.metric("Overall Accuracy", f"{accuracy * 100:.0f}%")

def page():
    if not login():
        return

    st.header("📚 :rainbow[Word Lists]", divider="rainbow")
    
    # Show progress report at the top
    show_progress_report()
    
    db = get_db()

    # Find all word lists that belong to the current user
    word_lists = list(db["wordlist"].find({"user_id": st.session_state.user_id_str}))

    # Show a form to create a new word list
    # with st.expander("🌱 :green[Create a new word list]"):
    with st.popover("🌱 :green[Create a new word list]"):
        with st.form(key="new_wordlist", clear_on_submit=True):
            title = st.text_input("Title")
            description = st.text_area("Description")
            
            if st.form_submit_button("Create Word List"):
                # Check if word list with the same title already exists
                existing_list = db["wordlist"].find_one({
                    "user_id": st.session_state.user_id_str,
                    "title": title
                })
                
                if existing_list is not None:
                    st.error("A word list with this title already exists")
                elif title == "":
                    st.error("Title must be filled")
                else:
                    new_list = WordList(
                        user_id=st.session_state.user_id_str,
                        title=title,
                        description=description
                    )
                    db["wordlist"].insert_one(new_list.model_dump())
                    st.success("Word list created successfully!")
                    st.rerun()

    # Display existing word lists
    if not word_lists:
        st.info("You haven't created any word lists yet. Create one above to get started!")
    else:
        # Create two columns for the cards
        cols = st.columns(2)
        for idx, word_list in enumerate(word_lists):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"### 📝 {word_list['title']}")
                    st.markdown(f"**Description:** {word_list['description']}")

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button("Practice!", key=f"practice_{word_list['_id']}", type="primary"):
                            st.session_state.selected_wordlist_id = str(word_list['_id'])
                            st.session_state.current_page = sites.PRACTICE
                            st.session_state.chosen_word = None
                            st.rerun()
                    
                    # Only show delete button for root user
                    with col2:
                        if st.session_state.username == "root":
                            with st.popover(":red[Delete]", use_container_width=True):
                                st.error("Are you sure you want to delete this word?")
                                if st.button("🗑️ Delete", key=f"delete_{word_list['_id']}", type="secondary"):
                                    db["wordlist"].delete_one({"_id": word_list['_id']})
                                    st.success("Word list deleted successfully!")
                                    st.rerun()
