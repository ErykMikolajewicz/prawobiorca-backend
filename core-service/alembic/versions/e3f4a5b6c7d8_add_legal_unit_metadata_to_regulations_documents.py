"""add legal unit metadata to regulations_documents

Revision ID: e3f4a5b6c7d8
Revises: 942b744d74d6
Create Date: 2026-09-09 21:40:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e3f4a5b6c7d8'
down_revision: Union[str, Sequence[str], None] = '942b744d74d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('regulations_documents', sa.Column('unit_type', sa.String(length=32), nullable=True))
    op.add_column('regulations_documents', sa.Column('unit_number', sa.String(length=16), nullable=True))
    op.add_column('regulations_documents', sa.Column('unit_path', sa.ARRAY(sa.Text()), nullable=True))
    op.add_column(
        'regulations_documents', sa.Column('part_index', sa.Integer(), nullable=False, server_default='1')
    )
    op.add_column(
        'regulations_documents', sa.Column('parts_total', sa.Integer(), nullable=False, server_default='1')
    )
    with op.batch_alter_table('regulations_documents', schema=None) as batch_op:
        batch_op.alter_column('part_index', server_default=None)
        batch_op.alter_column('parts_total', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('regulations_documents', 'parts_total')
    op.drop_column('regulations_documents', 'part_index')
    op.drop_column('regulations_documents', 'unit_path')
    op.drop_column('regulations_documents', 'unit_number')
    op.drop_column('regulations_documents', 'unit_type')
