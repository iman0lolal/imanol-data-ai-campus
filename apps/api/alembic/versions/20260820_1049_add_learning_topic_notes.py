"""Add learning topic notes.

Revision ID: 20260820_1049
Revises: 20260820_1016
Create Date: 2026-08-20 10:49:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260820_1049"
down_revision: str | None = "20260820_1016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("learning_topics", sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("learning_topics", "notes")
