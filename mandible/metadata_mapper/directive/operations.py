from dataclasses import dataclass
from typing import Any

from .directive import TemplateDirective


@dataclass
class _BinOp(TemplateDirective, register=False):
    left: Any
    right: Any


@dataclass
class Add(_BinOp):
    """Perform a python + operation on two values."""

    def call(self) -> Any:
        return self.left + self.right


@dataclass
class FloorDiv(_BinOp):
    """Perform a python // operation on two values."""

    def call(self) -> Any:
        return self.left // self.right


@dataclass
class Mul(_BinOp):
    """Perform a python * operation on two values."""

    def call(self) -> Any:
        return self.left * self.right


@dataclass
class Sub(_BinOp):
    """Perform a python - operation on two values."""

    def call(self) -> Any:
        return self.left - self.right


@dataclass
class TrueDiv(_BinOp):
    """Perform a python / operation on two values."""

    def call(self) -> Any:
        return self.left / self.right
