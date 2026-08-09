"""Plan privé et immuable d'une réplication expérimentale P3 DEV."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from soinesis.domain.capabilities import CapabilityPerformanceObservation
from soinesis.experiments.p3._validation import validate_intrinsic_latent
from soinesis.experiments.p3.schedule import ExperimentalCapabilitySchedule

_TOTAL_CYCLES = 180


class InvalidExperimentalReplicationPlanError(ValueError):
    """Signaler un plan de réplication incompatible avec le protocole DEV P3."""


class ExperimentalReplicationPlan:
    """Associer en privé un calendrier équilibré et un latent intrinsèque par cycle."""

    def __init__(
        self,
        *,
        capability_order: Sequence[str],
        u_intrinsic_by_sequence: Sequence[float],
    ) -> None:
        copied_latents = tuple(u_intrinsic_by_sequence)
        if len(copied_latents) != _TOTAL_CYCLES:
            raise InvalidExperimentalReplicationPlanError(
                f"Le plan DEV P3 doit contenir exactement {_TOTAL_CYCLES} latents intrinsèques."
            )
        self._schedule = ExperimentalCapabilitySchedule(capability_order=capability_order)
        self._u_intrinsic_by_sequence = tuple(
            validate_intrinsic_latent(latent) for latent in copied_latents
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
