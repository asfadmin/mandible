import io

import pytest

from mandible.metadata_mapper.context import Context
from mandible.metadata_mapper.storage import LocalFile, S3File, Storage


def test_registry():
    assert Storage.get_subclass("LocalFile") is LocalFile
    assert Storage.get_subclass("S3File") is S3File


def test_registry_error():
    with pytest.raises(KeyError):
        Storage.get_subclass("FooBarBaz")


def test_local_file(data_path):
    context = Context(
        files={
            "local_file": {
                "path": str(data_path / "local_file.txt")
            }
        }
    )
    storage = LocalFile(name="local_file")

    with storage.open_file(context) as f:
        assert f.read() == b"Some local file content\n"


def test_local_file_name_match(data_path):
    context = Context(
        files={
            "local_file": {
                "path": str(data_path / "local_file.txt")
            }
        }
    )
    storage = LocalFile(name_match="local_.*")

    with storage.open_file(context) as f:
        assert f.read() == b"Some local file content\n"


def test_local_file_creation_error():
    with pytest.raises(ValueError, match="You must provide"):
        _ = LocalFile()
    with pytest.raises(ValueError, match="You can't provide"):
        _ = LocalFile(name="foo", name_match="foo")


def test_local_file_name_error():
    context = Context()
    storage = LocalFile(name="foo.txt")

    with pytest.raises(KeyError):
        storage.open_file(context)


def test_local_file_name_match_error():
    context = Context()
    storage = LocalFile(name_match="foo.*")

    with pytest.raises(RuntimeError, match="No files matched pattern"):
        storage.open_file(context)


def test_s3_file(s3_resource):
    bucket = s3_resource.Bucket("test-bucket")
    bucket.create()
    obj = bucket.Object("bucket_file.txt")
    obj.upload_fileobj(io.BytesIO(b"Some remote file content\n"))

    context = Context(
        files={
            "local_file": {
                "s3uri": "s3://test-bucket/bucket_file.txt"
            }
        }
    )
    storage = S3File(name="local_file")

    with storage.open_file(context) as f:
        assert f.read() == b"Some remote file content\n"
