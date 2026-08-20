from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.learning.models import LearningResource, LearningTopic
from app.learning.schemas import (
    LearningResourceCreate,
    LearningResourceRead,
    LearningStatus,
    LearningTopicCreate,
    LearningTopicRead,
    LearningTopicUpdate,
)

router = APIRouter(prefix="/learning/topics", tags=["learning"])


DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[LearningTopicRead])
def list_topics(
    db: DbSession,
    area: Annotated[str | None, Query(min_length=1, max_length=80)] = None,
    status_filter: Annotated[LearningStatus | None, Query(alias="status")] = None,
) -> list[LearningTopic]:
    statement = select(LearningTopic).order_by(LearningTopic.area, LearningTopic.title)
    if area is not None:
        statement = statement.where(LearningTopic.area == area)
    if status_filter is not None:
        statement = statement.where(LearningTopic.status == status_filter.value)

    return list(db.scalars(statement).all())


@router.post(
    "",
    response_model=LearningTopicRead,
    status_code=status.HTTP_201_CREATED,
)
def create_topic(topic: LearningTopicCreate, db: DbSession) -> LearningTopic:
    db_topic = LearningTopic(**topic.model_dump(mode="json"))
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic


@router.get("/{topic_id}", response_model=LearningTopicRead)
def get_topic(topic_id: int, db: DbSession) -> LearningTopic:
    topic = db.get(LearningTopic, topic_id)
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning topic not found",
        )
    return topic


@router.patch("/{topic_id}", response_model=LearningTopicRead)
def update_topic(
    topic_id: int, update: LearningTopicUpdate, db: DbSession
) -> LearningTopic:
    topic = db.get(LearningTopic, topic_id)
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning topic not found",
        )

    for field, value in update.model_dump(exclude_unset=True, mode="json").items():
        setattr(topic, field, value)

    db.commit()
    db.refresh(topic)
    return topic


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(topic_id: int, db: DbSession) -> Response:
    topic = db.get(LearningTopic, topic_id)
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning topic not found",
        )

    db.delete(topic)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{topic_id}/resources",
    response_model=list[LearningResourceRead],
)
def list_resources(topic_id: int, db: DbSession) -> list[LearningResource]:
    topic = db.get(LearningTopic, topic_id)
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning topic not found",
        )

    statement = (
        select(LearningResource)
        .where(LearningResource.topic_id == topic_id)
        .order_by(LearningResource.created_at, LearningResource.id)
    )
    return list(db.scalars(statement).all())


@router.post(
    "/{topic_id}/resources",
    response_model=LearningResourceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_resource(
    topic_id: int, resource: LearningResourceCreate, db: DbSession
) -> LearningResource:
    topic = db.get(LearningTopic, topic_id)
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning topic not found",
        )

    db_resource = LearningResource(
        topic_id=topic_id,
        **resource.model_dump(mode="json"),
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource


@router.delete(
    "/{topic_id}/resources/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_resource(topic_id: int, resource_id: int, db: DbSession) -> Response:
    topic = db.get(LearningTopic, topic_id)
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning topic not found",
        )

    resource = db.get(LearningResource, resource_id)
    if resource is None or resource.topic_id != topic_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning resource not found",
        )

    db.delete(resource)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
