from app.infrastructure.relational_db.repositories.users import UsersFilesRepository, UsersRepository
from app.infrastructure.relational_db.bases import BaseUnitOfWork


class UsersUnitOfWork(BaseUnitOfWork):
    async def __aenter__(self):
        self.users: UsersRepository = UsersRepository(self.session)
        self.files: UsersFilesRepository = UsersFilesRepository(self.session)
        return self
