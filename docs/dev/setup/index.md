# Developer Setup

This page documents the day-to-day development workflow for contributors who are already working in a repository created from this template.

The primary path is **Dev Container-first** for consistent environments across contributors.

## Prerequisites

- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Recommended Setup (Dev Container)

1. Open the repository folder in VS Code.
2. Select **Reopen in Container** when prompted.
3. If no prompt appears, run **Dev Containers: Reopen in Container** from Command Palette.
4. Wait for container setup to finish.

`scripts/setup.sh` runs during container creation, so the environment and dependencies are prepared automatically.

## Pre-commit Hooks

Hooks are typically installed by setup automation. If needed, re-install manually:

```bash
prek install --hook-type pre-commit --overwrite
prek install --hook-type commit-msg --overwrite
```

???+ tip "Warm up hooks"
    Run `prek run --all-files` after hook installation. This preloads environments and avoids first-commit surprises.

## Daily Commands

Use these commands from the repository root:

```bash
uv run ruff check
uv run ruff format --check
uv run ty check
uv run pytest --cov --cov-report=term-missing --cov-fail-under=80
uv run zensical build --clean
```

## Optional: Local Setup Without Dev Container

If you are not using Dev Containers, use the fallback local setup path in [Create a New Repository from This Template](from-template.md).

For local tooling details, see [Resources](../resources.md).

## Related

- [Create a New Repository from This Template](from-template.md)
- [Resources](../resources.md)
- [Authoring Documentation](../contributing/authoring-documentation.md)
- [Naming Conventions](../contributing/naming-conventions.md)
- [Documentation Principles](../contributing/documentation-principles/index.md)
