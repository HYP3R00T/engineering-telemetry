from __future__ import annotations

import json
from datetime import UTC, datetime
from urllib.request import Request

import pytest

from engineering_telemetry.collectors.base import CollectorError
from engineering_telemetry.collectors.github_actions import GitHubActionsCollector
from engineering_telemetry.collectors.github_releases import GitHubReleasesCollector
from engineering_telemetry.collectors.pepy import PepyCollector
from engineering_telemetry.models import EntityDefinition, SourceDefinition


class _FakeResponse:
    def __init__(self, payload: object) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


def test_github_actions_collector_reads_repository_totals(monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[str] = []

    def fake_urlopen(request: Request, timeout: int) -> _FakeResponse:
        full_url = request.full_url
        requests.append(full_url)
        if full_url.endswith("/actions/runs?per_page=1"):
            return _FakeResponse({"total_count": 127})
        if full_url.endswith("/actions/workflows?per_page=1"):
            return _FakeResponse({"total_count": 4})
        raise AssertionError(f"unexpected URL {full_url}")

    monkeypatch.setattr("engineering_telemetry.collectors.github_actions.urlopen", fake_urlopen)

    collector = GitHubActionsCollector()
    entity = EntityDefinition(
        entity_id="repository:acme/telemetry",
        entity_type="repository",
        name="telemetry",
        collector="github_actions",
        metrics=("workflow_runs_total", "workflows_total"),
        source=SourceDefinition(provider="github", external_id="acme/telemetry"),
    )

    snapshot = collector.collect(entity, captured_at=datetime(2026, 6, 28, tzinfo=UTC))

    assert requests == [
        "https://api.github.com/repos/acme/telemetry/actions/runs?per_page=1",
        "https://api.github.com/repos/acme/telemetry/actions/workflows?per_page=1",
    ]
    assert snapshot.metrics["workflow_runs_total"].value == 127
    assert snapshot.metrics["workflows_total"].value == 4
    assert snapshot.source.details["repository"] == "acme/telemetry"


def test_github_actions_collector_supports_workflow_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[str] = []

    def fake_urlopen(request: Request, timeout: int) -> _FakeResponse:
        requests.append(request.full_url)
        return _FakeResponse({"total_count": 33})

    monkeypatch.setattr("engineering_telemetry.collectors.github_actions.urlopen", fake_urlopen)

    collector = GitHubActionsCollector()
    entity = EntityDefinition(
        entity_id="workflow:acme/telemetry/ci",
        entity_type="workflow",
        name="ci",
        collector="github_actions",
        metrics=("workflow_runs_total",),
        source=SourceDefinition(
            provider="github",
            external_id="acme/telemetry",
            options={"workflow": ".github/workflows/ci.yml"},
        ),
    )

    snapshot = collector.collect(entity, captured_at=datetime(2026, 6, 28, tzinfo=UTC))

    assert requests == [
        "https://api.github.com/repos/acme/telemetry/actions/workflows/.github%2Fworkflows%2Fci.yml/runs?per_page=1"
    ]
    assert snapshot.metrics["workflow_runs_total"].value == 33
    assert snapshot.source.details["workflow"] == ".github/workflows/ci.yml"


def test_github_actions_collector_rejects_invalid_repo_identifier() -> None:
    collector = GitHubActionsCollector()
    entity = EntityDefinition(
        entity_id="repository:oops",
        entity_type="repository",
        name="oops",
        collector="github_actions",
        metrics=("workflow_runs_total",),
        source=SourceDefinition(provider="github", external_id="not-a-repo"),
    )

    with pytest.raises(CollectorError, match="owner/repository"):
        collector.collect(entity, captured_at=datetime(2026, 6, 28, tzinfo=UTC))


def test_github_releases_collector_reads_release_totals(monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[str] = []

    def fake_urlopen(request: Request, timeout: int) -> _FakeResponse:
        requests.append(request.full_url)
        return _FakeResponse([
            {"tag_name": "v1.0.0", "prerelease": False, "assets": [{"name": "wheel"}]},
            {"tag_name": "v1.1.0-rc1", "prerelease": True, "assets": []},
            {"tag_name": "v1.1.0", "prerelease": False, "assets": [{"name": "sdist"}, {"name": "wheel"}]},
        ])

    monkeypatch.setattr("engineering_telemetry.collectors.github_releases.urlopen", fake_urlopen)

    collector = GitHubReleasesCollector()
    entity = EntityDefinition(
        entity_id="release:acme/telemetry",
        entity_type="release",
        name="telemetry releases",
        collector="github_releases",
        metrics=("releases_total", "prereleases_total", "release_assets_total"),
        source=SourceDefinition(provider="github", external_id="acme/telemetry"),
    )

    snapshot = collector.collect(entity, captured_at=datetime(2026, 6, 28, tzinfo=UTC))

    assert requests == ["https://api.github.com/repos/acme/telemetry/releases?per_page=100"]
    assert snapshot.metrics["releases_total"].value == 3
    assert snapshot.metrics["prereleases_total"].value == 1
    assert snapshot.metrics["release_assets_total"].value == 3
    assert snapshot.source.details["repository"] == "acme/telemetry"


def test_github_releases_collector_rejects_invalid_repo_identifier() -> None:
    collector = GitHubReleasesCollector()
    entity = EntityDefinition(
        entity_id="release:oops",
        entity_type="release",
        name="oops releases",
        collector="github_releases",
        metrics=("releases_total",),
        source=SourceDefinition(provider="github", external_id="not-a-repo"),
    )

    with pytest.raises(CollectorError, match="owner/repository"):
        collector.collect(entity, captured_at=datetime(2026, 6, 28, tzinfo=UTC))


def test_pepy_collector_sends_explicit_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    seen_headers: dict[str, str] = {}

    def fake_urlopen(request: Request, timeout: int) -> _FakeResponse:
        seen_headers.update(dict(request.header_items()))
        return _FakeResponse({
            "total_downloads": 123,
            "downloads": {
                "2026-06-28": {"1.0.0": 10},
            },
            "versions": ["1.0.0"],
        })

    monkeypatch.setenv("PEPY_API_KEY", "test-key")
    monkeypatch.setattr("engineering_telemetry.collectors.pepy.urlopen", fake_urlopen)

    collector = PepyCollector()
    entity = EntityDefinition(
        entity_id="package:voicepad",
        entity_type="package",
        name="voicepad",
        collector="pepy",
        metrics=("downloads_total",),
        source=SourceDefinition(provider="pepy", external_id="voicepad"),
    )

    snapshot = collector.collect(entity, captured_at=datetime(2026, 6, 28, tzinfo=UTC))

    assert seen_headers["User-agent"] == "engineering-telemetry"
    assert seen_headers["X-api-key"] == "test-key"
    assert snapshot.metrics["downloads_total"].value == 123
