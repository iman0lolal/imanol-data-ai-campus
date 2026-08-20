"""Create learning topics.

Revision ID: 20260820_1016
Revises:
Create Date: 2026-08-20 10:16:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260820_1016"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LEARNING_TOPICS = [
    {
        "title": "SQL fundamentals",
        "area": "Data Engineering",
        "description": "Practice querying, filtering, joining, and aggregating data.",
        "status": "learning",
        "difficulty": "easy",
        "progress": 20,
    },
    {
        "title": "Data modeling",
        "area": "Data Engineering",
        "description": "Learn how to structure data for analytics and applications.",
        "status": "not_started",
        "difficulty": "medium",
        "progress": 0,
    },
    {
        "title": "ETL vs ELT",
        "area": "Data Engineering",
        "description": "Compare common data pipeline loading patterns.",
        "status": "not_started",
        "difficulty": "easy",
        "progress": 0,
    },
    {
        "title": "Python for data",
        "area": "Analytics",
        "description": "Use Python for data cleaning, analysis, and automation.",
        "status": "learning",
        "difficulty": "easy",
        "progress": 35,
    },
    {
        "title": "Power BI fundamentals",
        "area": "Analytics",
        "description": "Build simple semantic models and dashboards.",
        "status": "not_started",
        "difficulty": "medium",
        "progress": 0,
    },
    {
        "title": "Spark fundamentals",
        "area": "Data Engineering",
        "description": "Understand distributed data processing basics.",
        "status": "not_started",
        "difficulty": "hard",
        "progress": 0,
    },
    {
        "title": "Supervised learning",
        "area": "AI / ML",
        "description": "Study labeled-data modeling concepts and evaluation.",
        "status": "not_started",
        "difficulty": "medium",
        "progress": 0,
    },
    {
        "title": "Model evaluation",
        "area": "AI / ML",
        "description": "Use metrics to understand model quality and tradeoffs.",
        "status": "not_started",
        "difficulty": "medium",
        "progress": 0,
    },
    {
        "title": "Embeddings",
        "area": "GenAI",
        "description": "Represent text as vectors for similarity and retrieval.",
        "status": "not_started",
        "difficulty": "medium",
        "progress": 0,
    },
    {
        "title": "RAG fundamentals",
        "area": "GenAI",
        "description": (
            "Understand retrieval augmented generation at a conceptual level."
        ),
        "status": "not_started",
        "difficulty": "hard",
        "progress": 0,
    },
    {
        "title": "Docker fundamentals",
        "area": "Cloud",
        "description": (
            "Learn containers, images, Compose, and local development workflows."
        ),
        "status": "reviewing",
        "difficulty": "medium",
        "progress": 60,
    },
    {
        "title": "Cloud fundamentals",
        "area": "Cloud",
        "description": "Learn core cloud concepts used across providers.",
        "status": "not_started",
        "difficulty": "easy",
        "progress": 0,
    },
]


def upgrade() -> None:
    learning_topics = op.create_table(
        "learning_topics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("area", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="not_started",
        ),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "status in ('not_started', 'learning', 'reviewing', 'mastered')",
            name="ck_learning_topics_status",
        ),
        sa.CheckConstraint(
            "difficulty in ('easy', 'medium', 'hard')",
            name="ck_learning_topics_difficulty",
        ),
        sa.CheckConstraint(
            "progress >= 0 and progress <= 100",
            name="ck_learning_topics_progress",
        ),
    )
    op.create_index("ix_learning_topics_area", "learning_topics", ["area"])
    op.create_index("ix_learning_topics_status", "learning_topics", ["status"])
    op.bulk_insert(learning_topics, LEARNING_TOPICS)


def downgrade() -> None:
    op.drop_index("ix_learning_topics_status", table_name="learning_topics")
    op.drop_index("ix_learning_topics_area", table_name="learning_topics")
    op.drop_table("learning_topics")
