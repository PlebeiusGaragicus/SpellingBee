import os
import json
import time
import random
import subprocess

import streamlit as st

from src.login import login

def choose_word():
    st.session_state.chosen_word_index = random.randint(0, len(st.session_state['words']['list']) - 1)
    st.session_state.failed_attempts = 0
    st.session_state.given_up = False
    st.session_state.speak_word = True

def chosen_word():
    return st.session_state['words']['list'][st.session_state.chosen_word_index]['word']

def change_score(correct: bool):
    if correct:
        st.session_state['words']['list'][st.session_state.chosen_word_index]['score'] += 1
    # else:
        # st.session_state['words']['list'][st.session_state.chosen_word_index]['score'] -= 1

    st.session_state['words']['list'][st.session_state.chosen_word_index]['attempts'] += 1
    save_state()

def save_state():
    with open(f'./words/{st.session_state.username}_words.json', 'w') as f:
        json.dump(st.session_state.words, f)






###############################################
def page():
    if not login():
        return

    st.header('🧠 :rainbow[Spelling practice]', divider="rainbow")


    ### INIT
    if not 'spelling' in st.session_state:
        st.session_state.spelling = True

        with open(f'./words/{st.session_state.username}_words.json', 'r') as f:
            st.session_state.words = json.load(f)
        
        choose_word()






    ### GUESS SUBMISSION FORM
    with st.form(key='spell_test_form', clear_on_submit=True):
        guess = st.text_input('Type the word you hear:', key='word_input')
        if st.form_submit_button(':green[Submit]'):
            if guess.lower() == chosen_word():
                if st.session_state.given_up:
                    st.warning("Good practice!")
                else:
                    if st.session_state.failed_attempts < 2:
                        change_score(True)
                        st.toast("Correct!")
                choose_word()
                st.balloons()
                # st.success('Correct!')
                time.sleep(1)
                st.rerun()

                # STUDENT GOT IT WRONG
            else:
                st.session_state.speak_word = True
                change_score(False)
                if st.session_state.failed_attempts == 0:
                    st.error('Incorrect! Try again.')
                # elif st.session_state.failed_attempts == 1:
                    # st.error('Try one more time!')
                else:
                    st.markdown(f"# Sorry, the word was `{chosen_word()}`")
                    # choose_word()
                    # st.rerun()

                st.session_state.failed_attempts += 1


    # st.write(f"Score: {st.session_state['words']['list'][st.session_state.chosen_word_index]['score']}")
    # st.write(f"attempts: {st.session_state['words']['list'][st.session_state.chosen_word_index]['attempts']}")

    if st.session_state.failed_attempts < 2:
        ### BUTTONS
        cols = st.columns([3, 1, 1, 1])
        with cols[0]:
            if st.session_state['words']['list'][st.session_state.chosen_word_index]['attempts'] > 0:
                st.write(f"{st.session_state['words']['list'][st.session_state.chosen_word_index]['score'] / st.session_state['words']['list'][st.session_state.chosen_word_index]['attempts'] * 100:.2f}%")
            # else:
                # st.write("Never tried this word")

        with cols[1]:
            if st.button(":blue[Show]"):
                st.session_state.given_up = True
                # st.markdown(f":blue[{chosen_word()}]")

        with cols[2]:
            placeholder_sayitagain = st.empty()

        with cols[3]:
            placeholder_skip = st.empty()
            


        if st.session_state.given_up:
            st.markdown(f"# :blue[{chosen_word()}]")


        ### SPEAK THE WORD
        if st.session_state.speak_word:
            example = st.session_state['words']['list'][st.session_state.chosen_word_index]['example']
            if example != "":
                subprocess.run(['say', f"Spell: `{chosen_word()}`.\n\n", f"As in: '{example}'", '-v', 'Alex'])
            else:
                subprocess.run(['say', f"Spell: `{chosen_word()}`", '-v', 'Alex'])

            st.session_state.speak_word = False

        if not st.session_state.given_up:
            if placeholder_sayitagain.button('Say it :orange[again]'):
                st.session_state.speak_word = True
                st.rerun()
        
        if placeholder_skip.button(":red[Skip]"):
            choose_word()
            st.rerun()


    # with st.sidebar.popover("Debugging"):
    #     st.write(st.session_state)
