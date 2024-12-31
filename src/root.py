import streamlit as st

from src.database import get_db
from src.login import login

def page():
    # if not login("root"):
    if not login(need_root=True):
        return

    st.header(f":red[ROOT PANEL]")

    db = get_db()

    st.markdown("## Collections")
    st.write(db.list_collection_names())

    users = db["users"]
    all_users = list(users.find())

    st.header("Users", divider=True)
    for user in all_users:
        with st.container(border=True):
            cols2 = st.columns(3)
            with cols2[0]:
                st.write(f":orange[{user['name']}]")

            with cols2[1]:
                with st.popover("info"):
                    st.write(user)

            with cols2[2]:
                with st.popover(":red[Delete User]"):
                    st.warning("Are you sure?")
                    if st.button(f"Delete {user['name']}"):
                        users.delete_one({"name": user["name"]})
                        st.rerun()
