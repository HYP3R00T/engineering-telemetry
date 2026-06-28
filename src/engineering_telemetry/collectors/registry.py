"""Collector registry for config-driven execution."""

from __future__ import annotations

from collections.abc import Iterable

from engineering_telemetry.collectors.base import Collector, CollectorError
from engineering_telemetry.collectors.github_actions import GitHubActionsCollector
from engineering_telemetry.collectors.github_releases import GitHubReleasesCollector
from engineering_telemetry.collectors.pepy import PepyCollector


class CollectorRegistry:
    """Resolve configured collector names to implementations."""

    def __init__(self, collectors: dict[str, Collector] | None = None) -> None:
        self._collectors = collectors or {}

    def register(self, name: str, collector: Collector) -> None:
        """Register a collector instance."""
        self._collectors[name] = collector

    def get(self, name: str) -> Collector:
        """Return a collector or raise a useful error."""
        try:
            return self._collectors[name]
        except KeyError as error:
            available = ", ".join(sorted(self._collectors)) or "<none>"
            raise CollectorError(f"Unknown collector {name!r}. Available collectors: {available}") from error

    def names(self) -> Iterable[str]:
        """Return registered collector names."""
        return self._collectors.keys()


def default_registry() -> CollectorRegistry:
    """Return the built-in collector registry."""
    registry = CollectorRegistry()
    registry.register("github_actions", GitHubActionsCollector())
    registry.register("github_releases", GitHubReleasesCollector())
    registry.register("pepy", PepyCollector())
    return registry
