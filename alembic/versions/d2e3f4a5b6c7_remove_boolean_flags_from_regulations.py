"""remove boolean flags from regulations

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-08-28 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d2e3f4a5b6c7"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("regulations", "is_prepared")
    op.drop_column("regulations", "is_uploaded")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("regulations", sa.Column("is_uploaded", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("regulations", sa.Column("is_prepared", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute("UPDATE regulations SET is_prepared = TRUE, is_uploaded = TRUE WHERE preparation_status = 'PREPARED'")
    with op.batch_alter_table("regulations", schema=None) as batch_op:
        batch_op.alter_column("is_uploaded", server_default=None)
        batch_op.alter_column("is_prepared", server_default=None)
