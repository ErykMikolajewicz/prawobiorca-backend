from uuid import UUID

import pytest
from fastapi import status
from sqlalchemy import delete, insert, select

from main import prawobiorca
from src.app.dtos.regulations import RegulationUploadTarget
from src.domain.value_objects.regulations import RegulationPreparationStatus, RegulationType
from src.framework.dependencies.ai_services import get_texts_embedder
from src.infrastructure.relational_db.schemas.documents import regulations_documents_table
from src.infrastructure.relational_db.schemas.regulations import regulations_table
from src.shared.consts import ACCESS_COOKIE_NAME, VECTOR_LENGTH
from tests.consts import ACCESS_TOKEN, USER_ID


async def test_get_public_regulations(client, override_session_maker, session_maker, set_user, clean_user):
    async with session_maker.begin() as session:
        statement = (
            insert(regulations_table)
            .values(
                [
                    {
                        "user_id": None,
                        "presentation_name": "Public act.pdf",
                        "preparation_status": RegulationPreparationStatus.PREPARED,
                        "regulation_type": RegulationType.ACT,
                    },
                    {
                        "user_id": None,
                        "presentation_name": "Public decree.pdf",
                        "preparation_status": RegulationPreparationStatus.NOT_STARTED,
                        "regulation_type": RegulationType.DECREE,
                    },
                    {
                        "user_id": USER_ID,
                        "presentation_name": "Private act.pdf",
                        "preparation_status": RegulationPreparationStatus.PREPARED,
                        "regulation_type": RegulationType.ACT,
                    },
                ]
            )
            .returning(regulations_table.c.id)
        )

        result = await session.scalars(statement)

    regulations_ids = result.all()
    public_act_id, public_decree_id, private_act_id = regulations_ids

    try:
        response = await client.get("/api/regulations", params={"documentType": RegulationType.ACT})

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "id": str(public_act_id),
                "presentationName": "Public act.pdf",
                "regulationType": RegulationType.ACT,
                "preparationStatus": RegulationPreparationStatus.PREPARED,
            }
        ]

    finally:
        async with session_maker.begin() as session:
            await session.execute(delete(regulations_table).where(regulations_table.c.id.in_(regulations_ids)))


class StubTextsEmbedder:
    @staticmethod
    async def embed_queries(queries):
        assert queries == ["public document query"]
        return [[1.0] * VECTOR_LENGTH]


async def test_search_regulations_documents(client, override_session_maker, session_maker, set_user, clean_user):
    query_vector = [1.0] * VECTOR_LENGTH
    other_vector = [1.0, *[0.0] * (VECTOR_LENGTH - 1)]

    prawobiorca.dependency_overrides[get_texts_embedder] = lambda: StubTextsEmbedder()

    async with session_maker.begin() as session:
        regulation_ids = await session.scalars(
            insert(regulations_table)
            .values(
                [
                    {
                        "user_id": None,
                        "presentation_name": "Public searchable regulation.pdf",
                        "preparation_status": RegulationPreparationStatus.PREPARED,
                        "regulation_type": RegulationType.ACT,
                    },
                    {
                        "user_id": USER_ID,
                        "presentation_name": "User searchable regulation.pdf",
                        "preparation_status": RegulationPreparationStatus.PREPARED,
                        "regulation_type": RegulationType.ACT,
                    },
                ]
            )
            .returning(regulations_table.c.id)
        )

        regulation_id, other_regulation_id = regulation_ids

        document_ids = (
            await session.scalars(
                insert(regulations_documents_table)
                .values(
                    [
                        {
                            "header": "Public document",
                            "text": "Matching public regulation document",
                            "chunk_order": 0,
                            "vector": query_vector,
                            "regulation_id": regulation_id,
                            "user_id": None,
                        },
                        {
                            "header": "Private document",
                            "text": "Matching user regulation document",
                            "chunk_order": 0,
                            "vector": query_vector,
                            "regulation_id": other_regulation_id,
                            "user_id": USER_ID,
                        },
                        {
                            "header": "Other public document",
                            "text": "Unrelated public regulation document",
                            "chunk_order": 1,
                            "vector": other_vector,
                            "regulation_id": regulation_id,
                            "user_id": None,
                        },
                    ]
                )
                .returning(regulations_documents_table.c.id)
            )
        ).all()

    public_document_id, hidden_user_document_id, other_public_document_id = document_ids

    try:
        response = await client.get(
            f"/api/regulations/{regulation_id}/documents",
            params={"threshold": 0.9, "limit": 10, "query": "public document query"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "id": str(public_document_id),
                "score": pytest.approx(1.0),
                "header": "Public document",
                "text": "Matching public regulation document",
            }
        ]
    finally:
        prawobiorca.dependency_overrides.pop(get_texts_embedder, None)
        async with session_maker.begin() as session:
            await session.execute(
                delete(regulations_documents_table).where(
                    regulations_documents_table.c.id.in_([public_document_id, other_public_document_id])
                )
            )
            await session.execute(delete(regulations_table).where(regulations_table.c.id == regulation_id))


async def test_add_public_regulation_as_admin(
    client,
    override_session_maker,
    session_maker,
    override_authorize_admin_user,
    override_get_regulations_storage,
    mock_regulations_storage,
):
    regulation_data = {"name": "public-regulation.pdf", "regulation_type": RegulationType.DECREE}

    mock_regulations_storage.get_upload_target.side_effect = lambda id_: RegulationUploadTarget(
        id=id_, url="http://storage.local/bucket", fields={"key": str(id_)}
    )

    client.cookies.set(ACCESS_COOKIE_NAME, ACCESS_TOKEN)

    response = await client.post("/api/regulations", json=regulation_data)

    assert response.status_code == status.HTTP_201_CREATED

    response_json = response.json()
    assert "id" in response_json
    assert "url" in response_json
    assert "fields" in response_json
    regulation_id = UUID(response_json["id"])

    try:
        async with session_maker() as session:
            statement = select(regulations_table).where(regulations_table.c.id == regulation_id)
            result = await session.execute(statement)
        regulation = result.one_or_none()

        assert regulation is not None
        assert regulation.user_id is None
        assert regulation.presentation_name == "public-regulation.pdf"
        assert regulation.preparation_status == RegulationPreparationStatus.NOT_STARTED
        assert regulation.regulation_type == RegulationType.DECREE
    finally:
        async with session_maker.begin() as session:
            await session.execute(delete(regulations_table).where(regulations_table.c.id == regulation_id))


async def test_confirm_public_regulation_upload_as_admin(
    client,
    override_session_maker,
    session_maker,
    override_authorize_admin_user,
    override_get_regulations_storage,
    mock_regulations_storage,
    override_get_regulations_preparation_scheduler,
    mock_regulation_preparation_scheduler,
):
    async with session_maker.begin() as session:
        regulation_id = await session.scalar(
            insert(regulations_table)
            .values(
                user_id=None,
                presentation_name="public_confirm.pdf",
                regulation_type=RegulationType.ACT,
            )
            .returning(regulations_table.c.id)
        )

    mock_regulations_storage.check_regulation_exists.return_value = True

    client.cookies.set(ACCESS_COOKIE_NAME, ACCESS_TOKEN)

    try:
        response = await client.post(f"/api/regulations/{regulation_id}/confirm-upload")

        assert response.status_code == status.HTTP_202_ACCEPTED
        mock_regulations_storage.check_regulation_exists.assert_awaited_once_with(regulation_id)
        mock_regulation_preparation_scheduler.schedule_regulation_preparation.assert_awaited_once_with(
            None, regulation_id
        )

        async with session_maker() as session:
            statement = select(regulations_table).where(regulations_table.c.id == regulation_id)
            result = await session.execute(statement)
        regulation = result.one_or_none()

        assert regulation is not None
        assert regulation.preparation_status == RegulationPreparationStatus.IN_PROGRESS
    finally:
        async with session_maker.begin() as session:
            await session.execute(delete(regulations_table).where(regulations_table.c.id == regulation_id))
