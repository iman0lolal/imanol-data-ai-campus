from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class LearningStatus(StrEnum):
    not_started = "not_started"
    learning = "learning"
    reviewing = "reviewing"
    mastered = "mastered"


class LearningDifficulty(StrEnum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class LearningResourceType(StrEnum):
    documentation = "documentation"
    article = "article"
    video = "video"
    course = "course"
    repository = "repository"
    exercise = "exercise"
    other = "other"


class LearningTopicBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    area: str = Field(min_length=1, max_length=80)
    description: str | None = None
    notes: str | None = None
    status: LearningStatus = LearningStatus.not_started
    difficulty: LearningDifficulty = LearningDifficulty.medium
    progress: int = Field(default=0, ge=0, le=100)


class LearningTopicCreate(LearningTopicBase):
    pass


class LearningTopicUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    area: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = None
    notes: str | None = None
    status: LearningStatus | None = None
    difficulty: LearningDifficulty | None = None
    progress: int | None = Field(default=None, ge=0, le=100)


class LearningTopicRead(LearningTopicBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LearningResourceBase(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    url: HttpUrl
    resource_type: LearningResourceType = LearningResourceType.other
    description: str | None = None


class LearningResourceCreate(LearningResourceBase):
    pass


class LearningResourceRead(LearningResourceBase):
    id: int
    topic_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
