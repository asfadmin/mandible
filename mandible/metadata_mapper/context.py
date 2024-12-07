from dataclasses import dataclass, field
from typing import Any


@dataclass
class Context:
    files: list[dict[str, Any]] = field(default_factory=list)
    meta: list[str, Any] = field(default_factory=dict)
