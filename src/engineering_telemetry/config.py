"""Configuration models and loading for telemetry collection."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, PrivateAttr
from utilityhub_config import load_settings
from utilityhub_config.metadata import SettingsMetadata

from engineering_telemetry.models import EntityDefinition, EntityType, SourceDefinition


class ProjectSettings(BaseModel):
    """Top-level project settings."""

    data_dir: Path = Path("data")


class SourceSettings(BaseModel):
    """Provider-specific source configuration."""

    provider: str
    external_id: str
    api_url: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class EntitySettings(BaseModel):
    """Configuration for one tracked entity."""

    id: str
    type: EntityType
    name: str
    collector: str
    metrics: list[str] = Field(default_factory=list)
    source: SourceSettings
    settings: dict[str, Any] = Field(default_factory=dict)

    def to_definition(self) -> EntityDefinition:
        """Convert validated settings into the runtime entity definition."""
        return EntityDefinition(
            entity_id=self.id,
            entity_type=self.type,
            name=self.name,
            collector=self.collector,
            metrics=tuple(self.metrics),
            source=SourceDefinition(
                provider=self.source.provider,
                external_id=self.source.external_id,
                api_url=self.source.api_url,
                options=dict(self.source.options),
            ),
            settings=dict(self.settings),
        )


class TelemetryConfig(BaseModel):
    """Validated telemetry configuration loaded by utilityhub_config."""

    project: ProjectSettings = Field(default_factory=ProjectSettings)
    entities: list[EntitySettings] = Field(default_factory=list)

    _config_path: Path = PrivateAttr(default=Path("telemetry.toml"))
    _metadata: SettingsMetadata = PrivateAttr(default_factory=lambda: SettingsMetadata(per_field={}))

    @property
    def config_path(self) -> Path:
        """Return the path used to load this config."""
        return self._config_path

    @property
    def metadata(self) -> SettingsMetadata:
        """Expose utilityhub_config source metadata."""
        return self._metadata

    @property
    def data_dir(self) -> Path:
        """Return the resolved output directory for generated telemetry data."""
        data_dir = self.project.data_dir
        if data_dir.is_absolute():
            return data_dir
        return self.config_path.parent / data_dir

    @property
    def entity_definitions(self) -> tuple[EntityDefinition, ...]:
        """Return runtime entity definitions derived from the config."""
        return tuple(entity.to_definition() for entity in self.entities)


def load_config(path: str | Path) -> TelemetryConfig:
    """Load telemetry settings through utilityhub_config."""
    config_path = Path(path).resolve()
    settings, metadata = load_settings(
        TelemetryConfig,
        app_name="engineering-telemetry",
        cwd=config_path.parent,
        env_prefix="ENGINEERING_TELEMETRY",
        config_file=config_path,
    )
    settings._config_path = config_path
    settings._metadata = metadata
    return settings
