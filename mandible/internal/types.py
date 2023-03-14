from typing import MutableMapping, TypeVar

T = TypeVar("T")
Registry = MutableMapping[str, T]
