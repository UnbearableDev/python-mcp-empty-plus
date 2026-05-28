# 08 — Troubleshooting

## `apify run` exits immediately with no output

The Actor is not configured for Standby mode. Check `actor.json`:

```json
"usesStandbyMode": true
```

## `apify run` starts but the server is not reachable

Check the port. Apify sets `APIFY_CONTAINER_PORT` — your server must bind to that port, not a hardcoded one. In `src/main.py`:

```python
port = int(os.environ.get("APIFY_CONTAINER_PORT", "3000"))
```

During local `apify run`, this defaults to 3000 and is forwarded to the same port.

## `tools/list` returns an empty list after push

The `get_server()` function in `src/server.py` is being called but returning None or not being called at all. The server entry point in `src/main.py` must call `get_server()` and pass its result to uvicorn.

Also check that `server.py` has `return server` at the end of `get_server()`. Forgetting the return is the most common mistake.

## PPE charges not flowing

1. Confirm `Actor.charge("event-name")` is called inside the tool.
2. Confirm the event name matches a key in `pay_per_event.json`.
3. Confirm the Actor is on the Apify Store with PPE pricing live (check `startedAt` — must be in the past).
4. Confirm the user's account is past their $5/month free credit threshold.

## `apify push` says build succeeded but the Actor is not responding

The build may be cached. Force a fresh build:

```bash
apify push --force-build
```

## Cold-start takes > 30 seconds on Apify cloud

The Docker image is too large. Check `pip freeze` output — are you pulling in dev dependencies? The production Actors in this fleet have images that cold-start in 5-10 seconds with only `apify`, `fastmcp`, `mcp`, and `uvicorn` installed.

## `Actor.charge()` raises `RuntimeError: Actor not initialized`

You called `Actor.charge()` before `Actor.init()` completed, or you are running without the Apify runtime (e.g. in a unit test). Use the shim:

```python
import os
if os.environ.get("APIFY_TOKEN"):
    from apify import Actor
else:
    from src.apify_shim import Actor  # type: ignore[assignment]
```

## Smoke test fails on cloud but passes locally

Usually one of:
1. Missing `APIFY_TOKEN` — set it before running the cloud smoke.
2. Build is still in progress — wait 2 minutes and retry.
3. The Actor is not public and the token belongs to a different account.
4. Cold-start timeout — run the smoke test twice; the second run should be fast.

## GitHub Actions CI failing on Dockerfile check

The `sha256sum` utility is different on macOS CI runners (`shasum -a 256`). The guard script uses `sha256sum` (Linux). If your CI runs on macOS:

```bash
# macOS-compatible alternative
shasum -a 256 Dockerfile | awk '{print $1}'
```

Or use `openssl dgst -sha256 -hex Dockerfile | awk '{print $2}'` which works on both.
