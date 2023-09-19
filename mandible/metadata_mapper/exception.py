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
