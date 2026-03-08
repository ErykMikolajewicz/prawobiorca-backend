from uuid import UUID

import sqlalchemy as sqla
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.relational_db.connection import Base
from app.infrastructure.relational_db.schemas.mixins import CreateDateMixin
from app.shared.consts import HASH_LENGTH, MAX_FILENAME_LENGTH


class PublicFiles(Base, CreateDateMixin):
    __tablename__ = "public_files"

    hash: Mapped[bytes] = mapped_column(sqla.LargeBinary(HASH_LENGTH), primary_key=True)
    presentation_name: Mapped[str] = mapped_column(sqla.String(MAX_FILENAME_LENGTH), nullable=False)
    is_prepared: Mapped[bool] = mapped_column(sqla.Boolean, nullable=False, default=False)


class UsersFiles(Base, CreateDateMixin):
    __tablename__ = "users_files"

    hash: Mapped[bytes] = mapped_column(sqla.LargeBinary(HASH_LENGTH), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(sqla.ForeignKey("users.id"), primary_key=True)
    presentation_name: Mapped[str] = mapped_column(sqla.String(MAX_FILENAME_LENGTH), nullable=False)
    is_prepared: Mapped[bool] = mapped_column(sqla.Boolean, nullable=False, default=False)
