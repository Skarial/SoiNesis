from __future__ import annotations

import sqlite3
from pathlib import Path

from soinesis.domain.models import MemoryType, SourceType
from soinesis.experiments.exp_001_p2 import (
    ChainFamily,
    DatasetEvent,
    EventKind,
    ExperimentChain,
    ExperimentDataset,
)
from soinesis.experiments.exp_001_p2_consistency import audit_structured_consistency
from soinesis.experiments.exp_001_p2_readers import StructuredHistoryCondition


def _dataset() -> ExperimentDataset:
    dataset_id = "fixture-consistency"
    subject = "Couleur du repère de cohérence"
    belief_key = f"{dataset_id}:belief:01"
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
    events: list[DatasetEvent] = []
    for index, (kind, value, source) in enumerate(
        zip(kinds, values, sources, strict=True),
        start=1,
    ):
        if kind is EventKind.INITIAL:
            content = f"{subject} est « {value} »."
            reason = "État initial reçu."
        elif kind is EventKind.CONTRADICTION:
            content = f"Information contradictoire : {subject} est « {value} »."
            reason = "Contradiction explicite laissée non résolue."
        elif kind is EventKind.CONFIRMATION:
            content = f"Confirmation : {subject} reste « {value} »."
            reason = "Confirmation sans changement de croyance."
        else:
            content = f"Résolution explicite : {subject} est fixé à « {value} »."
            reason = "Résolution explicite de la contradiction."
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
                family=ChainFamily.S4_CONTRADICTION_RESOLUTION,
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
        family=ChainFamily.S4_CONTRADICTION_RESOLUTION,
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


def test_consistency_audit_accepts_traceable_revisions_and_confirmation(tmp_path: Path) -> None:
    dataset = _dataset()
    database_path = tmp_path / "consistent.db"
    StructuredHistoryCondition(dataset, database_path)

    audit = audit_structured_consistency(
        dataset=dataset,
        structured_database_path=database_path,
    )

    assert audit.expected_observation_count == 4
    assert audit.actual_observation_count == 4
    assert audit.expected_version_count == 3
    assert audit.actual_version_count == 3
    assert audit.expected_confirmation_count == 1
    assert audit.actual_confirmation_count == 1
    assert audit.expected_revision_count == 2
    assert audit.actual_revision_count == 2
    assert audit.expected_status_change_count == 3
    assert audit.actual_status_change_count == 3
    assert audit.confirmation_cycles_with_versions == ()
    assert audit.invalid_parent_links == ()
    assert audit.missing_or_extra_journal_cycles == ()
    assert audit.all_valid is True


def test_consistency_audit_detects_artificial_version_on_confirmation(tmp_path: Path) -> None:
    dataset = _dataset()
    database_path = tmp_path / "artificial-version.db"
    StructuredHistoryCondition(dataset, database_path)
    confirmation_cycle = dataset.events[2].cycle_id

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO memories (
                id, agent_id, cycle_id, source_observation_id, memory_type,
                title, content, source_type, confidence, importance, status,
                created_at, is_direct_experience, belief_key,
                parent_memory_ids_json, transition_reason
            )
            SELECT
                'tampered-memory', agent_id, ?, source_observation_id, memory_type,
                title, content, source_type, confidence, importance, status,
                created_at, is_direct_experience, belief_key,
                parent_memory_ids_json, transition_reason
            FROM memories
            ORDER BY created_at ASC
            LIMIT 1
            """,
            (confirmation_cycle,),
        )
        connection.commit()

    audit = audit_structured_consistency(
        dataset=dataset,
        structured_database_path=database_path,
    )

    assert audit.version_count_valid is False
    assert audit.confirmation_invariant_valid is False
    assert audit.confirmation_cycles_with_versions == (confirmation_cycle,)
    assert audit.all_valid is False


def test_consistency_audit_detects_missing_transition_journal_entry(tmp_path: Path) -> None:
    dataset = _dataset()
    database_path = tmp_path / "missing-journal.db"
    StructuredHistoryCondition(dataset, database_path)
    resolution_cycle = dataset.events[3].cycle_id

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            DELETE FROM journal_events
            WHERE id = (
                SELECT id FROM journal_events
                WHERE cycle_id = ? AND event_type = 'MEMORY_STATUS_CHANGED'
                ORDER BY id ASC
                LIMIT 1
            )
            """,
            (resolution_cycle,),
        )
        connection.commit()

    audit = audit_structured_consistency(
        dataset=dataset,
        structured_database_path=database_path,
    )

    assert audit.journal_trace_valid is False
    assert audit.actual_status_change_count == 2
    assert f"{resolution_cycle}:MEMORY_STATUS_CHANGED" in audit.missing_or_extra_journal_cycles
    assert audit.all_valid is False
