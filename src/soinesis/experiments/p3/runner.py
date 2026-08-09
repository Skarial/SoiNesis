"""Orchestration causale et reprenable d'un unique cycle P3 DEV."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from soinesis.domain.capabilities import (
    CapabilityDecision,
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
)
from soinesis.experiments.p3.checkpoint import (
    ExperimentalCycleCheckpoint,
    ExperimentalCycleCheckpointStatus,
)
from soinesis.experiments.p3.outcome import ExperimentalTrialOutcome
from soinesis.experiments.p3.plan import ExperimentalReplicationPlan


class ExperimentalCycleStartContext(BaseModel):
    """Contexte public fourni uniquement lors du démarrage d'un cycle neuf."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    performance_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    trial_id: str = Field(min_length=1)
    cycle_id: str = Field(min_length=1)
    observed_at: datetime


class ExperimentalCycleRunResult(BaseModel):
    """Résultat scientifique stable d'un cycle expérimental terminé."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    checkpoint: ExperimentalCycleCheckpoint
    performance: CapabilityPerformanceObservation
    outcome: ExperimentalTrialOutcome

    @model_validator(mode="after")
    def validate_cycle_coherence(self) -> ExperimentalCycleRunResult:
        """Lier les trois artefacts sans exposer les statuts opérationnels intermédiaires."""
        checkpoint = self.checkpoint
        performance = self.performance
        outcome = self.outcome
        if checkpoint.status is not ExperimentalCycleCheckpointStatus.COMPLETED:
            raise ValueError("Le résultat d'un cycle exige un checkpoint COMPLETED.")
        checkpoint_context = (
            checkpoint.performance_id,
            checkpoint.agent_id,
            checkpoint.trial_id,
            checkpoint.cycle_id,
            checkpoint.sequence_index,
            checkpoint.capability_key,
            checkpoint.observed_at,
        )
        performance_context = (
            performance.id,
            performance.agent_id,
            performance.trial_id,
            performance.cycle_id,
            performance.sequence_index,
            performance.capability_key,
            performance.observed_at,
        )
        if checkpoint_context != performance_context:
            raise ValueError("La performance ne correspond pas au checkpoint terminé.")
        outcome_context = (
            outcome.performance_id,
            outcome.agent_id,
            outcome.trial_id,
            outcome.cycle_id,
            outcome.sequence_index,
            outcome.capability_key,
        )
        if outcome_context != performance_context[:-1]:
            raise ValueError("Le résultat corrigé ne correspond pas à la performance.")
        if (
            outcome.action is not checkpoint.decision.action
            or outcome.intrinsic_success is not performance.intrinsic_success
        ):
            raise ValueError("Le résultat corrigé n'utilise pas la décision et la preuve figées.")
        return self


class ExperimentalCycleRunnerError(RuntimeError):
    """Erreur de base de l'orchestrateur mono-cycle P3 DEV."""


class ExperimentalCycleStartContextRequiredError(ExperimentalCycleRunnerError):
    """Refuser un nouveau cycle sans contexte public de départ."""


class ExperimentalCycleRunnerIntegrityError(ExperimentalCycleRunnerError):
    """Refuser un plan ou un contexte incompatible avec le checkpoint canonique."""


class _CapabilityDecisionService(Protocol):
    def decide(self, *, boundary: CapabilityHistoryBoundary) -> CapabilityDecision: ...


class _CapabilityPerformanceRecordingService(Protocol):
    def record(self, *, observation: CapabilityPerformanceObservation) -> object: ...


class _PostPerformanceProcessor(Protocol):
    def process(self, *, performance_id: str) -> object: ...


class _ExperimentalCycleCheckpointService(Protocol):
    def get(
        self, *, execution_id: str, sequence_index: int
    ) -> ExperimentalCycleCheckpoint | None: ...

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
    ) -> ExperimentalCycleCheckpoint: ...

    def complete(
        self, *, execution_id: str, sequence_index: int
    ) -> ExperimentalCycleCheckpoint: ...


class ExperimentalCycleRunner:
    """Exécuter ou reprendre un cycle sans jamais recalculer sa décision figée."""

    def __init__(
        self,
        *,
        plan: ExperimentalReplicationPlan,
        checkpoint_service: _ExperimentalCycleCheckpointService,
        decision_service: _CapabilityDecisionService,
        recording_service: _CapabilityPerformanceRecordingService,
        post_performance_processor: _PostPerformanceProcessor | None = None,
    ) -> None:
        self._plan = plan
        self._checkpoint_service = checkpoint_service
        self._decision_service = decision_service
        self._recording_service = recording_service
        self._post_performance_processor = post_performance_processor

    def run(
        self,
        *,
        execution_id: str,
        sequence_index: int,
        start_context: ExperimentalCycleStartContext | None = None,
    ) -> ExperimentalCycleRunResult:
        """Exécuter un cycle neuf ou reprendre son checkpoint persistant."""
        checkpoint = self._checkpoint_service.get(
            execution_id=execution_id,
            sequence_index=sequence_index,
        )
        if checkpoint is None:
            checkpoint = self._begin_new_cycle(
                execution_id=execution_id,
                sequence_index=sequence_index,
                start_context=start_context,
            )
        else:
            self._validate_optional_start_context(
                checkpoint=checkpoint,
                start_context=start_context,
            )
            expected_capability_key = self._plan.capability_key_for_sequence(
                checkpoint.sequence_index
            )
            self._validate_checkpoint_capability(
                checkpoint=checkpoint,
                expected_capability_key=expected_capability_key,
            )

        performance = self._plan.attempt(
            performance_id=checkpoint.performance_id,
            agent_id=checkpoint.agent_id,
            trial_id=checkpoint.trial_id,
            cycle_id=checkpoint.cycle_id,
            sequence_index=checkpoint.sequence_index,
            observed_at=checkpoint.observed_at,
        )
        outcome = self._plan.resolve_outcome(
            decision=checkpoint.decision,
            performance=performance,
        )
        if checkpoint.status is ExperimentalCycleCheckpointStatus.COMPLETED:
            return ExperimentalCycleRunResult(
                checkpoint=checkpoint,
                performance=performance,
                outcome=outcome,
            )

        self._recording_service.record(observation=performance)
        if self._post_performance_processor is not None:
            self._post_performance_processor.process(performance_id=performance.id)
        completed_checkpoint = self._checkpoint_service.complete(
            execution_id=checkpoint.execution_id,
            sequence_index=checkpoint.sequence_index,
        )
        return ExperimentalCycleRunResult(
            checkpoint=completed_checkpoint,
            performance=performance,
            outcome=outcome,
        )

    def _begin_new_cycle(
        self,
        *,
        execution_id: str,
        sequence_index: int,
        start_context: ExperimentalCycleStartContext | None,
    ) -> ExperimentalCycleCheckpoint:
        if start_context is None:
            raise ExperimentalCycleStartContextRequiredError(
                "Un nouveau cycle exige son contexte public de départ."
            )
        capability_key = self._plan.capability_key_for_sequence(sequence_index)
        boundary = CapabilityHistoryBoundary(
            agent_id=start_context.agent_id,
            capability_key=capability_key,
            trial_id=start_context.trial_id,
            cycle_id=start_context.cycle_id,
            sequence_index=sequence_index,
        )
        decision = self._decision_service.decide(boundary=boundary)
        checkpoint = self._checkpoint_service.begin(
            execution_id=execution_id,
            sequence_index=sequence_index,
            performance_id=start_context.performance_id,
            agent_id=start_context.agent_id,
            trial_id=start_context.trial_id,
            cycle_id=start_context.cycle_id,
            capability_key=capability_key,
            observed_at=start_context.observed_at,
            decision=decision,
        )
        self._validate_checkpoint_capability(
            checkpoint=checkpoint,
            expected_capability_key=capability_key,
        )
        return checkpoint

    @staticmethod
    def _validate_optional_start_context(
        *,
        checkpoint: ExperimentalCycleCheckpoint,
        start_context: ExperimentalCycleStartContext | None,
    ) -> None:
        if start_context is None:
            return
        frozen_context = ExperimentalCycleStartContext(
            performance_id=checkpoint.performance_id,
            agent_id=checkpoint.agent_id,
            trial_id=checkpoint.trial_id,
            cycle_id=checkpoint.cycle_id,
            observed_at=checkpoint.observed_at,
        )
        if start_context != frozen_context:
            raise ExperimentalCycleRunnerIntegrityError(
                "Le contexte fourni diffère du contexte déjà figé."
            )

    @staticmethod
    def _validate_checkpoint_capability(
        *,
        checkpoint: ExperimentalCycleCheckpoint,
        expected_capability_key: str,
    ) -> None:
        if checkpoint.capability_key != expected_capability_key:
            raise ExperimentalCycleRunnerIntegrityError(
                "Le checkpoint ne correspond pas au plan expérimental injecté."
            )
