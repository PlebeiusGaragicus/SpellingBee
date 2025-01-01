import os
import pathlib
from PIL import Image

import streamlit as st

# from src.common import cprint, Colors
from src.interface import hide_markdown_header_links
from src.pages import Pages
from src.login import login


APP_NAME = "Spelling Bee"
STATIC_PATH = pathlib.Path(__file__).parent.parent / "static"


def cmp_header():
    favicon = Image.open(os.path.join(STATIC_PATH, "favicon.ico"))
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=favicon,
        layout="wide",
        initial_sidebar_state="auto",
    )



# def log_rerun():
#     ip_addr = st.context.headers.get('X-Forwarded-For', "?")
#     user_agent = st.context.headers.get('User-Agent', "?")
#     lang = st.context.headers.get('Accept-Language', "?")

#     cprint(f"RUNNING for: {ip_addr} - {lang} - {user_agent}", Colors.YELLOW)







def main_page():
    # if os.getenv("DEBUG"):
    #     log_rerun()
    cmp_header()

    if not login():
        return

    hide_markdown_header_links()

    if "current_page" not in st.session_state:
        st.session_state.current_page = Pages.WORD_LISTS.value[0]


    def on_click(page):
        st.session_state.current_page = page

    with st.sidebar:
        for p in Pages:
            # root only
            if p.value[3] and st.session_state.get("username", None) != "root":
                continue

            if p.value[2]: # visible
                button_text = p.value[0]
                if st.session_state.current_page == p.value[0]:
                    button_text = f"⭐️ **{button_text}** ⭐️"
                st.button(button_text, on_click=on_click, args=(p.value[0],), use_container_width=True)


    for p in Pages:
        if st.session_state.current_page == p.value[0]:
            p.value[1]()
            break

    if st.session_state.username == "root":
        if os.getenv("DEBUG"):
            with st.sidebar:
                st.header("", divider="rainbow")
                with st.expander(label=":orange[Debug]", icon="🕷️"):
                    st.write(st.session_state)

                with st.expander(label=":orange[Context]", icon="🍪"):
                    st.write( st.context.cookies )
                    st.write( st.context.headers )
