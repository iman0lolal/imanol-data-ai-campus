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

LEARNING_STATUSES = ("not_started", "learning", "reviewing", "mastered")
LEARNING_DIFFICULTIES = ("easy", "medium", "hard")
LEARNING_RESOURCE_TYPES = (
    "documentation",
    "article",
    "video",
    "course",
    "repository",
    "exercise",
    "other",
)


class LearningTopic(Base):
    __tablename__ = "learning_topics"
    __table_args__ = (
        CheckConstraint(
            "status in ('not_started', 'learning', 'reviewing', 'mastered')",
            name="ck_learning_topics_status",
        ),
        CheckConstraint(
            "difficulty in ('easy', 'medium', 'hard')",
            name="ck_learning_topics_difficulty",
        ),
        CheckConstraint(
            "progress >= 0 and progress <= 100",
            name="ck_learning_topics_progress",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    area: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="not_started", index=True
    )
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    resources: Mapped[list["LearningResource"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class LearningResource(Base):
    __tablename__ = "learning_resources"
    __table_args__ = (
        CheckConstraint(
            (
                "resource_type in ('documentation', 'article', 'video', "
                "'course', 'repository', 'exercise', 'other')"
            ),
            name="ck_learning_resources_resource_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("learning_topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    topic: Mapped[LearningTopic] = relationship(back_populates="resources")
