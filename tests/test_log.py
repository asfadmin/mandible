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


def test_init_custom_log_record_factory_called_multiple_times(caplog):
    for _ in range(1100):
        init_custom_log_record_factory({})

    with caplog.at_level(logging.INFO):
        log = logging.getLogger(__name__)
        log.info("TEST MESSAGE")
        assert "TEST MESSAGE" in caplog.text


def test_init_custom_log_record_factory_update(caplog):
    init_custom_log_record_factory({})

    with caplog.at_level(logging.INFO):
        log = logging.getLogger(__name__)
        log.info("TEST 1")
        assert caplog.records[0].cirrus_daac_version is None
        assert caplog.records[0].cirrus_core_version is None
        assert caplog.records[0].cumulus_version is None
        assert caplog.records[0].granule_name is None
        assert caplog.records[0].workflow_execution_name is None

    init_custom_log_record_factory(
        {
            "cumulus_meta": {
                "cumulus_version": "v0.0.0",
            },
        }
    )

    caplog.clear()
    with caplog.at_level(logging.INFO):
        log = logging.getLogger(__name__)
        log.info("TEST 2")
        assert caplog.records[0].cirrus_daac_version is None
        assert caplog.records[0].cirrus_core_version is None
        assert caplog.records[0].cumulus_version == "v0.0.0"
        assert caplog.records[0].granule_name is None
        assert caplog.records[0].workflow_execution_name is None


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
