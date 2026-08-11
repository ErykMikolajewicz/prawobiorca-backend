"""add chunk_order to regulations_documents

Revision ID: b1c7f3a92d44
Revises: a9f8d0aa9530
Create Date: 2026-08-06 21:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c7f3a92d44'
down_revision: Union[str, Sequence[str], None] = 'a9f8d0aa9530'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('regulations_documents', sa.Column('chunk_order', sa.Integer(), nullable=False, server_default='0'))
    with op.batch_alter_table('regulations_documents', schema=None) as batch_op:
        batch_op.alter_column('chunk_order', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('regulations_documents', 'chunk_order')
