"""add state to Pet

Revision ID: 1950ee25973e
Revises: 047acfbd6858
Create Date: 2025-06-25 00:24:45.122301

"""
from typing import Sequence, Union
from sqlalchemy import Column, String
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1950ee25973e'
down_revision: Union[str, None] = '047acfbd6858'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
    "pets",
    sa.Column("state", sa.String(), nullable=False, server_default="normal")
)


def downgrade() -> None:
    op.drop_column("pets", "state")
