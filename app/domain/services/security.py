import asyncio
import secrets
from math import ceil

import bcrypt

from app.shared.consts import BEARER_TOKEN_LENGTH, EMAIL_VERIFICATION_TOKEN_LENGTH, SECURITY_MIN_RESPONSE_TIME

url_safe_bearer_token_length = ceil(BEARER_TOKEN_LENGTH * 4 / 3)
url_safe_email_verification_token_length = ceil(EMAIL_VERIFICATION_TOKEN_LENGTH * 4 / 3)


class Secret:
    def __init__(self, value: str):
        self.__value = value

    def __repr__(self):
        return "Secret(**********)"

    def __str__(self):
        return "**********"

    def get_value(self):
        return self.__value


def hash_password(password: Secret) -> bytes:
    password = password.get_value()
    password = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed_password


def generate_token(token_length: int = BEARER_TOKEN_LENGTH) -> str:
    token = secrets.token_urlsafe(token_length)
    return token


def verify_password(password: Secret, hashed_password: bytes) -> bool:
    password = password.get_value()
    password = password.encode("utf-8")
    return bcrypt.checkpw(password, hashed_password)


async def prevent_timing_attack(execution_start_time: float):
    elapsed_execution_time = asyncio.get_event_loop().time() - execution_start_time
    delay = max(0.0, SECURITY_MIN_RESPONSE_TIME - elapsed_execution_time)
    await asyncio.sleep(delay)
