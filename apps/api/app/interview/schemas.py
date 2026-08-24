from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class InterviewQuestionType(StrEnum):
    coding = "coding"
    conceptual = "conceptual"
    scenario = "scenario"
    behavioral = "behavioral"


class InterviewDifficulty(StrEnum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class InterviewAnswerFormat(StrEnum):
    sql = "sql"
    python = "python"
    free_text = "free_text"
    star = "star"


class InterviewQuestionRead(BaseModel):
    id: int
    question: str
    category: str
    topic: str
    subtopic: str | None
    question_type: InterviewQuestionType
    difficulty: InterviewDifficulty
    answer_format: InterviewAnswerFormat
    expected_concepts: str | None
    reference_answer: str | None
    source: str | None
    source_context: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
