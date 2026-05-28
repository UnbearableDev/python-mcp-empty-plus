"""Monkey-patch mcp.shared.session to return -32601 (Method Not Found)
instead of -32602 (Invalid Params) for unknown JSON-RPC methods.

Root cause: mcp SDK validation of an unknown method like triggers/list
fails Pydantic parsing and the except block emits INVALID_PARAMS (-32602).
Per JSON-RPC 2.0 spec, -32601 (Method Not Found) is correct for methods
that the server does not recognise — e.g. triggers/list, roots/list.

Smithery's capability probe sends these unimplemented-method calls during
catalog indexing and logs a warning when it receives -32602. This patch
silences the warning by returning the correct code.

Import this module at the top of main.py (after from __future__ imports,
before any other imports that trigger mcp initialisation).
"""
from __future__ import annotations

import mcp.shared.session as _sess
import mcp.types as _types

# Replace the INVALID_PARAMS name in the mcp.shared.session module namespace.
# The except block in BaseSession._receive_loop references INVALID_PARAMS by
# name from its module dict at call time — overwriting it here changes what
# the handler sees for all subsequent invocations.
_sess.INVALID_PARAMS = _types.METHOD_NOT_FOUND
