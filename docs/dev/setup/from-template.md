# Create a New Repository from This Template

This guide explains how to create your own repository from this template and complete first-time bootstrap.

## Prerequisites

- GitHub account with permission to create repositories
- Git installed locally
- [Docker](https://docker.com/) installed and running
- [Visual Studio Code](https://code.visualstudio.com)
- [VS Code Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Mise](https://mise.jdx.dev/)
- [uv](https://docs.astral.sh/uv/)

## Create Your Repository

1. Open the template repository on GitHub.
2. Select **Use this template**.
3. Choose an owner and repository name.
4. Select visibility (public or private).
5. Create the repository.

## Clone and Enter the Project

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

## Recommended: Open in Dev Container

1. Open the repository in VS Code:

```bash
code .
```

1. When prompted, select **Reopen in Container**.
2. If no prompt appears, run the command palette action:
    **Dev Containers: Reopen in Container**.
3. Wait for container setup to complete.

The dev container runs project setup automatically and provides a consistent toolchain.

## Alternative: Local Setup (without Dev Container)

If you are not using the dev container workflow, set up dependencies locally:

```bash
mise install
uv sync
```

Activate the virtual environment:

=== "Linux/MacOS"

    ```sh
    source ./.venv/bin/activate
    ```

=== "Windows"

    ```sh
    .venv/Scripts/Activate.ps1
    ```

## Install Git Hooks

```bash
prek install --hook-type pre-commit --overwrite
prek install --hook-type commit-msg --overwrite
```

## First Project Customization Checklist

- Update project metadata in `pyproject.toml`.
- Update docs metadata in `zensical.toml`:
    - `site_name`
    - `site_description`
    - `repo_name`
    - `repo_url`
    - `site_author`
- Replace placeholder content in `README.md`.
- Review `docs/` and remove or adapt pages that do not apply.

## Verify Your Setup

Run the baseline checks once after bootstrap:

```bash
uv run ruff check
uv run ruff format --check
uv run ty check
uv run pytest --cov --cov-report=term-missing --cov-fail-under=80
uv run zensical build --clean
```

## Next Steps

- Continue with [Developer Setup](index.md) for day-to-day development workflows.
- Review [Resources](../resources.md) for official tool and standards links.
