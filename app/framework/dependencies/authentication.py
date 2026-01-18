from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio.client import Redis

from app.framework.dependencies.key_value_repository import get_key_value_repository
from app.shared.enums import KeyPrefix


async def validate_token(
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/auth/login"))],
    request: Request,
    key_value_repo: Annotated[Redis, Depends(get_key_value_repository)],
) -> tuple[str, str]:
    user_id = await key_value_repo.get(f"{KeyPrefix.ACCESS_TOKEN}:{token}")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    request.state.user_id = user_id
    request.state.access_token = token
    return token, user_id
