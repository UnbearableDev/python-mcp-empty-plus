"""Tests for the fix-snippet generation pattern (src/snippets.py).

These tests document the exact behaviours that DCS-037 and DFA-002 guarded
against. Keep them green — a regression here means generated fix snippets
will be semantically wrong, which is worse than returning no snippet at all.
"""

import pytest
from src.snippets import _parse_from, _strip_tag, make_fix_snippet


class TestParseFrom:
    """DCS-037: block-prefix extraction must be lossless."""

    def test_no_prefix(self):
        assert _parse_from("nginx:latest") == ""

    def test_pipe_prefix(self):
        assert _parse_from("|- value") == "|- "

    def test_pipe_no_chomp(self):
        assert _parse_from("| value") == "| "

    def test_folded_prefix(self):
        assert _parse_from("> folded text") == "> "

    def test_pipe_indent(self):
        assert _parse_from("|2 indented") == "|2 "

    def test_empty_string(self):
        assert _parse_from("") == ""


class TestStripTag:
    """DFA-002: YAML tag removal must not corrupt the value."""

    def test_no_tag(self):
        assert _strip_tag("nginx:latest") == "nginx:latest"

    def test_unsafe_tag(self):
        assert _strip_tag("!unsafe nginx:latest") == "nginx:latest"

    def test_bang_str_tag(self):
        assert _strip_tag("!!str 42") == "42"

    def test_ruby_object_tag(self):
        assert _strip_tag("!ruby/object:Foo bar") == "bar"

    def test_empty_string(self):
        assert _strip_tag("") == ""


class TestMakeFixSnippet:
    """Integration: make_fix_snippet must produce valid YAML key-value output."""

    def test_simple(self):
        assert make_fix_snippet("image", "nginx:1.27.0") == "image: nginx:1.27.0"

    def test_preserves_block_prefix(self):
        # DCS-037: block prefix must survive round-trip
        result = make_fix_snippet("command", "|- echo hello")
        assert result == "command: |- echo hello"

    def test_strips_unsafe_tag(self):
        # DFA-002: tag must be stripped before output
        result = make_fix_snippet("image", "!unsafe nginx:latest")
        assert result == "image: nginx:latest"

    def test_strips_tag_not_value(self):
        # DFA-002: only the tag prefix is removed, not the value itself
        result = make_fix_snippet("image", "!!str my-image:1.0")
        assert result == "image: my-image:1.0"
        assert "!!str" not in result

    def test_empty_value(self):
        result = make_fix_snippet("key", "")
        assert result == "key: "
