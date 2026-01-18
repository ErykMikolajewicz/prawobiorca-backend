from app.infrastructure.file_storage.repository import GCSStorageRepository
from app.shared.config import settings


def storage_repo_factory(is_public: bool):
    public_collection = settings.file_storage.PUBLIC_COLLECTION
    private_collection = settings.file_storage.PRIVATE_COLLECTION

    def _get_storage_repo():
        if is_public:
            bucket_name = public_collection
        else:
            bucket_name = private_collection
        return GCSStorageRepository(
            bucket_name=bucket_name,
            is_public=is_public,
        )

    return _get_storage_repo
