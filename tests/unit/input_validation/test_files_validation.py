import pytest

from app.application.dtos.files import FileData
from app.domain.exceptions import FileNameTooLong, InvalidCharacterInFileName


@pytest.mark.parametrize(
    "file_name, file_content, expected_error_message",
    [
        ("test.txt", b"", "Plik test.txt jest pusty, nie można dodać pustego pliku!"),
        ("a" * 256, b"content", f"Nazwa {'a' * 256} jest zbyt długa!"),
        ("test/file.txt", b"content", "Nazwa test/file.txt zawiera niedozwolone znaki!"),
        ("test\x00file.txt", b"content", "Nazwa test\x00file.txt zawiera niedozwolone znaki!"),
    ],
)
def test_add_file_validation_errors(client, override_get_file_storage, file_name, file_content, expected_error_message):
    files = {"file": (file_name, file_content, "text/plain")}

    response = client.post("/files", files=files, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_file_data_validation_direct():
    with pytest.raises(ValueError):
        FileData(file_name="test.txt", file=b"")

    long_name = "a" * 256
    with pytest.raises(FileNameTooLong):
        FileData(file_name=long_name, file=b"content")

    with pytest.raises(InvalidCharacterInFileName):
        FileData(file_name="test/file", file=b"content")

    with pytest.raises(InvalidCharacterInFileName):
        FileData(file_name="test\x00file", file=b"content")

    fd = FileData(file_name="valid.txt", file=b"content")
    assert fd.file_name == "valid.txt"
    assert fd.file == b"content"
