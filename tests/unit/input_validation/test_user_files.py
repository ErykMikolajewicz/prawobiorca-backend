from fastapi import status

from app.framework.dependencies.user_files import add_user_file_provider


def test_add_user_file_missing_file_field(
    client, override_validate_token, assure_use_case_not_executed
):
    assure_use_case_not_executed(add_user_file_provider)

    access_token, _ = override_validate_token
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post("/user/files", headers=headers, files={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
