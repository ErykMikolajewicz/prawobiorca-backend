from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Integer, DateTime, text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.relational_db.connection import Base


class IntIdMixin(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class UuidIdMixin(Base):
    __abstract__ = True
    id: Mapped[UUID] = mapped_column(Integer, primary_key=True, server_default=text('gen_random_uuid()'))


class CreateDateMixin(Base):
    __abstract__ = True
    create_date: Mapped[datetime] = mapped_column(server_default=text('now()'))


class UpdateDateMixin(CreateDateMixin):
    __abstract__ = True
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
