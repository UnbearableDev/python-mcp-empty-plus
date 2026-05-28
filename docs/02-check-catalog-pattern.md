# 02 — Check-Catalog Pattern

The check-catalog pattern is how all production Unbearable TechTips audit Actors expose their logic. It separates concerns cleanly:

- **Finding** (dataclass) — the output of one check on one input.
- **Check function** — pure function that takes a parsed document and yields Findings.
- **Registry** — maps category names to lists of check functions.
- **`list_checks` MCP tool** — reads metadata from the registry to return a browsable catalog without running any checks.

## When to use this pattern

Use it when your Actor is audit-style: given an input artifact, return a list of typed findings with severity, description, and remediation. If your Actor is data-query style (e.g. a database lookup), skip the registry and write tool functions directly in `server.py`.

## Minimal implementation

```python
# src/findings.py
from dataclasses import dataclass, field
from typing import Literal

Severity = Literal["high", "medium", "low", "info"]

@dataclass
class Finding:
    id: str           # e.g. "EX-001"
    category: str     # e.g. "security"
    severity: Severity
    title: str
    description: str
    remediation: str
    fix_snippet: str | None = None

def check_meta(*, id: str, severity: Severity, title: str):
    """Decorator attaching catalog metadata to a check function."""
    def decorator(fn):
        fn.__check_meta__ = {"id": id, "severity": severity, "title": title}
        return fn
    return decorator
```

```python
# src/checks/example.py
from src.findings import Finding, check_meta

CATEGORY = "example"

@check_meta(id="EX-001", severity="medium", title="Example check")
def check_something(doc) -> list[Finding]:
    if some_condition(doc):
        return [Finding(
            id="EX-001", category=CATEGORY, severity="medium",
            title="Example check", description="...", remediation="...",
        )]
    return []

CHECKS = [check_something]
```

```python
# src/registry.py
from src.checks import example

CATEGORY_REGISTRY = {"example": example.CHECKS}
ALL_CATEGORIES = list(CATEGORY_REGISTRY.keys())

def catalog() -> list[dict]:
    entries = []
    for category, checks in CATEGORY_REGISTRY.items():
        for check in checks:
            meta = getattr(check, "__check_meta__", None)
            if meta:
                entries.append({**meta, "category": category})
    return sorted(entries, key=lambda e: e["id"])
```

## Adding a `list_checks` tool

```python
@server.tool(annotations=_ANNOTATIONS)
async def list_checks(category: str | None = None) -> dict:
    """List the full catalog of available checks."""
    await Actor.charge("light-read")
    items = catalog()
    if category:
        items = [c for c in items if c["category"] == category]
    return {
        "type": "text",
        "text": f"{len(items)} checks ({len(ALL_CATEGORIES)} categories).",
        "structuredContent": {"categories": ALL_CATEGORIES, "checks": items},
    }
```

See the production implementation in [UnbearableDev/docker-compose-audit](https://github.com/UnbearableDev/docker-compose-audit).
