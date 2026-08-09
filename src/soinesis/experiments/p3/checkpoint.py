"""Checkpoint persistant privé pour l'exécution causale P3 DEV."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from soinesis.domain.capabilities import CapabilityDecision


class ExperimentalCycleCheckpointStatus(StrEnum):
    """États persistants autorisés pour un cycle expérimental."""

    STARTED = "STARTED"
    COMPLETED = "COMPLETED"


class ExperimentalCycleCheckpoint(BaseModel):
    """Contexte et décision publics figés avant une tentative P3."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(min_length=1)
    sequence_index: int = Field(ge=0, strict=True)
    performance_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    trial_id: str = Field(min_length=1)
    cycle_id: str = Field(min_length=1)
    capability_key: str = Field(min_length=1)
    observed_at: datetime
    decision: CapabilityDecision
    status: ExperimentalCycleCheckpointStatus

    @model_validator(mode="after")
    def validate_decision_scope(self) -> ExperimentalCycleCheckpoint:
        """Garantir que la décision figée concerne exactement ce cycle."""
        if self.decision.estimate.agent_id != self.agent_id:
            raise ValueError("La décision doit concerner le même agent que le checkpoint.")
        if self.decision.estimate.capability_key != self.capability_key:
            raise ValueError("La décision doit concerner la même capacité que le checkpoint.")
        return self


class ExperimentalCycleCheckpointError(RuntimeError):
    """Erreur de base du checkpoint expérimental P3 DEV."""


class ExperimentalCycleCheckpointIntegrityError(ExperimentalCycleCheckpointError):
    """Signale une collision avec un contexte ou une décision différents."""


class ExperimentalCycleCheckpointOrderError(ExperimentalCycleCheckpointError):
    """Signale une tentative qui viole l'ordre causal d'une exécution."""


class ExperimentalCycleCheckpointNotFoundError(ExperimentalCycleCheckpointError):
    """Signale une tentative de complétion sans checkpoint correspondant."""


class ExperimentalCycleCheckpointRepository(Protocol):
    """Persistance atomique propre au banc expérimental P3 DEV."""

    def get(
        self, *, execution_id: str, sequence_index: int
    ) -> ExperimentalCycleCheckpoint | None: ...

    def begin(self, checkpoint: ExperimentalCycleCheckpoint) -> ExperimentalCycleCheckpoint: ...

    def complete(
        self, *, execution_id: str, sequence_index: int
    ) -> ExperimentalCycleCheckpoint: ...


class ExperimentalCycleCheckpointService:
    """Façade expérimentale des transitions atomiques d'un checkpoint."""

    def __init__(self, repository: ExperimentalCycleCheckpointRepository) -> None:
        self._repository = repository

    def get(self, *, execution_id: str, sequence_index: int) -> ExperimentalCycleCheckpoint | None:
        """Relire un snapshot persistant sans recalculer sa décision."""
        return self._repository.get(
            execution_id=execution_id,
            sequence_index=sequence_index,
        )

    def begin(
        self,
        *,
        execution_id: str,
        sequence_index: int,
        performance_id: str,
        agent_id: str,
        trial_id: str,
        cycle_id: str,
        capability_key: str,
        observed_at: datetime,
        decision: CapabilityDecision,
    ) -> ExperimentalCycleCheckpoint:
        """Figer le contexte pré-performance ou relire le checkpoint identique."""
        checkpoint = ExperimentalCycleCheckpoint(
            execution_id=execution_id,
            sequence_index=sequence_index,
            performance_id=performance_id,
            agent_id=agent_id,
            trial_id=trial_id,
            cycle_id=cycle_id,
            capability_key=capability_key,
            observed_at=observed_at,
            decision=decision,
            status=ExperimentalCycleCheckpointStatus.STARTED,
        )
        return self._repository.begin(checkpoint)

    def complete(self, *, execution_id: str, sequence_index: int) -> ExperimentalCycleCheckpoint:
        """Marquer le cycle terminé sans créer le cycle suivant."""
        return self._repository.complete(
            execution_id=execution_id,
            sequence_index=sequence_index,
        )
