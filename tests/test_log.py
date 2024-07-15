import logging

import pytest

from mandible.log import init_custom_log_record_factory, log_errors


@pytest.fixture
def event_config():
    return {
        "cma": {
            "event": {
                "cumulus_meta": {
                    "execution_name": "this_is_a_test_execution",
                    "cumulus_version": "TEST_CUMULUS",
                },
                "payload": {
                    "granules": [{"granuleId": "test_granule"}],
                },
            },
        },
    }


def test_custom_log_record_factory(caplog, monkeypatch, event_config):
    monkeypatch.setenv("DAAC_VERSION", "TEST_DAAC")
    monkeypatch.setenv("CORE_VERSION", "TEST_CORE")
    with caplog.at_level(logging.INFO):
        log = logging.getLogger(__name__)
        init_custom_log_record_factory(event_config)
        log.info("TEST")
        assert caplog.records[0].cirrus_daac_version == "TEST_DAAC"
        assert caplog.records[0].cirrus_core_version == "TEST_CORE"
        assert caplog.records[0].cumulus_version == "TEST_CUMULUS"
        assert caplog.records[0].granule_name == "test_granule"
        assert caplog.records[0].workflow_execution_name == "this_is_a_test_execution"


def test_log_errors(caplog):
    with pytest.raises(Exception):
        with caplog.at_level("ERROR"):
            with log_errors():
                raise Exception("test")

    assert "Exception: test" in caplog.text


def test_log_errors_configure_types(caplog):
    with pytest.raises(Exception):
        with caplog.at_level("ERROR"):
            # Only log KeyErrors and TypeErrors
            with log_errors(KeyError, TypeError):
                raise Exception("test")

    assert "Exception: test" not in caplog.text


def test_log_errors_chained(caplog):
    with pytest.raises(Exception):
        with caplog.at_level("ERROR"):
            with log_errors():
                try:
                    raise Exception("Cause")
                except Exception as e:
                    raise Exception("Result") from e

    assert "Exception: Cause" in caplog.text
    assert "Exception: Result" in caplog.text
    assert "The above exception was the direct cause" in caplog.text
