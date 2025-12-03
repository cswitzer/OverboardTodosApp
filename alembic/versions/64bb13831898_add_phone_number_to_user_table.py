"""add phone number to user table

Revision ID: 64bb13831898
Revises: 2a02eb9ccc1e
Create Date: 2025-12-03 12:39:53.210264

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "64bb13831898"
down_revision: Union[str, Sequence[str], None] = "2a02eb9ccc1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users", sa.Column("phone_number", sa.String(length=20), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "phone_number")
