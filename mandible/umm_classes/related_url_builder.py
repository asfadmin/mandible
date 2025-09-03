"""Classes for generating RelatedUrl links"""

import urllib.parse
from abc import ABC, abstractmethod
from typing import Optional, Union

from .factory import related_url
from .types import CMAGranuleFile, RelatedUrl


class RelatedUrlBuilder(ABC):
    RELATED_URL_HTTP_TYPE_MAP = {
        "browse": "GET RELATED VISUALIZATION",
        "data": "GET DATA",
        "linkage": "VIEW RELATED INFORMATION",
        "metadata": "EXTENDED METADATA",
        "qa": "VIEW RELATED INFORMATION",
    }
    RELATED_URL_S3_TYPE_MAP = {
        **RELATED_URL_HTTP_TYPE_MAP,
        "data": "GET DATA VIA DIRECT ACCESS",
    }

    def __init__(self, file: CMAGranuleFile, include_s3_uri: bool = True):
        self.file = file
        self.include_s3_uri = include_s3_uri

    def get_http_description(self) -> Optional[str]:
        return f"Download {self.file['fileName']}"

    def get_http_format(self) -> Optional[str]:
        return None

    def get_http_mime_type(self) -> Optional[str]:
        return None

    def get_http_size(self) -> Optional[Union[float, int]]:
        return None

    def get_http_size_unit(self) -> Optional[str]:
        return None

    def get_http_subtype(self) -> Optional[str]:
        return None

    def get_http_type(self) -> str:
        file_type = self.file.get("type", "data")
        return self.RELATED_URL_HTTP_TYPE_MAP[file_type]

    @abstractmethod
    def get_http_url(self) -> str:
        pass

    def get_related_urls(self) -> list[RelatedUrl]:
        http_url = self.get_related_url_http()

        if self.include_s3_uri:
            # It seems that Earthdata Search will blindly use the first browse
            # image RelatedUrl it finds so we need to put the HTTP url first.
            return [
                http_url,
                self.get_related_url_s3(),
            ]

        return [http_url]

    def get_related_url_http(self) -> RelatedUrl:
        return related_url(
            url=self.get_http_url(),
            type=self.get_http_type(),
            subtype=self.get_http_subtype(),
            description=self.get_http_description(),
            format=self.get_http_format(),
            mime_type=self.get_http_mime_type(),
            size=self.get_http_size(),
            size_unit=self.get_http_size_unit(),
        )

    def get_related_url_s3(self) -> RelatedUrl:
        return related_url(
            url=self.get_s3_url(),
            type=self.get_s3_type(),
            subtype=self.get_s3_subtype(),
            description=self.get_s3_description(),
            format=self.get_s3_format(),
            mime_type=self.get_s3_mime_type(),
            size=self.get_s3_size(),
            size_unit=self.get_s3_size_unit(),
        )

    def get_s3_description(self) -> Optional[str]:
        return f"This link provides direct download access via S3 to {self.file['fileName']}"

    def get_s3_format(self) -> Optional[str]:
        return None

    def get_s3_mime_type(self) -> Optional[str]:
        return None

    def get_s3_size(self) -> Optional[Union[float, int]]:
        return None

    def get_s3_size_unit(self) -> Optional[str]:
        return None

    def get_s3_subtype(self) -> Optional[str]:
        return None

    def get_s3_type(self) -> str:
        file_type = self.file.get("type", "data")
        return self.RELATED_URL_S3_TYPE_MAP[file_type]

    def get_s3_url(self) -> str:
        return f"s3://{self.file['bucket']}/{self.file['key']}"


class DatapoolUrlBuilder(RelatedUrlBuilder):
    def __init__(
        self,
        file: CMAGranuleFile,
        download_host: str,
        processing_type: str,
        mission: str,
        include_s3_uri: bool = True,
    ):
        super().__init__(file, include_s3_uri)

        self.download_host = download_host
        self.processing_type = processing_type
        self.mission = mission

    def get_http_url(self) -> str:
        return f"https://{self.download_host}/{self.processing_type}/{self.mission}/{self.file['fileName']}"


class TeaUrlBuilder(RelatedUrlBuilder):
    def __init__(
        self,
        file: CMAGranuleFile,
        download_url: str,
        path_prefix: str,
        include_s3_uri: bool = True,
    ):
        super().__init__(file, include_s3_uri)

        self.download_url = download_url
        self.path_prefix = path_prefix

    def get_http_url(self) -> str:
        return urllib.parse.urljoin(
            self.download_url,
            f"{self.path_prefix}/{self.file['key']}",
        )
