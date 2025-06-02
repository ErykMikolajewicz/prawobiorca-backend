import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from fastapi import UploadFile
from starlette.datastructures import Headers
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import FileNameExist, EmptyFileException
from app.services.user_files import add_user_file

import io


class DummyAsyncContextManager:
    def __init__(self, return_object):
        self.return_object = return_object

    async def __aenter__(self):
        return self.return_object

    async def __aexit__(self, exc_type, exc, tb):
        return None


@pytest.fixture
def uow():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return uow


@pytest.fixture
def storage_client():
    return MagicMock()


def make_upload_file(name="test.txt", content=b"test-content"):
    file = io.BytesIO(content)
    upload_file = UploadFile(filename=name, file=file, headers=Headers())
    return upload_file


@pytest.mark.asyncio
async def test_add_user_file_success(uow, storage_client):
    # Arrange
    upload_file = make_upload_file()
    fake_file_id = uuid4()

    add_result = MagicMock()
    add_result.id = fake_file_id
    uow.files.add = AsyncMock(return_value=add_result)

    with patch("app.services.user_files.upload_file_to_cloud_storage", new_callable=AsyncMock) as mock_upload:
        result = await add_user_file(uow, upload_file, storage_client)

    uow.files.add.assert_awaited_once_with({"file_name": "test.txt"})
    mock_upload.assert_awaited_once_with(storage_client, fake_file_id, upload_file)
    assert result == fake_file_id


@pytest.mark.asyncio
async def test_add_user_file_duplicate_file_name(uow, storage_client):
    upload_file = make_upload_file()
    uow.files.add = AsyncMock(side_effect=IntegrityError("msg", None, Exception()))
    with patch("app.services.user_files.upload_file_to_cloud_storage", new_callable=AsyncMock):
        with pytest.raises(FileNameExist):
            await add_user_file(uow, upload_file, storage_client)


@pytest.mark.asyncio
async def test_add_user_file_empty_file(uow, storage_client):
    upload_file = make_upload_file(content=b"")
    with pytest.raises(EmptyFileException):
        await add_user_file(uow, upload_file, storage_client)

