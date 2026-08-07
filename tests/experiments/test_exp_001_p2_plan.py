from __future__ import annotations

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


def _chain(slot: int, family: ChainFamily) -> ExperimentChain:
    dataset_id = "fixture-plan"
    subject = f"Sujet {slot}"
    event = DatasetEvent(
        id=f"event-{slot}",
        dataset_id=dataset_id,
        stream_position=slot,
        chain_slot=slot,
        event_number=1,
        cycle_id=f"{dataset_id}-cycle-{slot:03d}",
        belief_key=f"{dataset_id}:belief:{slot:02d}",
        subject=subject,
        family=family,
        kind=EventKind.INITIAL,
        value=f"v{slot}",
        content=f"{subject} est « v{slot} ».",
        transition_reason="État initial reçu.",
        source_type=SourceType.JORDAN_INPUT,
        memory_type=MemoryType.RECEIVED_INFORMATION,
    )
    return ExperimentChain(
        id=f"chain-{slot:02d}",
        dataset_id=dataset_id,
        slot=slot,
        belief_key=event.belief_key,
        subject=subject,
        family=family,
        historical_event_number=1,
        misleading_value=("faux" if family is ChainFamily.S6_MISLEADING_REWRITE else None),
        events=(event,),
    )


def _dataset() -> ExperimentDataset:
    families = tuple(ChainFamily)
    chains = tuple(_chain(index, family) for index, family in enumerate(families, start=1))
    return ExperimentDataset(
        id="fixture-plan",
        namespace="fixture-only",
        events=tuple(chain.events[0] for chain in chains),
        chains=chains,
    )


def test_plan_is_deterministic_and_contiguously_ordered() -> None:
    dataset = _dataset()

    first = build_trial_plan((dataset,))
    second = build_trial_plan((dataset,))

    assert first == second
    assert tuple(entry.order for entry in first) == tuple(range(1, len(first) + 1))
    assert len({entry.trial_id for entry in first}) == len(first)


def test_t7_is_limited_to_s6_and_compares_b_with_c() -> None:
    plan = build_trial_plan((_dataset(),))
    entries = tuple(entry for entry in plan if entry.trial_type is TrialType.T7_MISLEADING_REWRITE)

    assert entries
    assert {entry.family for entry in entries} == {ChainFamily.S6_MISLEADING_REWRITE}
    assert {entry.condition for entry in entries} == {
        ExperimentCondition.B,
        ExperimentCondition.C,
    }
    assert all(entry.ablation_enabled is False for entry in entries)


def test_t9_uses_only_c_and_one_preselected_chain_per_dependent_family() -> None:
    plan = build_trial_plan((_dataset(),))
    entries = tuple(entry for entry in plan if entry.trial_type is TrialType.T9_TARGETED_ABLATION)

    assert len(entries) == 5
    assert {entry.condition for entry in entries} == {ExperimentCondition.C}
    assert {entry.family for entry in entries} == {
        ChainFamily.S1_SIMPLE_CORRECTION,
        ChainFamily.S2_MULTIPLE_REVISIONS,
        ChainFamily.S3_UNRESOLVED_CONTRADICTION,
        ChainFamily.S4_CONTRADICTION_RESOLUTION,
        ChainFamily.S6_MISLEADING_REWRITE,
    }
    assert all(entry.ablation_enabled is True for entry in entries)


def test_normal_trial_scope_matches_protocol_families() -> None:
    plan = build_trial_plan((_dataset(),))

    t1_families = {
        entry.family for entry in plan if entry.trial_type is TrialType.T1_CURRENT_STATE
    }
    t5_families = {
        entry.family
        for entry in plan
        if entry.trial_type is TrialType.T5_UNRESOLVED_CONTRADICTION
    }
    t6_families = {
        entry.family
        for entry in plan
        if entry.trial_type is TrialType.T6_CONFIRMATION_NO_REVISION
    }

    assert ChainFamily.S3_UNRESOLVED_CONTRADICTION not in t1_families
    assert t5_families == {ChainFamily.S3_UNRESOLVED_CONTRADICTION}
    assert t6_families == {ChainFamily.S5_CONFIRMATION_NO_CHANGE}
