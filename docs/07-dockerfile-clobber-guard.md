# 07 — Dockerfile Clobber Guard

## The problem

When an AI agent is editing files in an Actor repo, it can accidentally write to `Dockerfile` instead of its intended target. This happened during the development of multiple production Actors in the Unbearable TechTips fleet. The Dockerfile was overwritten silently, the change was committed, and the next `apify push` produced a broken build.

The fix is a pre-commit hook that fails loudly if the committed Dockerfile hash diverges from the pinned hash in `Dockerfile.sha256`.

## Setup

```bash
cp scripts/check-dockerfile-hash.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

From then on, any commit that modifies `Dockerfile` without updating `Dockerfile.sha256` will fail:

```
ERROR: Dockerfile hash mismatch
  expected: a3833afb165538a3caf7c0dde0aee9ad81a5bb1a39dd8b7b3b9970a82a66be9f
  actual:   7f4b92c1...

If this change is intentional, regenerate the hash:
  sha256sum Dockerfile | awk '{print $1}' > Dockerfile.sha256
```

## Intentional Dockerfile changes

When you intentionally change the Dockerfile (e.g. to update the base image), regenerate the hash:

```bash
sha256sum Dockerfile | awk '{print $1}' > Dockerfile.sha256
git add Dockerfile Dockerfile.sha256
```

On macOS (no `sha256sum`):

```bash
shasum -a 256 Dockerfile | awk '{print $1}' > Dockerfile.sha256
```

## pre-commit framework

If you use the `pre-commit` Python package, the `.pre-commit-config.yaml` wires the guard automatically:

```bash
pip install pre-commit
pre-commit install
```

The `pre-commit` approach is slightly more portable but requires the package. The manual `cp` approach works in any environment including CI.

## Why not just pin the base image digest?

Pinning the base image digest in the `FROM` line (`FROM apify/actor-python:3.14@sha256:...`) is complementary, not a substitute. The Dockerfile guard protects against the entire file being replaced, not just the base image tag drifting. Both defences are useful.
