"""Create interview attempts.

Revision ID: 20260820_1155
Revises: 20260820_1135
Create Date: 2026-08-20 11:55:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260820_1155"
down_revision: str | None = "20260820_1135"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "interview_attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("confidence", sa.String(length=20), nullable=True),
        sa.Column("result", sa.String(length=20), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "confidence in ('low', 'medium', 'high')",
            name="ck_interview_attempts_confidence",
        ),
        sa.CheckConstraint(
            "result in ('needs_work', 'acceptable', 'strong')",
            name="ck_interview_attempts_result",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["interview_questions.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_interview_attempts_question_id",
        "interview_attempts",
        ["question_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_interview_attempts_question_id", table_name="interview_attempts")
    op.drop_table("interview_attempts")
