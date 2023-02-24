from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Context:
    files: Dict[str, Dict] = field(default_factory=dict)
    meta: Dict = field(default_factory=dict)
