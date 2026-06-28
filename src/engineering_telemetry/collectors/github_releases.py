"""GitHub releases collector for repository release telemetry."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from engineering_telemetry.collectors.base import Collector, CollectorError
from engineering_telemetry.collectors.github_common import as_int, github_headers, parse_repository
from engineering_telemetry.models import EntityDefinition, MetricValue, Snapshot, SnapshotSource


class GitHubReleasesCollector(Collector):
    """Collect release telemetry from the GitHub releases REST API."""

    api_base_url = "https://api.github.com"

    def collect(self, entity: EntityDefinition, *, captured_at: datetime) -> Snapshot:
        owner, repo = parse_repository(entity.source.external_id, source_name="GitHub releases")
        releases_payload = self._get_json(_releases_url(owner, repo))

        metrics = {
            "releases_total": MetricValue(
                value=len(releases_payload),
                unit="count",
                category="delivery",
            ),
            "prereleases_total": MetricValue(
                value=sum(1 for release in releases_payload if _is_true(release.get("prerelease"))),
                unit="count",
                category="delivery",
            ),
            "release_assets_total": MetricValue(
                value=sum(as_int(release.get("assets_count")) for release in releases_payload),
                unit="count",
                category="delivery",
            ),
        }

        missing = set(entity.metrics) - set(metrics)
        if missing:
            raise CollectorError(f"GitHub releases collector did not produce configured metrics: {sorted(missing)}")

        return Snapshot(
            entity=entity,
            captured_at=captured_at,
            source=SnapshotSource(
                provider="github",
                api_url=_releases_url(owner, repo),
                fetched_at=datetime.now(UTC),
                details={"repository": f"{owner}/{repo}"},
            ),
            metrics={name: metrics[name] for name in entity.metrics},
        )

    def _get_json(self, url: str) -> list[dict[str, object]]:
        request = Request(url, headers=github_headers())

        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise CollectorError(f"GitHub releases request failed with HTTP {error.code}: {detail}") from error
        except URLError as error:
            raise CollectorError(f"GitHub releases request failed: {error.reason}") from error

        if not isinstance(payload, Sequence) or isinstance(payload, (str, bytes, bytearray)):
            raise CollectorError("GitHub releases response was not a JSON array.")

        releases: list[dict[str, object]] = []
        for item in payload:
            if not isinstance(item, Mapping):
                raise CollectorError("GitHub releases response included a non-object release entry.")
            release = dict(item)
            release["assets_count"] = _assets_count(release.get("assets"))
            releases.append(release)

        return releases


def _releases_url(owner: str, repo: str) -> str:
    return f"{GitHubReleasesCollector.api_base_url}/repos/{owner}/{repo}/releases?per_page=100"


def _assets_count(value: object) -> int:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return 0
    return len(value)


def _is_true(value: object) -> bool:
    return value is True
