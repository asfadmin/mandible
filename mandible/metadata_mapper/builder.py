from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

from .directive import Mapped, Reformatted
from .types import Key, Template


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


def mapped(
    source: str,
    key: Key,
) -> DirectiveBuilder:
    directive_name = Mapped.directive_name
    assert directive_name is not None

    return DirectiveBuilder(
        directive_name,
        {
            "source": source,
            "key": key,
        },
    )


def reformatted(
    format: str,
    value: Any,
    key: Key,
) -> DirectiveBuilder:
    directive_name = Reformatted.directive_name
    assert directive_name is not None

    return DirectiveBuilder(
        directive_name,
        {
            "format": format,
            "value": value,
            "key": key,
        },
    )


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
