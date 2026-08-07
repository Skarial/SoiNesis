from __future__ import annotations

from pathlib import Path

import pytest

import soinesis.experiments.exp_001_p2_official as official_module
from soinesis.experiments.exp_001_p2 import ExperimentDataset
from soinesis.experiments.exp_001_p2_export import FROZEN_DATASET_SHA256
from soinesis.experiments.exp_001_p2_official import (
    OFFICIAL_CONFIRMATION,
    OFFICIAL_DATASET_PATH,
    GitRepositoryState,
    P2OfficialRunError,
    validate_official_preconditions,
)


def _git_state(
    *,
    branch: str = "main",
    clean: bool = True,
    head_commit: str = "1" * 40,
    origin_main_commit: str = "1" * 40,
) -> GitRepositoryState:
    return GitRepositoryState(
        head_commit=head_commit,
        origin_main_commit=origin_main_commit,
        branch=branch,
        clean=clean,
    )


def _development_datasets() -> tuple[ExperimentDataset, ...]:
    return tuple(
        ExperimentDataset(
            id=f"dev-dataset-{index}",
            namespace=f"dev-namespace-{index}",
            events=(),
            chains=(),
        )
        for index in range(1, 6)
    )


def _valid_git_state(_: Path) -> GitRepositoryState:
    return _git_state()


def _valid_dataset_hash(_: Path) -> str:
    return FROZEN_DATASET_SHA256


def _valid_development_datasets(_: Path) -> tuple[ExperimentDataset, ...]:
    return _development_datasets()


def _patch_valid_external_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(official_module, "inspect_git_repository", _valid_git_state)
    monkeypatch.setattr(official_module, "verify_frozen_dataset", _valid_dataset_hash)
    monkeypatch.setattr(official_module, "load_datasets", _valid_development_datasets)


def test_official_preconditions_require_exact_explicit_confirmation(tmp_path: Path) -> None:
    with pytest.raises(P2OfficialRunError, match="Confirmation officielle requise"):
        validate_official_preconditions(
            repo_root=tmp_path,
            output_directory=tmp_path / "bundle",
            confirmation="yes",
        )


def test_official_preconditions_reject_feature_branch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def feature_branch_state(_: Path) -> GitRepositoryState:
        return _git_state(branch="agent/implementer-exp-001-p2")

    monkeypatch.setattr(
        official_module,
        "inspect_git_repository",
        feature_branch_state,
    )

    with pytest.raises(P2OfficialRunError, match="branche main"):
        validate_official_preconditions(
            repo_root=tmp_path,
            output_directory=tmp_path / "bundle",
            confirmation=OFFICIAL_CONFIRMATION,
        )


def test_official_preconditions_reject_dirty_or_unpublished_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def dirty_git_state(_: Path) -> GitRepositoryState:
        return _git_state(clean=False)

    monkeypatch.setattr(
        official_module,
        "inspect_git_repository",
        dirty_git_state,
    )
    with pytest.raises(P2OfficialRunError, match="entièrement propre"):
        validate_official_preconditions(
            repo_root=tmp_path,
            output_directory=tmp_path / "dirty",
            confirmation=OFFICIAL_CONFIRMATION,
        )

    def unpublished_git_state(_: Path) -> GitRepositoryState:
        return _git_state(origin_main_commit="2" * 40)

    monkeypatch.setattr(
        official_module,
        "inspect_git_repository",
        unpublished_git_state,
    )
    with pytest.raises(P2OfficialRunError, match="origin/main"):
        validate_official_preconditions(
            repo_root=tmp_path,
            output_directory=tmp_path / "unpublished",
            confirmation=OFFICIAL_CONFIRMATION,
        )


def test_git_inspection_rejects_stale_origin_main(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    local_sha = "1" * 40
    remote_sha = "2" * 40
    responses: dict[tuple[str, ...], str] = {
        ("rev-parse", "HEAD"): local_sha,
        ("rev-parse", "origin/main"): local_sha,
        ("ls-remote", "origin", "refs/heads/main"): f"{remote_sha}\trefs/heads/main",
        ("branch", "--show-current"): "main",
        ("status", "--porcelain=v1", "--untracked-files=all"): "",
    }

    def fake_git(_: Path, *arguments: str) -> str:
        return responses[arguments]

    monkeypatch.setattr(official_module, "_git", fake_git)

    with pytest.raises(P2OfficialRunError, match="périmée"):
        official_module.inspect_git_repository(tmp_path)


def test_official_preconditions_anchor_dataset_to_repository_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed_paths: list[Path] = []

    def record_dataset_hash(path: Path) -> str:
        observed_paths.append(path)
        return FROZEN_DATASET_SHA256

    def record_dataset_load(path: Path) -> tuple[ExperimentDataset, ...]:
        observed_paths.append(path)
        return _development_datasets()

    monkeypatch.setattr(official_module, "inspect_git_repository", _valid_git_state)
    monkeypatch.setattr(official_module, "verify_frozen_dataset", record_dataset_hash)
    monkeypatch.setattr(official_module, "load_datasets", record_dataset_load)

    validate_official_preconditions(
        repo_root=tmp_path,
        output_directory=tmp_path / "bundle",
        confirmation=OFFICIAL_CONFIRMATION,
    )

    expected = tmp_path / OFFICIAL_DATASET_PATH
    assert observed_paths == [expected, expected]


def test_official_preconditions_accept_only_frozen_complete_suite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_external_state(monkeypatch)

    preconditions, datasets = validate_official_preconditions(
        repo_root=tmp_path,
        output_directory=tmp_path / "bundle",
        confirmation=OFFICIAL_CONFIRMATION,
    )

    assert preconditions.git.branch == "main"
    assert preconditions.git.clean is True
    assert preconditions.git.head_commit == preconditions.git.origin_main_commit
    assert preconditions.dataset_sha256 == FROZEN_DATASET_SHA256
    assert preconditions.dataset_ids == tuple(dataset.id for dataset in datasets)
    assert len(datasets) == 5


def test_official_preconditions_refuse_existing_output_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_external_state(monkeypatch)
    output_directory = tmp_path / "bundle"
    output_directory.mkdir()

    with pytest.raises(P2OfficialRunError, match="existe déjà"):
        validate_official_preconditions(
            repo_root=tmp_path,
            output_directory=output_directory,
            confirmation=OFFICIAL_CONFIRMATION,
        )
