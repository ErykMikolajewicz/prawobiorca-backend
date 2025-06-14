import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from starlette.datastructures import Headers

from app.core.exceptions import EmptyFileException, FileNameExist
from app.services.user_files import add_user_file


def make_upload_file(name="test.txt", content=b"test-content"):
    file = io.BytesIO(content)
    upload_file = UploadFile(filename=name, file=file, headers=Headers())
    return upload_file


@pytest.mark.asyncio
async def test_add_user_file_success(uow, storage_client, uuid_generator):
    upload_file = make_upload_file()
    user_id = next(uuid_generator)
    fake_file_id = next(uuid_generator)

    add_result = MagicMock()
    add_result.id = fake_file_id
    uow.files.add = AsyncMock(return_value=add_result)

    with patch("app.services.user_files.upload_file_to_cloud_storage", new_callable=AsyncMock) as mock_upload:
        await add_user_file(uow, upload_file, user_id, storage_client)

    uow.files.add.assert_awaited_once_with({"file_name": "test.txt", "user_id": user_id})
    mock_upload.assert_awaited_once_with(storage_client, str(fake_file_id), upload_file)


@pytest.mark.asyncio
async def test_add_user_file_duplicate_file_name(uow, storage_client, uuid_generator):
    upload_file = make_upload_file()
    user_id = next(uuid_generator)
    uow.files.add = AsyncMock(side_effect=IntegrityError("msg", None, Exception()))
    with patch("app.services.user_files.upload_file_to_cloud_storage", new_callable=AsyncMock):
        with pytest.raises(FileNameExist):
            await add_user_file(uow, upload_file, user_id, storage_client)


@pytest.mark.asyncio
async def test_add_user_file_empty_file(uow, storage_client, uuid_generator):
    user_id = next(uuid_generator)
    upload_file = make_upload_file(content=b"")
    with pytest.raises(EmptyFileException):
        await add_user_file(uow, upload_file, user_id, storage_client)
