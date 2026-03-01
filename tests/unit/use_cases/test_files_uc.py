import pytest

from app.application.dtos.files import FileData
from app.application.use_cases.files import ListPublicFiles
from app.application.use_cases.user_files import AddUserFile
from app.domain.exceptions import FileNameExist


@pytest.mark.asyncio
async def test_add_file_success(mock_files_repo):
    file_data = FileData(file_name="test_file.txt", file=b"test_content")
    use_case = AddUserFile(file_data=file_data, files_repository=mock_files_repo)

    await use_case.execute()

    mock_files_repo.upload_file.assert_awaited_once_with(file_data)


@pytest.mark.asyncio
async def test_add_file_already_exists(mock_files_repo):
    file_data = FileData(file_name="existing_file.txt", file=b"content")
    mock_files_repo.upload_file.side_effect = FileNameExist("existing_file.txt")
    use_case = AddUserFile(file_data=file_data, files_repository=mock_files_repo)

    with pytest.raises(FileNameExist):
        await use_case.execute()

    mock_files_repo.upload_file.assert_awaited_once_with(file_data)


@pytest.mark.asyncio
async def test_list_files_success(mock_files_repo):
    expected_files = ["file1.txt", "file2.jpg"]
    mock_files_repo.list_files.return_value = expected_files
    use_case = ListPublicFiles(files_repository=mock_files_repo)

    result = await use_case.execute()

    assert result == expected_files
    mock_files_repo.list_files.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_files_empty(mock_files_repo):
    mock_files_repo.list_files.return_value = []
    use_case = ListPublicFiles(files_repository=mock_files_repo)

    result = await use_case.execute()

    assert result == []
    mock_files_repo.list_files.assert_awaited_once()
