#!/usr/bin/env bash
# MCP protocol smoke test.
#
# Usage:
#   ./tests/smoke.sh                          # local apify run (default port 3000)
#   ./tests/smoke.sh http://localhost:3000    # explicit local URL
#   APIFY_TOKEN=your_token ./tests/smoke.sh https://unbearable-dev--your-actor.apify.actor
#
# Exit codes:
#   0 = all checks passed
#   1 = one or more checks failed
#
# The test exercises:
#   1. HTTP reachability (curl to /mcp)
#   2. MCP initialize handshake (JSON-RPC 2.0)
#   3. tools/list returns at least one tool
#   4. tools/call on the first advertised tool

set -euo pipefail

BASE_URL="${1:-http://localhost:3000}"
MCP_URL="$BASE_URL/mcp"
SESSION_ID="smoke-$$"
PASS=0
FAIL=0

green() { printf '\033[0;32m%s\033[0m\n' "$1"; }
red()   { printf '\033[0;31m%s\033[0m\n' "$1"; }
check() {
    local label="$1" result="$2"
    if [[ "$result" == "ok" ]]; then
        green "  PASS  $label"
        PASS=$((PASS+1))
    else
        red   "  FAIL  $label ($result)"
        FAIL=$((FAIL+1))
    fi
}

echo ""
echo "MCP smoke test — $MCP_URL"
echo "─────────────────────────────────────────"

# 1. Reachability
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$MCP_URL" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    ${APIFY_TOKEN:+-H "Authorization: Bearer $APIFY_TOKEN"} \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0.1"}}}' \
    2>/dev/null)
check "HTTP reachable (expected 200)" "$([[ "$STATUS" == "200" ]] && echo ok || echo "got HTTP $STATUS")"

# 2. Initialize + parse session ID
INIT_RESPONSE=$(curl -s -D - \
    -X POST "$MCP_URL" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    ${APIFY_TOKEN:+-H "Authorization: Bearer $APIFY_TOKEN"} \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0.1"}}}' \
    2>/dev/null)

# Extract session ID from headers
SESSION_ID=$(echo "$INIT_RESPONSE" | grep -i 'mcp-session-id' | awk '{print $2}' | tr -d '\r' || true)
INIT_BODY=$(echo "$INIT_RESPONSE" | sed '1,/^\r$/d')

SERVER_NAME=$(echo "$INIT_BODY" | python3 -c "import sys,json; d=json.loads(sys.stdin.read().split('data: ')[-1]); print(d.get('result',{}).get('serverInfo',{}).get('name',''))" 2>/dev/null || true)
check "Initialize returned serverInfo.name" "$([[ -n "$SERVER_NAME" ]] && echo ok || echo "no serverInfo.name in response")"

# 3. tools/list
TOOLS_RESPONSE=$(curl -s \
    -X POST "$MCP_URL" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    ${SESSION_ID:+-H "mcp-session-id: $SESSION_ID"} \
    ${APIFY_TOKEN:+-H "Authorization: Bearer $APIFY_TOKEN"} \
    -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
    2>/dev/null)

TOOL_COUNT=$(echo "$TOOLS_RESPONSE" | python3 -c "
import sys,json
raw = sys.stdin.read()
# handle SSE envelope
body = raw.split('data: ')[-1].strip()
try:
    d = json.loads(body)
    tools = d.get('result',{}).get('tools',[])
    print(len(tools))
except Exception:
    print(0)
" 2>/dev/null || echo "0")
check "tools/list returns >= 1 tool (got $TOOL_COUNT)" "$([[ "$TOOL_COUNT" -ge 1 ]] && echo ok || echo "got $TOOL_COUNT tools")"

FIRST_TOOL=$(echo "$TOOLS_RESPONSE" | python3 -c "
import sys,json
raw = sys.stdin.read()
body = raw.split('data: ')[-1].strip()
try:
    d = json.loads(body)
    tools = d.get('result',{}).get('tools',[])
    print(tools[0]['name'] if tools else '')
except Exception:
    print('')
" 2>/dev/null || true)

# 4. tools/call on first tool
if [[ -n "$FIRST_TOOL" ]]; then
    CALL_RESPONSE=$(curl -s \
        -X POST "$MCP_URL" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json, text/event-stream" \
        ${SESSION_ID:+-H "mcp-session-id: $SESSION_ID"} \
        ${APIFY_TOKEN:+-H "Authorization: Bearer $APIFY_TOKEN"} \
        -d "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/call\",\"params\":{\"name\":\"$FIRST_TOOL\",\"arguments\":{}}}" \
        2>/dev/null)
    HAS_CONTENT=$(echo "$CALL_RESPONSE" | python3 -c "
import sys,json
raw = sys.stdin.read()
body = raw.split('data: ')[-1].strip()
try:
    d = json.loads(body)
    content = d.get('result',{}).get('content',[])
    print('ok' if content else 'empty')
except Exception:
    print('parse-error')
" 2>/dev/null || echo "parse-error")
    check "tools/call '$FIRST_TOOL' returns content" "$HAS_CONTENT"
fi

echo "─────────────────────────────────────────"
if [[ "$FAIL" -eq 0 ]]; then
    green "All $PASS checks passed."
    exit 0
else
    red "$FAIL/$((PASS+FAIL)) checks FAILED."
    exit 1
fi
