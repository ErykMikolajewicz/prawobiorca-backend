"""add preparation_status to regulations

Revision ID: c1d2e3f4a5b6
Revises: a45d973c4187
Create Date: 2026-08-28 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'a45d973c4187'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

regulationpreparationstatus = sa.Enum(
    "NOT_STARTED", "IN_PROGRESS", "PREPARED", "FAILED", name="regulationpreparationstatus"
)


def upgrade() -> None:
    """Upgrade schema."""
    regulationpreparationstatus.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "regulations",
        sa.Column(
            "preparation_status", regulationpreparationstatus, nullable=False, server_default="NOT_STARTED"
        ),
    )
    op.execute("UPDATE regulations SET preparation_status = 'PREPARED' WHERE is_prepared IS TRUE")
    with op.batch_alter_table("regulations", schema=None) as batch_op:
        batch_op.alter_column("preparation_status", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("regulations", "preparation_status")
    regulationpreparationstatus.drop(op.get_bind(), checkfirst=True)
