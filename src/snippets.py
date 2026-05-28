"""Fix-snippet generation pattern — annotated example.

This module shows the pattern used across all production Unbearable TechTips
audit Actors for generating actionable fix snippets alongside findings.

Two production bugs (DCS-037 and DFA-002) shaped this pattern. Read the
lessons below before writing your own snippet generators.

---

LESSON 1: Preserve the prefix (from DCS-037)
=============================================

DCS-037 surfaced when the docker-compose-audit Actor was incorrectly stripping
block-style YAML prefixes (e.g. "|- " or "|2 " from multi-line strings) when
generating fix_yaml_snippet fields. The stripped prefix changed the semantic
meaning of the generated YAML — what looked like a valid fix was actually
broken YAML that Docker Compose would reject.

The pattern: ALWAYS extract and re-apply the original prefix when round-tripping
a value through your snippet generator.

    BEFORE (buggy):
        def make_snippet(key, value):
            return f"{key}: {value.strip()}"   # strips leading whitespace/prefix

    AFTER (correct):
        def make_snippet(key, raw_value):
            prefix = _parse_from(raw_value)    # extract "|- ", "|2 ", etc.
            clean = _strip_tag(raw_value)      # remove tag, preserve value
            return f"{key}: {prefix}{clean}"   # re-apply prefix

---

LESSON 2: Strip the YAML tag, not the value (from DFA-002)
===========================================================

DFA-002 surfaced in the dockerfile-audit Actor when generating FROM-line fix
snippets. The fix generator was passing the full raw node representation
(including the !unsafe YAML tag prefix) into the output snippet, producing
snippets like:

    FROM !unsafe apify/actor-python:3.14

instead of:

    FROM apify/actor-python:3.14

The pattern: strip the YAML tag (anything matching /^![a-z]+\s+/) separately
from stripping the block prefix. These are two different transformations.

---

EXAMPLE IMPLEMENTATION
=======================

Neither lesson requires a complex library. Here is the minimal correct pattern:
"""

from __future__ import annotations

import re

# Matches YAML block-scalar prefixes like "|- ", "|2 ", "| ", "> "
_BLOCK_PREFIX_RE = re.compile(r'^(?:\|-?|>-?|\|[0-9]+)\s*')

# Matches YAML tags like "!unsafe ", "!ruby/object:", "!!str "
_YAML_TAG_RE = re.compile(r'^![a-zA-Z/]+\s+')


def _parse_from(raw_value: str) -> str:
    """Extract the block-scalar prefix from a raw YAML value string.

    Returns the prefix (e.g. "|- ", "|2 ") or empty string if none.

    This is the function DCS-037 was missing.
    """
    match = _BLOCK_PREFIX_RE.match(raw_value)
    return match.group(0) if match else ""


def _strip_tag(raw_value: str) -> str:
    """Remove a YAML tag from the start of a raw value string.

    Returns the value with the tag prefix removed.

    This is the transformation DFA-002 was missing.
    """
    return _YAML_TAG_RE.sub("", raw_value)


def make_fix_snippet(key: str, raw_value: str) -> str:
    """Generate a valid YAML fix snippet for a single key-value pair.

    Preserves the original block-scalar prefix (DCS-037 lesson) and
    strips any YAML tag (DFA-002 lesson).

    Args:
        key: The YAML key (e.g. "image", "command", "entrypoint").
        raw_value: The raw value string from the parsed YAML node.

    Returns:
        A YAML snippet string safe to include in a fix_snippet field.

    Example:
        >>> make_fix_snippet("image", "nginx:latest")
        'image: nginx:latest'

        >>> make_fix_snippet("command", "|- echo hello")
        'command: |- echo hello'

        >>> make_fix_snippet("image", "!unsafe nginx:latest")
        'image: nginx:latest'
    """
    # Step 1: Extract block prefix (DCS-037)
    prefix = _parse_from(raw_value)

    # Step 2: Strip YAML tag if present (DFA-002)
    clean = _strip_tag(raw_value)

    return f"{key}: {prefix}{clean}"


# ── Example check using the pattern ──────────────────────────────────────────
#
# This is how a real check function uses make_fix_snippet. Uncomment and
# adapt for your domain. The check_meta decorator attaches catalog metadata
# that the CheckRegistry uses to build the tools/list response.
#
# from dataclasses import dataclass, field
# from typing import Literal
#
# Severity = Literal["high", "medium", "low", "info"]
#
# @dataclass
# class Finding:
#     id: str
#     category: str
#     severity: Severity
#     title: str
#     description: str
#     remediation: str
#     fix_snippet: str | None = None
#
#
# EXAMPLE_CHECK_ID = "EXAMPLE-001"
#
# def check_example(doc) -> list[Finding]:
#     """Example check: flags any 'image: latest' usage in a compose file."""
#     findings = []
#     for service_name, service in doc.items():
#         raw_image = service.get("image", "")
#         if str(raw_image).endswith(":latest") or ":" not in str(raw_image):
#             findings.append(Finding(
#                 id=EXAMPLE_CHECK_ID,
#                 category="image_hygiene",
#                 severity="medium",
#                 title="Unpinned image tag",
#                 description=f"Service '{service_name}' uses an unpinned image tag.",
#                 remediation="Pin to a specific digest: image: nginx@sha256:<digest>",
#                 fix_snippet=make_fix_snippet("image", "nginx:1.27.0"),
#             ))
#     return findings
