from __future__ import annotations

import json
from pathlib import Path

import pytest

import soinesis.experiments.exp_001_p2_export as export_module
from soinesis.experiments.exp_001_p2 import load_datasets
from soinesis.experiments.exp_001_p2_analysis import (
    HypothesisAssessment,
    P2Analysis,
    P2AnalysisError,
    analyze_run_bundle,
)
from soinesis.experiments.exp_001_p2_export import export_run_bundle, sha256_file
from soinesis.experiments.exp_001_p2_runner import DatasetRun, run_dataset

_OFFICIAL_DATASET_PATH = Path("data/exp-001-p2/datasets-v1.json")
_CODE_COMMIT = "3" * 40


def _development_dataset_file(tmp_path: Path) -> Path:
    payload = json.loads(_OFFICIAL_DATASET_PATH.read_text(encoding="utf-8"))
    for dataset in payload["datasets"]:
        dataset["id"] = f"analysis-dev-{dataset['id']}"
        dataset["namespace"] = f"analysis-dev-{dataset['namespace']}"
    for chain in payload["chains"]:
        chain["subject_template"] = f"ANALYSIS DEV {chain['subject_template']}"
        chain["values"] = [f"analysis-dev-{value}" for value in chain["values"]]
        if chain["misleading_value"] is not None:
            chain["misleading_value"] = f"analysis-dev-{chain['misleading_value']}"

    path = tmp_path / "analysis-development-datasets.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


@pytest.fixture(scope="module")
def development_bundle(
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch_module: pytest.MonkeyPatch,
) -> tuple[Path, Path]:
    root = tmp_path_factory.mktemp("p2-analysis")
    dataset_path = _development_dataset_file(root)
    monkeypatch_module.setattr(export_module, "FROZEN_DATASET_SHA256", sha256_file(dataset_path))
    datasets = load_datasets(dataset_path)
    runs: list[DatasetRun] = []
    for dataset in datasets:
        runs.append(
            run_dataset(
                dataset=dataset,
                work_directory=root / "runs" / dataset.id,
                code_commit=_CODE_COMMIT,
            )
        )
    bundle_directory = root / "bundle"
    export_run_bundle(
        output_directory=bundle_directory,
        dataset_path=dataset_path,
        datasets=datasets,
        runs=tuple(runs),
        code_commit=_CODE_COMMIT,
    )
    return dataset_path, bundle_directory


@pytest.fixture(scope="module")
def monkeypatch_module(request: pytest.FixtureRequest) -> pytest.MonkeyPatch:
    patch = pytest.MonkeyPatch()
    request.addfinalizer(patch.undo)
    return patch


def test_analysis_applies_only_preregistered_thresholds_to_verified_bundle(
    development_bundle: tuple[Path, Path],
) -> None:
    dataset_path, bundle_directory = development_bundle

    analysis = analyze_run_bundle(
        bundle_directory=bundle_directory,
        dataset_path=dataset_path,
        require_official_dataset=False,
    )

    assert isinstance(analysis, P2Analysis)
    assert analysis.integrity.all_valid is True
    assert analysis.integrity.complete_dataset_suite is True
    assert analysis.primary_continuity_h01_h02_h03.c_overall_rate == 1.0
    assert analysis.primary_continuity_h01_h02_h03.b_overall_rate == 1.0
    assert analysis.primary_continuity_h01_h02_h03.assessment is HypothesisAssessment.NOT_SUPPORTED
    assert analysis.traceability_h04.assessment is HypothesisAssessment.NOT_SUPPORTED
    assert analysis.rewrite_h05.assessment is HypothesisAssessment.ABSOLUTE_INTEGRITY_ONLY
    assert (
        analysis.ablation_h06.assessment
        is HypothesisAssessment.AUTOMATED_CRITERIA_MET_MANUAL_AUDIT_REQUIRED
    )


def test_analysis_rejects_tampered_raw_results(
    tmp_path: Path,
    development_bundle: tuple[Path, Path],
) -> None:
    dataset_path, source_bundle = development_bundle
    tampered_bundle = tmp_path / "tampered-bundle"
    tampered_bundle.mkdir()
    for name in (
        "freeze-manifest.json",
        "preevaluation.json",
        "raw-trials.jsonl",
        "checksums.json",
    ):
        (tampered_bundle / name).write_bytes((source_bundle / name).read_bytes())
    with (tampered_bundle / "raw-trials.jsonl").open("a", encoding="utf-8") as handle:
        handle.write("{}\n")

    with pytest.raises(P2AnalysisError, match="intégrité pré-analyse"):
        analyze_run_bundle(
            bundle_directory=tampered_bundle,
            dataset_path=dataset_path,
            require_official_dataset=False,
        )


def test_official_analysis_gate_rejects_development_dataset(
    development_bundle: tuple[Path, Path],
) -> None:
    dataset_path, bundle_directory = development_bundle

    with pytest.raises(P2AnalysisError, match="intégrité pré-analyse"):
        analyze_run_bundle(
            bundle_directory=bundle_directory,
            dataset_path=dataset_path,
        )
