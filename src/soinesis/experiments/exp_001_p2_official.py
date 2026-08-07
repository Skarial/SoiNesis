"""Orchestration strictement gardée de l'exécution officielle EXP-001-P2.

Ce module ne doit être utilisé qu'après fusion de l'implémentation figée sur
``main``. Il vérifie l'état Git local, l'identité du corpus officiel et
l'absence d'état résiduel avant d'exécuter les cinq jeux puis d'exporter le
bundle brut. Il ne calcule aucune interprétation scientifique.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from soinesis.experiments.exp_001_p2 import ExperimentDataset, load_datasets
from soinesis.experiments.exp_001_p2_export import (
    FROZEN_DATASET_SHA256,
    ExportedRunBundle,
    export_run_bundle,
    verify_frozen_dataset,
)
from soinesis.experiments.exp_001_p2_runner import DatasetRun, run_dataset

OFFICIAL_BRANCH = "main"
OFFICIAL_CONFIRMATION = "RUN EXP-001-P2 OFFICIAL"
OFFICIAL_DATASET_PATH = Path("data/exp-001-p2/datasets-v1.json")
_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class GitRepositoryState(FrozenModel):
    head_commit: str = Field(min_length=40, max_length=40)
    origin_main_commit: str = Field(min_length=40, max_length=40)
    branch: str = Field(min_length=1)
    clean: bool


class OfficialPreconditions(FrozenModel):
    git: GitRepositoryState
    dataset_sha256: str = Field(min_length=64, max_length=64)
    dataset_ids: tuple[str, ...]


class P2OfficialRunError(RuntimeError):
    """Une condition nécessaire à l'exécution officielle P2 n'est pas satisfaite."""


def inspect_git_repository(repo_root: Path) -> GitRepositoryState:
    """Lit uniquement l'état Git local nécessaire au gel officiel."""

    head = _git(repo_root, "rev-parse", "HEAD")
    origin_main = _git(repo_root, "rev-parse", "origin/main")
    branch = _git(repo_root, "branch", "--show-current")
    status = _git(repo_root, "status", "--porcelain=v1", "--untracked-files=all")
    if _COMMIT_PATTERN.fullmatch(head) is None or _COMMIT_PATTERN.fullmatch(origin_main) is None:
        raise P2OfficialRunError("Git n'a pas fourni des SHA complets valides sur 40 caractères.")
    if not branch:
        raise P2OfficialRunError("L'exécution officielle P2 refuse un HEAD détaché.")
    return GitRepositoryState(
        head_commit=head,
        origin_main_commit=origin_main,
        branch=branch,
        clean=(status == ""),
    )


def validate_official_preconditions(
    *,
    repo_root: Path,
    output_directory: Path,
    confirmation: str,
    dataset_path: Path = OFFICIAL_DATASET_PATH,
) -> tuple[OfficialPreconditions, tuple[ExperimentDataset, ...]]:
    """Valide toutes les conditions préalables sans lancer l'expérience."""

    if confirmation != OFFICIAL_CONFIRMATION:
        raise P2OfficialRunError(
            f"Confirmation officielle requise exactement : {OFFICIAL_CONFIRMATION!r}."
        )
    if output_directory.exists():
        raise P2OfficialRunError(
            "Le répertoire de sortie officiel existe déjà ; aucun écrasement n'est autorisé."
        )

    git = inspect_git_repository(repo_root)
    if git.branch != OFFICIAL_BRANCH:
        raise P2OfficialRunError("L'exécution officielle initiale P2 exige la branche main.")
    if git.head_commit != git.origin_main_commit:
        raise P2OfficialRunError(
            "HEAD doit correspondre exactement à origin/main avant le run officiel."
        )
    if not git.clean:
        raise P2OfficialRunError("Le dépôt Git doit être entièrement propre avant le run officiel.")

    try:
        dataset_sha256 = verify_frozen_dataset(dataset_path)
    except (OSError, ValueError) as error:
        raise P2OfficialRunError(
            "Le corpus officiel P2 ne passe pas le contrôle SHA-256."
        ) from error
    if dataset_sha256 != FROZEN_DATASET_SHA256:
        raise P2OfficialRunError("Le corpus P2 chargé n'est pas le corpus officiel préenregistré.")

    datasets = load_datasets(dataset_path)
    if len(datasets) != 5:
        raise P2OfficialRunError("L'exécution officielle P2 exige exactement cinq jeux de données.")
    if len({dataset.id for dataset in datasets}) != 5:
        raise P2OfficialRunError(
            "Les cinq jeux officiels P2 doivent avoir des identifiants uniques."
        )

    return (
        OfficialPreconditions(
            git=git,
            dataset_sha256=dataset_sha256,
            dataset_ids=tuple(dataset.id for dataset in datasets),
        ),
        datasets,
    )


def run_official_experiment(
    *,
    repo_root: Path,
    output_directory: Path,
    confirmation: str,
    dataset_path: Path = OFFICIAL_DATASET_PATH,
) -> ExportedRunBundle:
    """Exécute les cinq jeux officiels puis exporte immédiatement le bundle brut."""

    preconditions, datasets = validate_official_preconditions(
        repo_root=repo_root,
        output_directory=output_directory,
        confirmation=confirmation,
        dataset_path=dataset_path,
    )
    execution_timestamp = datetime.now(UTC)

    with tempfile.TemporaryDirectory(prefix="soinesis-exp-001-p2-official-") as temporary:
        work_root = Path(temporary)
        runs: list[DatasetRun] = []
        for dataset in datasets:
            runs.append(
                run_dataset(
                    dataset=dataset,
                    work_directory=work_root / dataset.id,
                    code_commit=preconditions.git.head_commit,
                    execution_timestamp=execution_timestamp,
                )
            )

        bundle = export_run_bundle(
            output_directory=output_directory,
            dataset_path=dataset_path,
            datasets=datasets,
            runs=tuple(runs),
            code_commit=preconditions.git.head_commit,
        )

    if not bundle.manifest.complete_dataset_suite:
        raise P2OfficialRunError("Le bundle produit n'est pas une suite officielle complète.")
    if bundle.manifest.dataset_sha256 != FROZEN_DATASET_SHA256:
        raise P2OfficialRunError("Le bundle produit ne référence pas le corpus officiel P2.")
    return bundle


def _git(repo_root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "erreur Git inconnue"
        raise P2OfficialRunError(f"Commande Git impossible : {detail}")
    return completed.stdout.strip()
