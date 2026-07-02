from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.domain.services.security import url_safe_authorization_token_length


class LoginOutput(BaseModel):
    session_id: Annotated[
        str,
        StringConstraints(
            min_length=url_safe_authorization_token_length, max_length=url_safe_authorization_token_length
        ),
    ]
    expires_in: int
