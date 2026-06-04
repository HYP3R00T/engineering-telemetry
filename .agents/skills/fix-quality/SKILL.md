---
name: fix-quality
description: 'Run Python quality gates in order after code edits: format, lint, and type-check, and resolve all remaining issues before finishing.'
argument-hint: 'Describe which files changed and whether any current ruff or ty errors are known.'
---

# Skill: fix-quality

Run this skill after every code change before committing.

## When to use

After any edit to `.py` files.

## Steps

1. Format first - see [references/ruff-format.md](references/ruff-format.md)
2. Fix lint violations - see [references/ruff-lint.md](references/ruff-lint.md)
3. Resolve type errors - see [references/ty-check.md](references/ty-check.md)

## Quick sequence

```sh
uv run ruff format
uv run ruff check --fix
uv run ruff check          # review any remaining unfixable violations
uv run ty check            # fix all reported errors before proceeding
```

All four must pass clean before the task is considered done.
