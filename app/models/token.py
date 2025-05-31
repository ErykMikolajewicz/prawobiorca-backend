from typing import Annotated

from pydantic import BaseModel
from pydantic.types import StringConstraints

from app.core.enums import TokenType
from app.core.security import url_safe_bearer_token_length


class AccessToken(BaseModel):
    access_token: Annotated[str, StringConstraints(min_length=url_safe_bearer_token_length,
                                                   max_length=url_safe_bearer_token_length)]
    expires_in: int
    token_type: TokenType
