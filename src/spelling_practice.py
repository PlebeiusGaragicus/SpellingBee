import os
import json
import time
import random
import subprocess

import streamlit as st
from datetime import datetime

from src.login import login
from src.database import get_db
from src.schema import UserAttempt

def get_random_word(word_list):
    """Get a random word from the word list that hasn't been practiced recently"""
    if not word_list.get('words'):
        return None
    return random.choice(word_list['words'])

def speak_word(word, voice="Victoria"):
    """Use macOS say command to speak the word"""
    try:
        st.session_state.last_spoken = word
        st.runtime.scriptrunner.add_script_run_ctx()
        command = f'say -v {voice} "{word}"'
        os.system(command)
    except Exception as e:
        st.error(f"Error speaking word: {e}")

def page():
    if not login():
        return

    st.header('🎯 :rainbow[Spelling Practice]', divider="rainbow")
    
    db = get_db()
    
    # Get the selected word list
    if not st.session_state.get('selected_wordlist_id'):
        st.warning("Please select a word list to practice from the Word Lists page")
        if st.button("Go to Word Lists"):
            # st.switch_page("sites/page_word_lists.py")
            st.session_state.current_page = Pages.WORD_LISTS.value[0]
        return
        
    word_list = db["wordlist"].find_one({"_id": st.session_state.selected_wordlist_id})
    if not word_list:
        st.error("Selected word list not found!")
        return
        
    st.subheader(f"Practicing: {word_list['title']}")
    
    # Initialize or get current word
    if 'current_word' not in st.session_state:
        st.session_state.current_word = get_random_word(word_list)
    
    if not st.session_state.current_word:
        st.warning("This word list is empty! Add some words first.")
        if st.button("Edit Word List"):
            st.switch_page("sites/collection_edit.py")
        return
    
    # Practice interface
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔊 Hear Word", use_container_width=True):
            speak_word(st.session_state.current_word['word'])
            
    with col2:
        if st.button("➡️ Next Word", use_container_width=True):
            st.session_state.current_word = get_random_word(word_list)
            st.rerun()
    
    # Word input
    with st.form("spelling_form", clear_on_submit=True):
        user_input = st.text_input("Type the word:", key="word_input")
        submitted = st.form_submit_button("Check")
        
        if submitted:
            if user_input.lower().strip() == st.session_state.current_word['word'].lower().strip():
                st.success("Correct! 🎉")
                # Record the attempt
                attempt = UserAttempt(
                    user_id=st.session_state.user_id_str,
                    word_id=str(st.session_state.current_word['_id']),
                    was_correct=True
                )
                db["attempts"].insert_one(attempt.model_dump())
                # Get new word
                st.session_state.current_word = get_random_word(word_list)
                st.rerun()
            else:
                st.error("Not quite right. Try again!")
                attempt = UserAttempt(
                    user_id=st.session_state.user_id_str,
                    word_id=str(st.session_state.current_word['_id']),
                    was_correct=False
                )
                db["attempts"].insert_one(attempt.model_dump())
    
    # Show example usage
    if st.session_state.current_word.get('example_usage'):
        st.info(f"Example: {st.session_state.current_word['example_usage']}")
        
    # Show notes if available
    if st.session_state.current_word.get('notes'):
        st.info(f"📝 Note: {st.session_state.current_word['notes']}")
        
    # Option to reveal word
    if st.button("Show Word"):
        st.write(f"The word is: **{st.session_state.current_word['word']}**")
