from typing import Annotated

from app.application.interfaces.file_managment import PublicFileManager
from fastapi import Depends, Request

from app.application.interfaces.regulations import RegulationsManager
from app.application.interfaces.relational import AsyncSession
from app.framework.dependencies.relational import get_relational_session
from app.infrastructure.relational_db.repositories.file_managment import (
    PublicFileManagerRepository,
    RegulationsManagerRepository,
)


async def get_public_file_manager(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
) -> PublicFileManager:
    return PublicFileManagerRepository(session)


async def get_user_file_manager(
    session: Annotated[AsyncSession, Depends(get_relational_session)], request: Request
) -> RegulationsManager:
    user_id = request.state.user_id
    return RegulationsManagerRepository(session, user_id)
