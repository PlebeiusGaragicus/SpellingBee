import streamlit as st
from datetime import datetime
import time

from src.database import get_db
from src.login import login
from src.schema import WordList
from src.interface import centered_button_trick

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
    # if not login():
    #     return

    
    # Show progress report at the top
    show_progress_report()
    
    db = get_db()

    # Find all word lists
    word_lists = list(db["wordlist"].find())

    # Display existing word lists
    if not word_lists:
        st.info("No word lists have been created yet.")
    else:
        st.header("📚 :rainbow[Word Lists]", divider="rainbow")

        for word_list in word_lists:
            # Header row with title and buttons
            with st.container(border=True):
                col1, col3 = st.columns([1, 1])

                # Display words in an expander
                with st.expander("View Words"):
                    st.divider()
                    problems = list(db["problem"].find({
                        "problem_set_id": str(word_list['_id']),
                        "problem_type": "spelling"
                    }))

                    if not problems:
                        st.info("No words in this list yet.")
                    else:
                        for problem in problems:
                            cols = st.columns([1, 1, 1, 1])
                            with cols[0]:
                                # st.write(f"**{problem['word']}**")
                                st.markdown(f"#### {problem['word']}")
                                if problem.get('usage'):
                                    st.write(f"_Usage:_ {problem['usage']}")
                            
                            with cols[1]:
                                attempts = list(db["attempts"].find({
                                    "user_id": st.session_state.user_id_str,
                                    "word_id": str(problem['_id'])
                                }))
                                
                                num_correct = sum([attempt['was_correct'] for attempt in attempts])
                                num_attempts = len(attempts)

                                with st.container(border=True):
                                    st.metric(f":blue[__Attempts__]:", f"{num_correct}/{num_attempts}")

                            with cols[2]:
                                accuracy = num_correct / num_attempts if num_attempts > 0 else 0
                                color = "green" if accuracy > 0.8 else "red"
                                with st.container(border=True):
                                    st.metric(f":{color}[__Accuracy__]:", f"{accuracy * 100:.0f}%")

                            with cols[3]:
                                if st.session_state.username == "root":
                                    with st.popover("🗑️", use_container_width=True):
                                        st.error("Delete this word?")
                                        if st.button("Delete", key=f"delete_word_{problem['_id']}", use_container_width=True):
                                            db["problem"].delete_one({"_id": problem["_id"]})
                                            st.success("Word deleted!")
                                            st.rerun()

                            st.divider()



            with col1:
                # with st.container(border=True):
                st.subheader(f"📝 {word_list['title']}")
                st.caption(word_list['description'])

            # with col3:
                # if st.button("Practice!", key=f"practice_{word_list['_id']}", type="primary", use_container_width=True):
                if st.button("Practice!", key=f"practice_{word_list['_id']}", type="primary"):
                    st.session_state.selected_wordlist_id = str(word_list['_id'])
                    st.session_state.current_page = sites.PRACTICE
                    st.session_state.chosen_word = None
                    st.rerun()
            
            # Only show add/delete buttons for root user
            with col3:
                if st.session_state.username == "root":
                    col3_1, col3_2 = st.columns(2)
                    with col3_1:
                        with st.popover(":green[Add Word]", icon="🌱", use_container_width=True):
                            with st.form(key=f"add_word_{word_list['_id']}", clear_on_submit=True):
                                word = st.text_input("Word")
                                usage = st.text_area("Example usage(optional)")
                                
                                if st.form_submit_button("Add Word"):
                                    if not word:
                                        st.error("Word is required")
                                    else:
                                        # Check if word already exists in this list
                                        existing_word = db["problem"].find_one({
                                            "problem_set_id": str(word_list['_id']),
                                            "problem_type": "spelling",
                                            "word": word.strip()
                                        })
                                        
                                        if existing_word:
                                            st.error(f"'{word}' is already in this word list!")
                                        else:
                                            new_problem = {
                                                "problem_type": "spelling",
                                                "problem_set_id": str(word_list['_id']),
                                                "word": word.strip(),
                                                "usage": usage,
                                            }
                                            db["problem"].insert_one(new_problem)
                                            st.success("Word added successfully!")
                                            st.rerun()
                    with col3_2:
                        with st.popover(":red[Delete List]", icon="🗑️", use_container_width=True):
                            st.error("Are you sure you want to delete this word list?")
                            if st.button("🗑️ Delete", key=f"delete_{word_list['_id']}", type="secondary"):
                                db["wordlist"].delete_one({"_id": word_list['_id']})
                                st.success("Word list deleted successfully!")
                                st.rerun()
            
            # st.divider()

    # Create new word list button (only for root)
    with centered_button_trick():
        if st.session_state.username == "root":
            with st.popover(":green[Create a new word list]", icon="🌱", use_container_width=True):
                with st.form(key="new_wordlist", clear_on_submit=True):
                    title = st.text_input("Title")
                    description = st.text_area("Description")
                    
                    if st.form_submit_button("Create Word List"):
                        # Check if word list with the same title already exists
                        existing_list = db["wordlist"].find_one({
                            "title": title
                        })
                        
                        if existing_list is not None:
                            st.error("A word list with this title already exists")
                        elif title == "":
                            st.error("Title must be filled")
                        else:
                            new_list = WordList(
                                title=title,
                                description=description
                            )
                            db["wordlist"].insert_one(new_list.model_dump())
                            st.success("Word list created successfully!")
                            st.rerun()