from .format import (
    FORMAT_REGISTRY,
    Format,
    FormatError,
    Json,
    SimpleFormat,
    Zip,
    ZipInfo,
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
    "Format",
    "FormatError",
    "H5",
    "Json",
    "SimpleFormat",
    "Xml",
    "Zip",
    "ZipInfo",
)
