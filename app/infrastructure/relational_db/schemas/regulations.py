import sqlalchemy as sqla

from app.application.dtos.regulations import RegulationRepresentation
from app.domain.value_objects.regulations import RegulationType
from app.infrastructure.relational_db.connection import mapper_registry, metadata
from app.shared.consts import MAX_FILENAME_LENGTH

regulations_table = sqla.Table(
    "regulations",
    metadata,
    sqla.Column("id", sqla.UUID, primary_key=True, server_default=sqla.text("gen_random_uuid()")),
    sqla.Column("create_date", sqla.DateTime, server_default=sqla.text("now()"), nullable=False),
    sqla.Column("user_id", sqla.UUID, sqla.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
    sqla.Column("presentation_name", sqla.String(MAX_FILENAME_LENGTH), nullable=False),
    sqla.Column("is_prepared", sqla.Boolean, nullable=False, default=False),
    sqla.Column("regulation_type", sqla.Enum(RegulationType, name="regulationtype"), nullable=True, default=None),
    sqla.UniqueConstraint("id", "user_id", name="uq_regulations_id_user_id"),
)


mapper_registry.map_imperatively(RegulationRepresentation, regulations_table)
