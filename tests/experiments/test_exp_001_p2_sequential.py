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
from soinesis.experiments.exp_001_p2_audit import capture_integrity_snapshot
from soinesis.experiments.exp_001_p2_readers import (
    StructuredHistoryCondition,
    TextHistoryCondition,
    build_query,
)
from soinesis.experiments.exp_001_p2_sequential import (
    SequentialStructuredHistoryCondition,
    SequentialTextHistoryCondition,
    audit_sequential_parity,
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
    dataset_id = "fixture-sequential"
    subject = "Couleur du témoin séquentiel"
    belief_key = f"{dataset_id}:fixture-belief"
    kinds = (
        EventKind.INITIAL,
        EventKind.CONTRADICTION,
        EventKind.CONFIRMATION,
        EventKind.RESOLUTION,
    )
    values = ("rouge", "bleu", "bleu", "vert")
    sources = (
        SourceType.JORDAN_INPUT,
        SourceType.EXTERNAL_TOOL,
        SourceType.DEDUCTION,
        SourceType.JORDAN_INPUT,
    )
    events = tuple(
        DatasetEvent(
            id=f"fixture-event-{index}",
            dataset_id=dataset_id,
            stream_position=index,
            chain_slot=1,
            event_number=index,
            cycle_id=f"{dataset_id}-cycle-{index:03d}",
            belief_key=belief_key,
            subject=subject,
            family=ChainFamily.S4_CONTRADICTION_RESOLUTION,
            kind=kind,
            value=value,
            content=_content(kind, subject, value),
            transition_reason=_reason(kind),
            source_type=source,
            memory_type=_memory_type(source),
        )
        for index, (kind, value, source) in enumerate(
            zip(kinds, values, sources, strict=True),
            start=1,
        )
    )
    chain = ExperimentChain(
        id=f"{dataset_id}-fixture-chain",
        dataset_id=dataset_id,
        slot=1,
        belief_key=belief_key,
        subject=subject,
        family=ChainFamily.S4_CONTRADICTION_RESOLUTION,
        historical_event_number=2,
        misleading_value=None,
        events=events,
    )
    return ExperimentDataset(
        id=dataset_id,
        namespace="fixture-only",
        events=events,
        chains=(chain,),
    )


def test_b_and_c_capture_one_parity_snapshot_after_each_event(tmp_path: Path) -> None:
    dataset = _fixture_dataset()
    text = SequentialTextHistoryCondition(dataset)
    structured = SequentialStructuredHistoryCondition(dataset, tmp_path / "sequential.db")

    audit = audit_sequential_parity(
        dataset=dataset,
        text_snapshots=text.ingestion_snapshots,
        structured_snapshots=structured.ingestion_snapshots,
    )

    assert len(text.ingestion_snapshots) == 4
    assert len(structured.ingestion_snapshots) == 4
    assert tuple(snapshot.event_count for snapshot in text.ingestion_snapshots) == (1, 2, 3, 4)
    assert tuple(snapshot.event_count for snapshot in structured.ingestion_snapshots) == (
        1,
        2,
        3,
        4,
    )
    assert audit.metadata_matches_expected is True
    assert audit.evidence_parity_valid is True
    assert audit.bc_sequence_valid is True


def test_sequential_conditions_preserve_the_frozen_reader_behavior(tmp_path: Path) -> None:
    dataset = _fixture_dataset()
    query = build_query(dataset.chains[0])

    reference_text = TextHistoryCondition(dataset)
    sequential_text = SequentialTextHistoryCondition(dataset)
    reference_structured = StructuredHistoryCondition(dataset, tmp_path / "reference.db")
    sequential_structured = SequentialStructuredHistoryCondition(
        dataset, tmp_path / "sequential.db"
    )

    assert sequential_text.history == reference_text.history
    assert sequential_text.inspect(query) == reference_text.inspect(query)
    assert sequential_structured.inspect(query).model_dump(exclude={"retrieved_memory_ids"}) == (
        reference_structured.inspect(query).model_dump(exclude={"retrieved_memory_ids"})
    )


def test_final_sequential_snapshot_matches_final_persistent_integrity(tmp_path: Path) -> None:
    dataset = _fixture_dataset()
    database_path = tmp_path / "sequential.db"
    text = SequentialTextHistoryCondition(dataset)
    structured = SequentialStructuredHistoryCondition(dataset, database_path)

    integrity = capture_integrity_snapshot(
        text_history=text.history,
        structured_database_path=database_path,
    )

    assert text.ingestion_snapshots[-1].persistent_digest == integrity.text_digest
    assert structured.ingestion_snapshots[-1].persistent_digest == integrity.structured_digest


def test_sequential_audit_rejects_a_tampered_snapshot(tmp_path: Path) -> None:
    dataset = _fixture_dataset()
    text = SequentialTextHistoryCondition(dataset)
    structured = SequentialStructuredHistoryCondition(dataset, tmp_path / "sequential.db")
    tampered = list(text.ingestion_snapshots)
    tampered[1] = tampered[1].model_copy(update={"evidence_digest": "0" * 64})

    audit = audit_sequential_parity(
        dataset=dataset,
        text_snapshots=tuple(tampered),
        structured_snapshots=structured.ingestion_snapshots,
    )

    assert audit.metadata_matches_expected is True
    assert audit.evidence_parity_valid is False
    assert audit.bc_sequence_valid is False
