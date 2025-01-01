import streamlit as st


def column_fix():
    st.write("""<style>
[data-testid="column"] {
    width: calc(33.3333% - 1rem) !important;
    flex: 1 1 calc(33.3333% - 1rem) !important;
    min-width: calc(33% - 1rem) !important;
}
</style>""", unsafe_allow_html=True)



def center_text(type, text, size=None):
    if size == None:
        st.write(f"<{type} style='text-align: center;'>{text}</{type}>", unsafe_allow_html=True)
    else:
        st.write(f"<{type} style='text-align: center; font-size: {size}px;'>{text}</{type}>", unsafe_allow_html=True)


def centered_button_trick():
    """ Use this in a `with` statement to center a button.
    
    Example:
    ```python
    with centered_button_trick():
        st.button(
            "👈 back",
            on_click=go_to_main_page,
            use_container_width=True)
    ```
    """
    columns = st.columns((1, 2, 1))
    with columns[0]:
        st.empty()
    # with columns[1]:
        # normally the button logic would go here
    with columns[2]:
        st.empty()

    return columns[1]


# def hide_markdown_header_links():
#     st.markdown("""
# .css-m70y {display:none}
# """, unsafe_allow_html=True)


# def hide_anchor_link():
def hide_markdown_header_links():
    """
    https://discuss.streamlit.io/t/hide-titles-link/19783/3
    """

        # <style>
        # .css-15zrgzn {display: none}
        # .css-eczf16 {display: none}
        # .css-jn99sy {display: none}
        # .st-emotion-cache-gi0tri {display: none}
        # .e121c1cl3 {display: none}
        # </style>
    st.markdown("""
        <style>
        .stApp a:first-child {
            display: none;
        }
        </style>
        """, unsafe_allow_html=True)


# <span data-testid="stHeaderActionElements" class="st-emotion-cache-gi0tri e121c1cl3"><a href="#f3e94a7" class="st-emotion-cache-ubko3j e121c1cl1"><svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 7h3a5 5 0 0 1 5 5 5 5 0 0 1-5 5h-3m-6 0H6a5 5 0 0 1-5-5 5 5 0 0 1 5-5h3"></path><line x1="8" y1="12" x2="16" y2="12"></line></svg></a></span>