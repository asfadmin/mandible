from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, Type, TypeVar

from .directive import (
    Add,
    FloorDiv,
    Mapped,
    Mul,
    Reformatted,
    Sub,
    TemplateDirective,
    TrueDiv,
)
from .types import Key, Template

# For testing purposes to ensure we implement builders for all directives
_DIRECTIVE_BUILDER_REGISTRY: Dict[str, Callable[..., "DirectiveBuilder"]] = {}


@dataclass
class BuildConfig:
    directive_marker: str


class Builder(ABC):
    @abstractmethod
    def build(self, config: BuildConfig) -> Template:
        pass


class DirectiveBuilder(Builder):
    def __init__(
        self,
        name: str,
        params: Dict[str, Any],
    ):
        self.name = name
        self.params = params

    def build(self, config: BuildConfig) -> Template:
        return {
            f"{config.directive_marker}{self.name}": {
                k: v.build(config) if isinstance(v, Builder) else v
                for k, v in self.params.items()
            },
        }

    def __add__(self, other: Any) -> "DirectiveBuilder":
        return add(self, other)

    def __radd__(self, other: Any) -> "DirectiveBuilder":
        return add(other, self)

    def __floordiv__(self, other: Any) -> "DirectiveBuilder":
        return floordiv(self, other)

    def __rfloordiv__(self, other: Any) -> "DirectiveBuilder":
        return floordiv(other, self)

    def __mul__(self, other: Any) -> "DirectiveBuilder":
        return mul(self, other)

    def __rmul__(self, other: Any) -> "DirectiveBuilder":
        return mul(other, self)

    def __sub__(self, other: Any) -> "DirectiveBuilder":
        return sub(self, other)

    def __rsub__(self, other: Any) -> "DirectiveBuilder":
        return sub(other, self)

    def __truediv__(self, other: Any) -> "DirectiveBuilder":
        return truediv(self, other)

    def __rtruediv__(self, other: Any) -> "DirectiveBuilder":
        return truediv(other, self)


T = TypeVar("T")


def _directive_builder(directive: Type["TemplateDirective"]) -> Callable[[T], T]:
    directive_name = directive.directive_name
    assert directive_name is not None

    def decorator(func):
        func.__doc__ = directive.__doc__

        _DIRECTIVE_BUILDER_REGISTRY[directive_name] = func
        return func

    return decorator


@_directive_builder(Mapped)
def mapped(
    source: str,
    key: Key,
    **key_options,
) -> DirectiveBuilder:
    directive_name = Mapped.directive_name
    assert directive_name is not None

    params = {
        "source": source,
        "key": key,
    }
    if key_options:
        params["key_options"] = key_options

    return DirectiveBuilder(
        directive_name,
        params,
    )


@_directive_builder(Reformatted)
def reformatted(
    format: str,
    value: Any,
    key: Key,
    **key_options,
) -> DirectiveBuilder:
    directive_name = Reformatted.directive_name
    assert directive_name is not None

    params = {
        "format": format,
        "value": value,
        "key": key,
    }
    if key_options:
        params["key_options"] = key_options

    return DirectiveBuilder(
        directive_name,
        params,
    )

#
# Operations
#


def _binop_directive(directive_name: str, left: Any, right: Any):
    return DirectiveBuilder(
        directive_name,
        {
            "left": left,
            "right": right,
        },
    )


@_directive_builder(Add)
def add(
    left: Any,
    right: Any,
) -> DirectiveBuilder:
    directive_name = Add.directive_name
    assert directive_name is not None

    return _binop_directive(directive_name, left, right)


@_directive_builder(FloorDiv)
def floordiv(
    left: Any,
    right: Any,
) -> DirectiveBuilder:
    directive_name = FloorDiv.directive_name
    assert directive_name is not None

    return _binop_directive(directive_name, left, right)


@_directive_builder(Mul)
def mul(
    left: Any,
    right: Any,
) -> DirectiveBuilder:
    directive_name = Mul.directive_name
    assert directive_name is not None

    return _binop_directive(directive_name, left, right)


@_directive_builder(Sub)
def sub(
    left: Any,
    right: Any,
) -> DirectiveBuilder:
    directive_name = Sub.directive_name
    assert directive_name is not None

    return _binop_directive(directive_name, left, right)


@_directive_builder(TrueDiv)
def truediv(
    left: Any,
    right: Any,
) -> DirectiveBuilder:
    directive_name = TrueDiv.directive_name
    assert directive_name is not None

    return _binop_directive(directive_name, left, right)


def build(template: Any, directive_marker: str = "@") -> Template:
    """Convert a template created with builder classes to a standard template
    that is ready to be used with the metadata mapper.

    When using builder classes, you must convert your template using `build`.

    :param template: template with possible `Builder` values
    :param directive_marker: marker to use for identifying directives
    :returns: Template - a standard template with all `Builder`s replaced
    """
    config = BuildConfig(directive_marker=directive_marker)

    return build_with_config(template, config)


def build_with_config(template: Any, config: BuildConfig) -> Template:
    """Same as build but takes configuration options as a BuildConfig object.

    :param template: template with possible `Builder` values
    :param config: BuildConfig object to customize generation
    :returns: Template - a standard template with all `Builder`s replaced
    """
    if isinstance(template, dict):
        return {
            k: build_with_config(v, config)
            for k, v in template.items()
        }
    elif isinstance(template, list):
        return [build_with_config(v, config) for v in template]
    elif isinstance(template, Builder):
        return template.build(config)
    elif isinstance(template, tuple):
        return tuple(build_with_config(v, config) for v in template)
    elif isinstance(template, set):
        return set(build_with_config(v, config) for v in template)
    elif isinstance(template, (str, int, float, bool)):
        return template

    raise ValueError(template)
