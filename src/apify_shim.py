"""Apify SDK shim for local / self-hosted multiplexer use.

When running inside an Apify Actor (cloud or `apify run`), use the real SDK:
    from apify import Actor

When running the MCP server locally without Apify (e.g. in the unbearable-mcp
multiplexer on a self-hosted Pi), the Actor.init() / Actor.charge() calls would
fail because there is no Apify runtime context. This shim provides no-op versions.

Usage in main.py:

    try:
        from apify import Actor
    except ImportError:
        from src.apify_shim import Actor  # type: ignore[assignment]

Or conditionally based on environment:

    import os
    if os.environ.get('APIFY_TOKEN'):
        from apify import Actor
    else:
        from src.apify_shim import Actor  # type: ignore[assignment]

The shim is also useful for local smoke testing without needing Apify credentials.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class _FakeLog:
    """Minimal logger shim matching the Actor.log interface."""

    def info(self, msg: str, *args, **kwargs) -> None:
        logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        logger.error(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        logger.exception(msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs) -> None:
        logger.debug(msg, *args, **kwargs)


class Actor:
    """No-op Apify Actor shim for non-Apify runtimes."""

    log = _FakeLog()

    @staticmethod
    async def init() -> None:
        logger.info("Apify shim: Actor.init() called (no-op)")

    @staticmethod
    async def charge(event_name: str, count: int = 1) -> None:
        logger.debug(f"Apify shim: Actor.charge({event_name!r}, {count}) (no-op)")

    @staticmethod
    async def exit(exit_code: int = 0, status_message: str = "") -> None:
        logger.info(f"Apify shim: Actor.exit({exit_code}) (no-op)")
