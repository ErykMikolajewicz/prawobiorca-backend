from dataclasses import dataclass

from app.shared.enums import TokenType


@dataclass(frozen=True)
class RefreshTokenData:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: TokenType


@dataclass(frozen=True)
class AccessTokenData:
    access_token: str
    expires_in: int
    token_type: TokenType
