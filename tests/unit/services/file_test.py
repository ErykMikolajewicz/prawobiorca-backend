import io
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from starlette.datastructures import Headers

from app.domain.services.user_files import add_user_file
from app.shared.exceptions import EmptyFileException, FileNameExist


def make_upload_file(name="test.txt", content=b"test-content"):
    file = io.BytesIO(content)
    upload_file = UploadFile(filename=name, file=file, headers=Headers())
    return upload_file


async def test_add_user_file_success(uow, storage_client, uuid_generator):
    upload_file = make_upload_file()
    user_id = next(uuid_generator)
    fake_file_id = next(uuid_generator)

    add_result = MagicMock()
    add_result.id = fake_file_id
    uow.files.add = AsyncMock(return_value=add_result)
    storage_client.upload_file = AsyncMock()

    await add_user_file(uow, upload_file, user_id, storage_client)

    uow.files.add.assert_awaited_once_with({"file_name": "test.txt", "user_id": user_id})
    storage_client.upload_file.assert_awaited_once_with(upload_file, fake_file_id)


async def test_add_user_file_duplicate_file_name(uow, storage_client, uuid_generator):
    upload_file = make_upload_file()
    user_id = next(uuid_generator)
    uow.files.add = AsyncMock(side_effect=IntegrityError("msg", None, Exception()))
    with pytest.raises(FileNameExist):
        await add_user_file(uow, upload_file, user_id, storage_client)


async def test_add_user_file_empty_file(uow, storage_client, uuid_generator):
    user_id = next(uuid_generator)
    upload_file = make_upload_file(content=b"")
    with pytest.raises(EmptyFileException):
        await add_user_file(uow, upload_file, user_id, storage_client)
