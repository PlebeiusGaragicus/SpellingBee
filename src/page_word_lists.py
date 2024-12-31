import streamlit as st
from datetime import datetime

from src.database import get_db
from src.login import login
from src.schema import WordList, SpellingWord

import src.sites as sites

def page():
    if not login():
        return

    st.header("📚 :rainbow[Word Lists]", divider="rainbow")
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

                    if st.button("Practice!", key=f"practice_{word_list['_id']}", type="primary"):
                        st.session_state.selected_wordlist_id = str(word_list['_id'])
                        st.session_state.current_page = sites.PRACTICE # turn into function for better readability
                        # st.session_state.practice_set = st.session_state.selected_wordlist_id
                        # del st.session_state.chosen_word # TODO - this is to cumbersome
                        st.session_state.chosen_word = None
                        st.rerun()
