from mandible.umm_classes import TeaUrlBuilder
from mandible.umm_classes.types import CMAGranuleFile


def test_tea_url_builder_no_type():
    file: CMAGranuleFile = {
        "fileName": "test.txt",
        "bucket": "test_bucket",
        "key": "test-prefix/test.txt",
    }
    builder = TeaUrlBuilder(
        file,
        "https://test-example.123/",
        "FOO/TEST",
    )

    assert builder.get_related_urls() == [
        {
            "URL": "https://test-example.123/FOO/TEST/test-prefix/test.txt",
            "Description": "Download test.txt",
            "Type": "GET DATA",
        },
        {
            "URL": "s3://test_bucket/test-prefix/test.txt",
            "Description": "This link provides direct download access via S3 to test.txt",
            "Type": "GET DATA VIA DIRECT ACCESS",
        },
    ]
