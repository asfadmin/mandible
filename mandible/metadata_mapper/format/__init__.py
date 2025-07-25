from .format import (
    FORMAT_REGISTRY,
    FileFormat,
    Format,
    FormatError,
    Json,
    ZipInfo,
    ZipMember,
)

try:
    from .h5 import H5
except ImportError:
    from .placeholder import H5  # type: ignore

try:
    from .xml import Xml
except ImportError:
    from .placeholder import Xml  # type: ignore


__all__ = (
    "FORMAT_REGISTRY",
    "FileFormat",
    "Format",
    "FormatError",
    "H5",
    "Json",
    "Xml",
    "ZipInfo",
    "ZipMember",
)
