from app.infrastructure.relational_db.bases import BaseUnitOfWork
from app.infrastructure.relational_db.repositories.users import UsersRepository, UsersTokensRepository


class UsersUnitOfWork(BaseUnitOfWork):
    async def __aenter__(self):
        self.users = UsersRepository(self.session)
        self.users_tokens = UsersTokensRepository(self.session)
        return self
