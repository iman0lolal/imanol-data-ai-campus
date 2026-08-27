from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


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


class InterviewConfidence(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class InterviewResult(StrEnum):
    needs_work = "needs_work"
    acceptable = "acceptable"
    strong = "strong"


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


class InterviewProgressOverall(BaseModel):
    total_questions: int
    attempted_questions: int
    unattempted_questions: int
    coverage_percentage: float
    total_attempts: int


class InterviewProgressBreakdownItem(BaseModel):
    name: str
    total_questions: int
    attempted_questions: int
    coverage_percentage: float


class InterviewRevisitQuestion(BaseModel):
    id: int
    question: str
    category: str
    topic: str
    difficulty: InterviewDifficulty
    latest_confidence: InterviewConfidence | None
    latest_result: InterviewResult | None
    latest_attempted_at: datetime


class InterviewProgressRead(BaseModel):
    overall: InterviewProgressOverall
    by_category: list[InterviewProgressBreakdownItem]
    by_difficulty: list[InterviewProgressBreakdownItem]
    revisit_questions: list[InterviewRevisitQuestion]


class InterviewAttemptCreate(BaseModel):
    answer: str = Field(min_length=1)
    confidence: InterviewConfidence | None = None
    result: InterviewResult | None = None


class InterviewAttemptRead(InterviewAttemptCreate):
    id: int
    question_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
