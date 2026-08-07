"""Snapshots séquentiels d'ingestion pour EXP-001-P2.

Cette couche audite l'évolution de B et C après chaque événement injecté sans
exposer la vérité terrain aux mécanismes de lecture utilisés pendant les essais.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from soinesis.domain.models import SourceType
from soinesis.experiments.exp_001_p2 import DatasetEvent, ExperimentDataset
from soinesis.experiments.exp_001_p2_readers import (
    AGENT_ID,
    ExperimentCondition,
    StructuredHistoryCondition,
    TextHistoryCondition,
)

_TEXT_LINE_PATTERN = re.compile(r"^Moment (?P<position>\d{3})\. (?P<source>.+?)\. (?P<content>.+)$")
_LABEL_SOURCES = {
    "Jordan indique": SourceType.JORDAN_INPUT,
    "Un outil externe indique": SourceType.EXTERNAL_TOOL,
    "Une déduction interne conclut": SourceType.DEDUCTION,
}


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class IngestionSnapshot(FrozenModel):
    condition: ExperimentCondition
    stream_position: int = Field(ge=1)
    cycle_id: str = Field(min_length=1)
    event_count: int = Field(ge=1)
    evidence_digest: str = Field(min_length=64, max_length=64)
    persistent_digest: str = Field(min_length=64, max_length=64)


class SequentialParityAudit(FrozenModel):
    dataset_id: str = Field(min_length=1)
    expected_snapshot_count: int = Field(ge=0)
    text_snapshot_count: int = Field(ge=0)
    structured_snapshot_count: int = Field(ge=0)
    metadata_matches_expected: bool
    evidence_parity_valid: bool
    bc_sequence_valid: bool


class SequentialTextHistoryCondition(TextHistoryCondition):
    """Condition B construite événement par événement avec snapshots auditables."""

    def __init__(self, dataset: ExperimentDataset) -> None:
        reference_history = TextHistoryCondition(dataset).history
        reference_lines = reference_history.splitlines()
        if len(reference_lines) != len(dataset.events):
            raise RuntimeError("La construction textuelle B ne correspond pas au flux P2.")

        self._dataset_id = dataset.id
        self._history = ""
        snapshots: list[IngestionSnapshot] = []
        lines: list[str] = []

        for event, line in zip(dataset.events, reference_lines, strict=True):
            lines.append(line)
            self._history = "\n".join(lines)
            snapshots.append(
                _text_snapshot(
                    dataset_id=dataset.id,
                    history=self._history,
                    event=event,
                )
            )

        self._ingestion_snapshots = tuple(snapshots)

    @property
    def ingestion_snapshots(self) -> tuple[IngestionSnapshot, ...]:
        return self._ingestion_snapshots


class SequentialStructuredHistoryCondition(StructuredHistoryCondition):
    """Condition C avec capture de l'état persistant après chaque injection."""

    def __init__(self, dataset: ExperimentDataset, database_path: Path) -> None:
        self._snapshot_database_path = database_path
        self._ingestion_snapshot_buffer: list[IngestionSnapshot] = []
        super().__init__(dataset, database_path)
        self._ingestion_snapshots = tuple(self._ingestion_snapshot_buffer)

    @property
    def ingestion_snapshots(self) -> tuple[IngestionSnapshot, ...]:
        return self._ingestion_snapshots

    def _ingest_event(self, event: DatasetEvent, state: Any) -> None:
        super()._ingest_event(event, state)
        self._ingestion_snapshot_buffer.append(
            _structured_snapshot(
                database_path=self._snapshot_database_path,
                event=event,
            )
        )


def audit_sequential_parity(
    *,
    dataset: ExperimentDataset,
    text_snapshots: tuple[IngestionSnapshot, ...],
    structured_snapshots: tuple[IngestionSnapshot, ...],
) -> SequentialParityAudit:
    expected_count = len(dataset.events)
    metadata_matches = (
        len(text_snapshots) == expected_count and len(structured_snapshots) == expected_count
    )
    evidence_parity = metadata_matches

    if metadata_matches:
        for index, event in enumerate(dataset.events, start=1):
            text = text_snapshots[index - 1]
            structured = structured_snapshots[index - 1]
            expected_metadata = (
                event.stream_position,
                event.cycle_id,
                index,
            )
            if (text.stream_position, text.cycle_id, text.event_count) != expected_metadata or (
                structured.stream_position,
                structured.cycle_id,
                structured.event_count,
            ) != expected_metadata:
                metadata_matches = False
            if text.evidence_digest != structured.evidence_digest:
                evidence_parity = False

    return SequentialParityAudit(
        dataset_id=dataset.id,
        expected_snapshot_count=expected_count,
        text_snapshot_count=len(text_snapshots),
        structured_snapshot_count=len(structured_snapshots),
        metadata_matches_expected=metadata_matches,
        evidence_parity_valid=evidence_parity,
        bc_sequence_valid=metadata_matches and evidence_parity,
    )


def _text_snapshot(
    *,
    dataset_id: str,
    history: str,
    event: DatasetEvent,
) -> IngestionSnapshot:
    evidence = _text_evidence(dataset_id, history)
    _validate_latest_event(evidence, event)
    return IngestionSnapshot(
        condition=ExperimentCondition.B,
        stream_position=event.stream_position,
        cycle_id=event.cycle_id,
        event_count=len(evidence),
        evidence_digest=_evidence_digest(evidence),
        persistent_digest=hashlib.sha256(history.encode("utf-8")).hexdigest(),
    )


def _structured_snapshot(
    *,
    database_path: Path,
    event: DatasetEvent,
) -> IngestionSnapshot:
    evidence = _structured_evidence(database_path)
    _validate_latest_event(evidence, event)
    with sqlite3.connect(database_path) as connection:
        dump = "\n".join(connection.iterdump())
    return IngestionSnapshot(
        condition=ExperimentCondition.C,
        stream_position=event.stream_position,
        cycle_id=event.cycle_id,
        event_count=len(evidence),
        evidence_digest=_evidence_digest(evidence),
        persistent_digest=hashlib.sha256(dump.encode("utf-8")).hexdigest(),
    )


def _text_evidence(dataset_id: str, history: str) -> tuple[tuple[str, str, str], ...]:
    evidence: list[tuple[str, str, str]] = []
    for line in history.splitlines():
        match = _TEXT_LINE_PATTERN.fullmatch(line)
        if match is None:
            raise ValueError("Une ligne B ne respecte pas le format textuel figé de P2.")
        position = int(match.group("position"))
        source_type = _LABEL_SOURCES.get(match.group("source"))
        if source_type is None:
            raise ValueError("Une provenance textuelle B est inconnue pendant le snapshot.")
        evidence.append(
            (
                f"{dataset_id}-cycle-{position:03d}",
                match.group("content"),
                source_type.value,
            )
        )
    return tuple(evidence)


def _structured_evidence(database_path: Path) -> tuple[tuple[str, str, str], ...]:
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT cycle_id, raw_content, source_type
            FROM observations
            WHERE agent_id = ?
            ORDER BY received_at ASC, id ASC
            """,
            (AGENT_ID,),
        ).fetchall()
    return tuple(
        (
            str(row["cycle_id"]),
            str(row["raw_content"]),
            str(row["source_type"]),
        )
        for row in rows
    )


def _evidence_digest(evidence: tuple[tuple[str, str, str], ...]) -> str:
    payload = json.dumps(evidence, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_latest_event(
    evidence: tuple[tuple[str, str, str], ...],
    event: DatasetEvent,
) -> None:
    if len(evidence) != event.stream_position:
        raise RuntimeError("Le snapshot P2 ne contient pas le nombre d'événements attendu.")
    if not evidence or evidence[-1][0] != event.cycle_id:
        raise RuntimeError("Le snapshot P2 ne se termine pas sur le cycle injecté.")
