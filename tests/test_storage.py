from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from engineering_telemetry.config import EntitySettings, ProjectSettings, SourceSettings, TelemetryConfig
from engineering_telemetry.models import (
    EntityDefinition,
    MetricValue,
    Snapshot,
    SnapshotSource,
    SourceDefinition,
)
from engineering_telemetry.storage import TelemetryStore


def test_store_writes_catalog_and_snapshot(tmp_path: Path) -> None:
    entity = EntityDefinition(
        entity_id="package:hypercli",
        entity_type="package",
        name="hypercli",
        collector="pepy",
        metrics=("downloads_total",),
        source=SourceDefinition(provider="pepy", external_id="hypercli"),
    )
    config = TelemetryConfig(
        project=ProjectSettings(data_dir=Path("data")),
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
        ],
    )
    config._config_path = tmp_path / "telemetry.toml"
    store = TelemetryStore(config.data_dir)
    now = datetime(2026, 6, 28, tzinfo=UTC)

    catalog_path = store.write_catalog(config, generated_at=now)
    snapshot = Snapshot(
        entity=entity,
        captured_at=now,
        source=SnapshotSource(provider="pepy", fetched_at=now),
        metrics={
            "downloads_total": MetricValue(
                value=123,
                unit="count",
                category="adoption",
            )
        },
    )
    latest_path, history_path = store.write_snapshot(snapshot)

    catalog = json.loads(catalog_path.read_text())
    latest = json.loads(latest_path.read_text())
    history_lines = history_path.read_text().strip().splitlines()

    assert catalog["entities"][0]["id"] == "package:hypercli"
    assert catalog["data_dir"] == "data"
    assert catalog["entities"][0]["paths"]["latest"] == "data/latest/package/hypercli.json"
    assert catalog["entities"][0]["paths"]["history"] == "data/history/package/hypercli.jsonl"
    assert latest["entity"]["name"] == "hypercli"
    assert latest["metrics"]["downloads_total"]["value"] == 123
    assert len(history_lines) == 1
    assert json.loads(history_lines[0])["metric_key"] == "downloads_total"
