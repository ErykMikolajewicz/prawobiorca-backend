import re
from string import punctuation
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, SecretStr, StringConstraints, field_validator

from app.infrastructure.utilities.security import url_safe_bearer_token_length
from app.shared.enums import TokenType


class AccountCreate(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=32)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr):
        password_str = value.get_secret_value()
        if not re.search(r"[A-Z]", password_str):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password_str):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", password_str):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(f"[{re.escape(punctuation)}]", password_str):
            raise ValueError("Password must contain at least one special character.")
        return value


class LoginOutput(BaseModel):
    access_token: Annotated[
        str, StringConstraints(min_length=url_safe_bearer_token_length, max_length=url_safe_bearer_token_length)
    ]
    expires_in: int
    token_type: TokenType
    refresh_token: Annotated[
        str, StringConstraints(min_length=url_safe_bearer_token_length, max_length=url_safe_bearer_token_length)
    ]
