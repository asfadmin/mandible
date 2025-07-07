from dataclasses import dataclass, field
from typing import IO, Any

import s3fs

from .storage import FilteredStorage


@dataclass
class S3File(FilteredStorage):
    """A storage which reads from an AWS S3 object"""

    s3fs_kwargs: dict[str, Any] = field(default_factory=dict)

    def _open_file(self, info: dict) -> IO[bytes]:
        s3 = s3fs.S3FileSystem(anon=False, **self.s3fs_kwargs)
        return s3.open(f"s3://{info['bucket']}/{info['key']}")
