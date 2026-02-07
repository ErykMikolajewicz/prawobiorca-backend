from enum import StrEnum


class TokenType(StrEnum):
    BEARER = "bearer"


class KeyPrefix(StrEnum):
    ACCESS_TOKEN = "access_token"  # noqa: S105
    USER_REFRESH_TOKEN = "user_refresh_token"  # noqa: S105
    REFRESH_TOKEN = "refresh_token"  # noqa: S105
    EMAIL_VERIFICATION_TOKEN = "email_verification_token" # noqa: S105
