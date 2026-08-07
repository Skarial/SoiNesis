"""Orchestration strictement gardée de l'exécution officielle EXP-001-P2.

Ce module ne doit être utilisé qu'après fusion de l'implémentation figée sur
``main``. Il vérifie l'état Git local et distant, l'identité du corpus officiel
et l'absence d'état résiduel avant d'exécuter les cinq jeux puis d'exporter le
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
_REMOTE_MAIN_REF = "refs/heads/main"


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
    """Vérifie l'état Git local et la fraîcheur de la référence distante main."""

    head = _git(repo_root, "rev-parse", "HEAD")
    origin_main = _git(repo_root, "rev-parse", "origin/main")
    remote_main = _remote_main_commit(repo_root)
    branch = _git(repo_root, "branch", "--show-current")
    status = _git(repo_root, "status", "--porcelain=v1", "--untracked-files=all")
    if _COMMIT_PATTERN.fullmatch(head) is None or _COMMIT_PATTERN.fullmatch(origin_main) is None:
        raise P2OfficialRunError("Git n'a pas fourni des SHA complets valides sur 40 caractères.")
    if origin_main != remote_main:
        raise P2OfficialRunError(
            "La référence locale origin/main est périmée par rapport au dépôt distant."
        )
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

    resolved_dataset_path = _resolve_dataset_path(repo_root, dataset_path)
    try:
        dataset_sha256 = verify_frozen_dataset(resolved_dataset_path)
    except (OSError, ValueError) as error:
        raise P2OfficialRunError(
            "Le corpus officiel P2 ne passe pas le contrôle SHA-256."
        ) from error
    if dataset_sha256 != FROZEN_DATASET_SHA256:
        raise P2OfficialRunError("Le corpus P2 chargé n'est pas le corpus officiel préenregistré.")

    datasets = load_datasets(resolved_dataset_path)
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

    resolved_dataset_path = _resolve_dataset_path(repo_root, dataset_path)
    preconditions, datasets = validate_official_preconditions(
        repo_root=repo_root,
        output_directory=output_directory,
        confirmation=confirmation,
        dataset_path=resolved_dataset_path,
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
            dataset_path=resolved_dataset_path,
            datasets=datasets,
            runs=tuple(runs),
            code_commit=preconditions.git.head_commit,
        )

    if not bundle.manifest.complete_dataset_suite:
        raise P2OfficialRunError("Le bundle produit n'est pas une suite officielle complète.")
    if bundle.manifest.dataset_sha256 != FROZEN_DATASET_SHA256:
        raise P2OfficialRunError("Le bundle produit ne référence pas le corpus officiel P2.")
    return bundle


def _resolve_dataset_path(repo_root: Path, dataset_path: Path) -> Path:
    return dataset_path if dataset_path.is_absolute() else repo_root / dataset_path


def _remote_main_commit(repo_root: Path) -> str:
    output = _git(repo_root, "ls-remote", "origin", _REMOTE_MAIN_REF)
    fields = output.split()
    if len(fields) != 2 or fields[1] != _REMOTE_MAIN_REF:
        raise P2OfficialRunError("Impossible d'identifier précisément la branche main distante.")
    commit = fields[0]
    if _COMMIT_PATTERN.fullmatch(commit) is None:
        raise P2OfficialRunError("Le dépôt distant n'a pas fourni un SHA main valide.")
    return commit


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
