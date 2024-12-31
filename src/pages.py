from enum import Enum

from src import page_word_lists
from src.progress_report import page as progress_report_page
from src.practice import page as practice_page

# from src.study_collections import page as study_collections_page
from src.collection_edit import page as collection_edit_page
from src.page_word_lists import page as word_lists_page

from src.root import page as root_page



class Pages(Enum):

    PRACTICE = ("🧠 :rainbow[Practice]", practice_page, False)

    # STUDY_COLLECTIONS = ("📚 :green[Word Lists]", page_word_lists, True)
    WORD_LISTS = ("📚 :green[Word Lists]", word_lists_page, True)
    COLLECTION_EDIT = ("📝 :blue[Edit a Collection]", collection_edit_page, True)

    PROGRESS_REPORT = ("📈 :violet[Progress Report]", progress_report_page, True)

    ROOT_PANEL = ("🔒 :red[Root panel]", root_page, True)
