from collections.abc import MutableMapping
from typing import TypeVar

T = TypeVar("T")
Registry = MutableMapping[str, T]
