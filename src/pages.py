from enum import Enum

from src.practice import page as practice_page
from src.word_lists_page import page as word_lists_page
from src.root import page as root_page


class Pages(Enum):
    # (name, page, visible, root_only)
    PRACTICE = ("🧠 :rainbow[Practice]", practice_page, False, False)

    WORD_LISTS = ("📚 :green[Home Page]", word_lists_page, True, False)

    ROOT_PANEL = ("🔒 :red[Root panel]", root_page, True, True)
