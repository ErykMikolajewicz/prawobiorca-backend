from datetime import datetime
from uuid import UUID

import sqlalchemy as sqla
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.relational_db.connection import Base
from app.infrastructure.relational_db.schemas.mixins import CreateDateMixin, UuidIdMixin


class Users(Base, UuidIdMixin, CreateDateMixin):
    __tablename__ = "users"
    __table_args__ = (sqla.UniqueConstraint("username"),)

    hashed_password: Mapped[bytes] = mapped_column(sqla.LargeBinary(60))
    username: Mapped[str] = mapped_column(sqla.String(40), nullable=False, index=True)


class UsersTokens(Base, CreateDateMixin):
    __tablename__ = "users_tokens"

    user_id: Mapped[UUID] = mapped_column(sqla.ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(
        sqla.String(64),
        primary_key=True,
    )
    valid_until: Mapped[datetime]
