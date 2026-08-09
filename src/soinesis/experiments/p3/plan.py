"""Plan privé et immuable d'une réplication expérimentale P3 DEV."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from soinesis.domain.capabilities import (
    CapabilityDecision,
    CapabilityPerformanceObservation,
)
from soinesis.experiments.p3._validation import (
    validate_correction_latent,
    validate_intrinsic_latent,
)
from soinesis.experiments.p3.outcome import (
    ExperimentalTrialOutcome,
    ExperimentalTrialOutcomeResolver,
)
from soinesis.experiments.p3.schedule import ExperimentalCapabilitySchedule

_TOTAL_CYCLES = 180


class InvalidExperimentalReplicationPlanError(ValueError):
    """Signaler un plan de réplication incompatible avec le protocole DEV P3."""


class ExperimentalPlanPerformanceMismatchError(ValueError):
    """Refuser une performance qui ne provient pas du cycle correspondant du plan."""


class ExperimentalReplicationPlan:
    """Associer un calendrier et deux latents privés communs à chaque cycle."""

    def __init__(
        self,
        *,
        capability_order: Sequence[str],
        u_intrinsic_by_sequence: Sequence[float],
        u_correction_by_sequence: Sequence[float],
    ) -> None:
        copied_intrinsic_latents = tuple(u_intrinsic_by_sequence)
        copied_correction_latents = tuple(u_correction_by_sequence)
        if len(copied_intrinsic_latents) != _TOTAL_CYCLES:
            raise InvalidExperimentalReplicationPlanError(
                f"Le plan DEV P3 doit contenir exactement {_TOTAL_CYCLES} latents intrinsèques."
            )
        if len(copied_correction_latents) != _TOTAL_CYCLES:
            raise InvalidExperimentalReplicationPlanError(
                f"Le plan DEV P3 doit contenir exactement {_TOTAL_CYCLES} latents de correction."
            )
        self._schedule = ExperimentalCapabilitySchedule(capability_order=capability_order)
        self._u_intrinsic_by_sequence = tuple(
            validate_intrinsic_latent(latent) for latent in copied_intrinsic_latents
        )
        self._u_correction_by_sequence = tuple(
            validate_correction_latent(latent) for latent in copied_correction_latents
        )

    def capability_key_for_sequence(self, sequence_index: int) -> str:
        """Déléguer l'exposition de la seule capacité courante au calendrier privé."""
        return self._schedule.capability_key_for_sequence(sequence_index)

    def attempt(
        self,
        *,
        performance_id: str,
        agent_id: str,
        trial_id: str,
        cycle_id: str,
        sequence_index: int,
        observed_at: datetime,
    ) -> CapabilityPerformanceObservation:
        """Appliquer le latent privé indexé et ne retourner que la preuve publique."""
        self._schedule.capability_key_for_sequence(sequence_index)
        u_intrinsic = self._u_intrinsic_by_sequence[sequence_index]
        return self._schedule.attempt(
            performance_id=performance_id,
            agent_id=agent_id,
            trial_id=trial_id,
            cycle_id=cycle_id,
            sequence_index=sequence_index,
            observed_at=observed_at,
            u_intrinsic=u_intrinsic,
        )

    def resolve_outcome(
        self,
        *,
        decision: CapabilityDecision,
        performance: CapabilityPerformanceObservation,
    ) -> ExperimentalTrialOutcome:
        """Résoudre le résultat avec le latent privé du cycle de la performance."""
        sequence_index = performance.sequence_index
        self._schedule.capability_key_for_sequence(sequence_index)
        expected_performance = self.attempt(
            performance_id=performance.id,
            agent_id=performance.agent_id,
            trial_id=performance.trial_id,
            cycle_id=performance.cycle_id,
            sequence_index=sequence_index,
            observed_at=performance.observed_at,
        )
        if expected_performance != performance:
            raise ExperimentalPlanPerformanceMismatchError(
                "La performance fournie est incompatible avec le cycle du plan expérimental."
            )
        u_correction = self._u_correction_by_sequence[sequence_index]
        return ExperimentalTrialOutcomeResolver().resolve(
            decision=decision,
            performance=performance,
            u_correction=u_correction,
        )
