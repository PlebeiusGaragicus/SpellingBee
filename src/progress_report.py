import os
# from datetime import datetime
import time

import streamlit as st

from src.login import login
from src.database import get_db
from src.schema import UserAttempt


###############################################
def page():
    if not login():
        return

    st.header('📈 :rainbow[Spelling progress]', divider="rainbow")

    db = get_db()

    # find all UserAttempts inside "userattempt" collection that belong to the current user
    user_attempts = list(db["attempts"].find({"user_id": st.session_state.user_id_str}))
    # st.write(f"ALL UserAttempts: {user_attempts}")

    with st.container(border=True):
        attempts_in_last_2_days = [attempt for attempt in user_attempts if attempt['attempt_date'].timestamp() > time.time() - 2 * 24 * 60 * 60]
        st.write(f"Number of attempts in the last 2 days: `{len(attempts_in_last_2_days)}`")

    # with st.container(border=True):
    #     attempts_in_last_12_hours = [attempt for attempt in user_attempts if attempt['attempt_date'].timestamp() > time.time() - 12 * 60 * 60]
    #     st.write(f"Number of attempts in the last 12 hours: `{len(attempts_in_last_12_hours)}`")


    with st.container(border=True):
        attempts_in_last_6_hours = [attempt for attempt in user_attempts if attempt['attempt_date'].timestamp() > time.time() - 6 * 60 * 60]

        correct_attempts = [attempt for attempt in user_attempts if attempt['was_correct']]

        cols2 = st.columns(2)
        with cols2[0]:
            st.write(f"Number of attempts in the last 6 hours: `{len(attempts_in_last_6_hours)}`")
        with cols2[1]:
            st.write(f"Number of correct attempts: `{len(correct_attempts)}` / `{len(user_attempts)}`")

        ratio = len(correct_attempts) / len(attempts_in_last_6_hours) if len(attempts_in_last_6_hours) > 0 else 0

        colscen = st.columns((1, 2 ,1))
        with colscen[1]:
            if ratio > 0.8:
                st.success(f"Accuracy: {ratio * 100:.0f}%")
            else:
                st.error(f"Accuracy: {ratio * 100:.0f}%")

