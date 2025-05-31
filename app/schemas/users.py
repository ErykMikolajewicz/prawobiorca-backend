import sqlalchemy as sqla
from sqlalchemy.orm import Mapped, mapped_column

from app.relational_db.connection import Base
from app.schemas.mixins import UuidIdMixin, CreateDateMixin


class Users(Base, UuidIdMixin, CreateDateMixin):
    __tablename__ = 'users'
    __table_args__ = (
        sqla.UniqueConstraint('login'),
    )

    hashed_password: Mapped[bytes] = mapped_column(sqla.LargeBinary(60))
    login: Mapped[str] = mapped_column(sqla.String(32))


class UsersFiles(Base, UuidIdMixin, CreateDateMixin):
    __tablename__ = 'user_files'
    __table_args__ = (
        sqla.UniqueConstraint('file_name'),
    )

    file_name: Mapped[str] = mapped_column(sqla.String(256))
