import re

import pytest

from mandible.metadata_mapper import (
    ConfigSourceProvider,
    Context,
    FileSource,
    MetadataMapper,
    MetadataMapperError,
    PySourceProvider,
)
from mandible.metadata_mapper.format import Json, Xml
from mandible.metadata_mapper.storage import LocalFile


@pytest.fixture
def mapper(config):
    return MetadataMapper(
        template=config["template"],
        source_provider=ConfigSourceProvider(config["sources"]),
    )


def test_empty_mapping_empty_context():
    mapper = MetadataMapper({})
    assert mapper.get_metadata(Context()) == {}


def test_constant_mapping_empty_context():
    template = {
        "foo": "bar",
        "baz": "qux",
    }
    mapper = MetadataMapper(template)

    assert mapper.get_metadata(Context()) == template


def test_empty_context(fixed_name_file_config):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "fixed_name_file",
                    "key": "foo",
                },
            },
        },
        source_provider=ConfigSourceProvider({
            "fixed_name_file": fixed_name_file_config,
        }),
    )
    context = Context()

    with pytest.raises(
        MetadataMapperError,
        match=(
            "failed to query source 'fixed_name_file': "
            "no files in context"
        ),
    ):
        mapper.get_metadata(context)


@pytest.mark.xml
def test_basic(mapper, context):
    assert mapper.get_metadata(context) == {
        "foo": "value for foo",
        "outer": {
            "nested": "value for nested",
            "bar": "value for bar",
        },
        "namespace_xml_foobar_1": "testing_1",
        "namespace_xml_foobar_2": "2",
        "xml_foobar_1": "testing_1",
        "xml_foobar_2": "2",
    }


def test_custom_directive_marker(context, fixed_name_file_config):
    mapper = MetadataMapper(
        template={
            "foo": {
                "#mapped": {
                    "source": "fixed_name_file",
                    "key": "foo",
                },
            },
        },
        source_provider=ConfigSourceProvider({
            "fixed_name_file": fixed_name_file_config,
        }),
        directive_marker="#",
    )
    assert mapper.get_metadata(context) == {
        "foo": "value for foo",
    }


def test_custom_directive_marker_long(context, fixed_name_file_config):
    mapper = MetadataMapper(
        template={
            "foo": {
                "###mapped": {
                    "source": "fixed_name_file",
                    "key": "foo",
                },
            },
        },
        source_provider=ConfigSourceProvider({
            "fixed_name_file": fixed_name_file_config,
        }),
        directive_marker="###",
    )
    assert mapper.get_metadata(context) == {
        "foo": "value for foo",
    }


@pytest.mark.xml
def test_basic_py_source_provider(config, context):
    mapper = MetadataMapper(
        template=config["template"],
        source_provider=PySourceProvider({
            "fixed_name_file": FileSource(
                storage=LocalFile(
                    filters={
                        "name": "fixed_name_file.json",
                    },
                ),
                format=Json(),
            ),
            "fixed_xml_file": FileSource(
                storage=LocalFile(
                    filters={
                        "name": "fixed_xml_file.xml",
                    },
                ),
                format=Xml(),
            ),
            "namespace_xml_file": FileSource(
                storage=LocalFile(
                    filters={
                        "name": "xml_with_namespace.xml",
                    },
                ),
                format=Xml(),
            ),
            "name_match_file": FileSource(
                storage=LocalFile(
                    filters={
                        "name": r".*match_me\.json",
                    },
                ),
                format=Json(),
            ),
            "name_match_file2": FileSource(
                storage=LocalFile(
                    filters={
                        "name": re.compile(r".*match_me\.json"),
                    },
                ),
                format=Json(),
            ),
        }),
    )
    assert mapper.get_metadata(context) == {
        "foo": "value for foo",
        "outer": {
            "nested": "value for nested",
            "bar": "value for bar",
        },
        "namespace_xml_foobar_1": "testing_1",
        "namespace_xml_foobar_2": "2",
        "xml_foobar_1": "testing_1",
        "xml_foobar_2": "2",
    }


@pytest.mark.s3
@pytest.mark.xml
def test_basic_s3_file(s3_resource, config, context):
    s3_resource.create_bucket(Bucket="test")
    s3_resource.Object("test", "fixed_name_file.json").put(
        Body=open(context.files[0]["path"]).read(),
    )
    context.files[0]["bucket"] = "test"
    context.files[0]["key"] = "fixed_name_file.json"

    config["sources"]["fixed_name_file"]["storage"]["class"] = "S3File"

    mapper = MetadataMapper(
        template=config["template"],
        source_provider=ConfigSourceProvider(config["sources"]),
    )

    assert mapper.get_metadata(context) == {
        "foo": "value for foo",
        "outer": {
            "nested": "value for nested",
            "bar": "value for bar",
        },
        "namespace_xml_foobar_1": "testing_1",
        "namespace_xml_foobar_2": "2",
        "xml_foobar_1": "testing_1",
        "xml_foobar_2": "2",
    }


def test_no_matching_files(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "source_file",
                    "key": "foo",
                },
            },
        },
        source_provider=ConfigSourceProvider({
            "source_file": {
                "storage": {
                    "class": "LocalFile",
                    "filters": {
                        "name": "does not exist",
                    },
                },
                "format": {
                    "class": "Json",
                },
            },
        }),
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            "failed to query source 'source_file': "
            "no files matched filters"
        ),
    ):
        mapper.get_metadata(context)


def test_source_non_existent_key(context, fixed_name_file_config):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "fixed_name_file",
                    "key": "does_not_exist",
                },
            },
        },
        source_provider=ConfigSourceProvider({
            "fixed_name_file": fixed_name_file_config,
        }),
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            "failed to query source 'fixed_name_file': "
            "key not found 'does_not_exist'"
        ),
    ):
        mapper.get_metadata(context)


def test_invalid_directive(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@does_not_exist": {},
            },
        },
        source_provider=ConfigSourceProvider({}),
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo\.@does_not_exist: "
            "invalid directive '@does_not_exist'"
        ),
    ):
        mapper.get_metadata(context)


def test_invalid_directive_config_type(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": 100,
            },
        },
        source_provider=ConfigSourceProvider({}),
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo\.@mapped: "
            "directive body should be type 'dict' not 'int'"
        ),
    ):
        mapper.get_metadata(context)


def test_multiple_directives(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {},
                "@invalid": {},
            },
        },
        source_provider=ConfigSourceProvider({}),
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo: "
            "multiple directives found in config: '@mapped', '@invalid'"
        ),
    ):
        mapper.get_metadata(context)


def test_context_values_missing():
    mapper = MetadataMapper(
        template={},
        source_provider=ConfigSourceProvider({
            "test": {
                "storage": {
                    "class": "LocalFile",
                    "filters": "$.meta.does-not-exist",
                },
                "format": {
                    "class": "Json",
                },
            },
        }),
    )
    context = Context()

    with pytest.raises(
        MetadataMapperError,
        match=(
            "failed to process context values for source 'test': .* for path "
            r"'\$\.meta\.does-not-exist'"
        ),
    ):
        mapper.get_metadata(context)


@pytest.mark.jsonpath
def test_context_values_multiple_values():
    mapper = MetadataMapper(
        template={},
        source_provider=ConfigSourceProvider({
            "test": {
                "storage": {
                    "class": "LocalFile",
                    "filters": "$.meta.foo[*].bar",
                },
                "format": {
                    "class": "Json",
                },
            },
        }),
    )
    context = Context(
        meta={
            "foo": [
                {"bar": 1},
                {"bar": 2},
            ],
        },
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            "failed to process context values for source 'test': "
            r"context path '\$\.meta\.foo\[\*\]\.bar' returned more than one "
            "value"
        ),
    ):
        mapper.get_metadata(context)


@pytest.mark.jsonpath
def test_context_values_invalid():
    mapper = MetadataMapper(
        template={},
        source_provider=ConfigSourceProvider({
            "test": {
                "storage": {
                    "class": "LocalFile",
                    "filters": "$.meta.bad-syntax[",
                },
                "format": {
                    "class": "Json",
                },
            },
        }),
    )
    context = Context()

    with pytest.raises(
        MetadataMapperError,
        match=(
            "failed to process context values for source 'test': "
            r"jsonpath error for path '\$\.meta\.bad-syntax\[': "
        ),
    ):
        mapper.get_metadata(context)
