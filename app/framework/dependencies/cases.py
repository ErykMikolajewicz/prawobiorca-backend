from typing import Annotated

from fastapi import Depends

import app.infrastructure.relational_db.repositories.cases as sqla_repos
from app.application.interfaces.cases import CaseDocumentsRepository, CasesRepository
from app.application.interfaces.relational import SessionMaker
from app.application.use_cases.cases import (
    AddCase,
    AddCaseDocument,
    DeleteCase,
    DeleteCaseDocument,
    ListCaseDocuments,
    ListCases,
)
from app.framework.dependencies.relational import get_session_maker


def get_cases_repo() -> CasesRepository:
    return sqla_repos.CasesRepository()


def get_case_documents_repo() -> CaseDocumentsRepository:
    return sqla_repos.CaseDocumentsRepository()


def get_list_user_cases(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    cases_repository: Annotated[CasesRepository, Depends(get_cases_repo)],
) -> ListCases:
    return ListCases(session_maker, cases_repository)


def get_add_user_case(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    cases_repository: Annotated[CasesRepository, Depends(get_cases_repo)],
) -> AddCase:
    return AddCase(session_maker, cases_repository)


def get_delete_user_case(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    cases_repository: Annotated[CasesRepository, Depends(get_cases_repo)],
) -> DeleteCase:
    return DeleteCase(session_maker, cases_repository)


def get_add_case_document(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    case_documents_repo: Annotated[CaseDocumentsRepository, Depends(get_case_documents_repo)],
) -> AddCaseDocument:
    return AddCaseDocument(session_maker, case_documents_repo)


def get_delete_case_document(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    case_documents_repo: Annotated[CaseDocumentsRepository, Depends(get_case_documents_repo)],
) -> DeleteCaseDocument:
    return DeleteCaseDocument(session_maker, case_documents_repo)


def get_list_case_documents(
    session_maker: Annotated[SessionMaker, Depends(get_session_maker)],
    case_documents_repo: Annotated[CaseDocumentsRepository, Depends(get_case_documents_repo)],
) -> ListCaseDocuments:
    return ListCaseDocuments(session_maker, case_documents_repo)
