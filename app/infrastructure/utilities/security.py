import secrets
from math import ceil

import bcrypt
from pydantic import SecretStr

from app.shared.consts import BEARER_TOKEN_LENGTH

url_safe_bearer_token_length = ceil(BEARER_TOKEN_LENGTH * 4 / 3)


def hash_password(password: SecretStr) -> bytes:
    password_str = password.get_secret_value()
    password_bytes = password_str.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_password


def generate_token(token_length: int = BEARER_TOKEN_LENGTH) -> str:
    token = secrets.token_urlsafe(token_length)
    return token


def verify_password(password: SecretStr, hashed_password: bytes) -> bool:
    password_str = password.get_secret_value()
    password_bytes = password_str.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_password)
