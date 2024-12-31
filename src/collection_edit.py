import streamlit as st
from datetime import datetime
from bson import ObjectId

from src.database import get_db
from src.login import login
from src.schema import WordList, SpellingWord

# from src.pages import Pages


def page():
    # if not login():
    #     return

    st.header("📝 :rainbow[Edit Word List]", divider="rainbow")
    db = get_db()

    # Get all word lists for this user
    word_lists = list(db["wordlist"].find({"user_id": st.session_state.user_id_str}))
    
    if not word_lists:
        st.info("You haven't created any word lists yet. Create one in the Word Lists page to get started!")
        return

    # Create a dictionary mapping titles to IDs for the select box
    word_list_dict = {wl['title']: str(wl['_id']) for wl in word_lists}

    # Segmented control for choosing word list
    selected_title = st.segmented_control(
        label=None,
        options=list(word_list_dict.keys()),
        selection_mode="single",
        label_visibility="hidden"
    )
    
    if not selected_title:
        st.info("Please select a word list to edit")
        return
        
    # Update the session state with the selected word list ID
    st.session_state.selected_wordlist_id = word_list_dict[selected_title]
    
    # Get the selected word list
    word_list = db["wordlist"].find_one({"_id": ObjectId(st.session_state.selected_wordlist_id)})
    if not word_list:
        st.error("Selected word list not found!")
        return


    # Add new word button and popover
    with st.popover("➕ Add New Word"):
        with st.form(key="add_word", clear_on_submit=True):
            word = st.text_input("Word")
            usage = st.text_area("Example usage(optional)")
            
            if st.form_submit_button("Add Word"):
                if not word:
                    st.error("Word is required")
                else:
                    # Create new problem in the problems collection
                    new_problem = {
                        "problem_type": "spelling",
                        "problem_set_id": st.session_state.selected_wordlist_id,
                        "word": word,
                        "usage": usage,
                    }
                    db["problem"].insert_one(new_problem)
                    st.success("Word added successfully!")
                    st.rerun()

    # Display existing words with stats
    st.subheader("Words in this List")
    problems = list(db["problem"].find({
        "problem_set_id": st.session_state.selected_wordlist_id,
        "problem_type": "spelling"
    }))
    
    if not problems:
        st.info("No words in this list yet. Add some words above to get started!")
    else:
        for problem in problems:
            with st.container(border=True):
                if st.session_state.username == "root":
                    cols = st.columns((3, 1, 1, 1))
                else:
                    cols = st.columns((3, 1))
                    
                with cols[0]:
                    st.write(f"**{problem['word']}**")
                    if problem.get('usage'):
                        st.write(f"_Usage:_ {problem['usage']}")

                with cols[1]:
                    attempts = list(db["attempts"].find({
                        "user_id": st.session_state.user_id_str,
                        "word_id": str(problem['_id'])
                    }))
                    
                    num_correct = sum([attempt['was_correct'] for attempt in attempts])
                    num_attempts = len(attempts)
                    accuracy = num_correct / num_attempts if num_attempts > 0 else 0
                    
                    color = "green" if accuracy > 0.8 else "red"
                    with st.container(border=True):
                        st.write(f"🎯 :blue[{num_correct}/{num_attempts}] :violet[|] :{color}[{accuracy * 100:.0f}%]")

                if st.session_state.username == "root":
                    with cols[2]:
                        with st.popover(":green[Reset stats]", use_container_width=True):
                            if st.button("Reset", key=f"reset_{problem['_id']}", use_container_width=True):
                                db["attempts"].delete_many({"word_id": str(problem["_id"])})
                                st.rerun()

                    with cols[3]:
                        with st.popover(":red[Delete]", use_container_width=True):
                            st.error("Are you sure you want to delete this word?")
                            if st.button(":red[Delete]", key=f"delete_{problem['_id']}", use_container_width=True):
                                db["problem"].delete_one({"_id": problem["_id"]})
                                st.success("Word deleted successfully!")
                                st.rerun()
