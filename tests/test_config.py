from __future__ import annotations

from pathlib import Path

from engineering_telemetry.config import load_config


def test_load_config_reads_entities(tmp_path: Path) -> None:
    config_file = tmp_path / "telemetry.toml"
    config_file.write_text(
        """
[project]
data_dir = "data"

[[entities]]
id = "package:hypercli"
type = "package"
name = "hypercli"
collector = "pepy"
metrics = ["downloads_total"]

[entities.source]
provider = "pepy"
external_id = "hypercli"
""".strip()
    )

    config = load_config(config_file)

    assert config.data_dir == tmp_path / "data"
    assert len(config.entities) == 1
    assert config.entity_definitions[0].entity_id == "package:hypercli"
    assert config.entity_definitions[0].metrics == ("downloads_total",)
    assert config.config_path == config_file.resolve()
