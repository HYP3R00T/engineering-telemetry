"""Shared helpers for GitHub-backed collectors."""

from __future__ import annotations

import os

from engineering_telemetry.collectors.base import CollectorError


def github_headers() -> dict[str, str]:
    """Return standard headers for GitHub REST API requests."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "engineering-telemetry",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def parse_repository(value: str, *, source_name: str) -> tuple[str, str]:
    """Parse a GitHub repository identifier in owner/repository format."""
    parts = value.split("/", maxsplit=1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise CollectorError(f"{source_name} source.external_id must be in 'owner/repository' format.")
    return parts[0], parts[1]


def as_int(value: object) -> int:
    """Convert GitHub numeric values into integers."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str) and value.strip():
        return int(value)
    raise CollectorError(f"Expected an integer-compatible value, received {value!r}.")
