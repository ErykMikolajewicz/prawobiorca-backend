"""Add chunk span

Revision ID: 4f9e0031df88
Revises: a7b8c9d0e1f2
Create Date: 2026-09-19 05:06:41.885654

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4f9e0031df88'
down_revision: Union[str, Sequence[str], None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('regulations_chunks', sa.Column('span_start_element', sa.Integer(), nullable=True))
    op.add_column('regulations_chunks', sa.Column('span_start_offset', sa.Integer(), nullable=True))
    op.add_column('regulations_chunks', sa.Column('span_end_element', sa.Integer(), nullable=True))
    op.add_column('regulations_chunks', sa.Column('span_end_offset', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('regulations_chunks', 'span_end_offset')
    op.drop_column('regulations_chunks', 'span_end_element')
    op.drop_column('regulations_chunks', 'span_start_offset')
    op.drop_column('regulations_chunks', 'span_start_element')
