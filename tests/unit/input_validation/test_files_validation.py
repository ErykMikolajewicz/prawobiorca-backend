import pytest

from app.application.dtos.regulations import RegulationData
from app.domain.value_objects.regulations import RegulationType


@pytest.mark.parametrize(
    "file_name, file_content, file_type, error_status_code",
    [
        ("file.txt", b"", RegulationType.DECREE, 400),
        ("", b"valid_content", RegulationType.STATUTE, 400),
        ("a" * 300, b"valid_content", RegulationType.ACT, 400),
        ("file.txt", b"valid_content", "invalid_regulation_type", 400),
    ],
    ids=("empty file", "empty file name", "file name too long", "invalid regulation type"),
)
def test_logged_used_add_file_validation(
    client,
    override_get_public_file_storage,
    override_set_user_by_session_id,
    file_name,
    file_content,
    error_status_code,
    file_type,
):
    files = {"regulation": {file_name, file_content, error_status_code, "plain/text"}}
    params = {"regulation_type": file_type}

    response = client.post("api/user/regulations", files=files, params=params)

    assert response.status_code == error_status_code


def test_unauthorized_user_add_file(client):
    files = {"regulation": {"test.txt", b"valid_content", "plain/text"}}
    params = {"regulation_type": RegulationType.DECREE}

    response = client.post("api/user/regulations", files=files, params=params)

    assert response.status_code == 400


def test_file_data_validation_direct():
    fd = RegulationData(name="valid.txt", file=b"content", document_type=RegulationType.ACT)
    assert fd.name == "valid.txt"
    assert fd.file == b"content"
    assert fd.document_type == RegulationType.ACT
