import re
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, StringConstraints

from app.core.enums import TokenType
from app.core.security import url_safe_bearer_token_length


class AccountCreate(BaseModel):
    login: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8, max_length=32)

    @field_validator("login")
    @classmethod
    def validate_login(cls, value):
        if not re.match(r"^[a-zA-Z0-9_.-]+$", value):
            raise ValueError("Login can only contain letters, digits, dots, underscores, and hyphens.")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character.")
        return value


class LoginOutput(BaseModel):
    access_token: Annotated[str, StringConstraints(min_length=url_safe_bearer_token_length,
                                                   max_length=url_safe_bearer_token_length)]
    expires_in: int
    token_type: TokenType
    refresh_token: Annotated[str, StringConstraints(min_length=url_safe_bearer_token_length,
                                                   max_length=url_safe_bearer_token_length)]
