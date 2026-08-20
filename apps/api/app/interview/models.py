from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

QUESTION_TYPES = ("coding", "conceptual", "scenario", "behavioral")
QUESTION_DIFFICULTIES = ("easy", "medium", "hard")
ANSWER_FORMATS = ("sql", "python", "free_text", "star")
ATTEMPT_CONFIDENCES = ("low", "medium", "high")
ATTEMPT_RESULTS = ("needs_work", "acceptable", "strong")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    __table_args__ = (
        CheckConstraint(
            "question_type in ('coding', 'conceptual', 'scenario', 'behavioral')",
            name="ck_interview_questions_question_type",
        ),
        CheckConstraint(
            "difficulty in ('easy', 'medium', 'hard')",
            name="ck_interview_questions_difficulty",
        ),
        CheckConstraint(
            "answer_format in ('sql', 'python', 'free_text', 'star')",
            name="ck_interview_questions_answer_format",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    subtopic: Mapped[str | None] = mapped_column(String(120), nullable=True)
    question_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    answer_format: Mapped[str] = mapped_column(String(20), nullable=False)
    expected_concepts: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(160), nullable=True)
    source_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    attempts: Mapped[list["InterviewAttempt"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class InterviewAttempt(Base):
    __tablename__ = "interview_attempts"
    __table_args__ = (
        CheckConstraint(
            "confidence in ('low', 'medium', 'high')",
            name="ck_interview_attempts_confidence",
        ),
        CheckConstraint(
            "result in ('needs_work', 'acceptable', 'strong')",
            name="ck_interview_attempts_result",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[str | None] = mapped_column(String(20), nullable=True)
    result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    question: Mapped[InterviewQuestion] = relationship(back_populates="attempts")
