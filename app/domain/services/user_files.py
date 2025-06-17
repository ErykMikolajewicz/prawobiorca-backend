from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError

from app.domain.interfaces.file_storage import StorageRepository
from app.infrastructure.relational_db.units_of_work.users import UsersUnitOfWork
from app.shared.exceptions import EmptyFileException, FileNameExist


async def add_user_file(
    users_unit_of_work: UsersUnitOfWork, user_file: UploadFile, user_id: str, storage_repo: StorageRepository
):
    file_name = user_file.filename

    first_byte = await user_file.read(1)
    if not first_byte:
        raise EmptyFileException()
    user_file.file.seek(0)

    file_data = {"file_name": file_name, "user_id": user_id}

    async with users_unit_of_work as uof:
        try:
            result = await uof.files.add(file_data)
        except IntegrityError:
            raise FileNameExist
        file_id = str(result.id)

        await storage_repo.upload_file(user_file, file_id)
