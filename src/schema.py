from typing import List, Union, Optional
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

# Spaced Repetition System

class User(BaseModel):
    name: str = Field(...)


class UserAttempt(BaseModel):
    user_id: str = Field(...)
    problem_id: str = Field(...)
    attempt_date: datetime = Field(default_factory=lambda: datetime.now())
    was_correct: bool = Field(...)


class Problem(BaseModel):
    problem_set_id: str = Field(...)
    problem_type: str = Field(...)


class SpellingProblem(Problem):
    word: str = Field(...)
    example_usage: str



class ProblemType(Enum):
    # ANY = "any"
    SPELLING = "spelling"
    MATH = "math"
    SHORT_ANSWER = "short_answer"
    DEFINITION = "definition"
    MULTIPLE_CHOICE = "multiple_choice"


class ProblemSet(BaseModel):
    user_id: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    type: Optional[str] = None  # Enum field set to optional
    # type: Optional[ProblemType] = None  # Enum field set to optional
