"""Mécanismes déterministes de lecture pour EXP-001-P2.

Ce module ne contient aucune vérité terrain de score. Les conditions B et C
reçoivent les mêmes événements externes, mais les conservent sous des formes
différentes conformément au protocole préenregistré.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from soinesis.application.memory import MemoryApplicationService
from soinesis.domain.models import AutobiographicalMemory, RecordStatus, SourceType
from soinesis.experiments.exp_001_p2 import (
    DatasetEvent,
    EventKind,
    ExperimentChain,
    ExperimentDataset,
)
from soinesis.infrastructure.sqlite import SQLiteDatabase, SQLiteUnitOfWorkFactory

AGENT_ID = "agent_soinesis_exp_001_p2"
_VALUE_PATTERN = re.compile(r"«([^»]+)»")
_TEXT_LINE_PATTERN = re.compile(r"^Moment (?P<position>\d{3})\. (?P<source>.+?)\. (?P<content>.+)$")


class ExperimentCondition(StrEnum):
    A = "A"
    B = "B"
    C = "C"


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class P2Query(FrozenModel):
    dataset_id: str = Field(min_length=1)
    belief_key: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    historical_cycle_id: str = Field(min_length=1)
    trace_cycle_id: str = Field(min_length=1)


class P2Prediction(FrozenModel):
    condition: ExperimentCondition
    current_value: str | None
    contested_values: tuple[str, ...] = ()
    unresolved_contradiction: bool | None
    historical_value: str | None
    historical_contested_values: tuple[str, ...] = ()
    ordered_values: tuple[str, ...] = ()
    transition_reason: str | None
    transition_source: SourceType | None
    transition_cycle_id: str | None
    retrieved_memory_ids: tuple[str, ...] = ()
    repository_access_count: int = Field(default=0, ge=0)
    ablation_enabled: bool = False
    reason: str = Field(min_length=1)


class RawObservation(FrozenModel):
    cycle_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source_type: SourceType
    value: str = Field(min_length=1)


class EvidenceEvent(FrozenModel):
    position: int = Field(ge=1)
    cycle_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source_type: SourceType
    kind: EventKind
    value: str = Field(min_length=1)


class ReducedHistory(FrozenModel):
    current_value: str | None
    contested_values: tuple[str, ...]
    historical_value: str | None
    historical_contested_values: tuple[str, ...]
    ordered_values: tuple[str, ...]


class P2ExperimentClock:
    def __init__(self) -> None:
        self._index = 0
        self._origin = datetime(2026, 8, 7, 12, 0, tzinfo=UTC)

    def now(self) -> datetime:
        self._index += 1
        return self._origin + timedelta(seconds=self._index)


class P2ExperimentIdentifiers:
    def __init__(self) -> None:
        self._index = 0

    def new(self, prefix: str) -> str:
        self._index += 1
        return f"{prefix}_{self._index:06d}"


@dataclass
class _BeliefIngestionState:
    active_ids: list[str] = field(default_factory=lambda: list[str]())
    contested_ids: list[str] = field(default_factory=lambda: list[str]())
    values_by_memory_id: dict[str, str] = field(default_factory=lambda: dict[str, str]())


class NoHistoryCondition:
    """Condition A : aucune histoire persistante n'est disponible."""

    def inspect(self, query: P2Query) -> P2Prediction:
        del query
        return P2Prediction(
            condition=ExperimentCondition.A,
            current_value=None,
            unresolved_contradiction=None,
            historical_value=None,
            transition_reason=None,
            transition_source=None,
            transition_cycle_id=None,
            reason="Aucune histoire persistante n'est accessible dans la condition A.",
        )


class TextHistoryCondition:
    """Condition B : seul un historique chronologique en langue naturelle persiste."""

    def __init__(self, dataset: ExperimentDataset) -> None:
        self._dataset_id = dataset.id
        self._history = "\n".join(_text_history_line(event) for event in dataset.events)

    @property
    def history(self) -> str:
        return self._history

    def inspect(self, query: P2Query) -> P2Prediction:
        if query.dataset_id != self._dataset_id:
            raise ValueError("La requête ne correspond pas au jeu textuel chargé.")
        evidence = tuple(
            event
            for event in _parse_text_history(self._history, self._dataset_id)
            if query.subject in event.content
        )
        reduced = _reduce_history(evidence, query.historical_cycle_id)
        trace = next((event for event in evidence if event.cycle_id == query.trace_cycle_id), None)
        return P2Prediction(
            condition=ExperimentCondition.B,
            current_value=reduced.current_value,
            contested_values=reduced.contested_values,
            unresolved_contradiction=bool(reduced.contested_values),
            historical_value=reduced.historical_value,
            historical_contested_values=reduced.historical_contested_values,
            ordered_values=reduced.ordered_values,
            transition_reason=None if trace is None else _reason_for_kind(trace.kind),
            transition_source=None if trace is None else trace.source_type,
            transition_cycle_id=None if trace is None else trace.cycle_id,
            reason="Réponse reconstruite exclusivement depuis l'historique textuel B.",
        )


class StructuredHistoryCondition:
    """Condition C : mémoire révisable structurée et persistée dans SQLite."""

    def __init__(self, dataset: ExperimentDataset, database_path: Path) -> None:
        database_path.unlink(missing_ok=True)
        self._database = SQLiteDatabase(database_path)
        self._database.initialize_schema()
        self._factory = SQLiteUnitOfWorkFactory(self._database)
        self._service = MemoryApplicationService(
            unit_of_work_factory=self._factory,
            clock=P2ExperimentClock(),
            identifiers=P2ExperimentIdentifiers(),
        )
        self._dataset_id = dataset.id
        self._revision_metadata_access_count = 0
        self._ingest(dataset)

    @property
    def revision_metadata_access_count(self) -> int:
        return self._revision_metadata_access_count

    def inspect(self, query: P2Query) -> P2Prediction:
        if query.dataset_id != self._dataset_id:
            raise ValueError("La requête ne correspond pas au jeu structuré chargé.")

        access_count_before = self._revision_metadata_access_count
        memories = self._structured_memories(query.belief_key)
        evidence = self._raw_evidence(query.subject)
        reduced = _reduce_history(evidence, query.historical_cycle_id)
        active = tuple(memory for memory in memories if memory.status is RecordStatus.ACTIVE)
        contested = tuple(memory for memory in memories if memory.status is RecordStatus.CONTESTED)

        if active and contested:
            raise RuntimeError(
                "Une croyance P2 ne peut pas être active et contestée simultanément."
            )
        if len(active) > 1:
            raise RuntimeError("Une croyance P2 ne peut pas avoir plusieurs versions actives.")

        current_value = None if not active else _value_from_content(active[0].content)
        contested_values = tuple(_value_from_content(memory.content) for memory in contested)
        trace = next(
            (memory for memory in memories if memory.cycle_id == query.trace_cycle_id), None
        )

        return P2Prediction(
            condition=ExperimentCondition.C,
            current_value=current_value,
            contested_values=contested_values,
            unresolved_contradiction=bool(contested_values),
            historical_value=reduced.historical_value,
            historical_contested_values=reduced.historical_contested_values,
            ordered_values=reduced.ordered_values,
            transition_reason=None if trace is None else trace.transition_reason,
            transition_source=None if trace is None else trace.source_type,
            transition_cycle_id=None if trace is None else trace.cycle_id,
            retrieved_memory_ids=tuple(memory.id for memory in memories),
            repository_access_count=(
                self._revision_metadata_access_count - access_count_before
            ),
            reason=(
                "État courant et transition lus depuis la mémoire structurée C ; "
                "continuité historique reconstruite depuis les événements bruts persistés."
            ),
        )

    def inspect_ablated(self, query: P2Query) -> P2Prediction:
        """Lit uniquement les observations brutes autorisées par l'ablation T9."""

        if query.dataset_id != self._dataset_id:
            raise ValueError("La requête ne correspond pas au jeu structuré chargé.")

        access_count_before = self._revision_metadata_access_count
        observations = self._raw_observations(query.subject)
        trace = next(
            (
                observation
                for observation in observations
                if observation.cycle_id == query.trace_cycle_id
            ),
            None,
        )
        access_count = self._revision_metadata_access_count - access_count_before
        if access_count != 0:
            raise RuntimeError("L'ablation P2 a consulté des métadonnées de révision interdites.")

        return P2Prediction(
            condition=ExperimentCondition.C,
            current_value=None,
            unresolved_contradiction=None,
            historical_value=None,
            ordered_values=tuple(observation.value for observation in observations),
            transition_reason=None,
            transition_source=None if trace is None else trace.source_type,
            transition_cycle_id=None if trace is None else trace.cycle_id,
            repository_access_count=access_count,
            ablation_enabled=True,
            reason=(
                "Ablation T9 active : seules les observations brutes, leur provenance et "
                "leur ordre sont accessibles ; aucun statut, lien, raison structurée ou "
                "journal de transition n'est consulté ni reconstruit."
            ),
        )

    def _ingest(self, dataset: ExperimentDataset) -> None:
        states: dict[str, _BeliefIngestionState] = {}
        for event in dataset.events:
            state = states.setdefault(event.belief_key, _BeliefIngestionState())
            self._ingest_event(event, state)

    def _ingest_event(self, event: DatasetEvent, state: _BeliefIngestionState) -> None:
        if event.kind is EventKind.INITIAL:
            if state.active_ids or state.contested_ids:
                raise ValueError("Un état initial ne peut pas être injecté deux fois.")
            recorded = self._service.record_memory(
                agent_id=AGENT_ID,
                cycle_id=event.cycle_id,
                title=event.subject,
                content=event.content,
                memory_type=event.memory_type,
                source_type=event.source_type,
                status=RecordStatus.ACTIVE,
                belief_key=event.belief_key,
                transition_reason=event.transition_reason,
            )
            state.active_ids = [recorded.memory.id]
            state.values_by_memory_id[recorded.memory.id] = event.value
            return

        if event.kind is EventKind.CONFIRMATION:
            target_id = self._confirmation_target(event, state)
            self._service.record_belief_confirmation(
                agent_id=AGENT_ID,
                cycle_id=event.cycle_id,
                memory_id=target_id,
                content=event.content,
                source_type=event.source_type,
            )
            return

        if event.kind is EventKind.CORRECTION:
            if len(state.active_ids) != 1 or state.contested_ids:
                raise ValueError("Une correction P2 attend exactement une version active.")
            parent_id = state.active_ids[0]
            recorded = self._service.record_belief_transition(
                agent_id=AGENT_ID,
                cycle_id=event.cycle_id,
                belief_key=event.belief_key,
                title=event.subject,
                content=event.content,
                memory_type=event.memory_type,
                source_type=event.source_type,
                parent_memory_ids=(parent_id,),
                parent_new_status=RecordStatus.SUPERSEDED,
                new_status=RecordStatus.ACTIVE,
                transition_reason=event.transition_reason,
            )
            state.active_ids = [recorded.memory.id]
            state.values_by_memory_id[recorded.memory.id] = event.value
            return

        if event.kind is EventKind.CONTRADICTION:
            if len(state.active_ids) != 1 or state.contested_ids:
                raise ValueError("Une contradiction P2 attend exactement une version active.")
            parent_id = state.active_ids[0]
            recorded = self._service.record_belief_transition(
                agent_id=AGENT_ID,
                cycle_id=event.cycle_id,
                belief_key=event.belief_key,
                title=event.subject,
                content=event.content,
                memory_type=event.memory_type,
                source_type=event.source_type,
                parent_memory_ids=(parent_id,),
                parent_new_status=RecordStatus.CONTESTED,
                new_status=RecordStatus.CONTESTED,
                transition_reason=event.transition_reason,
            )
            state.active_ids = []
            state.contested_ids = [parent_id, recorded.memory.id]
            state.values_by_memory_id[recorded.memory.id] = event.value
            return

        if not state.contested_ids or state.active_ids:
            raise ValueError("Une résolution P2 attend une contradiction ouverte.")
        recorded = self._service.record_belief_transition(
            agent_id=AGENT_ID,
            cycle_id=event.cycle_id,
            belief_key=event.belief_key,
            title=event.subject,
            content=event.content,
            memory_type=event.memory_type,
            source_type=event.source_type,
            parent_memory_ids=tuple(state.contested_ids),
            parent_new_status=RecordStatus.SUPERSEDED,
            new_status=RecordStatus.ACTIVE,
            transition_reason=event.transition_reason,
        )
        state.active_ids = [recorded.memory.id]
        state.contested_ids = []
        state.values_by_memory_id[recorded.memory.id] = event.value

    @staticmethod
    def _confirmation_target(event: DatasetEvent, state: _BeliefIngestionState) -> str:
        candidates = state.active_ids if state.active_ids else state.contested_ids
        matching = [
            memory_id
            for memory_id in candidates
            if state.values_by_memory_id.get(memory_id) == event.value
        ]
        if len(matching) != 1:
            raise ValueError("La confirmation ne correspond pas à une version unique.")
        return matching[0]

    def _structured_memories(self, belief_key: str) -> tuple[AutobiographicalMemory, ...]:
        self._revision_metadata_access_count += 1
        with self._factory() as unit_of_work:
            return tuple(
                unit_of_work.memories.list_for_belief(
                    agent_id=AGENT_ID,
                    belief_key=belief_key,
                )
            )

    def _raw_observations(self, subject: str) -> tuple[RawObservation, ...]:
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT cycle_id, raw_content, source_type
                FROM observations
                WHERE agent_id = ?
                ORDER BY received_at ASC, id ASC
                """,
                (AGENT_ID,),
            ).fetchall()
        observations: list[RawObservation] = []
        for row in rows:
            content = str(row["raw_content"])
            if subject not in content:
                continue
            observations.append(
                RawObservation(
                    cycle_id=str(row["cycle_id"]),
                    content=content,
                    source_type=SourceType(str(row["source_type"])),
                    value=_value_from_content(content),
                )
            )
        return tuple(observations)

    def _raw_evidence(self, subject: str) -> tuple[EvidenceEvent, ...]:
        return tuple(
            EvidenceEvent(
                position=_cycle_position(observation.cycle_id),
                cycle_id=observation.cycle_id,
                content=observation.content,
                source_type=observation.source_type,
                kind=_kind_from_content(observation.content),
                value=observation.value,
            )
            for observation in self._raw_observations(subject)
        )


def build_query(chain: ExperimentChain) -> P2Query:
    historical = chain.events[chain.historical_event_number - 1]
    trace = next(
        (
            event
            for event in reversed(chain.events)
            if event.kind
            in {
                EventKind.CORRECTION,
                EventKind.CONTRADICTION,
                EventKind.RESOLUTION,
            }
        ),
        chain.events[0],
    )
    return P2Query(
        dataset_id=chain.dataset_id,
        belief_key=chain.belief_key,
        subject=chain.subject,
        historical_cycle_id=historical.cycle_id,
        trace_cycle_id=trace.cycle_id,
    )


def _text_history_line(event: DatasetEvent) -> str:
    source = {
        SourceType.JORDAN_INPUT: "Jordan indique",
        SourceType.EXTERNAL_TOOL: "Un outil externe indique",
        SourceType.DEDUCTION: "Une déduction interne conclut",
    }[event.source_type]
    return f"Moment {event.stream_position:03d}. {source}. {event.content}"


def _parse_text_history(history: str, dataset_id: str) -> tuple[EvidenceEvent, ...]:
    events: list[EvidenceEvent] = []
    for line in history.splitlines():
        match = _TEXT_LINE_PATTERN.fullmatch(line)
        if match is None:
            raise ValueError("Une ligne de l'historique B ne respecte pas le format figé.")
        position = int(match.group("position"))
        source_type = {
            "Jordan indique": SourceType.JORDAN_INPUT,
            "Un outil externe indique": SourceType.EXTERNAL_TOOL,
            "Une déduction interne conclut": SourceType.DEDUCTION,
        }.get(match.group("source"))
        if source_type is None:
            raise ValueError("Provenance textuelle B inconnue.")
        content = match.group("content")
        events.append(
            EvidenceEvent(
                position=position,
                cycle_id=f"{dataset_id}-cycle-{position:03d}",
                content=content,
                source_type=source_type,
                kind=_kind_from_content(content),
                value=_value_from_content(content),
            )
        )
    return tuple(events)


def _reduce_history(
    events: tuple[EvidenceEvent, ...],
    historical_cycle_id: str,
) -> ReducedHistory:
    active: tuple[str, ...] = ()
    contested: tuple[str, ...] = ()
    historical_active: tuple[str, ...] = ()
    historical_contested: tuple[str, ...] = ()
    ordered_values: list[str] = []

    for event in events:
        if event.kind is not EventKind.CONFIRMATION:
            ordered_values.append(event.value)
        if event.kind is EventKind.INITIAL or event.kind is EventKind.CORRECTION:
            active = (event.value,)
            contested = ()
        elif event.kind is EventKind.CONTRADICTION:
            contested = tuple(dict.fromkeys((*active, event.value)))
            active = ()
        elif event.kind is EventKind.RESOLUTION:
            active = (event.value,)
            contested = ()

        if event.cycle_id == historical_cycle_id:
            historical_active = active
            historical_contested = contested

    if len(active) > 1 or len(historical_active) > 1:
        raise RuntimeError("Le réducteur P2 a produit plusieurs états actifs.")

    return ReducedHistory(
        current_value=None if not active else active[0],
        contested_values=contested,
        historical_value=None if not historical_active else historical_active[0],
        historical_contested_values=historical_contested,
        ordered_values=tuple(ordered_values),
    )


def _kind_from_content(content: str) -> EventKind:
    if content.startswith("Correction explicite :"):
        return EventKind.CORRECTION
    if content.startswith("Information contradictoire :"):
        return EventKind.CONTRADICTION
    if content.startswith("Résolution explicite :"):
        return EventKind.RESOLUTION
    if content.startswith("Confirmation :"):
        return EventKind.CONFIRMATION
    return EventKind.INITIAL


def _value_from_content(content: str) -> str:
    match = _VALUE_PATTERN.search(content)
    if match is None:
        raise ValueError("Aucune valeur entre guillemets français dans l'événement P2.")
    return match.group(1).strip()


def _reason_for_kind(kind: EventKind) -> str:
    return {
        EventKind.INITIAL: "État initial reçu.",
        EventKind.CORRECTION: "Correction explicite de la croyance précédente.",
        EventKind.CONTRADICTION: "Contradiction explicite laissée non résolue.",
        EventKind.RESOLUTION: "Résolution explicite de la contradiction.",
        EventKind.CONFIRMATION: "Confirmation sans changement de croyance.",
    }[kind]


def _cycle_position(cycle_id: str) -> int:
    try:
        return int(cycle_id.rsplit("-", 1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Cycle P2 invalide : {cycle_id}") from exc