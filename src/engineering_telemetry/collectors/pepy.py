"""Pepy collector for Python package download telemetry."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from datetime import UTC, date, datetime, timedelta
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from engineering_telemetry.collectors.base import Collector, CollectorError
from engineering_telemetry.models import EntityDefinition, MetricValue, Snapshot, SnapshotSource


class PepyCollector(Collector):
    """Collect package download telemetry from Pepy."""

    api_base_url = "https://api.pepy.tech/api/v2"

    def collect(self, entity: EntityDefinition, *, captured_at: datetime) -> Snapshot:
        api_key = os.getenv("PEPY_API_KEY")
        if not api_key:
            raise CollectorError("PEPY_API_KEY is required for the Pepy collector.")

        api_url = entity.source.api_url or f"{self.api_base_url}/projects/{entity.source.external_id}"
        request = Request(
            api_url,
            headers={
                "Accept": "application/json",
                "User-Agent": "engineering-telemetry",
                "X-API-Key": api_key,
            },
        )

        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise CollectorError(f"Pepy request failed with HTTP {error.code}: {detail}") from error
        except URLError as error:
            raise CollectorError(f"Pepy request failed: {error.reason}") from error

        metrics = _build_metrics(payload)
        missing = set(entity.metrics) - set(metrics)
        if missing:
            raise CollectorError(f"Pepy collector did not produce configured metrics: {sorted(missing)}")

        return Snapshot(
            entity=entity,
            captured_at=captured_at,
            source=SnapshotSource(
                provider="pepy",
                api_url=api_url,
                fetched_at=datetime.now(UTC),
                details={"package_version": payload.get("versions")},
            ),
            metrics={name: metrics[name] for name in entity.metrics},
        )


def _build_metrics(payload: dict[str, object]) -> dict[str, MetricValue]:
    raw_downloads = payload.get("downloads", {})
    if not isinstance(raw_downloads, Mapping):
        raise CollectorError("Pepy response did not include a valid downloads mapping.")
    downloads = _normalize_mapping(cast(Mapping[object, object], raw_downloads))

    return {
        "downloads_total": MetricValue(
            value=_as_int(payload.get("total_downloads")),
            unit="count",
            category="adoption",
        ),
        "downloads_last_30_days": MetricValue(
            value=_sum_recent_downloads(downloads, days=30),
            unit="count",
            category="adoption",
        ),
        "downloads_last_90_days": MetricValue(
            value=_sum_recent_downloads(downloads, days=90),
            unit="count",
            category="adoption",
        ),
    }


def _sum_recent_downloads(downloads: Mapping[str, object], *, days: int) -> int:
    cutoff = date.today() - timedelta(days=days - 1)
    total = 0

    for raw_day, raw_value in downloads.items():
        try:
            observed = date.fromisoformat(raw_day)
        except ValueError:
            continue

        if observed < cutoff:
            continue

        if not isinstance(raw_value, Mapping):
            continue

        total += sum(_as_int(count) for count in raw_value.values())

    return total


def _normalize_mapping(value: Mapping[object, object]) -> dict[str, object]:
    normalized: dict[str, object] = {}
    for key, item in value.items():
        normalized[str(key)] = item
    return normalized


def _as_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.strip():
        return int(value)
    raise CollectorError(f"Expected an integer-compatible value, received {value!r}.")
