"""Command-line interface for engineering telemetry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from utilityhub_config.errors import ConfigError, ConfigValidationError

from engineering_telemetry.collectors.base import CollectorError
from engineering_telemetry.collectors.registry import default_registry
from engineering_telemetry.config import TelemetryConfig, load_config
from engineering_telemetry.models import EntityType
from engineering_telemetry.service import collect_entities, plan_entities
from engineering_telemetry.storage import TelemetryStore

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Collect and persist engineering telemetry from configured sources.",
)


class AppState:
    """Shared CLI state."""

    def __init__(self) -> None:
        self.config: TelemetryConfig | None = None


def main() -> None:
    """Entry point for console scripts."""
    app()


@app.callback()
def callback(
    ctx: typer.Context,
    config: Annotated[
        Path,
        typer.Option(
            "--config",
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to the repository-local telemetry configuration file.",
        ),
    ] = Path("telemetry.toml"),
) -> None:
    """Load CLI state before executing a subcommand."""
    state = AppState()

    try:
        state.config = load_config(config)
    except FileNotFoundError as error:
        raise typer.BadParameter(str(error), param_hint="--config") from error
    except (CollectorError, ConfigError, ConfigValidationError, ValueError) as error:
        raise typer.Exit(code=_emit_error(str(error))) from error

    ctx.obj = state


@app.command("show-plan")
def show_plan(
    ctx: typer.Context,
    entity: Annotated[
        str | None,
        typer.Option("--entity", help="Show only one configured entity id."),
    ] = None,
    entity_type: Annotated[
        EntityType | None,
        typer.Option(
            "--type",
            help="Show only one entity type.",
        ),
    ] = None,
) -> None:
    """Show the configured collection plan."""
    config = _require_config(ctx)
    entities = plan_entities(config, entity_id=entity, entity_type=entity_type)
    payload = {
        "config_path": config.config_path.as_posix(),
        "data_dir": config.data_dir.as_posix(),
        "entities": [
            {
                "id": current.entity_id,
                "type": current.entity_type,
                "name": current.name,
                "collector": current.collector,
                "metrics": list(current.metrics),
            }
            for current in entities
        ],
    }
    typer.echo(json.dumps(payload, indent=2))


@app.command()
def collect(
    ctx: typer.Context,
    entity: Annotated[
        str | None,
        typer.Option("--entity", help="Collect only one configured entity id."),
    ] = None,
    entity_type: Annotated[
        EntityType | None,
        typer.Option(
            "--type",
            help="Collect only one entity type.",
        ),
    ] = None,
) -> None:
    """Collect metrics and write normalized JSON artifacts."""
    config = _require_config(ctx)
    registry = default_registry()
    store = TelemetryStore(config.data_dir)

    try:
        results = collect_entities(
            config,
            registry,
            store,
            entity_id=entity,
            entity_type=entity_type,
        )
    except CollectorError as error:
        raise typer.Exit(code=_emit_error(str(error))) from error

    payload = {
        "collected": [
            {
                "id": current.entity_id,
                "latest_path": latest_path,
                "history_path": history_path,
            }
            for current, (latest_path, history_path) in results
        ]
    }
    typer.echo(json.dumps(payload, indent=2))


def _require_config(ctx: typer.Context) -> TelemetryConfig:
    state = ctx.obj
    if not isinstance(state, AppState) or state.config is None:
        raise typer.Exit(code=_emit_error("Configuration was not loaded."))
    return state.config


def _emit_error(message: str) -> int:
    typer.echo(message, err=True)
    return 2


if __name__ == "__main__":
    main()
