"""Audit de cohérence interne de la mémoire structurée pour EXP-001-P2.

Ce module ne calcule aucun résultat expérimental. Il vérifie que la persistance C
respecte les invariants préenregistrés : une observation par événement, aucune
version artificielle pour une confirmation, liens de révision cohérents et
journalisation explicite des transitions.
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from soinesis.domain.models import EventType
from soinesis.experiments.exp_001_p2 import EventKind, ExperimentDataset
from soinesis.experiments.exp_001_p2_readers import AGENT_ID


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class StructuredConsistencyAudit(FrozenModel):
    dataset_id: str = Field(min_length=1)
    expected_observation_count: int = Field(ge=0)
    actual_observation_count: int = Field(ge=0)
    expected_version_count: int = Field(ge=0)
    actual_version_count: int = Field(ge=0)
    expected_confirmation_count: int = Field(ge=0)
    actual_confirmation_count: int = Field(ge=0)
    expected_revision_count: int = Field(ge=0)
    actual_revision_count: int = Field(ge=0)
    expected_status_change_count: int = Field(ge=0)
    actual_status_change_count: int = Field(ge=0)
    confirmation_cycles_with_versions: tuple[str, ...]
    invalid_parent_links: tuple[str, ...]
    missing_or_extra_journal_cycles: tuple[str, ...]
    observation_count_valid: bool
    version_count_valid: bool
    confirmation_invariant_valid: bool
    parent_links_valid: bool
    journal_trace_valid: bool
    all_valid: bool


def audit_structured_consistency(
    *,
    dataset: ExperimentDataset,
    structured_database_path: Path,
) -> StructuredConsistencyAudit:
    """Compare les invariants structurels attendus à la base C persistée."""

    expected_versions = tuple(
        event for event in dataset.events if event.kind is not EventKind.CONFIRMATION
    )
    confirmations = tuple(
        event for event in dataset.events if event.kind is EventKind.CONFIRMATION
    )
    revisions = tuple(
        event
        for event in dataset.events
        if event.kind in {EventKind.CORRECTION, EventKind.CONTRADICTION, EventKind.RESOLUTION}
    )
    expected_status_by_cycle = {
        event.cycle_id: 2 if event.kind is EventKind.RESOLUTION else 1 for event in revisions
    }

    with sqlite3.connect(structured_database_path) as connection:
        connection.row_factory = sqlite3.Row
        observations = connection.execute(
            "SELECT cycle_id FROM observations WHERE agent_id = ?",
            (AGENT_ID,),
        ).fetchall()
        memories = connection.execute(
            """
            SELECT id, cycle_id, belief_key, parent_memory_ids_json
            FROM memories
            WHERE agent_id = ?
            """,
            (AGENT_ID,),
        ).fetchall()
        journal = connection.execute(
            """
            SELECT cycle_id, event_type
            FROM journal_events
            WHERE agent_id = ?
            """,
            (AGENT_ID,),
        ).fetchall()

    memory_by_id = {str(row["id"]): row for row in memories}
    memory_cycles = {str(row["cycle_id"]) for row in memories}
    confirmation_cycles_with_versions = tuple(
        event.cycle_id for event in confirmations if event.cycle_id in memory_cycles
    )

    expected_parent_count = {
        event.cycle_id: 0
        if event.kind is EventKind.INITIAL
        else 2
        if event.kind is EventKind.RESOLUTION
        else 1
        for event in expected_versions
    }
    invalid_parent_links: list[str] = []
    for row in memories:
        memory_id = str(row["id"])
        cycle_id = str(row["cycle_id"])
        parent_ids = tuple(str(value) for value in json.loads(str(row["parent_memory_ids_json"])))
        expected_count = expected_parent_count.get(cycle_id)
        if expected_count is None or len(parent_ids) != expected_count:
            invalid_parent_links.append(memory_id)
            continue
        if memory_id in parent_ids or len(set(parent_ids)) != len(parent_ids):
            invalid_parent_links.append(memory_id)
            continue
        belief_key = str(row["belief_key"])
        if any(
            parent_id not in memory_by_id
            or str(memory_by_id[parent_id]["belief_key"]) != belief_key
            for parent_id in parent_ids
        ):
            invalid_parent_links.append(memory_id)

    actual_event_counts = Counter(str(row["event_type"]) for row in journal)
    actual_confirmation_count = actual_event_counts[EventType.MEMORY_CONFIRMED.value]
    actual_revision_count = actual_event_counts[EventType.MEMORY_REVISION_CREATED.value]
    actual_status_count = actual_event_counts[EventType.MEMORY_STATUS_CHANGED.value]

    expected_journal_by_cycle: Counter[tuple[str, str]] = Counter()
    for event in dataset.events:
        if event.kind is EventKind.INITIAL:
            expected_journal_by_cycle[(event.cycle_id, EventType.MEMORY_CREATED.value)] += 1
        elif event.kind is EventKind.CONFIRMATION:
            expected_journal_by_cycle[(event.cycle_id, EventType.MEMORY_CONFIRMED.value)] += 1
        else:
            expected_journal_by_cycle[(event.cycle_id, EventType.MEMORY_REVISION_CREATED.value)] += 1
            expected_journal_by_cycle[(event.cycle_id, EventType.MEMORY_STATUS_CHANGED.value)] += (
                expected_status_by_cycle[event.cycle_id]
            )

    actual_journal_by_cycle = Counter(
        (str(row["cycle_id"]), str(row["event_type"])) for row in journal
    )
    differing_journal_keys = sorted(
        key
        for key in set(expected_journal_by_cycle) | set(actual_journal_by_cycle)
        if expected_journal_by_cycle[key] != actual_journal_by_cycle[key]
    )
    missing_or_extra_journal_cycles = tuple(
        f"{cycle_id}:{event_type}" for cycle_id, event_type in differing_journal_keys
    )

    observation_count_valid = (
        len(observations) == len(dataset.events)
        and Counter(str(row["cycle_id"]) for row in observations)
        == Counter(event.cycle_id for event in dataset.events)
    )
    version_count_valid = len(memories) == len(expected_versions)
    confirmation_invariant_valid = (
        len(confirmations) == actual_confirmation_count
        and not confirmation_cycles_with_versions
    )
    parent_links_valid = not invalid_parent_links
    expected_status_change_count = sum(expected_status_by_cycle.values())
    journal_trace_valid = (
        actual_revision_count == len(revisions)
        and actual_status_count == expected_status_change_count
        and not missing_or_extra_journal_cycles
    )
    all_valid = all(
        (
            observation_count_valid,
            version_count_valid,
            confirmation_invariant_valid,
            parent_links_valid,
            journal_trace_valid,
        )
    )

    return StructuredConsistencyAudit(
        dataset_id=dataset.id,
        expected_observation_count=len(dataset.events),
        actual_observation_count=len(observations),
        expected_version_count=len(expected_versions),
        actual_version_count=len(memories),
        expected_confirmation_count=len(confirmations),
        actual_confirmation_count=actual_confirmation_count,
        expected_revision_count=len(revisions),
        actual_revision_count=actual_revision_count,
        expected_status_change_count=expected_status_change_count,
        actual_status_change_count=actual_status_count,
        confirmation_cycles_with_versions=confirmation_cycles_with_versions,
        invalid_parent_links=tuple(sorted(invalid_parent_links)),
        missing_or_extra_journal_cycles=missing_or_extra_journal_cycles,
        observation_count_valid=observation_count_valid,
        version_count_valid=version_count_valid,
        confirmation_invariant_valid=confirmation_invariant_valid,
        parent_links_valid=parent_links_valid,
        journal_trace_valid=journal_trace_valid,
        all_valid=all_valid,
    )
