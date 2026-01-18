from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.domain.services.security import url_safe_bearer_token_length
from app.shared.enums import TokenType


class LoginOutput(BaseModel):
    access_token: Annotated[
        str, StringConstraints(min_length=url_safe_bearer_token_length, max_length=url_safe_bearer_token_length)
    ]
    expires_in: int
    token_type: TokenType
    refresh_token: Annotated[
        str, StringConstraints(min_length=url_safe_bearer_token_length, max_length=url_safe_bearer_token_length)
    ]