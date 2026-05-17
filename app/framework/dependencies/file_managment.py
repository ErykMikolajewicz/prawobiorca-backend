from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request

from app.application.interfaces.file_managment import PublicFileManager, UserFileManager
from app.application.interfaces.relational import AsyncSession
from app.framework.dependencies.authentication import require_logged_user
from app.framework.dependencies.relational import get_relational_session
from app.infrastructure.relational_db.repositories.file_managment import (
    PublicFileManagerRepository,
    UserFileManagerRepository,
)


async def get_public_file_manager(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
) -> PublicFileManager:
    return PublicFileManagerRepository(session)


async def get_user_file_manager(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    request: Request,
    user_id: Annotated[UUID, Depends(require_logged_user)],
) -> UserFileManager:
    # user_id = request.state.user_id
    return UserFileManagerRepository(session, user_id)
