from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.interview.models import InterviewAttempt, InterviewQuestion
from app.interview.schemas import (
    InterviewAttemptCreate,
    InterviewAttemptRead,
    InterviewDifficulty,
    InterviewQuestionRead,
    InterviewQuestionType,
)

router = APIRouter(prefix="/interview/questions", tags=["interview"])


DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[InterviewQuestionRead])
def list_questions(
    db: DbSession,
    category: Annotated[str | None, Query(min_length=1, max_length=80)] = None,
    topic: Annotated[str | None, Query(min_length=1, max_length=80)] = None,
    difficulty: InterviewDifficulty | None = None,
    question_type: InterviewQuestionType | None = None,
) -> list[InterviewQuestion]:
    statement = select(InterviewQuestion).order_by(
        InterviewQuestion.category,
        InterviewQuestion.topic,
        InterviewQuestion.id,
    )
    if category is not None:
        statement = statement.where(InterviewQuestion.category == category)
    if topic is not None:
        statement = statement.where(InterviewQuestion.topic == topic)
    if difficulty is not None:
        statement = statement.where(InterviewQuestion.difficulty == difficulty.value)
    if question_type is not None:
        statement = statement.where(
            InterviewQuestion.question_type == question_type.value
        )

    return list(db.scalars(statement).all())


@router.get("/{question_id}", response_model=InterviewQuestionRead)
def get_question(question_id: int, db: DbSession) -> InterviewQuestion:
    question = db.get(InterviewQuestion, question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview question not found",
        )
    return question


@router.post(
    "/{question_id}/attempts",
    response_model=InterviewAttemptRead,
    status_code=status.HTTP_201_CREATED,
)
def create_attempt(
    question_id: int, attempt: InterviewAttemptCreate, db: DbSession
) -> InterviewAttempt:
    question = db.get(InterviewQuestion, question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview question not found",
        )

    db_attempt = InterviewAttempt(
        question_id=question_id,
        **attempt.model_dump(mode="json"),
    )
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt


@router.get(
    "/{question_id}/attempts",
    response_model=list[InterviewAttemptRead],
)
def list_attempts(question_id: int, db: DbSession) -> list[InterviewAttempt]:
    question = db.get(InterviewQuestion, question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview question not found",
        )

    statement = (
        select(InterviewAttempt)
        .where(InterviewAttempt.question_id == question_id)
        .order_by(InterviewAttempt.id.desc())
    )
    return list(db.scalars(statement).all())
