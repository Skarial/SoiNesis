from __future__ import annotations

from pathlib import Path

from soinesis.domain.models import MemoryType, SourceType
from soinesis.experiments.exp_001_p2 import (
    ChainFamily,
    DatasetEvent,
    EventKind,
    ExperimentChain,
    ExperimentDataset,
)
from soinesis.experiments.exp_001_p2_audit import (
    audit_bc_parity,
    capture_integrity_snapshot,
)
from soinesis.experiments.exp_001_p2_readers import (
    StructuredHistoryCondition,
    TextHistoryCondition,
    build_query,
)


def _dataset() -> ExperimentDataset:
    dataset_id = "fixture-audit"
    subject = "Couleur du repère d'audit"
    belief_key = f"{dataset_id}:belief:01"
    kinds = (
        EventKind.INITIAL,
        EventKind.CONFIRMATION,
        EventKind.CORRECTION,
        EventKind.CONFIRMATION,
    )
    values = ("ambre", "ambre", "bleu", "bleu")
    sources = (
        SourceType.JORDAN_INPUT,
        SourceType.EXTERNAL_TOOL,
        SourceType.DEDUCTION,
        SourceType.JORDAN_INPUT,
    )
    events: list[DatasetEvent] = []
    for index, (kind, value, source) in enumerate(
        zip(kinds, values, sources, strict=True),
        start=1,
    ):
        if kind is EventKind.INITIAL:
            content = f"{subject} est « {value} »."
            reason = "État initial reçu."
        elif kind is EventKind.CORRECTION:
            content = f"Correction explicite : {subject} est désormais « {value} »."
            reason = "Correction explicite de la croyance précédente."
        else:
            content = f"Confirmation : {subject} reste « {value} »."
            reason = "Confirmation sans changement de croyance."
        events.append(
            DatasetEvent(
                id=f"{dataset_id}-event-{index:03d}",
                dataset_id=dataset_id,
                stream_position=index,
                chain_slot=1,
                event_number=index,
                cycle_id=f"{dataset_id}-cycle-{index:03d}",
                belief_key=belief_key,
                subject=subject,
                family=ChainFamily.S1_SIMPLE_CORRECTION,
                kind=kind,
                value=value,
                content=content,
                transition_reason=reason,
                source_type=source,
                memory_type=(
                    MemoryType.DEDUCTION
                    if source is SourceType.DEDUCTION
                    else MemoryType.RECEIVED_INFORMATION
                ),
            )
        )
    chain = ExperimentChain(
        id=f"{dataset_id}-chain-01",
        dataset_id=dataset_id,
        slot=1,
        belief_key=belief_key,
        subject=subject,
        family=ChainFamily.S1_SIMPLE_CORRECTION,
        historical_event_number=2,
        misleading_value=None,
        events=tuple(events),
    )
    return ExperimentDataset(
        id=dataset_id,
        namespace="fixture-only",
        events=tuple(events),
        chains=(chain,),
    )


def test_bc_parity_audit_accepts_identical_external_evidence(tmp_path: Path) -> None:
    dataset = _dataset()
    database_path = tmp_path / "audit.db"
    text = TextHistoryCondition(dataset)
    StructuredHistoryCondition(dataset, database_path)

    audit = audit_bc_parity(
        dataset=dataset,
        text_history=text.history,
        structured_database_path=database_path,
    )

    assert audit.expected_event_count == 4
    assert audit.text_event_count == 4
    assert audit.structured_event_count == 4
    assert audit.text_matches_expected is True
    assert audit.structured_matches_expected is True
    assert audit.bc_parity_valid is True


def test_bc_parity_audit_rejects_a_tampered_text_history(tmp_path: Path) -> None:
    dataset = _dataset()
    database_path = tmp_path / "tampered.db"
    text = TextHistoryCondition(dataset)
    StructuredHistoryCondition(dataset, database_path)
    tampered = text.history.replace("ambre", "violet", 1)

    audit = audit_bc_parity(
        dataset=dataset,
        text_history=tampered,
        structured_database_path=database_path,
    )

    assert audit.text_matches_expected is False
    assert audit.structured_matches_expected is True
    assert audit.bc_parity_valid is False


def test_normal_queries_do_not_mutate_persistent_b_or_c_state(tmp_path: Path) -> None:
    dataset = _dataset()
    database_path = tmp_path / "integrity.db"
    text = TextHistoryCondition(dataset)
    structured = StructuredHistoryCondition(dataset, database_path)
    query = build_query(dataset.chains[0])
    before = capture_integrity_snapshot(
        text_history=text.history,
        structured_database_path=database_path,
    )

    text.inspect(query)
    structured.inspect(query)

    after = capture_integrity_snapshot(
        text_history=text.history,
        structured_database_path=database_path,
    )
    assert after == before
