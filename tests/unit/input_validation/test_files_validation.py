import pytest

from app.domain.value_objects.regulations import RegulationType

# @pytest.mark.parametrize(
#     "file_name, file_content",
#     [
#         ("test.txt", b""),
#         ("a" * 256, b"content"),
#     ],
# )
# def test_logged_user_add_file_validation_errors(
#     client,
#     override_set_user_by_session_id,
#     override_get_public_file_storage,
#     file_name,
#     file_content,
# ):
#     files = {"regulation": (file_name, file_content, "text/plain")}

#     response = client.post("/api/user/regulations", files=files, follow_redirects=False)


#     assert response.status_code == 400


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


# def test_unauthorized_user_cannot_add_file(client):
#     files = {"file": ("test.txt", b"content", "text/plain")}
#
#     response = client.post("/api/user/files", files=files, follow_redirects=False)
#
#     assert response.status_code == 401
#
#
# def test_file_data_validation_direct():
#     with pytest.raises(ValueError):
#         RegulationData(name="test.txt", file=b"")
#
#     fd = RegulationData(name="valid.txt", file=b"content")
#     assert fd.name == "valid.txt"
#     assert fd.file == b"content"
