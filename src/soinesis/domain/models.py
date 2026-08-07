"""Modèles du domaine utilisés par le socle expérimental de SoiNesis."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SourceType(StrEnum):
    """Provenance principale d'une information."""

    JORDAN_INPUT = "JORDAN_INPUT"
    EXPERIMENTER_INPUT = "EXPERIMENTER_INPUT"
    DIRECT_ENVIRONMENT = "DIRECT_ENVIRONMENT"
    INTERNAL_STATE = "INTERNAL_STATE"
    LANGUAGE_MODEL_OUTPUT = "LANGUAGE_MODEL_OUTPUT"
    EXTERNAL_TOOL = "EXTERNAL_TOOL"
    SYSTEM_RULE = "SYSTEM_RULE"
    DEDUCTION = "DEDUCTION"
    IMAGINATION = "IMAGINATION"
    UNKNOWN = "UNKNOWN"


class MemoryType(StrEnum):
    """Catégories minimales de souvenirs."""

    RECEIVED_INFORMATION = "RECEIVED_INFORMATION"
    DIRECT_EXPERIENCE = "DIRECT_EXPERIENCE"
    DEDUCTION = "DEDUCTION"
    IMAGINED_SCENARIO = "IMAGINED_SCENARIO"


class RecordStatus(StrEnum):
    """États persistants utilisés par la première tranche."""

    ACTIVE = "ACTIVE"
    CONTESTED = "CONTESTED"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"
    INVALID = "INVALID"


class EventType(StrEnum):
    """Événements immuables du journal d'évolution."""

    MEMORY_CREATED = "MEMORY_CREATED"
    MEMORY_STATUS_CHANGED = "MEMORY_STATUS_CHANGED"
    MEMORY_REVISION_CREATED = "MEMORY_REVISION_CREATED"
    MEMORY_CONFIRMED = "MEMORY_CONFIRMED"


class DomainModel(BaseModel):
    """Configuration commune aux modèles immuables du domaine."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class Observation(DomainModel):
    """Entrée structurée reçue ou produite pendant un cycle cognitif."""

    id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    cycle_id: str = Field(min_length=1)
    source_type: SourceType
    raw_content: str = Field(min_length=1)
    received_at: datetime
    confidence: float = Field(ge=0.0, le=1.0)
    is_direct_experience: bool = False

    @model_validator(mode="after")
    def validate_direct_experience(self) -> Observation:
        """Empêcher l'assimilation d'une information reçue à un vécu direct."""
        if self.is_direct_experience and self.source_type is not SourceType.DIRECT_ENVIRONMENT:
            raise ValueError(
                "Une observation ne peut être directe que si sa source est DIRECT_ENVIRONMENT."
            )
        return self


class AutobiographicalMemory(DomainModel):
    """Souvenir autobiographique persistant, sourcé et éventuellement révisable."""

    id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    cycle_id: str = Field(min_length=1)
    source_observation_id: str = Field(min_length=1)
    memory_type: MemoryType
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source_type: SourceType
    confidence: float = Field(ge=0.0, le=1.0)
    importance: float = Field(ge=0.0, le=1.0)
    status: RecordStatus = RecordStatus.ACTIVE
    created_at: datetime
    is_direct_experience: bool = False
    belief_key: str | None = Field(default=None, min_length=1)
    parent_memory_ids: tuple[str, ...] = ()
    transition_reason: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_memory_source(self) -> AutobiographicalMemory:
        """Conserver une séparation cohérente entre type, provenance et révision."""
        if self.is_direct_experience and self.source_type is not SourceType.DIRECT_ENVIRONMENT:
            raise ValueError("Un souvenir direct doit provenir de DIRECT_ENVIRONMENT.")
        if self.memory_type is MemoryType.DIRECT_EXPERIENCE and not self.is_direct_experience:
            raise ValueError(
                "Un souvenir DIRECT_EXPERIENCE doit être marqué comme expérience directe."
            )
        if (
            self.memory_type is MemoryType.DEDUCTION
            and self.source_type is not SourceType.DEDUCTION
        ):
            raise ValueError("Une déduction doit utiliser la source DEDUCTION.")
        if (
            self.memory_type is MemoryType.IMAGINED_SCENARIO
            and self.source_type is not SourceType.IMAGINATION
        ):
            raise ValueError("Un scénario imaginé doit utiliser la source IMAGINATION.")
        if self.memory_type is MemoryType.RECEIVED_INFORMATION and self.source_type in {
            SourceType.DEDUCTION,
            SourceType.IMAGINATION,
        }:
            raise ValueError(
                "Une déduction ou une imagination ne peut pas être classée comme information reçue."
            )
        if self.parent_memory_ids and self.belief_key is None:
            raise ValueError("Une relation de révision doit appartenir à une clé de croyance.")
        if self.transition_reason is not None and self.belief_key is None:
            raise ValueError("Une raison de transition doit appartenir à une clé de croyance.")
        if self.id in self.parent_memory_ids:
            raise ValueError("Un souvenir ne peut pas être son propre parent.")
        if len(set(self.parent_memory_ids)) != len(self.parent_memory_ids):
            raise ValueError("Les parents d'un souvenir doivent être uniques.")
        return self


class JournalEvent(DomainModel):
    """Événement immuable décrivant un changement important."""

    id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    cycle_id: str = Field(min_length=1)
    event_type: EventType
    target_entity_type: str = Field(min_length=1)
    target_entity_id: str = Field(min_length=1)
    occurred_at: datetime
    reason: str = Field(min_length=1)
    new_value: dict[str, Any] = Field(default_factory=dict)


class AblationConfiguration(DomainModel):
    """Configuration expérimentale minimale."""

    id: str = Field(min_length=1)
    autobiographical_memory_enabled: bool = True


class RecallDecision(DomainModel):
    """Décision de réponse produite à partir de la mémoire disponible."""

    answer: str | None
    confidence: float = Field(ge=0.0, le=1.0)
    source_type: SourceType | None
    retrieved_memory_ids: tuple[str, ...] = ()
    reason: str = Field(min_length=1)
