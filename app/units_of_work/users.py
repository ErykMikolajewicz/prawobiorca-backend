from app.repositories.users import UsersRepository, UsersFilesRepository
from app.units_of_work.base import BaseUnitOfWork

class UsersUnitOfWork(BaseUnitOfWork):
    async def __aenter__(self):
        self.users: UsersRepository = UsersRepository(self.session)
        self.files: UsersFilesRepository = UsersFilesRepository(self.session)
        return self
