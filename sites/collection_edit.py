import streamlit as st

from src.database import get_db
from src.login import login
from src.schema import ProblemSet, ProblemType

def page():
    if not login():
        return

    st.header("📝 :rainbow[Edit a Collection]", divider="rainbow")


    db = get_db()

    # user_id = db["users"].find_one({"name": st.session_state.username})["_id"]
    # user_id_str = str(user_id)
    # st.sidebar.write(f"User ID: '{user_id_str}'")


    # find all ProblemSets inside "problemset" collection that belong to the current user
    problemsets = list(db["problemset"].find({"user_id": st.session_state.user_id_str}))

    if not problemsets:
        st.warning("You have no study collections yet!")
        return

    set_titles = [ps['title'] for ps in problemsets]
    selected_title = st.selectbox("Select a problemset", set_titles)
    selected_problemset = db["problemset"].find_one({"title": selected_title, "user_id": st.session_state.user_id_str})

    # Assuming ProblemType is an enum, similar logic for problem type selection
    # new_problem_type = st.selectbox("Problem Type", [pt.value for pt in ProblemType])

    if selected_problemset['type'] is None:
        new_problem_type = st.selectbox("Problem Type", [problem_type.value for problem_type in ProblemType])
    else:
        new_problem_type = selected_problemset['type']
        st.markdown(f"Collection Problem Type: `{new_problem_type}`")

    with st.form(key="add_problem", clear_on_submit=True):
        
        if new_problem_type == ProblemType.SHORT_ANSWER.value:
            question = st.text_input("Question")
            answer = st.text_input("Answer")
            prompt = st.text_input("Prompt")
            if st.form_submit_button("Add Problem"):
                if question == "" or answer == "" or prompt == "":
                    st.error("All fields must be filled")
                else:
                    # Instead of checking within a 'problems' array, you now query the 'problem' collection
                    existing_problem = db["problem"].find_one({
                        "problem_set_id": str(selected_problemset["_id"]),
                        "question": question  # Assuming 'question' sufficiently identifies a ShortAnswerProblem
                    })
                    if existing_problem is None:
                        # Insert the new problem as a document in the 'problem' collection
                        db["problem"].insert_one({
                            "problem_set_id": str(selected_problemset["_id"]),
                            "problem_type": new_problem_type,
                            "question": question,
                            "answer": answer,
                            "prompt": prompt
                            # You no longer need a 'type' field since classes differentiate problem types
                        })
                        st.success("Problem added successfully!")
                        st.rerun()
                    else:
                        st.error("Problem already exists in the selected problemset")


        elif new_problem_type == ProblemType.SPELLING.value:
            st.header(":green[New spelling word]", divider=True)
            word = st.text_input("Word")
            example_usage = st.text_input("Example Usage")
            if st.form_submit_button("Add word"):
                if word == "":
                    st.error("Must enter a word")
                else:
                    existing_problem = db["problemset"].find_one({"problem_set_id": str(selected_problemset["_id"]), "word": word})
                    if existing_problem is None:
                        db["problem"].insert_one({
                            "problem_set_id": str(selected_problemset["_id"]),
                            "problem_type": new_problem_type,
                            "word": word,
                            "example_usage": example_usage
                        })
                        st.success("Word added successfully!")
                        st.rerun()


        elif new_problem_type == ProblemType.MATH.value:
            equation = st.text_input("Equation")
            answer = st.text_input("Answer")
            if st.form_submit_button("Add Problem"):
                if equation == "" or answer == "":
                    st.error("All fields must be filled")
                else:
                    existing_problem = db["problemset"].find_one({"problem_set_id": str(selected_problemset["_id"]), "equation": equation})
                    if existing_problem is None:
                        db["problem"].insert_one({
                            "problem_set_id": str(selected_problemset["_id"]),
                            "problem_type": new_problem_type,
                            "equation": equation,
                            "answer": answer
                        })
                        st.success("Problem added successfully!")
                        st.rerun()

        elif new_problem_type == ProblemType.DEFINITION.value:
            word = st.text_input("Word")
            definition = st.text_input("Definition")
            if st.form_submit_button("Add Problem"):
                if word == "" or definition == "":
                    st.error("All fields must be filled")
                else:
                    existing_problem = db["problemset"].find_one({"problem_set_id": str(selected_problemset["_id"]), "word": word})
                    if existing_problem is None:
                        db["problem"].insert_one({
                            "problem_set_id": str(selected_problemset["_id"]),
                            "problem_type": new_problem_type,
                            "word": word,
                            "definition": definition
                        })
                        st.success("Problem added successfully!")
                        st.rerun()
        
        elif new_problem_type == ProblemType.MULTIPLE_CHOICE.value:
            question = st.text_input("Question")
            choices = st.text_area("Choices", value="Choice 1\nChoice 2\nChoice 3\nChoice 4")
            answer = st.selectbox("Answer", [f"Choice {i+1}" for i in range(4)])
            if st.form_submit_button("Add Problem"):
                if question == "" or choices == "" or answer == "":
                    st.error("All fields must be filled")
                else:
                    existing_problem = db["problemset"].find_one({"problem_set_id": str(selected_problemset["_id"]), "question": question})
                    if existing_problem is None:
                        db["problem"].insert_one({
                            "problem_set_id": str(selected_problemset["_id"]),
                            "problem_type": new_problem_type,
                            "question": question,
                            "choices": choices.split("\n"),
                            "answer": int(answer.split(" ")[1]) - 1
                        })
                        # st.success("Problem added successfully!")
                        st.rerun()
                    else:
                        st.error("Problem already exists in the selected problemset")



    if new_problem_type == ProblemType.SPELLING.value:
        st.header(":violet[List of words in collection]", divider=True)
    else:
        st.header(":violet[List of problems in collection]", divider=True)

    # Query and list all problems related to the selected problem set
    problems = list(db["problem"].find({"problem_set_id": str(selected_problemset["_id"])}))
    if not problems:
        st.write("No problems in this collection yet.")
    else:
        for problem in problems:
            with st.container(border=True):
                # st.write(f"Problem Type: {problem['problem_type']}")
                # st.write(problem)

                if st.session_state.username == "root":
                    cols2 = st.columns((1, 1, 1, 1))
                else:
                    cols2 = st.columns((3, 1))
                with cols2[0]:
                    if problem['problem_type'] == "short_answer":
                        st.write(f"Question: {problem['question']}")
                        st.write(f"Answer: {problem['answer']}")
                        st.write(f"Prompt: {problem['prompt']}")

                    elif problem['problem_type'] == "spelling":
                        st.write(f"**{problem['word']}**")
                        st.caption(f"{problem['example_usage']}")

                    elif problem['problem_type'] == "math":
                        st.write(f"Equation: {problem['equation']}")
                        st.write(f"Answer: {problem['answer']}")

                    elif problem['problem_type'] == "definition":
                        st.write(f"Word: {problem['word']}")
                        st.write(f"Definition: {problem['definition']}")
                    
                    elif problem['problem_type'] == "multiple_choice":
                        st.write(f"Question: {problem['question']}")
                        for i, c in enumerate(problem['choices']):
                            if i == problem['answer']:
                                st.write(f"- :green[{c}]")
                            else:
                                st.markdown(f"- :red[{c}]")

                with cols2[1]:
                    attempts = list(db["attempts"].find({"user_id": st.session_state.user_id_str, "problem_id": str(problem['_id'])}))
                    # st.write(attempts)

                    # accuracy = sum([attempt['was_correct'] for attempt in attempts]) / len(attempts) if len(attempts) > 0 else 0
                    num_correct = sum([attempt['was_correct'] for attempt in attempts])
                    num_attempts = len(attempts)
                    accuracy = num_correct / num_attempts if num_attempts > 0 else 0

                    color = "green" if accuracy > 0.8 else "red"
                    # st.write(f"Accuracy: :{color}[{accuracy * 100:.0f}%]")
                    # st.button(f"🎯 :{color}[{accuracy * 100:.0f}%]", key=f"accuracy_{problem['_id']}", use_container_width=True, disabled=True)
                    # st.button(f"🎯 :{color}[{accuracy * 100:.0f}%]", key=f"accuracy_{problem['_id']}", use_container_width=True)
                    with st.container(border=True):
                        st.write(f"🎯 :blue[{num_correct}/{num_attempts}] :violet[|]  :{color}[{accuracy * 100:.0f}%]")
                        # st.write(f"% {num_correct}/{num_correct}")

                if st.session_state.username == "root":
                    with cols2[2]:
                        with st.popover(":green[Reset stats]", use_container_width=True):
                            if st.button("Reset", key=f"reset_{problem['_id']}", use_container_width=True):
                                db["attempts"].delete_many({"problem_id": str(problem["_id"])})
                                # st.success("Stats reset successfully!")
                                st.rerun()

                    with cols2[3]:
                        with st.popover(":red[Delete]", use_container_width=True):
                            st.error("Are you sure you want to delete this problem?")
                            if st.button(f":red[Delete]", key=f"delete_{problem['_id']}", use_container_width=True):
                                db["problem"].delete_one({"_id": problem["_id"]})
                                st.success("Problem deleted successfully!")
                                st.rerun()



    # if selected_problemset['type'] is None:
    #     new_problem_type = st.selectbox("Problem Type", [problem_type.value for problem_type in ProblemType])
    # else:
    #     new_problem_type = selected_problemset['type']
    #     st.markdown(f"Collection Problem Type: `{new_problem_type}`")

    # with st.form(key="add_problem", clear_on_submit=True):

    #     if new_problem_type == ProblemType.SHORT_ANSWER.value:
    #         question = st.text_input("Question")
    #         answer = st.text_input("Answer")
    #         prompt = st.text_input("Prompt")
    #         if st.form_submit_button("Add Problem"):
    #             if question == "" or answer == "" or prompt == "":
    #                 st.error("All fields must be filled")
    #             else:
    #                 existing_problem = db["problemset"].find_one({"title": selected_problemset['title'], "problems.question": question})
    #                 if existing_problem is None:
    #                     db["problemset"].update_one({"title": selected_problemset['title']}, {"$push": {"problems": {"type": new_problem_type, "question": question, "answer": answer, "prompt": prompt}}})
    #                     st.rerun()
    #                 else:
    #                     st.error("Problem already exists in the selected problemset")

    #     elif new_problem_type == ProblemType.SPELLING.value:
    #         st.header(":green[New spelling word]", divider=True)
    #         word = st.text_input("Word")
    #         example_usage = st.text_input("Example Usage")
    #         if st.form_submit_button("Add word"):
    #             if word == "" or example_usage == "":
    #                 st.error("All fields must be filled")
    #             else:
    #                 existing_problem = db["problemset"].find_one({"title": selected_problemset['title'], "problems.word": word})
    #                 if existing_problem is None:
    #                     db["problemset"].update_one({"title": selected_problemset['title']}, {"$push": {"problems": {"type": new_problem_type, "word": word, "example_usage": example_usage}}})
    #                     st.rerun()
    #                 else:
    #                     st.error("Problem already exists in the selected problemset")


    #     elif new_problem_type == ProblemType.MATH.value:
    #         equation = st.text_input("Equation")
    #         answer = st.text_input("Answer")
    #         if st.form_submit_button("Add Problem"):
    #             if equation == "" or answer == "":
    #                 st.error("All fields must be filled")
    #             else:
    #                 existing_problem = db["problemset"].find_one({"title": selected_problemset['title'], "problems.equation": equation})
    #                 if existing_problem is None:
    #                     db["problemset"].update_one({"title": selected_problemset['title']}, {"$push": {"problems": {"type": new_problem_type, "equation": equation, "answer": answer}}})
    #                     st.rerun()
    #                 else:
    #                     st.error("Problem already exists in the selected problemset")

    #     elif new_problem_type == ProblemType.DEFINITION.value:
    #         word = st.text_input("Word")
    #         definition = st.text_input("Definition")
    #         if st.form_submit_button("Add Problem"):
    #             if word == "" or definition == "":
    #                 st.error("All fields must be filled")
    #             else:
    #                 existing_problem = db["problemset"].find_one({"title": selected_problemset['title'], "problems.word": word})
    #                 if existing_problem is None:
    #                     db["problemset"].update_one({"title": selected_problemset['title']}, {"$push": {"problems": {"type": new_problem_type, "word": word, "definition": definition}}})
    #                     st.rerun()
    #                 else:
    #                     st.error("Problem already exists in the selected problemset")

    # if new_problem_type == ProblemType.SPELLING.value:
    #     st.header(":violet[List of words in collection]", divider=True)
    # else:
    #     st.header(":violet[List of problems in collection]", divider=True)

    # # list all problems in the selected problemset
    # # with st.expander("Problems"):
    # for problem in selected_problemset['problems']:
    #     with st.container(border=True):
    #         cols2 = st.columns((3, 1))
    #         with cols2[0]:
    #             if problem['type'] == "short_answer":
    #                 st.write(f"Question: {problem['question']}")
    #                 st.write(f"Answer: {problem['answer']}")
    #                 st.write(f"Prompt: {problem['prompt']}")
    #             elif problem['type'] == "spelling":
    #                 st.write(f"Word: {problem['word']}")
    #                 st.write(f"Example Usage: {problem['example_usage']}")
    #             elif problem['type'] == "math":

    #                 st.write(f"Equation: {problem['equation']}")
    #                 st.write(f"Answer: {problem['answer']}")
    #             elif problem['type'] == "definition":
    #                 # st.write("`Definition`")
    #                 st.write(f"Word: {problem['word']}")
    #                 st.write(f"Definition: {problem['definition']}")

    #         with cols2[1]:
    #             with st.popover(":red[Delete]"):
    #                 st.error("Are you sure you want to delete this problem?")
    #                 if st.button(f":red[Delete]", key=problem):
    #                     db["problemset"].update_one({"title": selected_problemset['title']}, {"$pull": {"problems": problem}})
    #                     st.rerun()

