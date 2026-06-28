from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from engineering_telemetry.cli import app

runner = CliRunner()


def test_show_plan_uses_repo_local_config(tmp_path: Path) -> None:
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
api_url = "https://api.pepy.tech/api/v2/projects/hypercli"
""".strip()
    )

    result = runner.invoke(app, ["--config", str(config_file), "show-plan"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["config_path"] == config_file.resolve().as_posix()
    assert payload["entities"][0]["id"] == "package:hypercli"
