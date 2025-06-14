from enum import StrEnum


class TokenType(StrEnum):
    BEARER = "bearer"


class RedisPrefix(StrEnum):
    ACCESS_TOKEN = "access_token"  # nosec
    USER_REFRESH_TOKEN = "user_refresh_token"  # nosec
    REFRESH_TOKEN = "refresh_token"  # nosec
