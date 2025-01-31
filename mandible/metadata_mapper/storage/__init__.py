from .storage import (
    STORAGE_REGISTRY,
    Dummy,
    FilteredStorage,
    LocalFile,
    S3File,
    Storage,
    StorageError,
)

try:
    from .cmr_query import CmrQuery
except ImportError:
    from .storage import CmrQuery  # type: ignore

try:
    from .http_request import HttpRequest
except ImportError:
    from .storage import HttpRequest  # type: ignore


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
