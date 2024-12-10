import urllib.parse
from dataclasses import InitVar, dataclass
from typing import Optional

from mandible.metadata_mapper.context import Context

from .http_request import HttpRequest


@dataclass
class CmrQuery(HttpRequest):
    """A convenience class for setting neccessary CMR parameters"""

    url: InitVar[None] = None

    base_url: str = ""
    path: str = ""
    format: str = ""
    token: Optional[str] = None

    def __post_init__(self, url: str):
        if url:
            raise ValueError(
                "do not set 'url' directly, use 'base_url' and 'path' instead",
            )

    def _get_override_request_args(self, context: Context) -> dict:
        return {
            "headers": self._get_headers(),
            "url": self._get_url(),
        }

    def _get_headers(self) -> Optional[dict]:
        if self.token is None:
            return self.headers

        return {
            **(self.headers or {}),
            "Authorization": self.token,
        }

    def _get_url(self) -> str:
        path = self.path
        if self.format:
            path = f"{self.path}.{self.format.lower()}"
        return urllib.parse.urljoin(self.base_url, path)
