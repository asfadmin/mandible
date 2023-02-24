import pytest

from mandible.log import log_errors


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
