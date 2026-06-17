import json
import logging
import sys
from io import StringIO


class TestJSONFormatter:
    def test_formatter_outputs_valid_json(self):
        """Test that JSONFormatter produces valid JSON with required fields."""
        from app.core.logging import JSONFormatter

        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="Test message", args=(), exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)

        assert "timestamp" in parsed
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Test message"
        assert parsed["logger"] == "test"

    def test_formatter_includes_exception_info(self):
        """Test that JSONFormatter includes exception and traceback when present."""
        from app.core.logging import JSONFormatter

        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            record = logging.LogRecord(
                name="test", level=logging.ERROR, pathname="test.py",
                lineno=1, msg="Error occurred", args=(), exc_info=sys.exc_info(),
            )

        output = formatter.format(record)
        parsed = json.loads(output)

        assert "exception" in parsed
        assert "traceback" in parsed
        assert "test error" in parsed["exception"]

    def test_formatter_merges_extra_fields(self):
        """Test that JSONFormatter merges custom extra fields into output."""
        from app.core.logging import JSONFormatter

        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="With extra", args=(), exc_info=None,
        )
        record.request_id = "abc123"
        record.duration_ms = 45.2
        output = formatter.format(record)
        parsed = json.loads(output)

        assert parsed["request_id"] == "abc123"
        assert parsed["duration_ms"] == 45.2


class TestSetupLogging:
    def test_setup_logging_sets_level_from_env(self, monkeypatch):
        """Test that setup_logging reads LOG_LEVEL from environment."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        from app.core.logging import setup_logging
        setup_logging()

        root = logging.getLogger()
        assert root.level == logging.DEBUG

    def test_setup_logging_defaults_to_info(self, monkeypatch):
        """Test that setup_logging defaults to INFO when LOG_LEVEL not set."""
        monkeypatch.delenv("LOG_LEVEL", raising=False)

        from app.core.logging import setup_logging
        setup_logging()

        root = logging.getLogger()
        assert root.level == logging.INFO

    def test_setup_logging_invalid_level_falls_back_to_info(self, monkeypatch):
        """Test that setup_logging falls back to INFO for invalid LOG_LEVEL."""
        monkeypatch.setenv("LOG_LEVEL", "INVALIDO")

        from app.core.logging import setup_logging
        setup_logging()

        root = logging.getLogger()
        assert root.level == logging.INFO

    def test_setup_logging_adds_stream_handler(self):
        """Test that setup_logging configures a StreamHandler with JSONFormatter."""
        from app.core.logging import JSONFormatter, setup_logging

        setup_logging()

        root = logging.getLogger()
        handlers = root.handlers
        assert len(handlers) == 1
        assert isinstance(handlers[0], logging.StreamHandler)
        assert isinstance(handlers[0].formatter, JSONFormatter)
