from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased

from app.db.session import get_db
from app.interview.models import InterviewAttempt, InterviewQuestion
from app.interview.schemas import (
    InterviewAttemptCreate,
    InterviewAttemptRead,
    InterviewConfidence,
    InterviewDifficulty,
    InterviewProgressBreakdownItem,
    InterviewProgressOverall,
    InterviewProgressRead,
    InterviewQuestionRead,
    InterviewQuestionType,
    InterviewResult,
    InterviewRevisitQuestion,
)

router = APIRouter(prefix="/interview", tags=["interview"])


DbSession = Annotated[Session, Depends(get_db)]


def _coverage_percentage(total_questions: int, attempted_questions: int) -> float:
    if total_questions == 0:
        return 0.0
    return round((attempted_questions / total_questions) * 100, 1)


def _latest_attempt_ids_subquery():
    return (
        select(
            InterviewAttempt.question_id.label("question_id"),
            func.max(InterviewAttempt.id).label("latest_attempt_id"),
        )
        .group_by(InterviewAttempt.question_id)
        .subquery()
    )


@router.get("/progress", response_model=InterviewProgressRead)
def get_progress(db: DbSession) -> InterviewProgressRead:
    attempted_question_ids = select(InterviewAttempt.question_id).distinct().subquery()

    total_questions = db.scalar(select(func.count(InterviewQuestion.id))) or 0
    attempted_questions = (
        db.scalar(select(func.count(func.distinct(InterviewAttempt.question_id)))) or 0
    )
    total_attempts = db.scalar(select(func.count(InterviewAttempt.id))) or 0

    category_rows = db.execute(
        select(
            InterviewQuestion.category,
            func.count(InterviewQuestion.id),
            func.count(attempted_question_ids.c.question_id),
        )
        .outerjoin(
            attempted_question_ids,
            attempted_question_ids.c.question_id == InterviewQuestion.id,
        )
        .group_by(InterviewQuestion.category)
        .order_by(InterviewQuestion.category)
    ).all()
    difficulty_rows = db.execute(
        select(
            InterviewQuestion.difficulty,
            func.count(InterviewQuestion.id),
            func.count(attempted_question_ids.c.question_id),
        )
        .outerjoin(
            attempted_question_ids,
            attempted_question_ids.c.question_id == InterviewQuestion.id,
        )
        .group_by(InterviewQuestion.difficulty)
        .order_by(InterviewQuestion.difficulty)
    ).all()

    latest_attempt_ids = _latest_attempt_ids_subquery()
    latest_attempt = aliased(InterviewAttempt)
    revisit_rows = db.execute(
        select(InterviewQuestion, latest_attempt)
        .join(
            latest_attempt_ids, latest_attempt_ids.c.question_id == InterviewQuestion.id
        )
        .join(
            latest_attempt, latest_attempt.id == latest_attempt_ids.c.latest_attempt_id
        )
        .where(
            or_(
                latest_attempt.confidence == InterviewConfidence.low.value,
                latest_attempt.result == InterviewResult.needs_work.value,
            )
        )
        .order_by(
            InterviewQuestion.category, InterviewQuestion.topic, InterviewQuestion.id
        )
        .limit(8)
    ).all()

    return InterviewProgressRead(
        overall=InterviewProgressOverall(
            total_questions=total_questions,
            attempted_questions=attempted_questions,
            unattempted_questions=total_questions - attempted_questions,
            coverage_percentage=_coverage_percentage(
                total_questions, attempted_questions
            ),
            total_attempts=total_attempts,
        ),
        by_category=[
            InterviewProgressBreakdownItem(
                name=category,
                total_questions=total,
                attempted_questions=attempted,
                coverage_percentage=_coverage_percentage(total, attempted),
            )
            for category, total, attempted in category_rows
        ],
        by_difficulty=[
            InterviewProgressBreakdownItem(
                name=difficulty,
                total_questions=total,
                attempted_questions=attempted,
                coverage_percentage=_coverage_percentage(total, attempted),
            )
            for difficulty, total, attempted in difficulty_rows
        ],
        revisit_questions=[
            InterviewRevisitQuestion(
                id=question.id,
                question=question.question,
                category=question.category,
                topic=question.topic,
                difficulty=question.difficulty,
                latest_confidence=attempt.confidence,
                latest_result=attempt.result,
                latest_attempted_at=attempt.created_at,
            )
            for question, attempt in revisit_rows
        ],
    )


@router.get("/questions", response_model=list[InterviewQuestionRead])
def list_questions(
    db: DbSession,
    category: Annotated[str | None, Query(min_length=1, max_length=80)] = None,
    topic: Annotated[str | None, Query(min_length=1, max_length=80)] = None,
    difficulty: InterviewDifficulty | None = None,
    question_type: InterviewQuestionType | None = None,
    attempted: bool | None = None,
    confidence: InterviewConfidence | None = None,
    result: InterviewResult | None = None,
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
    if attempted is not None:
        attempted_question_ids = select(InterviewAttempt.question_id)
        if attempted:
            statement = statement.where(
                InterviewQuestion.id.in_(attempted_question_ids)
            )
        else:
            statement = statement.where(
                InterviewQuestion.id.not_in(attempted_question_ids)
            )
    if confidence is not None or result is not None:
        latest_attempt_ids = _latest_attempt_ids_subquery()
        latest_attempt = aliased(InterviewAttempt)
        statement = statement.join(
            latest_attempt_ids, latest_attempt_ids.c.question_id == InterviewQuestion.id
        ).join(
            latest_attempt, latest_attempt.id == latest_attempt_ids.c.latest_attempt_id
        )
        if confidence is not None:
            statement = statement.where(latest_attempt.confidence == confidence.value)
        if result is not None:
            statement = statement.where(latest_attempt.result == result.value)

    return list(db.scalars(statement).all())


@router.get("/questions/{question_id}", response_model=InterviewQuestionRead)
def get_question(question_id: int, db: DbSession) -> InterviewQuestion:
    question = db.get(InterviewQuestion, question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview question not found",
        )
    return question


@router.post(
    "/questions/{question_id}/attempts",
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
    "/questions/{question_id}/attempts",
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
