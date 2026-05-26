from uuid import UUID

import sqlalchemy as sqla
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.value_objects.regulations import RegulationType
from app.infrastructure.relational_db.connection import Base
from app.infrastructure.relational_db.schemas.mixins import CreateDateMixin, UuidIdMixin
from app.shared.consts import MAX_FILENAME_LENGTH


class Regulations(Base, UuidIdMixin, CreateDateMixin):
    __tablename__ = "regulations"

    user_id: Mapped[UUID | None] = mapped_column(sqla.ForeignKey("users.id"), nullable=True)
    presentation_name: Mapped[str] = mapped_column(sqla.String(MAX_FILENAME_LENGTH), nullable=False)
    is_prepared: Mapped[bool] = mapped_column(sqla.Boolean, nullable=False, default=False)
    regulation_type: Mapped[RegulationType | None] = mapped_column(
        sqla.Enum(RegulationType), nullable=True, default=None
    )
