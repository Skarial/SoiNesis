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
            created_at=now,
            is_direct_experience=is_direct_experience,
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
            },
        )

        with self._unit_of_work_factory() as unit_of_work:
            unit_of_work.observations.add(observation)
            unit_of_work.memories.add(memory)
            unit_of_work.journal.append(event)
            unit_of_work.commit()

        return RecordedMemory(observation=observation, memory=memory, event=event)

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
