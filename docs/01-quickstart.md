# 01 — Quickstart

## Prerequisites

- [Apify CLI](https://docs.apify.com/cli/) (`npm install -g apify-cli`)
- Python 3.11+
- An [Apify account](https://apify.com/sign-up) (free tier is enough)

## Steps

```bash
# 1. Clone the scaffold
git clone https://github.com/UnbearableDev/python-mcp-empty-plus my-mcp-server
cd my-mcp-server

# 2. Install pre-commit hooks (Dockerfile guard)
cp scripts/check-dockerfile-hash.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 3. Install Python dependencies locally
pip install -r requirements.txt

# 4. Run locally — Apify CLI starts the server on port 3000
apify run

# In a second terminal, smoke-test the running server
./tests/smoke.sh http://localhost:3000

# 5. When ready to ship, push to Apify cloud
apify login
apify push

# 6. Smoke-test the cloud deployment
APIFY_TOKEN=your_token ./tests/smoke.sh https://unbearable-dev--your-actor.apify.actor
```

## What you should see

After `apify run`, the smoke test should print:

```
MCP smoke test — http://localhost:3000/mcp
─────────────────────────────────────────
  PASS  HTTP reachable (expected 200)
  PASS  Initialize returned serverInfo.name
  PASS  tools/list returns >= 1 tool (got 1)
  PASS  tools/call 'hello_world' returns content
─────────────────────────────────────────
All 4 checks passed.
```

## Next steps

1. Replace `hello_world` in `src/server.py` with your domain logic.
2. Update `actor.json` with your Actor name and description.
3. Set PPE pricing in `pay_per_event.json` — see [04-apify-ppe-economics.md](04-apify-ppe-economics.md).
4. Run `apify push` when ready. See [06-smoke-testing.md](06-smoke-testing.md) for cloud smoke.
