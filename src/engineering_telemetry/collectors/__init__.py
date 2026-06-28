"""Collector implementations and registry."""

from engineering_telemetry.collectors.base import Collector, CollectorError
from engineering_telemetry.collectors.github_actions import GitHubActionsCollector
from engineering_telemetry.collectors.github_releases import GitHubReleasesCollector
from engineering_telemetry.collectors.pepy import PepyCollector
from engineering_telemetry.collectors.registry import CollectorRegistry, default_registry

__all__ = [
    "Collector",
    "CollectorError",
    "CollectorRegistry",
    "GitHubActionsCollector",
    "GitHubReleasesCollector",
    "PepyCollector",
    "default_registry",
]
