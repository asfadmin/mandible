import io
from hashlib import md5

import pytest

from mandible.metadata_mapper.context import Context
from mandible.metadata_mapper.storage import (
    STORAGE_REGISTRY,
    LocalFile,
    S3File,
    Storage,
    StorageError,
)


def test_registry():
    assert STORAGE_REGISTRY == {
        "LocalFile": LocalFile,
        "S3File": S3File,
    }


def test_registry_intermediate_class():
    class Foo(Storage, register=False):
        pass

    assert "Foo" not in STORAGE_REGISTRY


def test_registry_error():
    with pytest.raises(KeyError):
        STORAGE_REGISTRY["FooBarBaz"]


def test_local_file(data_path):
    context = Context(
        files=[{
            "name": "local_file",
            "path": str(data_path / "local_file.txt")
        }]
    )
    storage = LocalFile(filters={"name": "local_file"})

    with storage.open_file(context) as f:
        assert f.read() == b"Some local file content\n"


def test_local_file_name_match(data_path):
    context = Context(
        files=[{
            "name": "local_file",
            "path": str(data_path / "local_file.txt")
        }]
    )
    storage = LocalFile(filters={"name": "local_.*"})

    with storage.open_file(context) as f:
        assert f.read() == b"Some local file content\n"


def test_local_file_int_filter(data_path):
    context = Context(
        files=[{
            "type": 0,
            "path": str(data_path / "local_file.txt")
        }]
    )
    storage = LocalFile(filters={"type": 0})

    with storage.open_file(context) as f:
        assert f.read() == b"Some local file content\n"


def test_local_file_creation():
    storage = LocalFile()
    assert storage.filters == {}


def test_local_file_name_match_error():
    context = Context(
        files=[{"name": "local_file"}]
    )
    storage = LocalFile(filters={"name": "foo.*"})

    with pytest.raises(StorageError, match="no files matched filters"):
        storage.open_file(context)


def test_local_file_empty_context_error():
    context = Context()
    storage = LocalFile(filters={"name": "foo.*"})

    with pytest.raises(StorageError, match="no files in context"):
        storage.open_file(context)


def test_s3_file_s3uri(s3_resource):
    bucket = s3_resource.Bucket("test-bucket")
    bucket.create()
    obj = bucket.Object("bucket_file.txt")
    obj.upload_fileobj(io.BytesIO(b"Some remote file content\n"))

    context = Context(
        files=[{
            "name": "s3_file",
            "bucket": "test-bucket",
            "key": "bucket_file.txt"
        }]
    )
    storage = S3File(filters={"name": "s3_file"})

    with storage.open_file(context) as f:
        assert f.read() == b"Some remote file content\n"


def test_s3_file_filters(s3_resource):
    bucket = s3_resource.Bucket("test-bucket")
    bucket.create()

    def create_file(bucket, name, contents=None, type="data"):
        contents = contents or f"Content from {name}\n".encode()
        obj = bucket.Object(name)
        obj.upload_fileobj(io.BytesIO(contents))

        return {
            "checksum": md5(contents).hexdigest(),
            "checksumType": "md5",
            "name": name,
            "size": len(contents),
            "type": type,
            "uri": f"https://example.asf.alaska.edu/{name}",
            "bucket": bucket.name,
            "key": name
        }

    context = Context(
        files=[
            create_file(bucket, "file1.txt"),
            create_file(bucket, "file2.txt", type="metadata"),
        ]
    )

    storage = S3File(filters={
        "name": "file1.txt"
    })
    with storage.open_file(context) as f:
        assert f.read() == b"Content from file1.txt\n"

    storage = S3File(filters={
        "type": "metadata"
    })
    with storage.open_file(context) as f:
        assert f.read() == b"Content from file2.txt\n"
