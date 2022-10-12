import os
from pathlib import Path

import boto3
import pytest
from moto import mock_s3


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def s3_resource(aws_credentials):
    with mock_s3():
        yield boto3.resource("s3")


@pytest.fixture(scope="session")
def data_path():
    return Path(__file__).parent.joinpath("data").resolve()
