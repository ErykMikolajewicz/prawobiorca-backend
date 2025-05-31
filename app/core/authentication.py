from typing import Annotated

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, Request, HTTPException, status
from redis.asyncio.client import Redis

from app.key_value_db.connection import get_redis


async def validate_token(
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl='/auth/login'))],
    request: Request,
    redis_client: Annotated[Redis, Depends(get_redis)]
):
    user_id = await redis_client.get(f'access_token:{token}')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    request.state.user_id = user_id
