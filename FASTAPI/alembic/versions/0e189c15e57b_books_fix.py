"""books fix

Revision ID: 0e189c15e57b
Revises: 7fb586c3415b
Create Date: 2025-06-30 16:32:51.966112
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0e189c15e57b'
down_revision: Union[str, None] = '7fb586c3415b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # сначала обновим все NULL → []
    op.execute("UPDATE pets SET read_books = '[]' WHERE read_books IS NULL")

    # теперь можно сделать колонку NOT NULL
    op.alter_column(
        'pets',
        'read_books',
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        'pets',
        'read_books',
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        nullable=True
    )

