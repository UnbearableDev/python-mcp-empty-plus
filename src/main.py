"""MCP server entry point for Apify Standby mode.

This module:
1. Calls Actor.init() to register with the Apify platform.
2. Starts a uvicorn HTTP server on the port Apify expects.
3. Wires the FastMCP app (from server.py) into the HTTP server.
4. Handles graceful shutdown on SIGINT.

You should not need to edit this file. Put your domain logic in server.py.
"""

from __future__ import annotations
from src import mcp_patch  # noqa: F401  # patches -32602 -> -32601 for unknown methods

import asyncio
import os

import uvicorn
from apify import Actor
from fastmcp import FastMCP

from src.server import get_server


async def main() -> None:
    await Actor.init()

    port = int(os.environ.get("APIFY_CONTAINER_PORT", "3000"))
    timeout_secs = int(os.environ.get("SESSION_TIMEOUT_SECS", "300"))

    server: FastMCP = get_server()
    app = server.http_app(transport="streamable-http")

    try:
        Actor.log.info(f"Starting MCP server on port {port}")
        config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")  # noqa: S104
        await uvicorn.Server(config).serve()
    except KeyboardInterrupt:
        Actor.log.info("Shutting down...")
    except Exception as e:
        Actor.log.error(f"Server failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
