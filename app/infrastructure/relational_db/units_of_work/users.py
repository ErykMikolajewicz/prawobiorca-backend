from app.infrastructure.relational_db.bases import BaseUnitOfWork
from app.infrastructure.relational_db.repositories.users import UsersRepository


class UsersUnitOfWork(BaseUnitOfWork):
    async def __aenter__(self):
        self.users: UsersRepository = UsersRepository(self.session)
        return self
