"""MCP server factory.

Replace the placeholder tool with your domain logic.
The get_server() function is the contract — main.py calls it,
and the multiplexer shim imports it directly for self-hosted use.
"""

from __future__ import annotations

import os

from fastmcp import FastMCP

# Import the real Apify SDK if available; fall back to the no-op shim.
# This lets the server run both inside Apify and locally / in the
# unbearable-mcp self-hosted multiplexer without code changes.
if os.environ.get("APIFY_TOKEN"):
    from apify import Actor  # type: ignore[import]
else:
    from src.apify_shim import Actor  # type: ignore[assignment]

_ANNOTATIONS = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}


def get_server() -> FastMCP:
    """Create and return the FastMCP server instance.

    This function is the single contract point:
    - main.py calls it to get the server for Apify Standby hosting.
    - The self-hosted multiplexer imports it directly.
    - Tests call it to get a server instance without starting uvicorn.

    Steps to add your own tools:
    1. Define async functions decorated with @server.tool(annotations=_ANNOTATIONS).
    2. Call Actor.charge('event-name') inside each tool (maps to pay_per_event.json).
    3. Return a dict with at minimum 'text' (str) and optionally 'structuredContent' (dict).
    """
    server = FastMCP("your-actor-name", "0.1.0")

    @server.tool(annotations=_ANNOTATIONS)
    async def hello_world(name: str = "world") -> dict:
        """A placeholder tool. Replace this with your domain logic.

        Args:
            name: Who to greet.

        Returns a greeting. In a real Actor this is where you'd call
        Actor.charge('heavy-call') and return your analysis results.
        """
        # Charge the 'light-read' PPE event defined in pay_per_event.json.
        # Comment this out until your Actor is live on Apify Store.
        # await Actor.charge('light-read')

        return {
            "type": "text",
            "text": f"Hello, {name}! This scaffold is working.",
            "structuredContent": {
                "greeting": f"Hello, {name}!",
                "scaffold_version": "0.1.0",
            },
        }

    return server
