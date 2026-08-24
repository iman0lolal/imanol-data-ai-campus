"""Create learning resources.

Revision ID: 20260820_1110
Revises: 20260820_1049
Create Date: 2026-08-20 11:10:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260820_1110"
down_revision: str | None = "20260820_1049"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "learning_resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("resource_type", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            (
                "resource_type in ('documentation', 'article', 'video', "
                "'course', 'repository', 'exercise', 'other')"
            ),
            name="ck_learning_resources_resource_type",
        ),
        sa.ForeignKeyConstraint(
            ["topic_id"],
            ["learning_topics.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_learning_resources_topic_id",
        "learning_resources",
        ["topic_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_learning_resources_topic_id", table_name="learning_resources")
    op.drop_table("learning_resources")
