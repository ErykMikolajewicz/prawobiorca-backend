"""split regulations_documents into sections and chunks

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
Create Date: 2026-09-11 19:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = 'f4a5b6c7d8e9'
down_revision: Union[str, Sequence[str], None] = 'e3f4a5b6c7d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

VECTOR_LENGTH = 768


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table('regulations_documents')

    op.create_table(
        'regulations_sections',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('create_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('header', sa.Text(), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('section_order', sa.Integer(), nullable=False),
        sa.Column('unit_type', sa.String(length=32), nullable=True),
        sa.Column('unit_number', sa.String(length=16), nullable=True),
        sa.Column('unit_path', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('regulation_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ['regulation_id', 'user_id'], ['regulations.id', 'regulations.user_id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_regulations_sections_regulation_id_user_id', 'regulations_sections', ['regulation_id', 'user_id']
    )

    op.create_table(
        'regulations_chunks',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('section_id', sa.UUID(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('vector', Vector(VECTOR_LENGTH), nullable=False),
        sa.ForeignKeyConstraint(['section_id'], ['regulations_sections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_regulations_chunks_section_id', 'regulations_chunks', ['section_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_regulations_chunks_section_id', table_name='regulations_chunks')
    op.drop_table('regulations_chunks')
    op.drop_index('ix_regulations_sections_regulation_id_user_id', table_name='regulations_sections')
    op.drop_table('regulations_sections')

    op.create_table(
        'regulations_documents',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('create_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('header', sa.Text(), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('chunk_order', sa.Integer(), nullable=False),
        sa.Column('unit_type', sa.String(length=32), nullable=True),
        sa.Column('unit_number', sa.String(length=16), nullable=True),
        sa.Column('unit_path', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('part_index', sa.Integer(), nullable=False),
        sa.Column('parts_total', sa.Integer(), nullable=False),
        sa.Column('vector', Vector(VECTOR_LENGTH), nullable=False),
        sa.Column('regulation_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ['regulation_id', 'user_id'], ['regulations.id', 'regulations.user_id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
    )
