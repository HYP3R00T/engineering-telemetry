"""Shared models for telemetry configuration and persisted data."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

EntityType = Literal["package", "repository", "workflow", "release", "script"]
MetricCategory = Literal["adoption", "reach", "operations", "delivery", "quality"]


@dataclass(slots=True, frozen=True)
class SourceDefinition:
    """Source metadata for a tracked entity."""

    provider: str
    external_id: str
    api_url: str | None = None
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class EntityDefinition:
    """Configuration for one tracked telemetry entity."""

    entity_id: str
    entity_type: EntityType
    name: str
    collector: str
    metrics: tuple[str, ...]
    source: SourceDefinition
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class MetricValue:
    """A normalized metric value."""

    value: int | float | str | bool | None
    unit: str
    category: MetricCategory


@dataclass(slots=True, frozen=True)
class SnapshotSource:
    """Runtime source metadata for one collection run."""

    provider: str
    fetched_at: datetime
    api_url: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class Snapshot:
    """Latest metrics for one entity at a point in time."""

    entity: EntityDefinition
    captured_at: datetime
    source: SnapshotSource
    metrics: dict[str, MetricValue]
