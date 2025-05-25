from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import text, func
from sqlalchemy.orm import Mapped, mapped_column


class IntIdMixin:
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class UuidIdMixin:
    __abstract__ = True
    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text('gen_random_uuid()'))


class CreateDateMixin:
    __abstract__ = True
    create_date: Mapped[datetime] = mapped_column(server_default=text('now()'))


class UpdateDateMixin(CreateDateMixin):
    __abstract__ = True
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
