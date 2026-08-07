from __future__ import annotations

import json
from pathlib import Path

import pytest

import soinesis.experiments.exp_001_p2_export as export_module
from soinesis.experiments.exp_001_p2 import ExperimentDataset, load_datasets
from soinesis.experiments.exp_001_p2_export import (
    FROZEN_DATASET_SHA256,
    ExportedRunBundle,
    build_freeze_manifest,
    export_run_bundle,
    sha256_file,
    verify_frozen_dataset,
)
from soinesis.experiments.exp_001_p2_runner import DatasetRun, run_dataset

_DATASET_PATH = Path("data/exp-001-p2/datasets-v1.json")
_CODE_COMMIT = "1" * 40


def _development_dataset_file(tmp_path: Path) -> Path:
    """Crée un corpus de développement distinct sans exécuter les valeurs officielles."""

    payload = json.loads(_DATASET_PATH.read_text(encoding="utf-8"))
    for dataset in payload["datasets"]:
        dataset["id"] = f"dev-{dataset['id']}"
        dataset["namespace"] = f"dev-{dataset['namespace']}"
    for chain in payload["chains"]:
        chain["subject_template"] = f"DEV {chain['subject_template']}"
        chain["values"] = [f"dev-{value}" for value in chain["values"]]
        if chain["misleading_value"] is not None:
            chain["misleading_value"] = f"dev-{chain['misleading_value']}"

    path = tmp_path / "datasets-development.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


@pytest.fixture
def development_export_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Path, ExperimentDataset, DatasetRun]:
    dataset_path = _development_dataset_file(tmp_path)
    monkeypatch.setattr(export_module, "FROZEN_DATASET_SHA256", sha256_file(dataset_path))
    dataset = load_datasets(dataset_path)[0]
    run = run_dataset(
        dataset=dataset,
        work_directory=tmp_path / "p2-export-run",
        code_commit=_CODE_COMMIT,
    )
    return dataset_path, dataset, run


def test_frozen_dataset_matches_preregistered_byte_hash(tmp_path: Path) -> None:
    assert verify_frozen_dataset(_DATASET_PATH) == FROZEN_DATASET_SHA256
    assert sha256_file(_DATASET_PATH) == FROZEN_DATASET_SHA256

    altered = tmp_path / "datasets-altered.json"
    altered.write_bytes(_DATASET_PATH.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="SHA-256 préenregistré"):
        verify_frozen_dataset(altered)


def test_export_writes_raw_trials_in_frozen_order_with_immediate_checksums(
    tmp_path: Path,
    development_export_run: tuple[Path, ExperimentDataset, DatasetRun],
) -> None:
    dataset_path, dataset, run = development_export_run
    bundle = export_run_bundle(
        output_directory=tmp_path / "bundle",
        dataset_path=dataset_path,
        datasets=(dataset,),
        runs=(run,),
        code_commit=_CODE_COMMIT,
    )

    assert isinstance(bundle, ExportedRunBundle)
    assert bundle.manifest.dataset_sha256 == sha256_file(dataset_path)
    assert bundle.manifest.complete_dataset_suite is False
    assert bundle.manifest.result_count == len(run.results)
    assert bundle.checksums.raw_trials_sha256 == sha256_file(bundle.raw_trials_path)
    assert bundle.checksums.freeze_manifest_sha256 == sha256_file(bundle.freeze_manifest_path)
    assert bundle.checksums.preevaluation_sha256 == sha256_file(bundle.preevaluation_path)

    raw_lines = bundle.raw_trials_path.read_text(encoding="utf-8").splitlines()
    raw_trial_ids = tuple(json.loads(line)["trial_id"] for line in raw_lines)
    assert raw_trial_ids == tuple(result.trial_id for result in run.results)
    assert len(raw_lines) == run.planned_trial_count

    checksums_payload = json.loads(bundle.checksums_path.read_text(encoding="utf-8"))
    assert checksums_payload["raw_trials_sha256"] == bundle.checksums.raw_trials_sha256


def test_export_refuses_to_overwrite_an_existing_bundle(
    tmp_path: Path,
    development_export_run: tuple[Path, ExperimentDataset, DatasetRun],
) -> None:
    dataset_path, dataset, run = development_export_run
    output_directory = tmp_path / "bundle-once"
    export_run_bundle(
        output_directory=output_directory,
        dataset_path=dataset_path,
        datasets=(dataset,),
        runs=(run,),
        code_commit=_CODE_COMMIT,
    )

    with pytest.raises(FileExistsError, match="aucun écrasement silencieux"):
        export_run_bundle(
            output_directory=output_directory,
            dataset_path=dataset_path,
            datasets=(dataset,),
            runs=(run,),
            code_commit=_CODE_COMMIT,
        )


def test_manifest_rejects_a_commit_different_from_the_executed_run(
    development_export_run: tuple[Path, ExperimentDataset, DatasetRun],
) -> None:
    dataset_path, dataset, run = development_export_run

    with pytest.raises(ValueError, match="commit figé"):
        build_freeze_manifest(
            dataset_path=dataset_path,
            datasets=(dataset,),
            runs=(run,),
            code_commit="2" * 40,
        )
