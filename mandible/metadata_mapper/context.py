from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Context:
    files: List[Dict[str, Any]] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
