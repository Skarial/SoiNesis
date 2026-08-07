"""Gel reproductible et export brut auditable pour EXP-001-P2.

Cette couche ne lance aucune expérience et ne calcule aucune conclusion. Elle
vérifie les entrées figées, ordonne les résultats selon le plan préenregistré,
écrit les artefacts bruts et calcule leurs empreintes SHA-256.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from soinesis.experiments.exp_001_p2 import (
    DATASET_VERSION,
    EXPERIMENT_ID,
    PROTOCOL_VERSION,
    ExperimentDataset,
    load_datasets,
)
from soinesis.experiments.exp_001_p2_plan import TrialPlanEntry, build_trial_plan
from soinesis.experiments.exp_001_p2_runner import DatasetRun, TrialResult

EXPORT_SCHEMA_VERSION = "1.0"
FROZEN_DATASET_SHA256 = "ffe17b73f8072e38358ccfc3aefce0f0a36ad8e67f696172a88fbed1ffcbb2cd"
_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class DatasetExecutionReference(FrozenModel):
    dataset_id: str = Field(min_length=1)
    planned_trial_count: int = Field(ge=1)
    result_count: int = Field(ge=1)
    execution_timestamp: str = Field(min_length=1)


class FreezeManifest(FrozenModel):
    experiment_id: str = Field(min_length=1)
    protocol_version: str = Field(min_length=1)
    dataset_version: str = Field(min_length=1)
    export_schema_version: str = Field(min_length=1)
    dataset_sha256: str = Field(min_length=64, max_length=64)
    trial_plan_sha256: str = Field(min_length=64, max_length=64)
    code_commit: str = Field(min_length=40, max_length=40)
    dataset_ids: tuple[str, ...]
    complete_dataset_suite: bool
    planned_trial_count: int = Field(ge=1)
    result_count: int = Field(ge=1)
    executions: tuple[DatasetExecutionReference, ...]


class ArtifactChecksums(FrozenModel):
    algorithm: str = "sha256"
    freeze_manifest_sha256: str = Field(min_length=64, max_length=64)
    preevaluation_sha256: str = Field(min_length=64, max_length=64)
    raw_trials_sha256: str = Field(min_length=64, max_length=64)


class ExportedRunBundle(FrozenModel):
    output_directory: Path
    freeze_manifest_path: Path
    preevaluation_path: Path
    raw_trials_path: Path
    checksums_path: Path
    manifest: FreezeManifest
    checksums: ArtifactChecksums


def sha256_file(path: Path) -> str:
    """Calcule l'empreinte SHA-256 des octets exacts d'un fichier."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_frozen_dataset(path: Path) -> str:
    """Refuse tout fichier de données différent de la version préenregistrée."""

    digest = sha256_file(path)
    if digest != FROZEN_DATASET_SHA256:
        raise ValueError(
            "Le fichier de données P2 ne correspond pas au SHA-256 préenregistré."
        )
    return digest


def trial_plan_sha256(plan: tuple[TrialPlanEntry, ...]) -> str:
    """Calcule une empreinte canonique du plan d'essais effectivement utilisé."""

    payload = [entry.model_dump(mode="json") for entry in plan]
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def build_freeze_manifest(
    *,
    dataset_path: Path,
    datasets: tuple[ExperimentDataset, ...],
    runs: tuple[DatasetRun, ...],
    code_commit: str,
) -> FreezeManifest:
    """Construit le manifeste avant toute interprétation des résultats."""

    _validate_code_commit(code_commit)
    dataset_digest = verify_frozen_dataset(dataset_path)
    frozen_datasets = load_datasets(dataset_path)
    _validate_dataset_subset(datasets=datasets, frozen_datasets=frozen_datasets)
    _validate_runs(datasets=datasets, runs=runs, code_commit=code_commit)

    plan = build_trial_plan(datasets)
    result_count = sum(len(run.results) for run in runs)
    if result_count != len(plan):
        raise ValueError("Le nombre de résultats P2 ne correspond pas au plan figé.")

    planned_ids = tuple(entry.trial_id for entry in plan)
    actual_ids = _ordered_result_ids(datasets=datasets, runs=runs)
    if actual_ids != planned_ids:
        raise ValueError("L'ordre ou l'identité des essais P2 diffère du plan figé.")

    frozen_ids = tuple(dataset.id for dataset in frozen_datasets)
    selected_ids = tuple(dataset.id for dataset in datasets)
    complete_dataset_suite = selected_ids == frozen_ids

    executions = tuple(
        DatasetExecutionReference(
            dataset_id=run.dataset_id,
            planned_trial_count=run.planned_trial_count,
            result_count=len(run.results),
            execution_timestamp=run.execution_timestamp.isoformat(),
        )
        for run in runs
    )
    return FreezeManifest(
        experiment_id=EXPERIMENT_ID,
        protocol_version=PROTOCOL_VERSION,
        dataset_version=DATASET_VERSION,
        export_schema_version=EXPORT_SCHEMA_VERSION,
        dataset_sha256=dataset_digest,
        trial_plan_sha256=trial_plan_sha256(plan),
        code_commit=code_commit,
        dataset_ids=selected_ids,
        complete_dataset_suite=complete_dataset_suite,
        planned_trial_count=len(plan),
        result_count=result_count,
        executions=executions,
    )


def export_run_bundle(
    *,
    output_directory: Path,
    dataset_path: Path,
    datasets: tuple[ExperimentDataset, ...],
    runs: tuple[DatasetRun, ...],
    code_commit: str,
) -> ExportedRunBundle:
    """Écrit un bundle immuable de données brutes, sans produire d'analyse."""

    if output_directory.exists():
        raise FileExistsError(
            "Le répertoire d'export P2 existe déjà ; aucun écrasement silencieux n'est autorisé."
        )

    manifest = build_freeze_manifest(
        dataset_path=dataset_path,
        datasets=datasets,
        runs=runs,
        code_commit=code_commit,
    )
    ordered_results = _ordered_results(datasets=datasets, runs=runs)

    output_directory.mkdir(parents=True, exist_ok=False)
    manifest_path = output_directory / "freeze-manifest.json"
    preevaluation_path = output_directory / "preevaluation.json"
    raw_trials_path = output_directory / "raw-trials.jsonl"
    checksums_path = output_directory / "checksums.json"

    _write_json(manifest_path, manifest.model_dump(mode="json"))
    _write_json(
        preevaluation_path,
        [
            {
                "dataset_id": run.dataset_id,
                "preevaluation": run.preevaluation.model_dump(mode="json"),
            }
            for run in runs
        ],
    )
    _write_jsonl(raw_trials_path, ordered_results)

    raw_trials_digest = sha256_file(raw_trials_path)
    checksums = ArtifactChecksums(
        freeze_manifest_sha256=sha256_file(manifest_path),
        preevaluation_sha256=sha256_file(preevaluation_path),
        raw_trials_sha256=raw_trials_digest,
    )
    _write_json(checksums_path, checksums.model_dump(mode="json"))

    return ExportedRunBundle(
        output_directory=output_directory,
        freeze_manifest_path=manifest_path,
        preevaluation_path=preevaluation_path,
        raw_trials_path=raw_trials_path,
        checksums_path=checksums_path,
        manifest=manifest,
        checksums=checksums,
    )


def _validate_code_commit(code_commit: str) -> None:
    if _COMMIT_PATTERN.fullmatch(code_commit) is None:
        raise ValueError("Un export P2 exige le SHA Git complet sur 40 caractères hexadécimaux.")


def _validate_dataset_subset(
    *,
    datasets: tuple[ExperimentDataset, ...],
    frozen_datasets: tuple[ExperimentDataset, ...],
) -> None:
    if not datasets:
        raise ValueError("Au moins un jeu de données P2 doit être exporté.")
    frozen_by_id = {dataset.id: dataset for dataset in frozen_datasets}
    if len({dataset.id for dataset in datasets}) != len(datasets):
        raise ValueError("Les jeux de données P2 exportés doivent être uniques.")
    for dataset in datasets:
        if frozen_by_id.get(dataset.id) != dataset:
            raise ValueError(f"Le jeu {dataset.id} ne correspond pas aux données P2 figées.")


def _validate_runs(
    *,
    datasets: tuple[ExperimentDataset, ...],
    runs: tuple[DatasetRun, ...],
    code_commit: str,
) -> None:
    if len(runs) != len(datasets):
        raise ValueError("Il faut exactement un run P2 par jeu exporté.")
    for dataset, run in zip(datasets, runs, strict=True):
        if run.dataset_id != dataset.id:
            raise ValueError("L'ordre des runs P2 doit suivre celui des jeux sélectionnés.")
        if run.experiment_id != EXPERIMENT_ID or run.protocol_version != PROTOCOL_VERSION:
            raise ValueError("Un run P2 ne correspond pas au protocole figé.")
        if run.code_commit != code_commit:
            raise ValueError("Tous les runs P2 doivent provenir du commit figé.")
        if not run.preevaluation.all_valid:
            raise ValueError("Un run P2 invalide en pré-évaluation ne peut pas être exporté.")
        expected_plan = build_trial_plan((dataset,))
        if run.planned_trial_count != len(expected_plan) or len(run.results) != len(expected_plan):
            raise ValueError("Un run P2 est incomplet par rapport au plan figé.")
        if tuple(result.trial_id for result in run.results) != tuple(
            entry.trial_id for entry in expected_plan
        ):
            raise ValueError("Un run P2 ne respecte pas l'ordre local du plan figé.")


def _ordered_result_ids(
    *,
    datasets: tuple[ExperimentDataset, ...],
    runs: tuple[DatasetRun, ...],
) -> tuple[str, ...]:
    return tuple(result.trial_id for result in _ordered_results(datasets=datasets, runs=runs))


def _ordered_results(
    *,
    datasets: tuple[ExperimentDataset, ...],
    runs: tuple[DatasetRun, ...],
) -> tuple[TrialResult, ...]:
    results_by_id: dict[str, TrialResult] = {}
    for run in runs:
        for result in run.results:
            if result.trial_id in results_by_id:
                raise ValueError(f"Essai P2 dupliqué : {result.trial_id}.")
            results_by_id[result.trial_id] = result

    plan = build_trial_plan(datasets)
    planned_ids = {entry.trial_id for entry in plan}
    if set(results_by_id) != planned_ids:
        raise ValueError("Les résultats P2 ne couvrent pas exactement le plan figé.")
    return tuple(results_by_id[entry.trial_id] for entry in plan)


def _write_json(path: Path, payload: object) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(_canonical_json(payload))
        handle.write("\n")


def _write_jsonl(path: Path, results: tuple[TrialResult, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for result in results:
            handle.write(_canonical_json(result.model_dump(mode="json")))
            handle.write("\n")


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
