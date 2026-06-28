"""Base collector interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from engineering_telemetry.models import EntityDefinition, Snapshot


class CollectorError(RuntimeError):
    """Raised when collection cannot proceed."""


class Collector(ABC):
    """Abstract collector interface."""

    @abstractmethod
    def collect(self, entity: EntityDefinition, *, captured_at: datetime) -> Snapshot:
        """Collect a normalized snapshot for one entity."""
