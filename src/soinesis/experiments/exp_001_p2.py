"""Chargement déterministe du jeu de données figé EXP-001-P2."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from enum import StrEnum
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from soinesis.domain.models import MemoryType, SourceType

EXPERIMENT_ID = "EXP-001-P2"
PROTOCOL_VERSION = "0.1"
DATASET_VERSION = "1.0"


class ChainFamily(StrEnum):
    """Familles de chaînes préenregistrées dans le protocole P2."""

    S1_SIMPLE_CORRECTION = "S1_SIMPLE_CORRECTION"
    S2_MULTIPLE_REVISIONS = "S2_MULTIPLE_REVISIONS"
    S3_UNRESOLVED_CONTRADICTION = "S3_UNRESOLVED_CONTRADICTION"
    S4_CONTRADICTION_RESOLUTION = "S4_CONTRADICTION_RESOLUTION"
    S5_CONFIRMATION_NO_CHANGE = "S5_CONFIRMATION_NO_CHANGE"
    S6_MISLEADING_REWRITE = "S6_MISLEADING_REWRITE"


class EventKind(StrEnum):
    """Sémantique externe d'un événement injecté."""

    INITIAL = "INITIAL"
    CORRECTION = "CORRECTION"
    CONTRADICTION = "CONTRADICTION"
    RESOLUTION = "RESOLUTION"
    CONFIRMATION = "CONFIRMATION"


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class DatasetSpec(FrozenModel):
    id: str = Field(min_length=1)
    namespace: str = Field(min_length=1)
    source_offset: int = Field(ge=0, le=2)


class ChainTemplate(FrozenModel):
    slot: int = Field(ge=1, le=12)
    family: ChainFamily
    subject_template: str = Field(min_length=1)
    values: tuple[str, str, str, str]
    event_kinds: tuple[EventKind, EventKind, EventKind, EventKind]
    historical_event_number: int = Field(ge=1, le=4)
    misleading_value: str | None = None

    @model_validator(mode="after")
    def validate_family_pattern(self) -> Self:
        expected = {
            ChainFamily.S1_SIMPLE_CORRECTION: (
                EventKind.INITIAL,
                EventKind.CONFIRMATION,
                EventKind.CORRECTION,
                EventKind.CONFIRMATION,
            ),
            ChainFamily.S2_MULTIPLE_REVISIONS: (
                EventKind.INITIAL,
                EventKind.CORRECTION,
                EventKind.CORRECTION,
                EventKind.CORRECTION,
            ),
            ChainFamily.S3_UNRESOLVED_CONTRADICTION: (
                EventKind.INITIAL,
                EventKind.CONFIRMATION,
                EventKind.CONTRADICTION,
                EventKind.CONFIRMATION,
            ),
            ChainFamily.S4_CONTRADICTION_RESOLUTION: (
                EventKind.INITIAL,
                EventKind.CONTRADICTION,
                EventKind.CONFIRMATION,
                EventKind.RESOLUTION,
            ),
            ChainFamily.S5_CONFIRMATION_NO_CHANGE: (
                EventKind.INITIAL,
                EventKind.CONFIRMATION,
                EventKind.CONFIRMATION,
                EventKind.CONFIRMATION,
            ),
            ChainFamily.S6_MISLEADING_REWRITE: (
                EventKind.INITIAL,
                EventKind.CORRECTION,
                EventKind.CONFIRMATION,
                EventKind.CORRECTION,
            ),
        }[self.family]
        if self.event_kinds != expected:
            raise ValueError(f"Motif d'événements invalide pour {self.family.value}.")
        if self.family is ChainFamily.S6_MISLEADING_REWRITE:
            if not self.misleading_value:
                raise ValueError("S6 exige une valeur de réécriture trompeuse.")
        elif self.misleading_value is not None:
            raise ValueError("Seules les chaînes S6 portent une réécriture trompeuse.")
        for index, kind in enumerate(self.event_kinds):
            if (
                kind is EventKind.CONFIRMATION
                and index > 0
                and self.values[index] != self.values[index - 1]
            ):
                raise ValueError("Une confirmation ne doit pas changer la valeur.")
        return self


class DatasetFile(FrozenModel):
    version: str
    source_order: tuple[SourceType, SourceType, SourceType]
    datasets: tuple[DatasetSpec, ...]
    chains: tuple[ChainTemplate, ...]
    event_stream: tuple[int, ...]

    @model_validator(mode="after")
    def validate_file(self) -> Self:
        if self.version != DATASET_VERSION:
            raise ValueError(f"Version de données attendue : {DATASET_VERSION}.")
        expected_sources = (
            SourceType.JORDAN_INPUT,
            SourceType.EXTERNAL_TOOL,
            SourceType.DEDUCTION,
        )
        if self.source_order != expected_sources:
            raise ValueError("L'ordre des trois provenances P2 est figé.")
        if len(self.datasets) != 5:
            raise ValueError("P2 exige exactement cinq jeux de données.")
        if len(self.chains) != 12:
            raise ValueError("Chaque jeu P2 doit contenir exactement douze chaînes.")
        if {chain.slot for chain in self.chains} != set(range(1, 13)):
            raise ValueError("Les slots de chaînes doivent couvrir 1 à 12.")
        family_counts = Counter(chain.family for chain in self.chains)
        if any(family_counts[family] != 2 for family in ChainFamily):
            raise ValueError("Chaque famille S1 à S6 doit apparaître exactement deux fois.")
        if len(self.event_stream) != 48:
            raise ValueError("Le flux global doit contenir exactement 48 événements.")
        if Counter(self.event_stream) != Counter({slot: 4 for slot in range(1, 13)}):
            raise ValueError("Chaque chaîne doit apparaître quatre fois dans le flux global.")
        return self


class DatasetEvent(FrozenModel):
    id: str
    dataset_id: str
    stream_position: int = Field(ge=1, le=48)
    chain_slot: int = Field(ge=1, le=12)
    event_number: int = Field(ge=1, le=4)
    cycle_id: str
    belief_key: str
    subject: str
    family: ChainFamily
    kind: EventKind
    value: str
    content: str
    transition_reason: str
    source_type: SourceType
    memory_type: MemoryType


class ExperimentChain(FrozenModel):
    id: str
    dataset_id: str
    slot: int
    belief_key: str
    subject: str
    family: ChainFamily
    historical_event_number: int
    misleading_value: str | None
    events: tuple[DatasetEvent, ...]


class ExperimentDataset(FrozenModel):
    id: str
    namespace: str
    events: tuple[DatasetEvent, ...]
    chains: tuple[ExperimentChain, ...]


def memory_type_for_source(source_type: SourceType) -> MemoryType:
    if source_type in {SourceType.JORDAN_INPUT, SourceType.EXTERNAL_TOOL}:
        return MemoryType.RECEIVED_INFORMATION
    if source_type is SourceType.DEDUCTION:
        return MemoryType.DEDUCTION
    raise ValueError(f"Provenance non autorisée dans P2 : {source_type.value}")


def _event_content(kind: EventKind, subject: str, value: str) -> str:
    if kind is EventKind.INITIAL:
        return f"{subject} est « {value} »."
    if kind is EventKind.CORRECTION:
        return f"Correction explicite : {subject} est désormais « {value} »."
    if kind is EventKind.CONTRADICTION:
        return f"Information contradictoire : {subject} est « {value} »."
    if kind is EventKind.RESOLUTION:
        return f"Résolution explicite : {subject} est fixé à « {value} »."
    return f"Confirmation : {subject} reste « {value} »."


def _transition_reason(kind: EventKind) -> str:
    return {
        EventKind.INITIAL: "État initial reçu.",
        EventKind.CORRECTION: "Correction explicite de la croyance précédente.",
        EventKind.CONTRADICTION: "Contradiction explicite laissée non résolue.",
        EventKind.RESOLUTION: "Résolution explicite de la contradiction.",
        EventKind.CONFIRMATION: "Confirmation sans changement de croyance.",
    }[kind]


def load_datasets(path: Path) -> tuple[ExperimentDataset, ...]:
    config = DatasetFile.model_validate_json(path.read_text(encoding="utf-8"))
    templates = {chain.slot: chain for chain in config.chains}
    datasets: list[ExperimentDataset] = []

    for dataset_index, spec in enumerate(config.datasets):
        event_counts: dict[int, int] = defaultdict(int)
        events: list[DatasetEvent] = []
        by_chain: dict[int, list[DatasetEvent]] = defaultdict(list)

        for stream_position, chain_slot in enumerate(config.event_stream, start=1):
            event_counts[chain_slot] += 1
            event_number = event_counts[chain_slot]
            template = templates[chain_slot]
            kind = template.event_kinds[event_number - 1]
            value = template.values[event_number - 1]
            source_index = (spec.source_offset + stream_position - 1) % 3
            source_type = config.source_order[source_index]
            subject = template.subject_template.format(namespace=spec.namespace)
            belief_key = f"{spec.id}:belief:{chain_slot:02d}"
            event = DatasetEvent(
                id=f"{spec.id}-event-{stream_position:03d}",
                dataset_id=spec.id,
                stream_position=stream_position,
                chain_slot=chain_slot,
                event_number=event_number,
                cycle_id=f"{spec.id}-cycle-{stream_position:03d}",
                belief_key=belief_key,
                subject=subject,
                family=template.family,
                kind=kind,
                value=value,
                content=_event_content(kind, subject, value),
                transition_reason=_transition_reason(kind),
                source_type=source_type,
                memory_type=memory_type_for_source(source_type),
            )
            events.append(event)
            by_chain[chain_slot].append(event)

        chains = tuple(
            ExperimentChain(
                id=f"{spec.id}-chain-{slot:02d}",
                dataset_id=spec.id,
                slot=slot,
                belief_key=f"{spec.id}:belief:{slot:02d}",
                subject=templates[slot].subject_template.format(namespace=spec.namespace),
                family=templates[slot].family,
                historical_event_number=templates[slot].historical_event_number,
                misleading_value=templates[slot].misleading_value,
                events=tuple(by_chain[slot]),
            )
            for slot in range(1, 13)
        )
        datasets.append(
            ExperimentDataset(
                id=spec.id,
                namespace=spec.namespace,
                events=tuple(events),
                chains=chains,
            )
        )

        if len(events) != 48:
            raise AssertionError(f"Jeu {dataset_index + 1} incomplet.")

    return tuple(datasets)


def canonical_dataset_json(path: Path) -> str:
    """Retourner la représentation JSON canonique utilisée pour le gel et le hash."""
    parsed = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
