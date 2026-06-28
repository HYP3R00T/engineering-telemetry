"""Persistence helpers for normalized telemetry data."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from engineering_telemetry.config import TelemetryConfig
from engineering_telemetry.models import EntityDefinition, Snapshot


class TelemetryStore:
    """Write catalog, latest snapshots, and history observations."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def write_catalog(self, config: TelemetryConfig, *, generated_at: datetime | None = None) -> Path:
        """Write the entity catalog file."""
        timestamp = _normalize_datetime(generated_at or datetime.now(UTC))
        payload = {
            "version": 1,
            "generated_at": timestamp,
            "data_dir": config.project.data_dir.as_posix(),
            "entities": [
                self._catalog_entity(entity, data_dir=config.project.data_dir) for entity in config.entity_definitions
            ],
        }
        catalog_path = self.data_dir / "catalog.json"
        self._write_json(catalog_path, payload)
        return catalog_path

    def write_snapshot(self, snapshot: Snapshot) -> tuple[Path, Path]:
        """Write the latest snapshot and append history records."""
        latest_path = self.latest_path(snapshot.entity)
        history_path = self.history_path(snapshot.entity)

        payload = {
            "schema_version": 1,
            "entity": {
                "id": snapshot.entity.entity_id,
                "type": snapshot.entity.entity_type,
                "name": snapshot.entity.name,
            },
            "captured_at": _normalize_datetime(snapshot.captured_at),
            "source": {
                "provider": snapshot.source.provider,
                "fetched_at": _normalize_datetime(snapshot.source.fetched_at),
                **({"api_url": snapshot.source.api_url} if snapshot.source.api_url else {}),
                **snapshot.source.details,
            },
            "metrics": {
                name: {
                    "value": metric.value,
                    "unit": metric.unit,
                    "category": metric.category,
                }
                for name, metric in snapshot.metrics.items()
            },
        }
        self._write_json(latest_path, payload)
        self._append_history(history_path, snapshot)
        return latest_path, history_path

    def latest_path(self, entity: EntityDefinition) -> Path:
        """Return the latest snapshot path for an entity."""
        return self.data_dir / "latest" / entity.entity_type / f"{_slugify(entity.name)}.json"

    def history_path(self, entity: EntityDefinition) -> Path:
        """Return the history file path for an entity."""
        return self.data_dir / "history" / entity.entity_type / f"{_slugify(entity.name)}.jsonl"

    def _catalog_entity(self, entity: EntityDefinition, *, data_dir: Path) -> dict[str, Any]:
        return {
            "id": entity.entity_id,
            "type": entity.entity_type,
            "name": entity.name,
            "source": {
                "provider": entity.source.provider,
                "external_id": entity.source.external_id,
                **({"api_url": entity.source.api_url} if entity.source.api_url else {}),
                **({"options": entity.source.options} if entity.source.options else {}),
            },
            "paths": {
                "latest": _relative_latest_path(data_dir, entity).as_posix(),
                "history": _relative_history_path(data_dir, entity).as_posix(),
            },
            "metrics": list(entity.metrics),
            **({"settings": entity.settings} if entity.settings else {}),
        }

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{json.dumps(payload, indent=2, sort_keys=True)}\n")

    def _append_history(self, path: Path, snapshot: Snapshot) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            for metric_key, metric in snapshot.metrics.items():
                record = {
                    "captured_at": _normalize_datetime(snapshot.captured_at),
                    "entity_id": snapshot.entity.entity_id,
                    "metric_key": metric_key,
                    "value": metric.value,
                    "unit": metric.unit,
                    "source": snapshot.source.provider,
                }
                handle.write(json.dumps(record, sort_keys=True))
                handle.write("\n")


def _normalize_datetime(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _slugify(value: str) -> str:
    return value.lower().replace("_", "-").replace(" ", "-")


def _relative_latest_path(data_dir: Path, entity: EntityDefinition) -> Path:
    return data_dir / "latest" / entity.entity_type / f"{_slugify(entity.name)}.json"


def _relative_history_path(data_dir: Path, entity: EntityDefinition) -> Path:
    return data_dir / "history" / entity.entity_type / f"{_slugify(entity.name)}.jsonl"
