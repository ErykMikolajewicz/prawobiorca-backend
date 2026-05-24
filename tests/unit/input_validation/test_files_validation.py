import pytest

from app.application.dtos.files import RegulationData


@pytest.mark.parametrize(
    "file_name, file_content",
    [
        ("test.txt", b""),
        ("a" * 256, b"content"),
    ],
)
def test_logged_user_add_file_validation_errors(
    client,
    override_set_user_by_session_id,
    override_get_users_file_repository,
    file_name,
    file_content,
):
    files = {"file": (file_name, file_content, "text/plain")}

    response = client.post("/api/user/files", files=files, follow_redirects=False)

    assert response.status_code == 400


def test_unauthorized_user_cannot_add_file(client):
    files = {"file": ("test.txt", b"content", "text/plain")}

    response = client.post("/api/user/files", files=files, follow_redirects=False)

    assert response.status_code == 401


def test_file_data_validation_direct():
    with pytest.raises(ValueError):
        RegulationData(name="test.txt", file=b"")

    fd = RegulationData(name="valid.txt", file=b"content")
    assert fd.name == "valid.txt"
    assert fd.file == b"content"
