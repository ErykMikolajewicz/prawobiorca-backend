import json

from fastapi import status
from sqlalchemy import insert, select

from app.infrastructure.relational_db.schemas.cases import CaseDocuments, Cases
from app.shared.consts import AUTHORIZATION_COOKIE_NAME
from tests.consts import ADMIN_ID, AUTHORIZATION_TOKEN, USER_ID


async def test_add_case_document(
    client, override_session_maker, session_maker, override_authorize_normal_user, set_user, clean_user
):
    async with session_maker.begin() as session:
        stmt = (
            insert(Cases)
            .values(
                {"user_id": USER_ID, "name": "Case with document"},
            )
            .returning(Cases.id)
        )
        case_id = await session.scalar(stmt)

    client.cookies.set(
        AUTHORIZATION_COOKIE_NAME,
        json.dumps({"session_id": AUTHORIZATION_TOKEN}),
    )

    response = client.post(
        f"/api/user/cases/{case_id}/documents",
        json={"presentationName": "document.pdf", "content": "Document content"},
    )

    assert response.status_code == status.HTTP_201_CREATED

    async with session_maker() as session:
        stmt = select(CaseDocuments).where(CaseDocuments.case_id == case_id)
        case_document = await session.scalar(stmt)

    assert case_document is not None
    assert case_document.case_id == case_id
    assert case_document.user_id == USER_ID
    assert case_document.presentation_name == "document.pdf"
    assert case_document.content == "Document content"


async def test_delete_case_document(
    client, override_session_maker, session_maker, override_authorize_normal_user, set_user, clean_user
):
    async with session_maker.begin() as session:
        create_case_stmt = (
            insert(Cases)
            .values(
                {"user_id": USER_ID, "name": "Case with document to delete"},
            )
            .returning(Cases.id)
        )
        case_id = await session.scalar(create_case_stmt)

        create_document_stmt = (
            insert(CaseDocuments)
            .values(
                {
                    "case_id": case_id,
                    "user_id": USER_ID,
                    "presentation_name": "document-to-delete.pdf",
                    "content": "Document content to delete",
                }
            )
            .returning(CaseDocuments.id)
        )
        document_id = await session.scalar(create_document_stmt)

    client.cookies.set(
        AUTHORIZATION_COOKIE_NAME,
        json.dumps({"session_id": AUTHORIZATION_TOKEN}),
    )

    response = client.delete(f"/api/user/cases/documents/{document_id}")

    assert response.status_code == status.HTTP_200_OK

    async with session_maker() as session:
        deleted_document = await session.get(CaseDocuments, document_id)

    assert deleted_document is None


async def test_get_case_documents(
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
        create_cases_stmt = (
            insert(Cases)
            .values(
                [
                    {"user_id": USER_ID, "name": "Case with documents"},
                    {"user_id": USER_ID, "name": "Other user case"},
                ]
            )
            .returning(Cases.id)
        )
        target_case_id, other_case_id = (await session.scalars(create_cases_stmt)).all()

        create_documents_stmt = (
            insert(CaseDocuments)
            .values(
                [
                    {
                        "case_id": target_case_id,
                        "user_id": USER_ID,
                        "presentation_name": "first-document.pdf",
                        "content": "First document content",
                    },
                    {
                        "case_id": target_case_id,
                        "user_id": USER_ID,
                        "presentation_name": "second-document.pdf",
                        "content": "Second document content",
                    },
                    {
                        "case_id": other_case_id,
                        "user_id": USER_ID,
                        "presentation_name": "other-case-document.pdf",
                        "content": "Other case document content",
                    },
                    {
                        "case_id": target_case_id,
                        "user_id": ADMIN_ID,
                        "presentation_name": "other-user-document.pdf",
                        "content": "Other user document content",
                    },
                ]
            )
            .returning(CaseDocuments.id)
        )
        first_document_id, second_document_id, _, _ = (await session.scalars(create_documents_stmt)).all()

    client.cookies.set(
        AUTHORIZATION_COOKIE_NAME,
        json.dumps({"session_id": AUTHORIZATION_TOKEN}),
    )

    response = client.get(f"/api/user/cases/{target_case_id}/documents")

    assert response.status_code == status.HTTP_200_OK
    assert sorted(response.json(), key=lambda document: document["presentationName"]) == [
        {
            "id": str(first_document_id),
            "caseId": str(target_case_id),
            "presentationName": "first-document.pdf",
            "content": "First document content",
        },
        {
            "id": str(second_document_id),
            "caseId": str(target_case_id),
            "presentationName": "second-document.pdf",
            "content": "Second document content",
        },
    ]
