"""GitHub Actions collector for repository and workflow execution telemetry."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from engineering_telemetry.collectors.base import Collector, CollectorError
from engineering_telemetry.collectors.github_common import as_int, github_headers, parse_repository
from engineering_telemetry.models import EntityDefinition, MetricValue, Snapshot, SnapshotSource


class GitHubActionsCollector(Collector):
    """Collect workflow execution telemetry from the GitHub Actions REST API."""

    api_base_url = "https://api.github.com"

    def collect(self, entity: EntityDefinition, *, captured_at: datetime) -> Snapshot:
        owner, repo = parse_repository(entity.source.external_id, source_name="GitHub Actions")
        workflow = _workflow_selector(entity)

        runs_payload = self._get_json(_runs_url(owner, repo, workflow))
        metrics = {
            "workflow_runs_total": MetricValue(
                value=as_int(runs_payload.get("total_count")),
                unit="count",
                category="operations",
            )
        }

        if "workflows_total" in entity.metrics:
            workflows_payload = self._get_json(_workflows_url(owner, repo))
            metrics["workflows_total"] = MetricValue(
                value=as_int(workflows_payload.get("total_count")),
                unit="count",
                category="operations",
            )

        missing = set(entity.metrics) - set(metrics)
        if missing:
            raise CollectorError(f"GitHub Actions collector did not produce configured metrics: {sorted(missing)}")

        return Snapshot(
            entity=entity,
            captured_at=captured_at,
            source=SnapshotSource(
                provider="github",
                api_url=_runs_url(owner, repo, workflow),
                fetched_at=datetime.now(UTC),
                details={
                    "repository": f"{owner}/{repo}",
                    **({"workflow": workflow} if workflow else {}),
                },
            ),
            metrics={name: metrics[name] for name in entity.metrics},
        )

    def _get_json(self, url: str) -> dict[str, object]:
        request = Request(url, headers=github_headers())

        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise CollectorError(f"GitHub Actions request failed with HTTP {error.code}: {detail}") from error
        except URLError as error:
            raise CollectorError(f"GitHub Actions request failed: {error.reason}") from error

        if not isinstance(payload, Mapping):
            raise CollectorError("GitHub Actions response was not a JSON object.")

        return dict(payload)


def _workflow_selector(entity: EntityDefinition) -> str | None:
    workflow = entity.source.options.get("workflow")
    if workflow is None:
        workflow = entity.source.options.get("workflow_id")
    if workflow is None:
        return None
    if not isinstance(workflow, str) or not workflow.strip():
        raise CollectorError("GitHub Actions workflow selector must be a non-empty string.")
    return workflow.strip()


def _runs_url(owner: str, repo: str, workflow: str | None) -> str:
    if workflow:
        return f"{GitHubActionsCollector.api_base_url}/repos/{owner}/{repo}/actions/workflows/{quote(workflow, safe='')}/runs?per_page=1"
    return f"{GitHubActionsCollector.api_base_url}/repos/{owner}/{repo}/actions/runs?per_page=1"


def _workflows_url(owner: str, repo: str) -> str:
    return f"{GitHubActionsCollector.api_base_url}/repos/{owner}/{repo}/actions/workflows?per_page=1"
