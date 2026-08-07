"""Contrôles d'équité et d'intégrité pour EXP-001-P2.

Ce module ne produit aucun score expérimental. Il vérifie que les conditions B
et C ont reçu les mêmes événements externes et fournit des empreintes stables de
leur état persistant avant/après interrogation.
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from soinesis.domain.models import SourceType
from soinesis.experiments.exp_001_p2 import ExperimentDataset
from soinesis.experiments.exp_001_p2_readers import AGENT_ID

_TEXT_LINE_PATTERN = re.compile(
    r"^Moment (?P<position>\d{3})\. (?P<source>.+?)\. (?P<content>.+)$"
)
_SOURCE_LABELS = {
    SourceType.JORDAN_INPUT: "Jordan indique",
    SourceType.EXTERNAL_TOOL: "Un outil externe indique",
    SourceType.DEDUCTION: "Une déduction interne conclut",
}
_LABEL_SOURCES = {label: source for source, label in _SOURCE_LABELS.items()}


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ExternalEvidence(FrozenModel):
    position: int = Field(ge=1)
    cycle_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source_type: SourceType


class ParityAudit(FrozenModel):
    dataset_id: str = Field(min_length=1)
    expected_event_count: int = Field(ge=0)
    text_event_count: int = Field(ge=0)
    structured_event_count: int = Field(ge=0)
    text_matches_expected: bool
    structured_matches_expected: bool
    bc_parity_valid: bool


class IntegritySnapshot(FrozenModel):
    text_digest: str = Field(min_length=64, max_length=64)
    structured_digest: str = Field(min_length=64, max_length=64)


def audit_bc_parity(
    *,
    dataset: ExperimentDataset,
    text_history: str,
    structured_database_path: Path,
) -> ParityAudit:
    """Vérifie contenu, provenance et ordre identiques entre données, B et C."""

    expected = _expected_evidence(dataset)
    text = _text_evidence(dataset.id, text_history)
    structured = _structured_evidence(structured_database_path)
    text_matches = text == expected
    structured_matches = structured == expected
    return ParityAudit(
        dataset_id=dataset.id,
        expected_event_count=len(expected),
        text_event_count=len(text),
        structured_event_count=len(structured),
        text_matches_expected=text_matches,
        structured_matches_expected=structured_matches,
        bc_parity_valid=text_matches and structured_matches and text == structured,
    )


def capture_integrity_snapshot(
    *,
    text_history: str,
    structured_database_path: Path,
) -> IntegritySnapshot:
    """Capture une empreinte canonique des états persistants B et C."""

    return IntegritySnapshot(
        text_digest=hashlib.sha256(text_history.encode("utf-8")).hexdigest(),
        structured_digest=_sqlite_digest(structured_database_path),
    )


def _expected_evidence(dataset: ExperimentDataset) -> tuple[ExternalEvidence, ...]:
    return tuple(
        ExternalEvidence(
            position=event.stream_position,
            cycle_id=event.cycle_id,
            content=event.content,
            source_type=event.source_type,
        )
        for event in dataset.events
    )


def _text_evidence(dataset_id: str, history: str) -> tuple[ExternalEvidence, ...]:
    evidence: list[ExternalEvidence] = []
    for line in history.splitlines():
        match = _TEXT_LINE_PATTERN.fullmatch(line)
        if match is None:
            raise ValueError("Une ligne B ne respecte pas le format textuel figé de P2.")
        position = int(match.group("position"))
        source_type = _LABEL_SOURCES.get(match.group("source"))
        if source_type is None:
            raise ValueError("Une provenance textuelle B est inconnue pendant l'audit.")
        evidence.append(
            ExternalEvidence(
                position=position,
                cycle_id=f"{dataset_id}-cycle-{position:03d}",
                content=match.group("content"),
                source_type=source_type,
            )
        )
    return tuple(evidence)


def _structured_evidence(database_path: Path) -> tuple[ExternalEvidence, ...]:
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
        ExternalEvidence(
            position=index,
            cycle_id=str(row["cycle_id"]),
            content=str(row["raw_content"]),
            source_type=SourceType(str(row["source_type"])),
        )
        for index, row in enumerate(rows, start=1)
    )


def _sqlite_digest(database_path: Path) -> str:
    with sqlite3.connect(database_path) as connection:
        dump = "\n".join(connection.iterdump())
    return hashlib.sha256(dump.encode("utf-8")).hexdigest()
