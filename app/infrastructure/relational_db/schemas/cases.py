from uuid import UUID

import sqlalchemy as sqla
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.relational_db.connection import Base
from app.infrastructure.relational_db.schemas.mixins import CreateDateMixin, UuidIdMixin
from app.shared.consts import MAX_FILENAME_LENGTH


class Cases(Base, UuidIdMixin, CreateDateMixin):
    __tablename__ = "cases"

    user_id: Mapped[UUID] = mapped_column(sqla.ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(sqla.String(MAX_FILENAME_LENGTH), nullable=False)


class CaseArticles(Base, UuidIdMixin, CreateDateMixin):
    __tablename__ = "case_articles"

    case_id: Mapped[UUID] = mapped_column(sqla.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(sqla.ForeignKey("users.id"), nullable=False)
    presentation_name: Mapped[str] = mapped_column(sqla.String(MAX_FILENAME_LENGTH), nullable=False)
    content: Mapped[str] = mapped_column(sqla.Text, nullable=False)
