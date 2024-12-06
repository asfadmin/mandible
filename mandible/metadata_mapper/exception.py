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


class ContextValueError(MetadataMapperError):
    """An error that occurred while processing the context value replacements."""

    def __init__(
        self,
        msg: str,
        source_name: str = None,
    ):
        super().__init__(msg)
        self.source_name = source_name

    def __str__(self) -> str:
        debug = ""
        if self.source_name is not None:
            debug = f" for source {repr(self.source_name)}"

        return f"failed to process context values{debug}: {self.msg}"
