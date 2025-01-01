import os
import pymongo
import streamlit as st
from urllib.parse import quote_plus

@st.cache_resource
def get_db():
    """
    Get MongoDB database connection using environment variables.
    Requires MONGODB_URI environment variable to be set.
    """
    mongodb_uri = os.getenv('MONGODB_URI')
    if not mongodb_uri:
        raise ValueError(
            "MONGODB_URI environment variable is not set. "
            "Please ensure your .env file contains MONGO_ROOT_USERNAME and MONGO_ROOT_PASSWORD"
        )
    
    client = pymongo.MongoClient(mongodb_uri)
    return client['spellingbee']

def init_db():
    """
    Initialize database collections and indexes if they don't exist.
    """
    db = get_db()
    
    # Create collections if they don't exist
    collections = ['word_lists', 'attempts']
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
    
    # Create indexes for word_lists collection
    word_lists = db.word_lists
    word_lists.create_index([('name', pymongo.ASCENDING)], unique=True)
    word_lists.create_index([('words', pymongo.ASCENDING)])
    
    # Create indexes for attempts collection
    attempts = db.attempts
    attempts.create_index([('user_id', pymongo.ASCENDING)])
    attempts.create_index([('attempt_date', pymongo.DESCENDING)])
    attempts.create_index([
        ('user_id', pymongo.ASCENDING),
        ('attempt_date', pymongo.DESCENDING)
    ])

# Initialize database when the module is imported
init_db()
