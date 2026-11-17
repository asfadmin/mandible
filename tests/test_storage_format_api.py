"""Tests for the API interaction between the Storage and Format implementations."""

from collections.abc import Sequence
from pathlib import Path

import pytest

from mandible.metadata_mapper.context import Context
from mandible.metadata_mapper.format import (
    FORMAT_REGISTRY,
    H5,
    Bzip2File,
    Json,
    Xml,
    ZipInfo,
    ZipMember,
)
from mandible.metadata_mapper.key import Key
from mandible.metadata_mapper.storage import (
    STORAGE_REGISTRY,
    CmrQuery,
    Dummy,
    HttpRequest,
    LocalFile,
    S3File,
)

STORAGE_FACTORIES = []


def storage_factory_fixture(id: str, marks: Sequence[pytest.MarkDecorator] = ()):
    """Decorator for registering storage factory fixtures"""

    def decorator(func):
        fixture = pytest.fixture(func)

        STORAGE_FACTORIES.append((pytest.param(fixture, marks=marks), id))
        return fixture

    return decorator


@storage_factory_fixture(
    id=CmrQuery.__name__,
    marks=[pytest.mark.http],
)
def make_cmr_query(requests_mock):
    def make_storage(path: Path):
        requests_mock.get("//test.com", body=path.open("rb"))

        return CmrQuery(base_url="http://test.com"), []

    return make_storage


@storage_factory_fixture(id=Dummy.__name__)
def make_dummy():
    def make_storage(path: Path):
        return Dummy(path.read_bytes()), []

    return make_storage


@storage_factory_fixture(
    id=HttpRequest.__name__,
    marks=[pytest.mark.http],
)
def make_http_request(requests_mock):
    def make_storage(path: Path):
        requests_mock.get("//test.com", body=path.open("rb"))

        return HttpRequest(url="http://test.com"), []

    return make_storage


@storage_factory_fixture(id=LocalFile.__name__)
def make_local_file():
    def make_storage(path: Path):
        context_files = [
            {
                "name": "local_file",
                "path": str(path),
            },
        ]
        storage = LocalFile(filters={"name": "local_file"})

        return storage, context_files

    return make_storage


@storage_factory_fixture(
    id=S3File.__name__,
    marks=[pytest.mark.s3],
)
def make_s3_file(s3_resource):
    bucket = s3_resource.Bucket("test-bucket")
    bucket.create()

    def make_storage(path: Path):
        obj = bucket.Object("bucket_file.txt")
        obj.upload_fileobj(path.open("rb"))

        context_files = [
            {
                "name": "s3_file",
                "bucket": "test-bucket",
                "key": "bucket_file.txt",
            },
        ]
        storage = S3File(filters={"name": "s3_file"})

        return storage, context_files

    return make_storage


@pytest.fixture(
    params=[param for param, _ in STORAGE_FACTORIES],
    ids=[id for _, id in STORAGE_FACTORIES],
)
def storage_factory(request):
    return request.getfixturevalue(request.param.name)


def test_storage_registry():
    # This test exists to ensure that if a new storage type is added, that an
    # accompanying fixture is added to this file as well.
    fixture_names = sorted(id for _, id in STORAGE_FACTORIES)
    assert sorted(STORAGE_REGISTRY.keys()) == fixture_names


def test_format_registry():
    # This test exists to ensure that if a new format type is added, that an
    # accompanying test is added to this file as well.
    assert sorted(FORMAT_REGISTRY.keys()) == sorted(
        [
            "Bzip2File",
            "H5",
            "Json",
            "Xml",
            "ZipInfo",
            "ZipMember",
        ],
    )


def test_storage_with_format_bzip2(storage_factory, data_path):
    storage, context_files = storage_factory(data_path / "example.json.bz2")
    context = Context(files=context_files)

    with storage.open_file(context) as f:
        assert Bzip2File(Json()).get_value(f, Key("description")) == "A store inventory"


@pytest.mark.h5
def test_storage_with_format_h5(storage_factory, data_path):
    storage, context_files = storage_factory(data_path / "example.h5")
    context = Context(files=context_files)

    with storage.open_file(context) as f:
        assert H5().get_value(f, Key("description")) == "A store inventory"


def test_storage_with_format_json(storage_factory, data_path):
    storage, context_files = storage_factory(data_path / "example.json")
    context = Context(files=context_files)

    with storage.open_file(context) as f:
        assert Json().get_value(f, Key("description")) == "A store inventory"


@pytest.mark.xml
def test_storage_with_format_xml(storage_factory, data_path):
    storage, context_files = storage_factory(data_path / "example.xml")
    context = Context(files=context_files)

    with storage.open_file(context) as f:
        assert Xml().get_value(f, Key("/root/description")) == "A store inventory"


def test_storage_with_format_zip_info(storage_factory, data_path):
    storage, context_files = storage_factory(data_path / "example.zip")
    context = Context(files=context_files)

    with storage.open_file(context) as f:
        assert ZipInfo().get_value(f, Key("infolist[0].filename")) == "example.json"


def test_storage_with_format_zip_member(storage_factory, data_path):
    storage, context_files = storage_factory(data_path / "example.zip")
    context = Context(files=context_files)

    with storage.open_file(context) as f:
        assert (
            ZipMember(
                filters={"filename": "example.json"},
                format=Json(),
            ).get_value(f, Key("description"))
            == "A store inventory"
        )
