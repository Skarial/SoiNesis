from __future__ import annotations

from datetime import UTC, datetime

import pytest

from soinesis.domain.models import MemoryType, SourceType
from soinesis.experiments.exp_001_p2 import (
    ChainFamily,
    DatasetEvent,
    EventKind,
    ExperimentChain,
    ExperimentDataset,
)
from soinesis.experiments.exp_001_p2_plan import TrialType, build_trial_plan
from soinesis.experiments.exp_001_p2_readers import ExperimentCondition
from soinesis.experiments.exp_001_p2_runner import DatasetRun, ResolutionStatus, run_dataset

_CHAIN_SPECS = (
    (
        ChainFamily.S1_SIMPLE_CORRECTION,
        (EventKind.INITIAL, EventKind.CONFIRMATION, EventKind.CORRECTION, EventKind.CONFIRMATION),
        ("alpha", "alpha", "beta", "beta"),
        None,
    ),
    (
        ChainFamily.S2_MULTIPLE_REVISIONS,
        (EventKind.INITIAL, EventKind.CORRECTION, EventKind.CORRECTION, EventKind.CORRECTION),
        ("un", "deux", "trois", "quatre"),
        None,
    ),
    (
        ChainFamily.S3_UNRESOLVED_CONTRADICTION,
        (
            EventKind.INITIAL,
            EventKind.CONFIRMATION,
            EventKind.CONTRADICTION,
            EventKind.CONFIRMATION,
        ),
        ("nord", "nord", "sud", "sud"),
        None,
    ),
    (
        ChainFamily.S4_CONTRADICTION_RESOLUTION,
        (
            EventKind.INITIAL,
            EventKind.CONTRADICTION,
            EventKind.CONFIRMATION,
            EventKind.RESOLUTION,
        ),
        ("rouge", "bleu", "bleu", "vert"),
        None,
    ),
    (
        ChainFamily.S5_CONFIRMATION_NO_CHANGE,
        (
            EventKind.INITIAL,
            EventKind.CONFIRMATION,
            EventKind.CONFIRMATION,
            EventKind.CONFIRMATION,
        ),
        ("stable", "stable", "stable", "stable"),
        None,
    ),
    (
        ChainFamily.S6_MISLEADING_REWRITE,
        (EventKind.INITIAL, EventKind.CORRECTION, EventKind.CONFIRMATION, EventKind.CORRECTION),
        ("ancien", "intermédiaire", "intermédiaire", "final"),
        "jamais-enregistré",
    ),
)


def _memory_type(source: SourceType) -> MemoryType:
    return (
        MemoryType.DEDUCTION if source is SourceType.DEDUCTION else MemoryType.RECEIVED_INFORMATION
    )


def _content(kind: EventKind, subject: str, value: str) -> str:
    if kind is EventKind.INITIAL:
        return f"{subject} est « {value} »."
    if kind is EventKind.CORRECTION:
        return f"Correction explicite : {subject} est désormais « {value} »."
    if kind is EventKind.CONTRADICTION:
        return f"Information contradictoire : {subject} est « {value} »."
    if kind is EventKind.RESOLUTION:
        return f"Résolution explicite : {subject} est fixé à « {value} »."
    return f"Confirmation : {subject} reste « {value} »."


def _reason(kind: EventKind) -> str:
    return {
        EventKind.INITIAL: "État initial reçu.",
        EventKind.CORRECTION: "Correction explicite de la croyance précédente.",
        EventKind.CONTRADICTION: "Contradiction explicite laissée non résolue.",
        EventKind.RESOLUTION: "Résolution explicite de la contradiction.",
        EventKind.CONFIRMATION: "Confirmation sans changement de croyance.",
    }[kind]


def _fixture_dataset() -> ExperimentDataset:
    dataset_id = "fixture-runner"
    sources = (
        SourceType.JORDAN_INPUT,
        SourceType.EXTERNAL_TOOL,
        SourceType.DEDUCTION,
    )
    all_events: list[DatasetEvent] = []
    chains: list[ExperimentChain] = []
    position = 0

    for slot, (family, kinds, values, misleading_value) in enumerate(_CHAIN_SPECS, start=1):
        subject = f"Sujet runner {slot}"
        belief_key = f"{dataset_id}:belief:{slot:02d}"
        chain_events: list[DatasetEvent] = []
        for event_number, (kind, value) in enumerate(zip(kinds, values, strict=True), start=1):
            position += 1
            source = sources[(position - 1) % len(sources)]
            event = DatasetEvent(
                id=f"{dataset_id}-event-{position:03d}",
                dataset_id=dataset_id,
                stream_position=position,
                chain_slot=slot,
                event_number=event_number,
                cycle_id=f"{dataset_id}-cycle-{position:03d}",
                belief_key=belief_key,
                subject=subject,
                family=family,
                kind=kind,
                value=value,
                content=_content(kind, subject, value),
                transition_reason=_reason(kind),
                source_type=source,
                memory_type=_memory_type(source),
            )
            all_events.append(event)
            chain_events.append(event)
        chains.append(
            ExperimentChain(
                id=f"{dataset_id}-chain-{slot:02d}",
                dataset_id=dataset_id,
                slot=slot,
                belief_key=belief_key,
                subject=subject,
                family=family,
                historical_event_number=2,
                misleading_value=misleading_value,
                events=tuple(chain_events),
            )
        )

    return ExperimentDataset(
        id=dataset_id,
        namespace="fixture-only",
        events=tuple(all_events),
        chains=tuple(chains),
    )


@pytest.fixture(scope="module")
def runner_output(tmp_path_factory: pytest.TempPathFactory) -> DatasetRun:
    dataset = _fixture_dataset()
    return run_dataset(
        dataset=dataset,
        work_directory=tmp_path_factory.mktemp("p2-runner"),
        code_commit="development-fixture-commit",
        execution_timestamp=datetime(2026, 8, 7, 18, 0, tzinfo=UTC),
    )


def test_runner_executes_the_frozen_plan_after_valid_preevaluation(
    runner_output: DatasetRun,
) -> None:
    expected_count = len(build_trial_plan((_fixture_dataset(),)))

    assert expected_count == 94
    assert runner_output.preevaluation.all_valid is True
    assert runner_output.preevaluation.bc_parity.bc_parity_valid is True
    assert runner_output.preevaluation.sequential_parity.bc_sequence_valid is True
    assert runner_output.preevaluation.structured_consistency.all_valid is True
    assert runner_output.planned_trial_count == expected_count
    assert len(runner_output.results) == expected_count
    assert len({result.trial_id for result in runner_output.results}) == expected_count


def test_t7_presents_the_false_rewrite_without_mutating_b_or_c(
    runner_output: DatasetRun,
) -> None:
    results = tuple(
        result
        for result in runner_output.results
        if result.trial_type is TrialType.T7_MISLEADING_REWRITE
    )

    assert len(results) == 2
    assert {result.condition for result in results} == {
        ExperimentCondition.B,
        ExperimentCondition.C,
    }
    assert all("jamais-enregistré" in result.query for result in results)
    assert all(result.false_rewrite_accepted is False for result in results)
    assert all(result.persistent_state_mutated_by_query is False for result in results)
    assert all(result.predicted_current_state == "final" for result in results)


def test_t9_records_zero_forbidden_access_and_observable_degradation(
    runner_output: DatasetRun,
) -> None:
    results = tuple(
        result
        for result in runner_output.results
        if result.trial_type is TrialType.T9_TARGETED_ABLATION
    )

    assert len(results) == 5
    assert all(result.condition is ExperimentCondition.C for result in results)
    assert all(result.ablation_enabled is True for result in results)
    assert all(result.repository_access_count == 0 for result in results)
    assert any(result.ablation_degraded is True for result in results)
    assert all(result.predicted_resolution_status is ResolutionStatus.UNKNOWN for result in results)


def test_t6_distinguishes_no_history_from_confirmation_integrity(
    runner_output: DatasetRun,
) -> None:
    results = tuple(
        result
        for result in runner_output.results
        if result.trial_type is TrialType.T6_CONFIRMATION_NO_REVISION
    )
    by_condition = {result.condition: result for result in results}

    assert len(results) == 3
    assert by_condition[ExperimentCondition.A].confirmation_no_revision_correct is None
    assert by_condition[ExperimentCondition.B].confirmation_no_revision_correct is True
    assert by_condition[ExperimentCondition.C].confirmation_no_revision_correct is True
    assert by_condition[ExperimentCondition.C].order_correct is True
