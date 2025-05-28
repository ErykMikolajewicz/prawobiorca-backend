from sqlalchemy.exc import IntegrityError
from fastapi import UploadFile

from app.core.exceptions import NoFileName, FileNameExist
from app.units_of_work.users import UsersUnitOfWork


async def add_user_file(users_unit_of_work: UsersUnitOfWork, user_file: UploadFile):
    file_name = user_file.filename
    if file_name is None:
        raise NoFileName

    file_data = {"file_name": file_name}

    try:
        async with users_unit_of_work as uof:
            await uof.files.add(file_data)
    except IntegrityError:
        raise FileNameExist
