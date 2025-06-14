from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.relational_db.connection import get_relational_session
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork


def get_users_unit_of_work(
    session: AsyncSession = Depends(get_relational_session)
) -> UsersUnitOfWork:
    return UsersUnitOfWork(session)