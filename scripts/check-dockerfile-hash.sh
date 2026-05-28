#!/usr/bin/env bash
# Dockerfile clobber guard.
# Fails with a clear message if the Dockerfile has been changed without updating
# Dockerfile.sha256. Add this as a pre-commit hook:
#
#   cp scripts/check-dockerfile-hash.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# To regenerate after an intentional Dockerfile change:
#   sha256sum Dockerfile | awk '{print $1}' > Dockerfile.sha256
set -euo pipefail

HASH_FILE="Dockerfile.sha256"
DOCKERFILE="Dockerfile"

if [[ ! -f "$HASH_FILE" ]]; then
    echo "ERROR: $HASH_FILE not found. Run: sha256sum $DOCKERFILE | awk '{print \$1}' > $HASH_FILE" >&2
    exit 1
fi

expected=$(cat "$HASH_FILE" | tr -d '[:space:]')
actual=$(sha256sum "$DOCKERFILE" | awk '{print $1}')

if [[ "$expected" != "$actual" ]]; then
    echo "ERROR: Dockerfile hash mismatch" >&2
    echo "  expected: $expected" >&2
    echo "  actual:   $actual" >&2
    echo "" >&2
    echo "If this change is intentional, regenerate the hash:" >&2
    echo "  sha256sum Dockerfile | awk '{print \$1}' > Dockerfile.sha256" >&2
    exit 1
fi

echo "Dockerfile hash OK ($actual)"
