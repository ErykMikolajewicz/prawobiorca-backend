import json
from uuid import UUID

from fastapi import status
from sqlalchemy import insert, select

from app.domain.value_objects.regulations import RegulationType
from app.infrastructure.relational_db.schemas.regulations import regulations_table
from app.shared.consts import AUTHORIZATION_COOKIE_NAME
from tests.consts import AUTHORIZATION_TOKEN, USER_ID


async def test_add_user_regulation(
    client,
    override_session_maker,
    session_maker,
    override_get_regulations_repository,
    override_authorize_normal_user,
    set_user,
    clean_user,
):

    with open("tests/data/pwr-regulamin_2025_slice_7-9.pdf", "rb") as f:
        regulation_content = f.read()
    files = {"regulation": ("user-regulation.pdf", regulation_content, "application/pdf")}
    params = {"regulationType": RegulationType.ACT}

    client.cookies.set(
        AUTHORIZATION_COOKIE_NAME,
        json.dumps({"session_id": AUTHORIZATION_TOKEN}),
    )

    response = client.post("/api/user/regulations", files=files, params=params)

    assert response.status_code == status.HTTP_201_CREATED

    regulation_id = UUID(response.json())

    async with session_maker() as session:
        statement = select(regulations_table).where(regulations_table.c.id == regulation_id)
        result = await session.execute(statement)
    regulation = result.one_or_none()

    assert regulation is not None
    assert regulation.user_id == USER_ID
    assert regulation.presentation_name == "user-regulation.pdf"
    assert regulation.is_prepared is False
    assert regulation.regulation_type == RegulationType.ACT


async def test_delete_user_regulation(
    client,
    override_session_maker,
    session_maker,
    override_get_regulations_repository,
    override_authorize_normal_user,
    set_user,
    clean_user,
):
    async with session_maker.begin() as session:
        regulation_id = await session.scalar(
            insert(regulations_table)
            .values(
                user_id=USER_ID,
                presentation_name="do_usuniecia.pdf",
                is_prepared=False,
                regulation_type=RegulationType.ACT,
            )
            .returning(regulations_table.c.id)
        )

    client.cookies.set(
        AUTHORIZATION_COOKIE_NAME,
        json.dumps({"session_id": AUTHORIZATION_TOKEN}),
    )

    response = client.delete(f"/api/user/regulations/{regulation_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    async with session_maker() as session:
        statement = select(regulations_table).where(regulations_table.c.id == regulation_id)
        result = await session.execute(statement)
    deleted_regulation = result.one_or_none()

    assert deleted_regulation is None
