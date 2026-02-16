"""Logging configuration — Django-style dictConfig with Rich handler.

Usage::

    from whatsapp.infrastructure.logging import setup_logging
    setup_logging(level="DEBUG")  # call once at startup

Then in any module::

    import logging
    logger = logging.getLogger(__name__)
    logger.debug("message received", extra={"chat_id": "...", "sender": "..."})
"""

from __future__ import annotations

import logging
import logging.config
from typing import Any

from rich.console import Console
from rich.logging import RichHandler


def _sanitize(value: Any) -> str:
    """Sanitize a value for log display — collapse newlines, trim length."""
    s = repr(value)
    # Protobuf repr() generates literal \n — collapse to single line
    s = s.replace("\n", " ").replace("\\n", " ")
    # Collapse multiple spaces
    while "  " in s:
        s = s.replace("  ", " ")
    # Trim overly long values
    if len(s) > 120:
        s = s[:117] + "..."
    return s


class WhatsAppRichHandler(RichHandler):
    """Custom Rich logging handler for the WhatsApp bot.

    Extends ``RichHandler`` with:

    - Automatic rendering of ``extra`` dict fields as ``key=value``
      on a separate line below the message, sanitized and compact.
    - A pre-configured stderr ``Console`` with markup enabled.

    Subclass this to customize rendering (e.g. color per sender,
    emoji per level, etc.) without touching the logging config.
    """

    # Standard LogRecord attributes to exclude from extra display
    _STANDARD_KEYS: frozenset[str] = frozenset({
        "args", "created", "exc_info", "exc_text", "filename", "funcName",
        "levelname", "levelno", "lineno", "message", "module", "msecs", "msg",
        "name", "pathname", "process", "processName", "relativeCreated",
        "stack_info", "thread", "threadName", "taskName",
        # RichHandler internals
        "markup", "highlighter", "rich_tracebacks",
    })

    def __init__(self, **kwargs: Any) -> None:
        console = Console(stderr=True, markup=True, width=140)
        defaults: dict[str, Any] = {
            "console": console,
            "show_time": True,
            "show_level": True,
            "show_path": True,
            "rich_tracebacks": True,
            "tracebacks_show_locals": True,
            "markup": True,
            "log_time_format": "%H:%M:%S",
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

    def emit(self, record: logging.LogRecord) -> None:
        """Enrich the log message with structured extra fields before emit."""
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in self._STANDARD_KEYS and not k.startswith("_")
        }
        if extras:
            pairs = "  ".join(
                f"[dim]{k}=[/]{_sanitize(v)}" for k, v in extras.items()
            )
            record.msg = f"{record.msg}\n       ╰─ {pairs}"
        super().emit(record)


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the whatsapp package using dictConfig.

    Parameters
    ----------
    level : str
        Root log level. Use ``"DEBUG"`` for full diagnostics.
    """
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "rich": {
                "()": WhatsAppRichHandler,
            },
        },
        "loggers": {
            "whatsapp": {
                "handlers": ["rich"],
                "level": level,
                "propagate": False,
            },
            "jayce": {
                "handlers": ["rich"],
                "level": level,
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["rich"],
            "level": "WARNING",
        },
    }
    logging.config.dictConfig(config)
