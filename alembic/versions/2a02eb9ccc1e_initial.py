"""initial

Revision ID: 2a02eb9ccc1e
Revises:
Create Date: 2025-11-26 17:30:50.040071

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2a02eb9ccc1e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("email", sa.String(255), unique=True),
        sa.Column("username", sa.String(50), unique=True),
        sa.Column("first_name", sa.String(100)),
        sa.Column("last_name", sa.String(100)),
        sa.Column("hashed_password", sa.String(255)),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("role", sa.String(50)),
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(50), unique=True),
    )

    op.create_table(
        "todos",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("title", sa.String(100), unique=True),
        sa.Column("description", sa.String(500)),
        sa.Column("priority", sa.Integer),
        sa.Column("complete", sa.Boolean, default=False),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id")),
    )

    op.create_table(
        "todo_tags",
        sa.Column("todo_id", sa.Integer, sa.ForeignKey("todos.id"), primary_key=True),
        sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id"), primary_key=True),
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Drop dependent (child) tables first
    op.drop_table("todo_tags")
    op.drop_table("todos")
    op.drop_table("tags")
    op.drop_table("users")
