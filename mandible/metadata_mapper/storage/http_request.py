import io
from dataclasses import dataclass
from typing import IO, Any, Optional, Union

import requests

from mandible.metadata_mapper.context import Context

from .storage import Storage


@dataclass
class HttpRequest(Storage):
    """A storage which returns the body of an HTTP response"""

    url: str
    method: str = "GET"
    params: Optional[dict] = None
    data: Optional[Union[dict, bytes]] = None
    json: Optional[Any] = None
    headers: Optional[dict] = None
    cookies: Optional[dict] = None
    timeout: Optional[Union[float, tuple[float, float]]] = None
    allow_redirects: bool = True

    def open_file(self, context: Context) -> IO[bytes]:
        response = requests.request(
            self.method,
            self.url,
            params=self.params,
            data=self.data,
            json=self.json,
            headers=self.headers,
            cookies=self.cookies,
            timeout=self.timeout,
            allow_redirects=self.allow_redirects,
            stream=True,
        )

        # TODO(reweeden): Using response.content causes the entire response
        # payload to be loaded into memory immediately. Ideally, we would
        # optimize here by returning a file-like object that could load the
        # response lazily. Requests does provide a response.raw file-like
        # object, however, this doesn't preform the content decoding that you
        # get when using response.content.
        return io.BytesIO(response.content)
