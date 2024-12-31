from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Spaced Repetition System

class User(BaseModel):
    name: str = Field(...)


class UserAttempt(BaseModel):
    user_id: str = Field(...)
    word_id: str = Field(...)
    attempt_date: datetime = Field(default_factory=lambda: datetime.now())
    was_correct: bool = Field(...)


class SpellingWord(BaseModel):
    word_list_id: str = Field(...)
    word: str = Field(...)
    example_usage: str = Field(...)
    notes: Optional[str] = None


class WordList(BaseModel):
    user_id: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    words: List[SpellingWord] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    last_modified: datetime = Field(default_factory=lambda: datetime.now())
