---
icon: lucide/play
---

# Usage Guide

This project is designed to collect telemetry on a schedule, store normalized JSON artifacts, and let other applications read from those artifacts instead of calling upstream APIs directly.

## Prerequisites

- Python `3.13`
- project dependencies installed
- a telemetry configuration file
- any required source credentials in environment variables

## Setup

Install the project dependencies:

```sh
mise install
uv sync
```

If you prefer to use the already-created virtual environment directly:

```sh
source .venv/bin/activate
```

## Configuration

Tracked entities live in [`telemetry.toml`](../telemetry.toml).

Configuration loading is handled through `utilityhub_config`. The CLI loads `telemetry.toml` by default, or another file you pass with `--config`, and still benefits from the package's normal precedence rules:

- the default config file is `telemetry.toml`
- you can point to another config file with `--config`
- global config, `.env`, and environment variables can override settings when present

Example:

```toml
[project]
data_dir = "data"

[[entities]]
id = "repository:HYP3R00T/voicepad"
type = "repository"
name = "voicepad workflows"
collector = "github_actions"
metrics = ["workflow_runs_total", "workflows_total"]

[entities.source]
provider = "github"
external_id = "HYP3R00T/voicepad"

[[entities]]
id = "release:HYP3R00T/voicepad"
type = "release"
name = "voicepad releases"
collector = "github_releases"
metrics = ["releases_total", "prereleases_total", "release_assets_total"]

[entities.source]
provider = "github"
external_id = "HYP3R00T/voicepad"

[[entities]]
id = "package:voicepad"
type = "package"
name = "voicepad"
collector = "pepy"
metrics = [
  "downloads_total",
  "downloads_last_30_days",
  "downloads_last_90_days",
]

[entities.source]
provider = "pepy"
external_id = "voicepad"
api_url = "https://api.pepy.tech/api/v2/projects/voicepad"

[[entities]]
id = "workflow:HYP3R00T/voicepad/release"
type = "workflow"
name = "release"
collector = "github_actions"
metrics = ["workflow_runs_total"]

[entities.source]
provider = "github"
external_id = "HYP3R00T/voicepad"

[entities.source.options]
workflow = ".github/workflows/release.yml"
```

Each entity defines:

- a stable internal id
- an entity type such as `package`, `repository`, `workflow`, or `release`
- the collector implementation to use
- the normalized metrics expected from that collector
- provider-specific source details

## Credentials

Collectors use environment variables for secrets.

Current built-in collector requirements:

- `pepy`: `PEPY_API_KEY`
- `github_actions`: optional `GITHUB_TOKEN` for higher rate limits or private repositories
- `github_releases`: optional `GITHUB_TOKEN` for higher rate limits or private repositories

Example:

```sh
export PEPY_API_KEY="your-api-key"
```

## Commands

The CLI is built with `Typer`. It exposes a small set of commands and leaves provider-specific behavior in config and collector implementations.

### Show the collection plan

Inspect what entities are configured:

```sh
uv run engineering-telemetry show-plan
```

If you are using the local virtual environment directly:

```sh
PYTHONPATH=src .venv/bin/python -m engineering_telemetry.cli show-plan
```

### Collect everything

Run all configured collectors:

```sh
uv run engineering-telemetry collect
```

Show help for the CLI or a subcommand:

```sh
uv run engineering-telemetry --help
uv run engineering-telemetry collect --help
```

### Collect one entity type

Run only package metrics:

```sh
uv run engineering-telemetry collect --type package
```

### Collect one entity

Run only one configured entity:

```sh
uv run engineering-telemetry collect --entity package:hypercli
```

### Use a different config file

Point the CLI at another TOML config:

```sh
uv run engineering-telemetry --config telemetry.toml show-plan
```

## Output

By default, output is written under `data/`:

```text
data/
  catalog.json
  latest/
  history/
```

Main artifacts:

- `data/catalog.json`: root index of tracked entities
- `data/latest/<type>/<name>.json`: latest snapshot for an entity
- `data/history/<type>/<name>.jsonl`: append-only history for that entity

Paths recorded in `data/catalog.json` are stored relative to the config root so the catalog can move between machines without rewriting entity metadata.

## Operational Model

This project is best run as a scheduled batch process:

- every 6 hours for fast-moving public metrics
- daily for slower-moving metrics

The intended pattern is:

1. run `collect`
2. overwrite the latest snapshot per entity
3. append history records for the same run
4. let other apps read the generated files

## Recommended Next Sources

After Pepy, the next useful collectors are:

- GitHub repository metrics
- GitHub Actions workflow metrics
- custom script analytics or download counters

Each new source should follow the same pattern:

1. fetch source data
2. normalize it into shared metric keys
3. write latest snapshot
4. append history entries
