from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

import soinesis.cli as cli_module
from soinesis.experiments.exp_001_p2_export import ExportedRunBundle


def test_cli_routes_guarded_official_p2_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: dict[str, object] = {}

    def fake_official_run(
        *,
        repo_root: Path,
        output_directory: Path,
        confirmation: str,
    ) -> ExportedRunBundle:
        observed["repo_root"] = repo_root
        observed["output_directory"] = output_directory
        observed["confirmation"] = confirmation
        return cast(ExportedRunBundle, object())

    monkeypatch.setattr(cli_module, "run_official_experiment", fake_official_run)

    result = cli_module.main(
        (
            "exp-001-p2",
            "run-official",
            "--repo-root",
            str(tmp_path),
            "--output",
            "results/official-p2",
            "--confirm",
            "RUN EXP-001-P2 OFFICIAL",
        )
    )

    assert result == 0
    assert observed == {
        "repo_root": tmp_path.resolve(),
        "output_directory": tmp_path.resolve() / "results/official-p2",
        "confirmation": "RUN EXP-001-P2 OFFICIAL",
    }
