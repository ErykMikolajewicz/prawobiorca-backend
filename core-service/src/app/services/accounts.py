import logging
from uuid import UUID

from src.app.dtos.account import LoginData
from src.app.interfaces.relational import AsyncSession
from src.app.interfaces.users import UsersRepository
from src.domain.services.security import verify_password

logger = logging.getLogger(__name__)


async def check_user_can_log(session: AsyncSession, users_repo: UsersRepository, login_data: LoginData) -> UUID | None:
    username = login_data.username
    user = await users_repo.get_by_username(session, username)
    if user is None:
        logger.warning("Failed login attempt. User not found!")
        return None

    password = login_data.password
    hashed_password = user.hashed_password
    if not verify_password(password, hashed_password):
        logger.warning("Failed login attempt. Invalid password!")
        return None

    user_id = user.id
    return user_id
