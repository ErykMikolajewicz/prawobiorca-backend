from fastapi import UploadFile

from app.application.interfaces.file_storage import StorageRepository
from app.shared.exceptions import EmptyFileException


async def add_file(file: UploadFile, storage_repo: StorageRepository):
    file_name = file.filename

    first_byte = await file.read(1)
    if not first_byte:
        raise EmptyFileException(file_name)
    file.file.seek(0)

    file = await file.read()

    await storage_repo.upload_file(file, file_name)
