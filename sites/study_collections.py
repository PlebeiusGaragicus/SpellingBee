import streamlit as st

from src.database import get_db
from src.login import login
from src.schema import ProblemSet, ProblemType


import sites


def page():
    if not login():
        return

    st.header("📚 :rainbow[Study Collections]", divider="rainbow")

    db = get_db()


    # DEBUG - view all problem sets
    all_problemsets = list(db["problemset"].find())
    st.json(all_problemsets)

    # find all ProblemSets inside "problemset" collection that belong to the current user
    problemsets = list(db["problemset"].find({"user_id": st.session_state.user_id_str}))
    # st.write(f"MY Problemsets: {problemsets}")


    # show a form to create a new collection
    with st.expander("🌱 :green[Create a new collection]"):
        with st.form(key="new_collection", clear_on_submit=True):
            title = st.text_input("Title")
            description = st.text_area("Description")
            type = st.selectbox("Type", [problem_type.value for problem_type in ProblemType], index=None, placeholder="Mixed")
            if st.form_submit_button("Create Collection"):
                # check if problemset with the same title already exists
                existing_problemset = db["problemset"].find_one({"title": title})
                if existing_problemset is not None:
                    st.error("Collection with the same title already exists")
                else:
                    if title == "":
                        st.error("Title must be filled")
                    else:
                        # new_problemset = ProblemSet(user_id=user_id, title=title, description=description, type=type, problems=[])
                        # new = new_problemset.model_dump()
                        # db["problemset"].insert_one( new )
                        db["problemset"].insert_one({
                            "user_id": st.session_state.user_id_str,
                            "title": title,
                            "description": description,
                            "type": type,
                        })

                        st.rerun()


    st.header(":green[Your Study Collections]", divider=True)

    if problemsets == []:
        st.warning("You have no study collections yet!")
        return


    # for each problemset, display its title, description, and problems
    for problemset in problemsets:
        with st.container(border=True):
            st.markdown(f"## :violet[{problemset['title']}]")
            # st.header(problemset['title'], divider=True)
            if problemset['description'] == "":
                st.caption("No description")
            else:
                st.caption(f"Description: {problemset['description']}")
            # st.write(problemset['description'])
            if problemset['type'] is None:
                st.write(f":green[Mixed problem types]")
            else:
                st.write(f"`{problemset['type']}`")

            with st.expander("Problems"):
                # Fetch and display problems associated with the current problemset
                problems = list(db["problem"].find({"problem_set_id": str(problemset["_id"])}))
                if not problems:
                    st.write("No problems in this collection yet.")
                else:
                    for problem in problems:
                            if problem['problem_type'] == "short_answer":
                                with st.container(border=True):
                                    st.write(f"Question: {problem['question']}")
                                    st.write(f"Answer: {problem['answer']}")
                                    st.write(f"Prompt: {problem['prompt']}")

                            elif problem['problem_type'] == "spelling":
                                st.markdown(f"* {problem['word']}")

                            elif problem['problem_type'] == "math":
                                with st.container(border=True):
                                    st.write(f"Equation: {problem['equation']}")
                                    st.write(f"Answer: {problem['answer']}")

                            elif problem['problem_type'] == "definition":
                                with st.container(border=True):
                                    st.write(f"Word: {problem['word']}")
                                    st.write(f"Definition: {problem['definition']}")
                            
                            elif problem['problem_type'] == "multiple_choice":
                                with st.container(border=True):
                                    st.write(f"Question: {problem['question']}")
                                    for c in problem['choices']:
                                        st.write(f"- {c}")
                                    st.write(f"Answer: {problem['answer']}")

            cols2 = st.columns((2, 2, 1))
            with cols2[0]:
                if st.button(":blue[Study this!]", key=f"study_{problemset['_id']}", use_container_width=True):
                    st.session_state.current_page = sites.PRACTICE # turn into function for better readability
                    st.session_state.practice_set = problemset
                    # del st.session_state.chosen_word # TODO - this is to cumbersome
                    st.session_state.chosen_word = None
                    st.rerun()
 
            if st.session_state.username == "root":
                with cols2[2]:
                    with st.popover(":red[Delete Collection]"):#, key=problemset["_id"]):
                        st.error("Warning: This action is irreversible!")
                        if st.button(f":red[Delete] {problemset['title']}", key=f"delete_{problemset['_id']}"):
                            db["problemset"].delete_one({"_id": problemset["_id"]})
                            st.rerun()
