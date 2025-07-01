from .storage import (
    STORAGE_REGISTRY,
    Dummy,
    FilteredStorage,
    LocalFile,
    Storage,
    StorageError,
)

try:
    from .cmr_query import CmrQuery
except ImportError:
    from .placeholder import CmrQuery  # type: ignore

try:
    from .http_request import HttpRequest
except ImportError:
    from .placeholder import HttpRequest  # type: ignore

try:
    from .s3file import S3File
except ImportError:
    from .placeholder import S3File  # type: ignore


__all__ = (
    "CmrQuery",
    "Dummy",
    "FilteredStorage",
    "HttpRequest",
    "LocalFile",
    "S3File",
    "STORAGE_REGISTRY",
    "Storage",
    "StorageError",
)
