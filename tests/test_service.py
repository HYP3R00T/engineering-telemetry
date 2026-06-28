from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from engineering_telemetry.collectors.base import Collector
from engineering_telemetry.collectors.registry import CollectorRegistry
from engineering_telemetry.config import EntitySettings, ProjectSettings, SourceSettings, TelemetryConfig
from engineering_telemetry.models import (
    EntityDefinition,
    EntityType,
    MetricValue,
    Snapshot,
    SnapshotSource,
    SourceDefinition,
)
from engineering_telemetry.service import collect_entities, plan_entities
from engineering_telemetry.storage import TelemetryStore


class FakeCollector(Collector):
    def collect(self, entity: EntityDefinition, *, captured_at: datetime) -> Snapshot:
        return Snapshot(
            entity=entity,
            captured_at=captured_at,
            source=SnapshotSource(provider="fake", fetched_at=captured_at),
            metrics={
                "downloads_total": MetricValue(
                    value=42,
                    unit="count",
                    category="adoption",
                )
            },
        )


def test_plan_entities_filters_by_type() -> None:
    config = _config(
        data_dir=Path("data"),
        entities=(
            _entity("package:hypercli", "package"),
            _entity("workflow:ci", "workflow"),
        ),
    )

    planned = plan_entities(config, entity_type="package")

    assert [entity.entity_id for entity in planned] == ["package:hypercli"]


def test_collect_entities_writes_output(tmp_path: Path) -> None:
    config = _config(
        data_dir=tmp_path / "data",
        entities=(_entity("package:hypercli", "package"),),
    )
    registry = CollectorRegistry({"fake": FakeCollector()})
    store = TelemetryStore(config.data_dir)
    captured_at = datetime(2026, 6, 28, tzinfo=UTC)

    results = collect_entities(
        config,
        registry,
        store,
        captured_at=captured_at,
    )

    assert len(results) == 1
    latest_path = tmp_path / "data" / "latest" / "package" / "hypercli.json"
    history_path = tmp_path / "data" / "history" / "package" / "hypercli.jsonl"
    assert latest_path.exists()
    assert history_path.exists()


def _entity(entity_id: str, entity_type: EntityType) -> EntityDefinition:
    return EntityDefinition(
        entity_id=entity_id,
        entity_type=entity_type,
        name=entity_id.split(":", maxsplit=1)[1],
        collector="fake",
        metrics=("downloads_total",),
        source=SourceDefinition(provider="fake", external_id=entity_id),
    )


def _config(*, data_dir: Path, entities: tuple[EntityDefinition, ...]) -> TelemetryConfig:
    config = TelemetryConfig(
        project=ProjectSettings(data_dir=data_dir),
        entities=[
            EntitySettings(
                id=entity.entity_id,
                type=entity.entity_type,
                name=entity.name,
                collector=entity.collector,
                metrics=list(entity.metrics),
                source=SourceSettings(
                    provider=entity.source.provider,
                    external_id=entity.source.external_id,
                    api_url=entity.source.api_url,
                    options=dict(entity.source.options),
                ),
                settings=dict(entity.settings),
            )
            for entity in entities
        ],
    )
    config._config_path = Path.cwd() / "telemetry.toml"
    return config
