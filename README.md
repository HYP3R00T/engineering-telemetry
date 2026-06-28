# Engineering Telemetry

A JSON-first telemetry aggregator for collecting engineering impact metrics from sources like PyPI, GitHub, CI workflows, and custom analytics counters.

## Quick Start

```sh
mise install
uv sync
export PEPY_API_KEY="your-api-key"
uv run engineering-telemetry show-plan
uv run engineering-telemetry collect --type package
```

The starter configuration tracks the sample package `hypercli` through the Pepy API.

## How It Works

- define tracked entities in `telemetry.toml`
- run the collector on a schedule
- write normalized JSON snapshots into `data/`
- let other apps read those files instead of calling upstream APIs directly

## CLI

The CLI now uses `Typer`, which gives us cleaner subcommands, built-in help, and an easier path for future commands without growing a brittle manual parser.

```sh
uv run engineering-telemetry --help
uv run engineering-telemetry show-plan --help
uv run engineering-telemetry collect --help
```

Configuration loading uses `utilityhub_config` directly. The CLI reads `telemetry.toml` by default, or another file passed with `--config`, while preserving the package's normal precedence across global config, `.env`, environment variables, and runtime overrides.

## Commands

- `uv run engineering-telemetry show-plan`
- `uv run engineering-telemetry collect`
- `uv run engineering-telemetry collect --type package`
- `uv run engineering-telemetry collect --type repository`
- `uv run engineering-telemetry collect --type release`
- `uv run engineering-telemetry collect --type workflow`
- `uv run engineering-telemetry collect --entity package:hypercli`

If you are working directly with the local virtual environment instead of `uv run`:

```sh
PYTHONPATH=src .venv/bin/python -m engineering_telemetry.cli show-plan
```

## Current Structure

- `src/engineering_telemetry/`: application package
- `telemetry.toml`: tracked entity configuration
- `schemas/`: JSON schemas for catalog, latest snapshots, and history entries
- `data/`: generated telemetry artifacts
- `docs/storage-model.md`: storage layout and schema design
- `docs/usage.md`: operator-focused setup and command guide
- `tests/`: focused unit tests for config loading, orchestration, and persistence

## Docs

- [Usage Guide](docs/usage.md)
- [Storage Model](docs/storage-model.md)
