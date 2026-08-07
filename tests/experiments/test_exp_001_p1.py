from pathlib import Path

from soinesis.domain.models import MemoryType, SourceType
from soinesis.experiments.exp_001_p1 import (
    ExperimentCondition,
    ExperimentRunner,
    TrialType,
    build_summary,
    load_datasets,
)

DATASETS = Path("data/exp-001-p1/datasets-v1.json")


def test_datasets_are_frozen_balanced_and_remapped() -> None:
    datasets = load_datasets(DATASETS)
    assert len(datasets) == 5
    assert all(len(dataset.items) == 20 for dataset in datasets)
    for dataset in datasets:
        counts = {source: 0 for source in SourceType}
        for item in dataset.items:
            counts[item.source_type] += 1
        assert counts[SourceType.JORDAN_INPUT] == 5
        assert counts[SourceType.EXTERNAL_TOOL] == 5
        assert counts[SourceType.DEDUCTION] == 5
        assert counts[SourceType.IMAGINATION] == 5
        assert len(dataset.false_source_slots) == 5
        assert len(dataset.false_contents) == 5
    assert len({dataset.items[0].source_type for dataset in datasets}) > 1


def test_memory_types_follow_provenance() -> None:
    for dataset in load_datasets(DATASETS):
        for item in dataset.items:
            if item.source_type is SourceType.DEDUCTION:
                assert item.memory_type is MemoryType.DEDUCTION
            elif item.source_type is SourceType.IMAGINATION:
                assert item.memory_type is MemoryType.IMAGINED_SCENARIO
            else:
                assert item.memory_type is MemoryType.RECEIVED_INFORMATION


def test_summary_b_stays_unstructured() -> None:
    summary = build_summary(load_datasets(DATASETS)[0])
    for structured_token in ("JORDAN_INPUT", "EXTERNAL_TOOL", "DEDUCTION", "IMAGINATION"):
        assert structured_token not in summary
    assert "memory_" not in summary
    assert len(summary.splitlines()) == 20


def test_full_p1_run_is_auditable_and_ablation_is_real(tmp_path: Path) -> None:
    run = ExperimentRunner(
        datasets=load_datasets(DATASETS),
        work_dir=tmp_path / "work",
        code_commit="test-commit",
    ).run()
    assert len(run.metrics) == 15
    assert run.assessment.ablation_valid is True
    ablations = [result for result in run.results if result.trial_type is TrialType.ABLATION]
    assert len(ablations) == 25
    assert all(result.condition is ExperimentCondition.C for result in ablations)
    assert all(result.memory_repository_access_count == 0 for result in ablations)
    assert all(not result.retrieved_memory_ids for result in ablations)
    assert len(run.results) == 5 * 3 * 70 + 25


def test_condition_c_rejects_false_source_attributions(tmp_path: Path) -> None:
    run = ExperimentRunner(
        datasets=load_datasets(DATASETS),
        work_dir=tmp_path / "work",
        code_commit="test-commit",
    ).run()
    misleading = [
        result
        for result in run.results
        if result.condition is ExperimentCondition.C
        and result.trial_type
        in {
            TrialType.T4_FALSE_ATTRIBUTION,
            TrialType.T6_DEDUCTION_CONFUSION,
            TrialType.T7_IMAGINATION_CONFUSION,
        }
    ]
    assert misleading
    assert all(result.source_correct for result in misleading)
    assert all(result.misleading_suggestion_rejected for result in misleading)
