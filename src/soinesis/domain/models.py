"""Modèles du domaine utilisés par la première tranche verticale."""

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
    """Catégories minimales de souvenirs pour la première tranche."""

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
    """Événements du journal produits par la première tranche."""

    MEMORY_CREATED = "MEMORY_CREATED"


class DomainModel(BaseModel):
    """Configuration commune aux modèles immuables du domaine."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class Observation(DomainModel):
    """Entrée structurée reçue pendant un cycle cognitif."""

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
    """Souvenir autobiographique persistant et sourcé."""

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

    @model_validator(mode="after")
    def validate_memory_source(self) -> AutobiographicalMemory:
        """Conserver une séparation cohérente entre type et provenance."""
        if self.is_direct_experience and self.source_type is not SourceType.DIRECT_ENVIRONMENT:
            raise ValueError("Un souvenir direct doit provenir de DIRECT_ENVIRONMENT.")
        if (
            self.memory_type is MemoryType.IMAGINED_SCENARIO
            and self.source_type is not SourceType.IMAGINATION
        ):
            raise ValueError("Un scénario imaginé doit utiliser la source IMAGINATION.")
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
