from uuid import UUID

import sqlalchemy as sqla
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.relational_db.connection import Base
from app.infrastructure.relational_db.schemas.mixins import CreateDateMixin, UuidIdMixin
from app.shared.consts import VECTOR_LENGTH


class RegulationsDocuments(Base, UuidIdMixin, CreateDateMixin):
    __tablename__ = "regulations_documents"
    header: Mapped[str] = mapped_column(sqla.Text, nullable=True)
    text: Mapped[str] = mapped_column(sqla.Text, nullable=False)
    vector: Mapped[list[float]] = mapped_column(Vector(VECTOR_LENGTH), nullable=False)
    regulation_id: Mapped[UUID] = mapped_column(sqla.ForeignKey("regulations.id"), nullable=False)
