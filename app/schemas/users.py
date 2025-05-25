from datetime import datetime
from uuid import UUID

import sqlalchemy as sqla
from sqlalchemy.orm import Mapped, mapped_column

from app.relational_db.connection import Base
from app.schemas.mixins import UuidIdMixin, CreateDateMixin


class Users(Base, UuidIdMixin, CreateDateMixin):
    __tablename__ = 'users'
    __table_args__ = (
        sqla.UniqueConstraint('login'),
    )

    hashed_password: Mapped[bytearray] = mapped_column(sqla.LargeBinary(256))
    login: Mapped[str] = mapped_column(sqla.String(256))



class UsersAccessTokens(Base):
    __tablename__ = 'users_access_tokens'

    access_token: Mapped[str] = mapped_column(sqla.String(256), primary_key=True)
    id: Mapped[UUID] = mapped_column(sqla.ForeignKey('users.id'))
    expiration_date: Mapped[datetime]
