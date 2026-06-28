---
icon: lucide/rocket
---

# Get started

Build a reusable engineering telemetry aggregator that collects adoption, delivery, and operational metrics into a JSON-first data store.

This project is focused on consolidating metrics from services like PyPI, GitHub, CI workflows, and custom analytics counters so other applications can read one normalized source of truth.

## Why This Project Exists

- **Centralized telemetry:** collect metrics once and let multiple apps consume the stored results.
- **Scheduled, not real-time:** refresh data periodically without hammering upstream APIs.
- **Normalized output:** convert provider-specific payloads into a stable internal schema.
- **History included:** preserve snapshots over time for reporting and trend analysis.

## What This Will Track

- **Package adoption:** package download totals and recent download windows.
- **Repository reach:** stars, forks, views, clones, and release activity.
- **Workflow operations:** CI run counts, success rates, and execution trends.
- **Script usage:** custom analytics such as executions, unique users, or unique hosts.

## Start Here

- **Learn how to run the collector:** setup, config, commands, and output locations are documented in the usage guide.
  [Open Usage Guide](usage.md)
- **Review telemetry storage design:** see the proposed schema and folder structure for collected metrics.
  [Open Storage Model](storage-model.md)
