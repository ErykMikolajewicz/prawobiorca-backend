import json
from uuid import UUID

import pytest
from fastapi import status
from sqlalchemy import delete, insert, select

from app.domain.value_objects.regulations import RegulationType
from app.framework.dependencies.text_transformation import get_texts_embedder
from app.infrastructure.relational_db.schemas.documents import RegulationsDocuments
from app.infrastructure.relational_db.schemas.regulations import Regulations
from app.shared.consts import AUTHORIZATION_COOKIE_NAME, VECTOR_LENGTH
from main import prawobiorca
from tests.consts import AUTHORIZATION_TOKEN, USER_ID


async def test_get_public_regulations(client, override_session_maker, session_maker, set_user, clean_user):
    async with session_maker.begin() as session:
        stmt = (
            insert(Regulations)
            .values(
                [
                    {
                        "user_id": None,
                        "presentation_name": "Public act.pdf",
                        "is_prepared": True,
                        "regulation_type": RegulationType.ACT,
                    },
                    {
                        "user_id": None,
                        "presentation_name": "Public decree.pdf",
                        "is_prepared": False,
                        "regulation_type": RegulationType.DECREE,
                    },
                    {
                        "user_id": USER_ID,
                        "presentation_name": "Private act.pdf",
                        "is_prepared": True,
                        "regulation_type": RegulationType.ACT,
                    },
                ]
            )
            .returning(Regulations.id)
        )

        result = await session.scalars(stmt)

    public_act_id, public_decree_id, private_act_id = result.all()

    try:
        response = client.get("/api/regulations", params={"documentType": RegulationType.ACT})

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "id": str(public_act_id),
                "presentationName": "Public act.pdf",
                "isPrepared": True,
            }
        ]
    finally:
        async with session_maker.begin() as session:
            await session.execute(
                delete(Regulations).where(Regulations.id.in_([public_act_id, public_decree_id, private_act_id]))
            )


class StubTextsEmbedder:
    async def embed_queries(self, queries):
        assert queries == ["public document query"]
        return [[1.0] * VECTOR_LENGTH]


async def test_search_regulations_documents(client, override_session_maker, session_maker, set_user, clean_user):
    query_vector = [1.0] * VECTOR_LENGTH
    other_vector = [1.0, *[0.0] * (VECTOR_LENGTH - 1)]

    prawobiorca.dependency_overrides[get_texts_embedder] = lambda: StubTextsEmbedder()

    async with session_maker.begin() as session:
        regulation_ids = await session.scalars(
            insert(Regulations)
            .values(
                [
                    {
                        "user_id": None,
                        "presentation_name": "Public searchable regulation.pdf",
                        "is_prepared": True,
                        "regulation_type": RegulationType.ACT,
                    },
                    {
                        "user_id": USER_ID,
                        "presentation_name": "User searchable regulation.pdf",
                        "is_prepared": True,
                        "regulation_type": RegulationType.ACT,
                    },
                ]
            )
            .returning(Regulations.id)
        )

        regulation_id, other_regulation_id = regulation_ids

        document_ids = (
            await session.scalars(
                insert(RegulationsDocuments)
                .values(
                    [
                        {
                            "header": "Public document",
                            "text": "Matching public regulation document",
                            "vector": query_vector,
                            "regulation_id": regulation_id,
                            "user_id": None,
                        },
                        {
                            "header": "Private document",
                            "text": "Matching user regulation document",
                            "vector": query_vector,
                            "regulation_id": other_regulation_id,
                            "user_id": USER_ID,
                        },
                        {
                            "header": "Other public document",
                            "text": "Unrelated public regulation document",
                            "vector": other_vector,
                            "regulation_id": regulation_id,
                            "user_id": None,
                        },
                    ]
                )
                .returning(RegulationsDocuments.id)
            )
        ).all()

    public_document_id, hidden_user_document_id, other_public_document_id = document_ids

    try:
        response = client.get(
            f"/api/regulations/{regulation_id}/documents",
            params={"threshold": 0.9, "limit": 10, "query": "public document query"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "id": str(public_document_id),
                "score": pytest.approx(1.0),
                "text": "Matching public regulation document",
            }
        ]
    finally:
        prawobiorca.dependency_overrides.pop(get_texts_embedder, None)
        async with session_maker.begin() as session:
            await session.execute(
                delete(RegulationsDocuments).where(
                    RegulationsDocuments.id.in_([public_document_id, other_public_document_id])
                )
            )
            await session.execute(delete(Regulations).where(Regulations.id == regulation_id))


async def test_add_public_regulation_as_admin(
    client,
    override_session_maker,
    session_maker,
    override_authorize_admin_user,
    override_get_regulations_repository,
):
    with open("tests/data/pwr-regulamin_2025_slice_7-9.pdf", "rb") as f:
        regulation_content = f.read()
    files = {"regulation": ("public-regulation.pdf", regulation_content, "plain/text")}
    params = {"regulation_type": RegulationType.DECREE}

    client.cookies.set(
        AUTHORIZATION_COOKIE_NAME,
        json.dumps({"session_id": AUTHORIZATION_TOKEN}),
    )

    response = client.post("/api/regulations", files=files, params=params)

    assert response.status_code == status.HTTP_201_CREATED

    regulation_id = UUID(response.json())

    try:
        async with session_maker() as session:
            stmt = select(Regulations).where(Regulations.id == regulation_id)
            regulation = await session.scalar(stmt)

        assert regulation is not None
        assert regulation.user_id is None
        assert regulation.presentation_name == "public-regulation.pdf"
        assert regulation.is_prepared is False
        assert regulation.regulation_type == RegulationType.DECREE
    finally:
        async with session_maker.begin() as session:
            await session.execute(delete(Regulations).where(Regulations.id == regulation_id))
