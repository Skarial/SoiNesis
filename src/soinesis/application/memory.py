"""Cas d'usage de la mémoire autobiographique."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from soinesis.domain.models import (
    AblationConfiguration,
    AutobiographicalMemory,
    EventType,
    JournalEvent,
    MemoryType,
    Observation,
    RecallDecision,
    RecordStatus,
    SourceType,
)
from soinesis.ports.repositories import UnitOfWorkFactory
from soinesis.ports.system import Clock, IdentifierGenerator


class RecordedMemory(BaseModel):
    """Résultat immuable de la consolidation d'un souvenir."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    observation: Observation
    memory: AutobiographicalMemory
    event: JournalEvent


class RecordedTransition(BaseModel):
    """Révision persistée avec ses changements de statut journalisés."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    observation: Observation
    memory: AutobiographicalMemory
    status_events: tuple[JournalEvent, ...]
    revision_event: JournalEvent


class RecordedConfirmation(BaseModel):
    """Confirmation persistée sans création artificielle d'une nouvelle version."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    observation: Observation
    memory_id: str
    event: JournalEvent


class MemoryApplicationService:
    """Orchestrer observation, mémoire, décision et journal."""

    def __init__(
        self,
        *,
        unit_of_work_factory: UnitOfWorkFactory,
        clock: Clock,
        identifiers: IdentifierGenerator,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._identifiers = identifiers

    def record_memory(
        self,
        *,
        agent_id: str,
        cycle_id: str,
        title: str,
        content: str,
        memory_type: MemoryType,
        source_type: SourceType,
        confidence: float = 1.0,
        importance: float = 0.5,
        status: RecordStatus = RecordStatus.ACTIVE,
        belief_key: str | None = None,
        parent_memory_ids: tuple[str, ...] = (),
        transition_reason: str | None = None,
    ) -> RecordedMemory:
        """Consolider atomiquement un souvenir explicitement typé et sourcé."""
        now = self._clock.now()
        is_direct_experience = memory_type is MemoryType.DIRECT_EXPERIENCE
        observation = Observation(
            id=self._identifiers.new("observation"),
            agent_id=agent_id,
            cycle_id=cycle_id,
            source_type=source_type,
            raw_content=content,
            received_at=now,
            confidence=confidence,
            is_direct_experience=is_direct_experience,
        )
        memory = AutobiographicalMemory(
            id=self._identifiers.new("memory"),
            agent_id=agent_id,
            cycle_id=cycle_id,
            source_observation_id=observation.id,
            memory_type=memory_type,
            title=title,
            content=content,
            source_type=source_type,
            confidence=confidence,
            importance=importance,
            status=status,
            created_at=now,
            is_direct_experience=is_direct_experience,
            belief_key=belief_key,
            parent_memory_ids=parent_memory_ids,
            transition_reason=transition_reason,
        )
        event = JournalEvent(
            id=self._identifiers.new("event"),
            agent_id=agent_id,
            cycle_id=cycle_id,
            event_type=EventType.MEMORY_CREATED,
            target_entity_type="AutobiographicalMemory",
            target_entity_id=memory.id,
            occurred_at=now,
            reason=f"Consolidation explicite d'un souvenir de type {memory_type.value}.",
            new_value={
                "memory_type": memory.memory_type.value,
                "source_type": memory.source_type.value,
                "title": memory.title,
                "confidence": memory.confidence,
                "importance": memory.importance,
                "status": memory.status.value,
                "belief_key": memory.belief_key,
                "parent_memory_ids": list(memory.parent_memory_ids),
                "transition_reason": memory.transition_reason,
            },
        )

        with self._unit_of_work_factory() as unit_of_work:
            unit_of_work.observations.add(observation)
            unit_of_work.memories.add(memory)
            unit_of_work.journal.append(event)
            unit_of_work.commit()

        return RecordedMemory(observation=observation, memory=memory, event=event)

    def record_belief_transition(
        self,
        *,
        agent_id: str,
        cycle_id: str,
        belief_key: str,
        title: str,
        content: str,
        memory_type: MemoryType,
        source_type: SourceType,
        parent_memory_ids: tuple[str, ...],
        parent_new_status: RecordStatus,
        new_status: RecordStatus,
        transition_reason: str,
        confidence: float = 1.0,
        importance: float = 0.5,
    ) -> RecordedTransition:
        """Créer une nouvelle version et modifier ses parents dans une transaction unique."""
        if not parent_memory_ids:
            raise ValueError("Une transition doit référencer au moins un souvenir parent.")

        now = self._clock.now()
        is_direct_experience = memory_type is MemoryType.DIRECT_EXPERIENCE
        observation = Observation(
            id=self._identifiers.new("observation"),
            agent_id=agent_id,
            cycle_id=cycle_id,
            source_type=source_type,
            raw_content=content,
            received_at=now,
            confidence=confidence,
            is_direct_experience=is_direct_experience,
        )
        memory = AutobiographicalMemory(
            id=self._identifiers.new("memory"),
            agent_id=agent_id,
            cycle_id=cycle_id,
            source_observation_id=observation.id,
            memory_type=memory_type,
            title=title,
            content=content,
            source_type=source_type,
            confidence=confidence,
            importance=importance,
            status=new_status,
            created_at=now,
            is_direct_experience=is_direct_experience,
            belief_key=belief_key,
            parent_memory_ids=parent_memory_ids,
            transition_reason=transition_reason,
        )

        with self._unit_of_work_factory() as unit_of_work:
            parents: list[AutobiographicalMemory] = []
            for parent_id in parent_memory_ids:
                parent = unit_of_work.memories.get(parent_id)
                if parent is None:
                    raise ValueError(f"Souvenir parent introuvable : {parent_id}")
                if parent.agent_id != agent_id:
                    raise ValueError("Une transition ne peut pas relier deux agents différents.")
                if parent.belief_key != belief_key:
                    raise ValueError("Tous les parents doivent appartenir à la même croyance.")
                if parent.status is parent_new_status:
                    raise ValueError("Une transition doit modifier réellement le statut de son parent.")
                parents.append(parent)

            unit_of_work.observations.add(observation)
            status_events: list[JournalEvent] = []
            for parent in parents:
                unit_of_work.memories.update_status(
                    memory_id=parent.id,
                    status=parent_new_status,
                )
                status_event = JournalEvent(
                    id=self._identifiers.new("event"),
                    agent_id=agent_id,
                    cycle_id=cycle_id,
                    event_type=EventType.MEMORY_STATUS_CHANGED,
                    target_entity_type="AutobiographicalMemory",
                    target_entity_id=parent.id,
                    occurred_at=now,
                    reason=transition_reason,
                    new_value={
                        "belief_key": belief_key,
                        "old_status": parent.status.value,
                        "new_status": parent_new_status.value,
                        "trigger_memory_id": memory.id,
                    },
                )
                unit_of_work.journal.append(status_event)
                status_events.append(status_event)

            unit_of_work.memories.add(memory)
            revision_event = JournalEvent(
                id=self._identifiers.new("event"),
                agent_id=agent_id,
                cycle_id=cycle_id,
                event_type=EventType.MEMORY_REVISION_CREATED,
                target_entity_type="AutobiographicalMemory",
                target_entity_id=memory.id,
                occurred_at=now,
                reason=transition_reason,
                new_value={
                    "belief_key": belief_key,
                    "status": new_status.value,
                    "parent_memory_ids": list(parent_memory_ids),
                    "transition_reason": transition_reason,
                    "source_type": source_type.value,
                },
            )
            unit_of_work.journal.append(revision_event)
            unit_of_work.commit()

        return RecordedTransition(
            observation=observation,
            memory=memory,
            status_events=tuple(status_events),
            revision_event=revision_event,
        )

    def record_belief_confirmation(
        self,
        *,
        agent_id: str,
        cycle_id: str,
        memory_id: str,
        content: str,
        source_type: SourceType,
        confidence: float = 1.0,
    ) -> RecordedConfirmation:
        """Journaliser une confirmation sans créer une nouvelle version de croyance."""
        now = self._clock.now()
        observation = Observation(
            id=self._identifiers.new("observation"),
            agent_id=agent_id,
            cycle_id=cycle_id,
            source_type=source_type,
            raw_content=content,
            received_at=now,
            confidence=confidence,
            is_direct_experience=False,
        )

        with self._unit_of_work_factory() as unit_of_work:
            memory = unit_of_work.memories.get(memory_id)
            if memory is None:
                raise ValueError(f"Souvenir à confirmer introuvable : {memory_id}")
            if memory.agent_id != agent_id:
                raise ValueError("Une confirmation ne peut pas viser un autre agent.")
            if memory.belief_key is None:
                raise ValueError("Une confirmation P2 doit viser une croyance structurée.")
            if memory.status not in {RecordStatus.ACTIVE, RecordStatus.CONTESTED}:
                raise ValueError("Seule une croyance active ou contestée peut être confirmée.")

            event = JournalEvent(
                id=self._identifiers.new("event"),
                agent_id=agent_id,
                cycle_id=cycle_id,
                event_type=EventType.MEMORY_CONFIRMED,
                target_entity_type="AutobiographicalMemory",
                target_entity_id=memory.id,
                occurred_at=now,
                reason="Confirmation persistée sans remplacement de la version courante.",
                new_value={
                    "belief_key": memory.belief_key,
                    "observation_id": observation.id,
                    "source_type": source_type.value,
                    "status": memory.status.value,
                },
            )
            unit_of_work.observations.add(observation)
            unit_of_work.journal.append(event)
            unit_of_work.commit()

        return RecordedConfirmation(
            observation=observation,
            memory_id=memory_id,
            event=event,
        )

    def record_received_information(
        self,
        *,
        agent_id: str,
        cycle_id: str,
        title: str,
        content: str,
        source_type: SourceType,
        confidence: float = 1.0,
        importance: float = 0.5,
    ) -> RecordedMemory:
        """Consolider une information reçue sans la confondre avec une production interne."""
        return self.record_memory(
            agent_id=agent_id,
            cycle_id=cycle_id,
            title=title,
            content=content,
            memory_type=MemoryType.RECEIVED_INFORMATION,
            source_type=source_type,
            confidence=confidence,
            importance=importance,
        )

    def record_deduction(
        self,
        *,
        agent_id: str,
        cycle_id: str,
        title: str,
        content: str,
        confidence: float = 1.0,
        importance: float = 0.5,
    ) -> RecordedMemory:
        """Consolider une déduction en conservant explicitement son origine interne."""
        return self.record_memory(
            agent_id=agent_id,
            cycle_id=cycle_id,
            title=title,
            content=content,
            memory_type=MemoryType.DEDUCTION,
            source_type=SourceType.DEDUCTION,
            confidence=confidence,
            importance=importance,
        )

    def record_imagination(
        self,
        *,
        agent_id: str,
        cycle_id: str,
        title: str,
        content: str,
        confidence: float = 1.0,
        importance: float = 0.5,
    ) -> RecordedMemory:
        """Consolider un scénario imaginé sans le transformer en fait reçu."""
        return self.record_memory(
            agent_id=agent_id,
            cycle_id=cycle_id,
            title=title,
            content=content,
            memory_type=MemoryType.IMAGINED_SCENARIO,
            source_type=SourceType.IMAGINATION,
            confidence=confidence,
            importance=importance,
        )

    def recall(
        self,
        *,
        agent_id: str,
        query: str,
        ablation: AblationConfiguration,
    ) -> RecallDecision:
        """Produire une décision simple à partir d'un souvenir pertinent."""
        if not ablation.autobiographical_memory_enabled:
            return RecallDecision(
                answer=None,
                confidence=0.0,
                source_type=None,
                retrieved_memory_ids=(),
                reason="Mémoire autobiographique désactivée par la configuration d'ablation.",
            )

        with self._unit_of_work_factory() as unit_of_work:
            memories = unit_of_work.memories.search(
                agent_id=agent_id,
                query=query,
                limit=5,
            )

        if not memories:
            return RecallDecision(
                answer=None,
                confidence=0.0,
                source_type=None,
                retrieved_memory_ids=(),
                reason="Aucun souvenir pertinent n'a été trouvé.",
            )

        selected = memories[0]
        return RecallDecision(
            answer=selected.content,
            confidence=selected.confidence,
            source_type=selected.source_type,
            retrieved_memory_ids=tuple(memory.id for memory in memories),
            reason="Réponse fondée sur le souvenir actif le plus pertinent.",
        )
