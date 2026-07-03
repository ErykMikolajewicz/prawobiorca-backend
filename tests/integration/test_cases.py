import json
from datetime import datetime
from uuid import UUID

from fastapi import status
from sqlalchemy import insert, select

from app.infrastructure.relational_db.schemas.cases import Cases
from app.shared.consts import AUTHORIZATION_COOKIE_NAME
from tests.consts import ADMIN_ID, AUTHORIZATION_TOKEN, USER_ID


async def test_get_cases_list(
    client,
    override_session_maker,
    session_maker,
    override_authorize_normal_user,
    set_user,
    clean_user,
    set_admin_user,
    clean_admin_user,
):
    async with session_maker.begin() as session:
        stmt = (
            insert(Cases)
            .values(
                [
                    {"user_id": USER_ID, "name": "First case", "create_date": datetime(2026, 1, 1, 10, 0, 0)},
                    {"user_id": USER_ID, "name": "Second case", "create_date": datetime(2026, 1, 2, 10, 0, 0)},
                    {"user_id": ADMIN_ID, "name": "Other user case", "create_date": datetime(2026, 1, 3, 10, 0, 0)},
                ]
            )
            .returning(Cases.id)
        )

        result = await session.scalars(stmt)

    ids = result.all()

    first_case_id, second_case_id, _ = ids

    client.cookies.set(
        AUTHORIZATION_COOKIE_NAME,
        json.dumps({"session_id": AUTHORIZATION_TOKEN}),
    )

    response = client.get("/api/user/cases")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"id": str(second_case_id), "name": "Second case"},
        {"id": str(first_case_id), "name": "First case"},
    ]


async def test_add_case(
    client, override_session_maker, session_maker, override_authorize_normal_user, set_user, clean_user
):
    client.cookies.set(
        AUTHORIZATION_COOKIE_NAME,
        json.dumps({"session_id": AUTHORIZATION_TOKEN}),
    )

    response = client.post("/api/user/cases", data={"caseName": "New case"})

    assert response.status_code == status.HTTP_200_OK

    case_id = UUID(response.json())

    async with session_maker() as session:
        stmt = select(Cases).where(Cases.id == case_id)
        case = await session.scalar(stmt)

    assert case is not None
    assert case.id == case_id
    assert case.user_id == USER_ID
    assert case.name == "New case"


async def test_delete_case(
    client, override_session_maker, session_maker, override_authorize_normal_user, set_user, clean_user
):
    async with session_maker.begin() as session:
        stmt = (
            insert(Cases)
            .values(
                {"user_id": USER_ID, "name": "Case to delete"},
            )
            .returning(Cases.id)
        )
        case_id = await session.scalar(stmt)

    client.cookies.set(
        AUTHORIZATION_COOKIE_NAME,
        json.dumps({"session_id": AUTHORIZATION_TOKEN}),
    )

    response = client.delete(f"/api/user/cases/{case_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    async with session_maker() as session:
        deleted_case = await session.get(Cases, case_id)

    assert deleted_case is None
