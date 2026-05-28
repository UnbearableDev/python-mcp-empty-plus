[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Apify Actor](https://img.shields.io/badge/runs%20on-Apify%20Actor%20Store-00BFA5)](https://apify.com/unbearable_dev?utm_source=github-scaffold&utm_medium=readme)
[![6 production Actors](https://img.shields.io/badge/production%20Actors-6-success)](https://github.com/UnbearableDev)

# python-mcp-empty-plus

**A production-hardened Python scaffold for building MCP servers on Apify.**

This is the same scaffold we used at Unbearable Labs to ship 6 production MCP Actors on the Apify Store. It starts where Apify's official `python-mcp-empty` template stops: add a Dockerfile clobber guard, a smoke-test harness, and the check-registry pattern that makes audit-style Actors composable. Clone it, fill in your domain logic, push to Apify.

Zero recurring API spend. Apify pay-per-event means your Actor sleeps when idle and charges only on calls. No idle $5-20/month VPS. No platform lock-in beyond the hosting layer.

---

## What this adds over the base template

### 1. Dockerfile clobber guard

`Dockerfile.sha256` + `scripts/check-dockerfile-hash.sh` + pre-commit hook. Any commit that overwrites `Dockerfile` without updating the hash fails immediately with a clear error. When an AI agent is editing files in your repo, this saves your build.

```
ERROR: Dockerfile hash mismatch
  expected: a3833afb...
  actual:   7f4b92c1...

If this change is intentional, regenerate the hash:
  sha256sum Dockerfile | awk '{print $1}' > Dockerfile.sha256
```

Wired as a pre-commit hook in `.pre-commit-config.yaml`. Manual setup: copy `scripts/check-dockerfile-hash.sh` to `.git/hooks/pre-commit` and `chmod +x` it. See [docs/07-dockerfile-clobber-guard.md](docs/07-dockerfile-clobber-guard.md).

### 2. Smoke-test harness

`tests/smoke.sh` exercises MCP protocol negotiation + `tools/list` + a representative tool call against the running server. Exits 0 on green, 1 on any failure. Works against both `apify run` (local) and the Apify Standby URL (cloud).

```bash
apify run &
./tests/smoke.sh                           # local
APIFY_TOKEN=... ./tests/smoke.sh https://unbearable-dev--your-actor.apify.actor  # cloud
```

See [docs/06-smoke-testing.md](docs/06-smoke-testing.md).

### 3. Fix-snippet generation pattern

`src/snippets.py` documents the `_parse_from` / `_strip_tag` / `make_fix_snippet` pattern from two production bugs (DCS-037 and DFA-002) that caused generated YAML fix snippets to be semantically wrong. The module is annotated with the lessons and `tests/test_snippets.py` pins them as regression tests.

For audit-style Actors only — skip this if you're building a data-query MCP.

See [docs/03-fix-snippet-generation.md](docs/03-fix-snippet-generation.md).

---

## 60-second quickstart

```bash
git clone https://github.com/UnbearableDev/python-mcp-empty-plus my-mcp-server
cd my-mcp-server

# Wire the Dockerfile clobber guard
cp scripts/check-dockerfile-hash.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Install dependencies and run locally
pip install -r requirements.txt
apify run

# In a second terminal, smoke-test
./tests/smoke.sh
```

Expected output:

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

Then replace the `hello_world` tool in `src/server.py` with your domain logic, and `apify push` when ready.

---

## What's in the box

```
python-mcp-empty-plus/
├── README.md
├── LICENSE                        # MIT
├── .gitignore
├── Dockerfile                     # apify/actor-python:3.14 base
├── Dockerfile.sha256              # pinned hash for clobber guard
├── .pre-commit-config.yaml        # wires the guard for pre-commit framework users
├── actor.json                     # Apify Actor spec — update name/title/description
├── pay_per_event.json             # PPE pricing with inline comments explaining economics
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py                    # uvicorn entry point for Apify Standby mode
│   ├── apify_shim.py              # no-op Actor shim for local / self-hosted use
│   ├── server.py                  # FastMCP server factory — put your logic here
│   └── snippets.py                # fix-snippet pattern with DCS-037/DFA-002 lessons
├── tests/
│   ├── smoke.sh                   # MCP protocol + tools/list + tools/call smoke test
│   └── test_snippets.py           # pytest covering the snippet pattern regression cases
├── scripts/
│   └── check-dockerfile-hash.sh   # Dockerfile clobber guard script
└── docs/
    ├── 01-quickstart.md
    ├── 02-check-catalog-pattern.md
    ├── 03-fix-snippet-generation.md
    ├── 04-apify-ppe-economics.md
    ├── 05-standby-url-pattern.md
    ├── 06-smoke-testing.md
    ├── 07-dockerfile-clobber-guard.md
    └── 08-troubleshooting.md
```

---

## PPE pricing

Configure in `pay_per_event.json`. The scaffold ships with two event types:

| Event | Price | Use for |
|-------|-------|---------|
| `light-read` | $0.005 | Catalog / list / lookup calls |
| `heavy-call` | $0.02 | Analysis / audit / generation calls |

Every Apify user gets $5/month in free credits = 250 heavy calls before the first paid dollar. Price for teams, not hobbyists. See [docs/04-apify-ppe-economics.md](docs/04-apify-ppe-economics.md) for the full economics and the `startedAt` gotcha that catches every first-time publisher.

---

## Standby URL pattern

```
https://<username-hyphenated>--<actor-slug>.apify.actor/mcp
```

Underscores in the Apify username become hyphens in the DNS hostname. All calls require a Bearer token. See [docs/05-standby-url-pattern.md](docs/05-standby-url-pattern.md) for MCP client configuration examples.

---

## Production Actors built with this scaffold

These are live on the Apify Store. Clone any of them to see the full pattern in production.

| Actor | What it does | Apify Store |
|-------|-------------|-------------|
| [docker-compose-audit](https://github.com/UnbearableDev/docker-compose-audit) | 25 checks, 9 security categories | [unbearable_dev/docker-compose-audit](https://apify.com/unbearable_dev/docker-compose-audit) |
| [dockerfile-audit](https://github.com/UnbearableDev/dockerfile-audit) | 19 checks, 5 categories | [unbearable_dev/dockerfile-audit](https://apify.com/unbearable_dev/dockerfile-audit) |
| [github-actions-audit](https://github.com/UnbearableDev/github-actions-audit) | 21 checks including supply-chain extension | [unbearable_dev/github-actions-audit](https://apify.com/unbearable_dev/github-actions-audit) |
| [k8s-manifest-audit](https://github.com/UnbearableDev/k8s-manifest-audit) | 63 kube-linter checks, 7 categories | [unbearable_dev/k8s-manifest-audit](https://apify.com/unbearable_dev/k8s-manifest-audit) |
| [iac-audit-pack](https://github.com/UnbearableDev/iac-audit-pack) | 4-domain bundle (Compose + Dockerfile + GHA + k8s) | [unbearable_dev/iac-audit-pack](https://apify.com/unbearable_dev/iac-audit-pack) |
| [hu-postcode-validator](https://github.com/UnbearableDev/hu-postcode-validator) | 3,484 HU postcodes validated in <10ms | [unbearable_dev/hu-postcode-validator](https://apify.com/unbearable_dev/hu-postcode-validator) |

---

## Want the deeper version?

This free scaffold gives you the pattern. The **MCP Server Boilerplate Pack** (coming soon) adds:

- 8 annotated docs covering every production lesson
- A complete example Actor (`markdown-linter-mcp`) you can study end-to-end
- The self-hosted multiplexer pattern for running multiple Actors behind a single MCP endpoint
- Check-catalog framework with the full registry implementation

Get notified when it ships: [subscribe to the Unbearable TechTips newsletter](https://unbearabletechtips.beehiiv.com).

---

## Changelog

### 2026-05-28
- Added `src/mcp_patch.py`: monkey-patches `mcp.shared.session.INVALID_PARAMS` to `METHOD_NOT_FOUND` (`-32601`) at startup. Fixes Smithery capability-probe warning: the mcp SDK emits `-32602` (Invalid Params) for unknown methods like `triggers/list` instead of the correct `-32601` (Method Not Found) per JSON-RPC 2.0 spec.

---

Built by Noel @ Unbearable Labs — get the weekly newsletter at https://unbearabletechtips.beehiiv.com
