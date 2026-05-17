import pytest

from app.application.dtos.files import FileData


@pytest.mark.parametrize(
    "file_name, file_content",
    [
        ("test.txt", b""),
        ("a" * 256, b"content"),
    ],
)
def test_add_file_validation_errors(client, override_get_users_file_repository, file_name, file_content):
    files = {"file": (file_name, file_content, "text/plain")}

    response = client.post("/api/user/files", files=files, follow_redirects=False)

    assert response.status_code in [400, 401]


def test_file_data_validation_direct():
    with pytest.raises(ValueError):
        FileData(name="test.txt", file=b"")

    fd = FileData(name="valid.txt", file=b"content")
    assert fd.name == "valid.txt"
    assert fd.file == b"content"
