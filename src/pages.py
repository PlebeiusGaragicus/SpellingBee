from enum import Enum

from src.practice import page as practice_page

from src.collection_edit import page as collection_edit_page
from src.page_word_lists import page as word_lists_page

from src.root import page as root_page


class Pages(Enum):
    PRACTICE = ("🧠 :rainbow[Practice]", practice_page, False)

    WORD_LISTS = ("📚 :green[Home Page]", word_lists_page, True)
    COLLECTION_EDIT = ("📝 :blue[Word Lists]", collection_edit_page, True)

    ROOT_PANEL = ("🔒 :red[Root panel]", root_page, True)
