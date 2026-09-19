"""change vector length for mmlw embeddings

Revision ID: a7b8c9d0e1f2
Revises: b6c7d8e9f0a1
Create Date: 2026-09-18 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "b6c7d8e9f0a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def change_vector_length(vector_length: int) -> None:
    op.execute("DELETE FROM regulations_sections")
    op.execute(
        "UPDATE regulations SET preparation_status = 'FAILED' WHERE preparation_status IN ('PREPARED', 'IN_PROGRESS')"
    )
    op.alter_column("regulations_chunks", "vector", type_=Vector(vector_length), existing_nullable=False)


def upgrade() -> None:
    """Upgrade schema."""
    change_vector_length(1024)


def downgrade() -> None:
    """Downgrade schema."""
    change_vector_length(768)
