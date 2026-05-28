# 05 — Standby URL Pattern

## URL format

```
https://<username-hyphenated>--<actor-slug>.apify.actor/<path>
```

Underscores in the Apify username become hyphens in the DNS hostname. Actor slug uses the slug from `actor.json`.

Examples:

| Apify username | Actor slug | Standby URL |
|----------------|-----------|-------------|
| `unbearable_dev` | `docker-compose-audit` | `https://unbearable-dev--docker-compose-audit.apify.actor/mcp` |
| `my_company` | `my-audit-tool` | `https://my-company--my-audit-tool.apify.actor/mcp` |

## MCP endpoint

The MCP server listens at `/mcp`. This is configured in `actor.json`:

```json
"webServerMcpPath": "/mcp"
```

To call a tool:

```bash
curl -X POST https://unbearable-dev--your-actor.apify.actor/mcp \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## Bearer token

All Standby calls require a Bearer token. Get yours from `https://console.apify.com/account/integrations`. Every user must supply their own token when they connect their MCP client.

In Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "your-actor": {
      "command": "npx",
      "args": ["-y", "@apify/actor-mcp-wrapper@latest", "--actor-url", "https://unbearable-dev--your-actor.apify.actor/mcp"],
      "env": {
        "APIFY_TOKEN": "your_apify_token_here"
      }
    }
  }
}
```

## Cold-start latency

The first request to a Standby Actor that has been idle wakes the container. Typical cold-start is 5-15 seconds. Subsequent requests within the same session are fast. The MCP initialize handshake is the natural cold-start warm-up — no special handling needed.

## Local development URL

During `apify run`, the server listens on:

```
http://localhost:3000/mcp
```

No token required locally. The `tests/smoke.sh` script defaults to this URL.
