import sqlalchemy as sqla
from pgvector.sqlalchemy import Vector

from src.infrastructure.relational_db.connection import mapper_registry, metadata
from src.shared.consts import VECTOR_LENGTH

regulations_documents_table = sqla.Table(
    "regulations_documents",
    metadata,
    sqla.Column("id", sqla.UUID, primary_key=True, server_default=sqla.text("gen_random_uuid()")),
    sqla.Column("create_date", sqla.DateTime, server_default=sqla.text("now()"), nullable=False),
    sqla.Column("header", sqla.Text, nullable=True),
    sqla.Column("text", sqla.Text, nullable=False),
    sqla.Column("chunk_order", sqla.Integer, nullable=False),
    sqla.Column("vector", Vector(VECTOR_LENGTH), nullable=False),
    sqla.Column("regulation_id", sqla.UUID, nullable=False),
    sqla.Column("user_id", sqla.UUID, nullable=True),
    sqla.ForeignKeyConstraint(
        ["regulation_id", "user_id"], ["regulations.id", "regulations.user_id"], ondelete="CASCADE"
    ),
)


class RegulationsDocuments:
    pass


mapper_registry.map_imperatively(RegulationsDocuments, regulations_documents_table)
