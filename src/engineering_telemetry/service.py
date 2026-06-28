"""Collection orchestration."""

from __future__ import annotations

from datetime import UTC, datetime

from engineering_telemetry.collectors.registry import CollectorRegistry
from engineering_telemetry.config import TelemetryConfig
from engineering_telemetry.models import EntityDefinition
from engineering_telemetry.storage import TelemetryStore


def plan_entities(
    config: TelemetryConfig,
    *,
    entity_id: str | None = None,
    entity_type: str | None = None,
) -> tuple[EntityDefinition, ...]:
    """Return configured entities after applying filters."""
    planned = tuple(
        entity
        for entity in config.entity_definitions
        if (entity_id is None or entity.entity_id == entity_id)
        and (entity_type is None or entity.entity_type == entity_type)
    )
    return planned


def collect_entities(
    config: TelemetryConfig,
    registry: CollectorRegistry,
    store: TelemetryStore,
    *,
    entity_id: str | None = None,
    entity_type: str | None = None,
    captured_at: datetime | None = None,
    write_catalog: bool = True,
) -> list[tuple[EntityDefinition, tuple[str, str]]]:
    """Collect snapshots for configured entities."""
    now = captured_at or datetime.now(UTC)
    entities = plan_entities(config, entity_id=entity_id, entity_type=entity_type)

    if write_catalog:
        store.write_catalog(config, generated_at=now)

    results: list[tuple[EntityDefinition, tuple[str, str]]] = []
    for entity in entities:
        collector = registry.get(entity.collector)
        snapshot = collector.collect(entity, captured_at=now)
        latest_path, history_path = store.write_snapshot(snapshot)
        results.append((entity, (latest_path.as_posix(), history_path.as_posix())))

    return results
