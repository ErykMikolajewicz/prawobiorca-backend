from uuid import UUID

import sqlalchemy as sqla
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.relational_db.connection import Base
from app.infrastructure.relational_db.schemas.mixins import CreateDateMixin, UuidIdMixin


class Cases(Base, UuidIdMixin, CreateDateMixin):
    __tablename__ = "cases"

    user_id: Mapped[UUID] = mapped_column(sqla.ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(sqla.String(255), nullable=False)


class CaseArticles(Base, UuidIdMixin, CreateDateMixin):
    __tablename__ = "case_articles"

    case_id: Mapped[UUID] = mapped_column(sqla.ForeignKey("cases.id"), nullable=False, index=True)
    document_name: Mapped[str] = mapped_column(sqla.String(255), nullable=False)
    article_content: Mapped[str] = mapped_column(sqla.Text, nullable=False)
