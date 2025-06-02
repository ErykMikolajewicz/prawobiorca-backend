from uuid import UUID

from sqlalchemy.exc import IntegrityError
from fastapi import UploadFile
from google.cloud.storage import Client as StorageClient

from app.core.exceptions import FileNameExist, EmptyFileException
from app.units_of_work.users import UsersUnitOfWork
from app.cloud_storage.utils import upload_file_to_cloud_storage


async def add_user_file(users_unit_of_work: UsersUnitOfWork, user_file: UploadFile,
                        storage_client: StorageClient) -> UUID:
    file_name = user_file.filename

    first_byte = await user_file.read(1)
    if not first_byte:
        raise EmptyFileException()
    user_file.file.seek(0)

    file_data = {"file_name": file_name}

    try:
        async with users_unit_of_work as uof:
            result = await uof.files.add(file_data)
    except IntegrityError:
        raise FileNameExist

    file_id = result.id

    await upload_file_to_cloud_storage(storage_client, file_id, user_file)

    return file_id
