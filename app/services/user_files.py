from fastapi import UploadFile
from google.cloud.storage import Client as StorageClient
from sqlalchemy.exc import IntegrityError

from app.cloud_storage.utils import upload_file_to_cloud_storage
from app.core.exceptions import EmptyFileException, FileNameExist
from app.units_of_work.users import UsersUnitOfWork


async def add_user_file(
    users_unit_of_work: UsersUnitOfWork, user_file: UploadFile, user_id: str, storage_client: StorageClient
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

        await upload_file_to_cloud_storage(storage_client, file_id, user_file)
