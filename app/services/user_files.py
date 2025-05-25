from sqlalchemy.exc import IntegrityError
from fastapi import UploadFile

from app.repositories.users import UserFilesRepository
from app.core.exceptions import NoFileName, FileNameExist


async def add_user_file(user_files_repo: UserFilesRepository, user_file: UploadFile):
    file_name = user_file.filename
    if file_name is None:
        raise NoFileName

    file_data = {"file_name": file_name}

    try:
        await user_files_repo.add(file_data)
    except IntegrityError:
        raise FileNameExist