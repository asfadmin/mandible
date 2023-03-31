import inspect
import logging
from abc import ABC, abstractmethod
from typing import Callable, Dict, Optional, Union

from .context import Context
from .source import Source, SourceProvider

log = logging.getLogger(__name__)


class MetadataMapperError(Exception):
    """A generic error raised by the MetadataMapper"""

    def __init__(self, msg: str):
        self.msg = msg


class TemplateError(MetadataMapperError):
    """An error that occurred while processing the metadata template."""

    def __init__(self, msg: str, debug_path: str = None):
        super().__init__(msg)
        self.debug_path = debug_path

    def __str__(self) -> str:
        debug = ""
        if self.debug_path is not None:
            debug = f" at {self.debug_path}"

        return f"failed to process template{debug}: {self.msg}"


class TemplateDirective(ABC):
    """Base class for directives in a metadata template.

    A directive is a special marker in the metadata template which will be
    replaced by the MetadataMapper.
    """

    def __init__(self, context: Context, sources: Dict[str, Source]):
        self.context = context
        self.sources = sources

    @abstractmethod
    def call(self):
        pass

    def prepare(self):
        pass


class Mapped(TemplateDirective):
    """A value mapped to the template from a metadata Source.

    The directive will be replaced by looking at the specified Source and
    extracting the defined key.
    """
    def __init__(
        self,
        context: Context,
        sources: Dict[str, Source],
        source: str,
        key: Union[str, Callable[[Context], str]]
    ):
        super().__init__(context, sources)

        if source not in sources:
            raise MetadataMapperError(f"source '{source}' does not exist")

        self.source = sources[source]
        if callable(key):
            key = key(context)
        self.key = key

    def call(self):
        return self.source.get_value(self.key)

    def prepare(self):
        self.source.add_key(self.key)


class MetadataMapper:
    def __init__(
        self,
        template,
        source_provider: SourceProvider = None,
        *,
        directive_marker: str = "@"
    ):
        self.template = template
        self.source_provider = source_provider
        self.directive_marker = directive_marker
        self.directives = {
            "mapped": Mapped
        }

    def get_metadata(self, context: Context) -> Dict:
        if self.source_provider is not None:
            sources = self.source_provider.get_sources()
        else:
            sources = {}

        try:
            self._cache_source_keys(context, sources)
        except TemplateError:
            raise
        except Exception as e:
            raise MetadataMapperError(
                f"failed to cache source keys: {e}"
            ) from e

        for name, source in sources.items():
            log.info("Querying source '%s': %s", name, source)
            try:
                source.query_all_values(context)
            except Exception as e:
                raise MetadataMapperError(
                    f"failed to query source '{name}': {e}"
                ) from e

        try:
            return self._replace_template(context, self.template, sources)
        except TemplateError:
            raise
        except Exception as e:
            raise MetadataMapperError(
                f"failed to evaluate template: {e}"
            ) from e

    def _cache_source_keys(self, context: Context, sources: Dict[str, Source]):
        for value, debug_path in _walk_values(self.template):
            if isinstance(value, dict):
                directive = self._get_directive(
                    context,
                    sources,
                    value,
                    debug_path
                )
                if directive is not None:
                    directive.prepare()

    def _replace_template(
        self,
        context: Context,
        template,
        sources: Dict[str, Source],
        debug_path: str = "$",
    ):
        if isinstance(template, dict):
            directive = self._get_directive(
                context,
                sources,
                template,
                debug_path
            )
            if directive is not None:
                return directive.call()

            return {
                k: self._replace_template(
                    context,
                    v,
                    sources,
                    debug_path=f"{debug_path}.{k}",
                )
                for k, v in template.items()
            }
        if isinstance(template, list):
            return [
                self._replace_template(
                    context,
                    v,
                    sources,
                    debug_path=f"{debug_path}[{i}]",
                )
                for i, v in enumerate(template)
            ]
        return template

    def _get_directive(
        self,
        context: Context,
        sources: Dict[str, Source],
        value: dict,
        debug_path: str,
    ) -> Optional[TemplateDirective]:
        directive_names = [
            key for key in value
            if key.startswith(self.directive_marker)
        ]
        if not directive_names:
            return None

        if len(directive_names) > 1:
            raise TemplateError(
                "multiple directives found in config: "
                f"{', '.join(repr(d) for d in directive_names)}",
                debug_path
            )

        directive_name = directive_names[0]

        cls = self.directives.get(directive_name[1:])
        if cls is None:
            raise TemplateError(
                f"invalid directive '{directive_name}'",
                debug_path
            )

        config = value[directive_name]
        argspec = inspect.getfullargspec(cls.__init__)

        # Ignore the `self`, `context`, and `sources` parameters
        required_keys = set(
            argspec.args[3:-len(argspec.defaults)]
            if argspec.defaults else
            argspec.args[3:]
        )
        config_keys = set(config.keys())
        diff = required_keys - config_keys

        if diff:
            s = ""
            if len(diff) > 1:
                s = "s"
            raise TemplateError(
                f"{directive_name} directive missing key{s}: "
                f"{', '.join(repr(d) for d in sorted(diff))}",
                debug_path
            )

        # For forward compatibility, ignore any unexpected keys
        all_keys = set(argspec.args[2:])
        kwargs = {
            k: v
            for k, v in config.items()
            if k in all_keys
        }

        try:
            return cls(context, sources, **kwargs)
        except Exception as e:
            raise TemplateError(str(e), debug_path) from e


def _walk_values(obj, debug_path: str = "$"):
    yield obj, debug_path
    if isinstance(obj, dict):
        for key, val in obj.items():
            yield from _walk_values(val, f"{debug_path}.{key}")
    elif isinstance(obj, (list, tuple, set)):
        for i, val in enumerate(obj):
            yield from _walk_values(val, f"{debug_path}[{i}]")
