import app.infrastructure.relational_db.repositories.users as sqla_repos
from app.application.interfaces.users import UsersRepository, UsersTokensRepository


async def get_users_tokens_repository() -> UsersTokensRepository:
    return sqla_repos.UsersTokensRepository()


async def get_users_repository() -> UsersRepository:
    return sqla_repos.UsersRepository()
