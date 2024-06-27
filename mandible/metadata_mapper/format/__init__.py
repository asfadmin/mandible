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
    from .format import H5

try:
    from .xml import Xml
except ImportError:
    from .format import Xml


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
