from dataclasses import dataclass

from app.shared.enums import TokenType


@dataclass
class RefreshTokenData:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: TokenType.BEARER
