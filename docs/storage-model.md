---
icon: lucide/database
---

# Telemetry Storage Model

This project stores engineering telemetry in a JSON-first format that is:

- easy for other applications to consume
- friendly to scheduled batch updates
- compact enough to avoid a single bloated file
- structured enough to preserve history and source metadata

## Design Goals

- **Latest data is easy to read:** downstream applications should be able to fetch one file per tracked entity.
- **History is preserved:** we keep append-only observations for trend analysis.
- **Files stay discoverable:** a small registry file explains what is tracked and where to find it.
- **Collectors stay decoupled:** each source can map its API response into a shared internal format.

## Recommended Layout

```text
data/
  catalog.json
  latest/
    package/
      hypercli.json
    repository/
      engineering-telemetry.json
    workflow/
      github-actions-ci.json
    script/
      installer-counter.json
  history/
    package/
      hypercli.jsonl
    repository/
      engineering-telemetry.jsonl
    workflow/
      github-actions-ci.jsonl
    script/
      installer-counter.jsonl
```

## Why This Layout

- `catalog.json` is the directory of tracked entities and metric definitions.
- `latest/.../<entity>.json` gives consumers a single current snapshot for each entity.
- `history/.../<entity>.jsonl` stores append-only observations without rewriting large files.

This gives us a practical middle ground:

- not one monolithic `telemetry.json`
- not one file per metric datapoint

## Entity Types

The first version should focus on a small set of entity types:

- `package`
- `repository`
- `workflow`
- `script`

These map well to the evidence you want to show:

- package adoption
- repository reach
- CI/CD execution
- script or tool usage

## Metric Categories

Each metric should belong to one of these categories:

- `adoption`
- `reach`
- `operations`
- `delivery`
- `quality`

Examples:

- `downloads_total` for a Python package is `adoption`
- `workflow_runs_total` is `operations`
- `deployments_total` is `delivery`
- `success_rate` is `quality`

## Registry File

`data/catalog.json` is the root index for everything we track.

It should answer:

- which entities exist
- where their latest and history files live
- which metrics are expected for each entity
- which source system owns the data

Example:

```json
{
  "version": 1,
  "generated_at": "2026-06-28T00:00:00Z",
  "data_dir": "data",
  "entities": [
    {
      "id": "package:hypercli",
      "type": "package",
      "name": "hypercli",
      "source": {
        "provider": "pepy",
        "external_id": "hypercli"
      },
      "paths": {
        "latest": "data/latest/package/hypercli.json",
        "history": "data/history/package/hypercli.jsonl"
      },
      "metrics": [
        "downloads_total",
        "downloads_last_30_days",
        "downloads_last_90_days"
      ]
    }
  ]
}
```

The catalog stores artifact paths relative to the config root so the metadata stays portable across machines and workspaces.

## Latest Snapshot File

Each latest snapshot file should contain:

- stable entity metadata
- a collection timestamp
- source metadata
- a normalized list of metrics

Example:

```json
{
  "schema_version": 1,
  "entity": {
    "id": "package:hypercli",
    "type": "package",
    "name": "hypercli"
  },
  "captured_at": "2026-06-28T00:00:00Z",
  "source": {
    "provider": "pepy",
    "api_url": "https://api.pepy.tech/api/v2/projects/hypercli",
    "fetched_at": "2026-06-28T00:00:00Z"
  },
  "metrics": {
    "downloads_total": {
      "value": 12345,
      "unit": "count",
      "category": "adoption"
    },
    "downloads_last_30_days": {
      "value": 978,
      "unit": "count",
      "category": "adoption"
    },
    "downloads_last_90_days": {
      "value": 2710,
      "unit": "count",
      "category": "adoption"
    }
  }
}
```

## History File

Each history file should be JSON Lines (`.jsonl`), with one observation event per line.

That keeps appends cheap and avoids rewriting a large JSON array.

Example lines:

```json
{"captured_at":"2026-06-28T00:00:00Z","entity_id":"package:hypercli","metric_key":"downloads_total","value":12345,"unit":"count","source":"pepy"}
{"captured_at":"2026-06-28T00:00:00Z","entity_id":"package:hypercli","metric_key":"downloads_last_30_days","value":978,"unit":"count","source":"pepy"}
{"captured_at":"2026-06-28T00:00:00Z","entity_id":"package:hypercli","metric_key":"downloads_last_90_days","value":2710,"unit":"count","source":"pepy"}
```

## Source-Specific Notes

Different providers expose very different raw payloads. We should normalize them into the shared schema rather than storing raw responses as the primary artifact.

Recommended pattern:

- store normalized snapshots in `data/latest`
- append normalized observations to `data/history`
- optionally keep raw API payloads in `data/raw/<provider>/...` only for debugging

Raw payload retention should be optional because it can grow quickly.

## Pepy Mapping

For PyPI package telemetry, `pepy` is a strong source because it gives package download counts in a recruiter-friendly format.

The `pepy` API documentation shows:

- the JSON API base URL is `https://api.pepy.tech`
- requests require an `X-API-Key`
- project responses include `total_downloads`
- project responses include `downloads` grouped by date and version for the last 3 months

That maps cleanly to:

- `downloads_total`
- `downloads_last_30_days`
- `downloads_last_90_days`
- optional per-version metrics later

## Recommended Update Cadence

Because this is not a real-time product, a scheduled refresh is enough:

- every 6 hours for active public metrics
- daily for slower-moving metrics

The collector should overwrite the latest snapshot and append only new history entries for the same run.

## Good V1 Metric Set

Start with a narrow, high-signal set:

- packages: `downloads_total`, `downloads_last_30_days`, `downloads_last_90_days`
- repositories: `stars`, `forks`, `watchers`, `views_total`, `clones_total`
- workflows: `workflow_runs_total`, `workflow_success_total`, `workflow_failure_total`, `workflow_success_rate`
- scripts: `executions_total`, `unique_users`, `unique_hosts`

## Recommended Next Step

Implement the collector contract around these responsibilities:

1. fetch raw provider data
2. map provider fields to normalized metrics
3. write the latest snapshot file
4. append history observations
5. regenerate `data/catalog.json` if tracked entities change
