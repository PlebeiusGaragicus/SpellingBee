import os
import time
import random

import streamlit as st

from src.login import login
from src.database import get_db
from src.schema import UserAttempt
from src.speech import TTS



def choose_word():
    st.session_state.failed_attempts = 0
    st.session_state.given_up = False

    # Check if a word list is selected
    if not st.session_state.get("selected_wordlist_id"):
        st.info("Please select a word list from the Word Lists page")
        st.stop()

    # query for problems with this problem set id
    db = get_db()
    problems = list(db["problem"].find({"problem_set_id": st.session_state.selected_wordlist_id}))
    
    if not problems:
        st.info("This word list has no words yet. Add some words to the list first!")
        st.stop()

    # Get all problem IDs
    problem_ids = [str(problem['_id']) for problem in problems]

    # Use aggregation pipeline to efficiently calculate accuracies
    pipeline = [
        {"$match": {"word_id": {"$in": problem_ids}}},
        {"$group": {
            "_id": "$word_id",
            "accuracy": {"$avg": {"$cond": [{"$eq": ["$was_correct", True]}, 1, 0]}}
        }}
    ]
    accuracies = {str(result['_id']): result['accuracy'] for result in db["attempts"].aggregate(pipeline)}
    
    # Create problems with accuracy list, defaulting to 0 for words with no attempts
    problems_with_accuracy = [(problem, accuracies.get(str(problem['_id']), 0)) for problem in problems]

    # Decide on the category only once per execution
    rand_choice = random.random()

    # Categorize problems
    if rand_choice < 0.7:  # 70% chance for hard problems
        problems_to_show = [problem for problem, accuracy in problems_with_accuracy if accuracy < 0.6]
    elif rand_choice < 0.8:  # 10% chance for easy problems, cumulative probability 0.7 + 0.1 = 0.8
        problems_to_show = [problem for problem, accuracy in problems_with_accuracy if accuracy >= 0.9]
    else:  # 20% chance for medium problems, rest of the probability space
        problems_to_show = [problem for problem, accuracy in problems_with_accuracy if 0.6 <= accuracy < 0.9]

    # Fallback to all problems if no problems fit the criteria
    if not problems_to_show:
        problems_to_show = [problem for problem, _ in problems_with_accuracy]

    if os.getenv("DEBUG"):
        st.write(problems_to_show)

    # Select a random problem to show
    random_problem = random.choice(problems_to_show)




    st.session_state.chosen_word_id = str(random_problem['_id'])
    st.session_state.chosen_word = random_problem['word']
    if random_problem['usage']:
        st.session_state.speak_this = f"Spell: '{random_problem['word']}'.\n\n As in: {random_problem['example_usage']}"
    else:
        st.session_state.speak_this = f"Spell: '{random_problem['word']}'."


def chosen_word():
    return st.session_state.chosen_word



def select_a_set():
    with st.container(border=True):
        db = get_db()

        # user_id = db["users"].find_one({"name": st.session_state.username})["_id"]
        # user_id_str = str(user_id)
        # st.sidebar.write(f"User ID: '{user_id_str}'")

        problemsets = list(db["problemset"].find({"user_id": st.session_state.user_id_str}))

        # find problem sets of type "spelling"
        spelling_sets = [problemset['title'] for problemset in problemsets if problemset['type'] == "spelling"]

        selected_set = st.selectbox("Spelling sets", spelling_sets, index=None)

        if selected_set:
            # find the selected set
            st.session_state.practice_set = db["problemset"].find_one({"title": selected_set})
            st.rerun()

    st.stop()



def show_attempts():
    db = get_db()
    attempts = list(db["attempts"].find({"user_id": st.session_state.user_id_str, "word_id": st.session_state.chosen_word_id}))
    # st.write(attempts)

    accuracy = sum([attempt['was_correct'] for attempt in attempts]) / len(attempts) if len(attempts) > 0 else 0
    color = "green" if accuracy > 0.8 else "red"
    st.write(f"Accuracy: :{color}[{accuracy * 100:.0f}%]")


def change_score(correct):
    if st.session_state.given_up:
        return

    db = get_db()
    attempt = UserAttempt(user_id=st.session_state.user_id_str,
                            word_id=st.session_state.chosen_word_id,
                            was_correct=correct)

    db['attempts'].insert_one(attempt.model_dump())



###############################################
def page():
    if not login():
        return

    st.header('🧠 :rainbow[Spelling practice]', divider="rainbow")


    if not st.session_state.get("chosen_word", None):
        choose_word()


    tts_placeholder = st.empty()

    show_attempts()

    # st.write(st.session_state.failed_attempts)

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
                st.session_state.failed_attempts += 1

                change_score(False)
                if st.session_state.failed_attempts == 0:
                    st.error('Incorrect! Try again.')
                    st.rerun()
                elif st.session_state.failed_attempts == 1:
                    st.error('Try one more time!')
                else:
                    st.markdown(f"# Sorry, the word was `{chosen_word()}`")
                    # choose_word()
                    # st.rerun()

    cols = st.columns([3, 1, 1, 1])
    give_up = st.empty()
    with cols[-1]:
        if st.button("😿 :grey[give up]"):    
            give_up.markdown(f"# :blue[{chosen_word()}]")
            st.session_state.given_up = True


    if st.session_state.failed_attempts < 2 and not st.session_state.given_up:
        with tts_placeholder:
            TTS(st.session_state.speak_this, slow=False)
