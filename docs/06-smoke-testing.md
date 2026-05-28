# 06 — Smoke Testing

## The smoke test

`tests/smoke.sh` exercises the four things that can silently break after a push:

1. HTTP reachability — the server is up and responding.
2. MCP initialize handshake — the protocol negotiation succeeds.
3. tools/list — FastMCP is wired correctly and advertises tools.
4. tools/call — the first tool executes and returns content.

Exit code 0 = all checks passed. Exit code 1 = at least one failure.

## Local smoke (after `apify run`)

```bash
# In terminal 1
apify run

# In terminal 2
./tests/smoke.sh

# Expected output:
# MCP smoke test — http://localhost:3000/mcp
# ─────────────────────────────────────────
#   PASS  HTTP reachable (expected 200)
#   PASS  Initialize returned serverInfo.name
#   PASS  tools/list returns >= 1 tool (got 1)
#   PASS  tools/call 'hello_world' returns content
# ─────────────────────────────────────────
# All 4 checks passed.
```

## Cloud smoke (after `apify push`)

```bash
APIFY_TOKEN=your_token ./tests/smoke.sh https://unbearable-dev--your-actor.apify.actor
```

The first run may be slow (cold-start). If it times out, run it again. If it fails twice, check `apify run` locally first.

## Common failures

**`tools/list` returns 0 tools**

FastMCP did not return the server from `get_server()`. Check `src/server.py`:

```python
def get_server() -> FastMCP:
    server = FastMCP("your-actor-name", "0.1.0")
    # ... add tools ...
    return server   # <-- must return the server
```

A common mistake is calling `server.run()` instead of returning the server. This works for stdio transport but breaks Standby mode.

**HTTP 401 on cloud smoke**

The Bearer token is missing or wrong. Set `APIFY_TOKEN` in the environment before running the smoke test.

**HTTP 503 on cloud smoke**

The Actor build failed or hasn't finished. Check the build log in the Apify Console.

**`tools/call` returns `isError: true`**

The tool raised an exception. Check the Actor log in the Apify Console (`apify actor logs`).

## Python MCP smoke test (alternative)

For deeper testing, the `mcp` Python client gives you structured responses:

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def smoke():
    async with streamablehttp_client("http://localhost:3000/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            init = await s.initialize()
            print(f"Server: {init.serverInfo.name}")
            tools = await s.list_tools()
            print(f"Tools: {[t.name for t in tools.tools]}")

asyncio.run(smoke())
```

See `mcp_http_smoke.py` in [UnbearableDev/docker-compose-audit](https://github.com/UnbearableDev/docker-compose-audit) for a full example.
