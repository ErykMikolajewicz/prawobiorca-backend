import pytest

from app.application.dtos.files import FileData


@pytest.mark.parametrize(
    "file_name, file_content, expected_error_message",
    [
        ("test.txt", b"", "Plik test.txt jest pusty, nie można dodać pustego pliku!"),
        ("a" * 256, b"content", f"Nazwa {'a' * 256} jest zbyt długa!"),
    ],
)
def test_add_file_validation_errors(
    client, override_get_users_file_repository, file_name, file_content, expected_error_message
):
    files = {"file": (file_name, file_content, "text/plain")}

    response = client.post("/user/files", files=files, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_file_data_validation_direct():
    with pytest.raises(ValueError):
        FileData(name="test.txt", file=b"")

    fd = FileData(name="valid.txt", file=b"content")
    assert fd.name == "valid.txt"
    assert fd.file == b"content"
