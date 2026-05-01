from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.application.dtos.files import FileData, FileRepresentation
from app.application.interfaces.file_managment import UserFileManager
from app.application.interfaces.file_storage import UsersFilesRepository
from app.application.interfaces.relational import AsyncSession
from app.application.use_cases.user_files import AddUserFile, DeleteUserFile, ListUserFiles
from app.framework.dependencies.authentication import set_user_by_session_id
from app.framework.dependencies.file_managment import get_user_file_manager
from app.framework.dependencies.file_storage import get_users_file_repository
from app.framework.dependencies.relational import get_relational_session
from app.framework.dependencies.user_files import get_delete_user_file, get_list_user_files

user_files_router = APIRouter(tags=["user_files"], dependencies=(Depends(set_user_by_session_id),), prefix="/api/v2")


@user_files_router.get("/user/files", responses={status.HTTP_204_NO_CONTENT: {"description": "No user files."}})
async def get_user_files(
    list_user_files: Annotated[ListUserFiles, Depends(get_list_user_files)],
) -> list[FileRepresentation]:
    user_files = await list_user_files.execute()
    if user_files:
        return user_files
    else:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No user files.")


@user_files_router.post("/user/files")
async def add_file(
    session: Annotated[AsyncSession, Depends(get_relational_session)],
    user_file_manager: Annotated[UserFileManager, Depends(get_user_file_manager)],
    file: UploadFile,
    files_repository: Annotated[UsersFilesRepository, Depends(get_users_file_repository)],
):
    file_bytes = await file.read()
    file_name = cast(str, file.filename)
    try:
        file_data = FileData(name=file_name, file=file_bytes)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plik {file_name} jest pusty, nie można dodać pustego pliku!",
        )

    add_file_ = AddUserFile(session, user_file_manager, file_data, files_repository)
    try:
        await add_file_.execute()
    except FileExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Plik o podanej nazwie już istnieje!")


@user_files_router.delete(
    "/user/files/{fileHashString}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_204_NO_CONTENT: {"description": "File deleted."}},
)
async def delete_file(
    delete_user_file: Annotated[DeleteUserFile, Depends(get_delete_user_file)],
):
    try:
        await delete_user_file.execute()
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plik nie został znaleziony.")
