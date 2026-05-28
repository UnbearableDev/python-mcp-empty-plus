# Smithery catalog submission

This is how Unbearable Labs listed 7 Actors on Smithery in one session. Follow these steps for every new Actor.

## Background: why you need the gateway parameter

Apify Standby URLs require `Authorization: Bearer <token>`. Smithery cannot auto-negotiate this auth during publish. Smithery's solution is its gateway proxy (`*.run.tools`) — it accepts a user-supplied token in the UI and injects it as `?token=<value>` on every request to your Actor. Your `main.py` must accept auth from either the `Authorization` header (direct calls) or the `?token=` query param (Smithery gateway calls).

This dual-config-path pattern is already wired in the scaffold's `src/main.py`.

## Step 1 — Publish via CLI (~30 seconds)

From `noelpi`:

```bash
smithery mcp publish \
  'https://unbearable-dev--<actor>.apify.actor/mcp' \
  -n 'unbearabledev/<actor>' \
  --config-schema /home/noelpi/apify/<actor>/smithery.yaml
```

If DNS hangs, add `104.21.6.248  api.smithery.ai` to `/etc/hosts` on the Pi first (IPv6 resolution for this host times out on some networks).

The `smithery.yaml` in this scaffold already includes the `token` config parameter stub — update the description to match your Actor's pricing.

## Step 2 — Configure gateway and publish (~3 min per Actor in web UI)

1. Open `https://smithery.ai/servers/unbearabledev/<actor>/releases`
2. Click the latest release row
3. In the "Configure" section, add parameter:
   - Name: `token` | Type: `string` | Location: `query` | Required: ON
   - Description: `Your Apify API token from console.apify.com → Settings → Integrations → API tokens.`
4. Click "Connect" — Smithery will test the gateway connection to your Actor
5. Click "Publish" to make this release active
6. On the server overview page: "Change visibility" → Public

## Step 3 — Verify

```bash
curl -sS -o /dev/null -w '%{http_code}\n' \
  https://smithery.ai/servers/unbearabledev/<actor>
# Expect: 200
```

## smithery.yaml stub (already in this scaffold)

```yaml
startCommand:
  type: url
  url: https://unbearable-dev--<actor>.apify.actor/mcp

config:
  token:
    type: string
    description: "Your Apify API token. Get it from console.apify.com → Settings → Integrations → API tokens."
    required: true
```

Update `url` and `description` before publishing. Do not change `name: token` or `location: query` — those must match what `main.py` reads.

See decision note: `02-Decisions/2026-05-28 Smithery distribution via gateway parameter pattern.md` in the Unbearable Labs vault for full context on the four dead paths investigated and why this approach works.
