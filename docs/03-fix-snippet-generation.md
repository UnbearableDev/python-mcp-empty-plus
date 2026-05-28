# 03 — Fix-Snippet Generation

A fix snippet is the YAML (or code) fragment that an AI agent can apply directly to resolve a finding. It is the feature that separates an audit MCP from a linter — the agent doesn't have to figure out the fix, it receives it verbatim.

Two production bugs shaped the pattern in `src/snippets.py`. Read these before writing your own snippet generators.

## DCS-037 — Preserve the block-scalar prefix

**What happened:** `docker-compose-audit` was stripping YAML block-scalar prefixes (`|-`, `|2`, `>`) when constructing fix snippets. The generated snippet looked like valid YAML but changed the semantic meaning of multi-line strings. Docker Compose would accept the syntax but interpret the value differently.

**The pattern:**

```python
def make_snippet(key: str, raw_value: str) -> str:
    prefix = _parse_from(raw_value)   # extract "|- ", "|2 ", etc.
    clean  = _strip_tag(raw_value)    # remove YAML tag if present
    return f"{key}: {prefix}{clean}"  # re-apply prefix
```

The `_parse_from` function must run before any string manipulation. Never call `.strip()` on a raw YAML value before extracting the prefix.

## DFA-002 — Strip the YAML tag, not the value

**What happened:** `dockerfile-audit` was passing raw YAML node representations directly into fix snippet fields. Some nodes carried `!unsafe` tags (from the PyYAML `yaml.unsafe_load` path). The output was:

```yaml
FROM !unsafe apify/actor-python:3.14
```

instead of:

```yaml
FROM apify/actor-python:3.14
```

**The pattern:**

```python
_YAML_TAG_RE = re.compile(r'^![a-zA-Z/]+\s+')

def _strip_tag(raw_value: str) -> str:
    return _YAML_TAG_RE.sub("", raw_value)
```

Apply `_strip_tag` on every value before using it in a snippet. Never pass a raw PyYAML node string to output.

## Implementation

`src/snippets.py` contains the full implementation with docstrings and an example check. `tests/test_snippets.py` pins both bug classes with regression tests. Keep those tests green.

## When fix snippets are not worth it

Fix snippets add value only when:
1. The fix is mechanical (a specific value to set, not "review your architecture").
2. The snippet can be generated deterministically from the finding data.
3. The snippet is short enough to be useful in a tool response (< 20 lines).

For architectural findings (e.g. "separate your web tier from your database tier"), skip the fix snippet and write a good `remediation` string instead.
