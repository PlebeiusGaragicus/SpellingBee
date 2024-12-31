import time
import yaml

import streamlit as st
import streamlit_authenticator as stauth

from src.database import get_db


def setup_user_id():
    if st.session_state.username == "root":
        with st.container(border=True):
            # list users in user collection
            db = get_db()
            users = db["users"]
            all_users = list(users.find())
            selected_user = st.selectbox("Assume a user", [all_users['name'] for all_users in all_users])
            if selected_user:
                # st.write(selected_user)
                user_id = db["users"].find_one({"name": selected_user})["_id"]
                st.session_state.user_id_str = str(user_id)
                st.caption(f"User ID: '{st.session_state.user_id_str}'")

            else:
                st.stop()
    else:
        if "user_id_str" not in st.session_state:
            db = get_db()
            user_id = db["users"].find_one({"name": st.session_state.username})
            if not user_id:
                # create a user
                db["users"].insert_one({"name": st.session_state.username,})
                st.balloons()
                st.toast("Welcome to Full Academy!", icon="🎉")
                time.sleep(2)
                st.rerun()
                # user_id = db["users"].find_one({"name": st.session_state.username})["_id"]
            user_id = user_id["_id"]
            st.session_state.user_id_str = str(user_id)
        # st.sidebar.write(f"User ID: '{st.session_state.user_id_str}'")
    



# def login(username: str = None):
def login(need_root: bool = False):
    """
    if st.session_state["authentication_status"]:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
        st.title('Some content')
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')
    """

    try:
        with open("./auth.yaml") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        st.error("This instance of PlebChat has not been configured.  Missing `auth.yaml` file.")
        # TODO - just create an empty file and then re-run?  Put default root password in there and have user change it?
        st.stop()

    st.session_state.authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        # config["preauthorized"],
    )

    # if st.session_state["authentication_status"] is None:
        # if 'appstate' in st.session_state:
        #     del st.session_state['appstate']
        #     st.error("Application state has been cleared!")

    if st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
        return False

    # https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
    # https://github.com/mkhorasani/Streamlit-Authenticator?ref=blog.streamlit.io
    st.session_state.authenticator.login(location="main", max_concurrent_users=1, fields={
        "Form name": "FullAcademy",
        "Username": "Username",
        "Password": "Password",
        "Login": "Enter, Teacher!",
    })


    if st.session_state["authentication_status"] is True:
        with st.sidebar:
            st.header("", divider="rainbow")
            st.session_state.authenticator.logout(button_name=f":red[👋🏻 Logout] `{st.session_state.username}`")

            setup_user_id()

        if need_root:
            if st.session_state.username == "root":
                return True
            else:
                st.error("You do not have permission to access this page.")
                return False
        else:
            return True

            #     # list users in user collection
            #     db = get_db()
            #     users = db["users"]
            #     all_users = list(users.find())
            #     selected_user = st.selectbox("Select a user", [all_users['name'] for all_users in all_users])
            #     if selected_user:
            #         st.write(selected_user)
            #         user_id = db["users"].find_one({"name": selected_user})["_id"]
            #         st.session_state.user_id_str = str(user_id)
            #         st.sidebar.write(f"User ID: '{st.session_state.user_id_str}'")

            #         setup_user_id()
            #         return True
            #     else:
            #         st.stop()
            # else:
            #     st.error("You do not have permission to access this page.")
            #     return False

        # else:
        #     if "user_id_str" not in st.session_state:
        #         db = get_db()
        #         user_id = db["users"].find_one({"name": st.session_state.username})
        #         if not user_id:
        #             # create a user
        #             db["users"].insert_one({
        #                 "name": st.session_state.username,
        #                 # "role": "student",
        #             })
        #             st.balloons()
        #             st.toast("New user!", "🎉")
        #             time.sleep(1)
        #             user_id = db["users"].find_one({"name": st.session_state.username})["_id"]
        #         user_id = user_id["_id"]
        #         st.session_state.user_id_str = str(user_id)
        #         st.sidebar.write(f"User ID: '{st.session_state.user_id_str}'")

        #     return True










# def login_required():
#     """
#     if st.session_state["authentication_status"]:
#         authenticator.logout()
#         st.write(f'Welcome *{st.session_state["name"]}*')
#         st.title('Some content')
#     elif st.session_state["authentication_status"] is False:
#         st.error('Username/password is incorrect')
#     elif st.session_state["authentication_status"] is None:
#         st.warning('Please enter your username and password')
#     """

#     try:
#         with open("./auth.yaml") as file:
#             config = yaml.safe_load(file)
#     except FileNotFoundError:
#         st.error("This instance of PlebChat has not been configured.  Missing `auth.yaml` file.")
#         # TODO - just create an empty file and then re-run?  Put default root password in there and have user change it?
#         st.stop()

#     st.session_state.authenticator = stauth.Authenticate(
#         config["credentials"],
#         config["cookie"]["name"],
#         config["cookie"]["key"],
#         config["cookie"]["expiry_days"],
#         # config["preauthorized"],
#     )


#     if st.session_state["authentication_status"] is False:
#         st.error("Username/password is incorrect")
#         return False

#     # https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
#     # https://github.com/mkhorasani/Streamlit-Authenticator?ref=blog.streamlit.io
#     st.session_state.authenticator.login(location="main", max_concurrent_users=1, fields={
#         "Form name": "FullAcademy",
#         "Username": "Username",
#         "Password": "Password",
#         "Login": "Enter, Teacher!",
#     })

#     if st.session_state["authentication_status"] is None:
#         st.warning("Please enter your username and password")
#         return False

#     if st.session_state["authentication_status"] is True:
#         with st.sidebar:
#             st.session_state.authenticator.logout(button_name=":red[👋🏻 Logout]")
        
#         return True
