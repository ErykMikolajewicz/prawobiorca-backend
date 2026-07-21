import sqlalchemy as sqla

from app.domain.entities.user import User
from app.infrastructure.relational_db.connection import mapper_registry, metadata

users_table = sqla.Table(
    "users",
    metadata,
    sqla.Column("id", sqla.UUID, primary_key=True, server_default=sqla.text("gen_random_uuid()")),
    sqla.Column("create_date", sqla.DateTime, server_default=sqla.text("now()"), nullable=False),
    sqla.Column("hashed_password", sqla.LargeBinary(60), nullable=False),
    sqla.Column("username", sqla.String(40), nullable=False),
    sqla.Column("is_admin", sqla.Boolean, default=False, server_default="false", nullable=False),
    sqla.UniqueConstraint("username"),
)

users_tokens_table = sqla.Table(
    "users_tokens",
    metadata,
    sqla.Column("create_date", sqla.DateTime, server_default=sqla.text("now()"), nullable=False),
    sqla.Column("user_id", sqla.UUID, sqla.ForeignKey("users.id"), nullable=False),
    sqla.Column("session_id", sqla.String(64), primary_key=True),
    sqla.Column("valid_until", sqla.DateTime(timezone=True), nullable=False),
)


class UserToken:
    pass


mapper_registry.map_imperatively(User, users_table, exclude_properties=["create_date", "is_admin"])


mapper_registry.map_imperatively(
    UserToken,
    users_tokens_table,
)
