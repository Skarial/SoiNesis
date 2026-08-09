"""Capacité synthétique P3 isolant la vérité expérimentale du système cognitif."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from types import MappingProxyType

from soinesis.domain.capabilities import CapabilityPerformanceObservation
from soinesis.domain.models import SourceType
from soinesis.experiments.p3._validation import (
    validate_intrinsic_latent,
    validate_true_success_probability,
)


class UnknownExperimentalCapabilityError(LookupError):
    """Refuser une capacité absente de la configuration expérimentale privée."""


class ExperimentalCapabilityModule:
    """Simuler une capacité autonome statique sans exposer sa fiabilité réelle."""

    def __init__(
        self,
        *,
        true_success_probabilities: Mapping[str, float],
    ) -> None:
        validated_probabilities: dict[str, float] = {}
        for capability_key, probability in true_success_probabilities.items():
            if not capability_key:
                raise ValueError("Une capability_key expérimentale ne peut pas être vide.")
            validated_probabilities[capability_key] = validate_true_success_probability(probability)
        self._true_success_probabilities: Mapping[str, float] = MappingProxyType(
            validated_probabilities
        )

    def attempt(
        self,
        *,
        performance_id: str,
        agent_id: str,
        trial_id: str,
        cycle_id: str,
        sequence_index: int,
        capability_key: str,
        observed_at: datetime,
        u_intrinsic: float,
    ) -> CapabilityPerformanceObservation:
        """Produire uniquement la preuve publique issue du latent expérimental fourni."""
        try:
            true_success_probability = self._true_success_probabilities[capability_key]
        except KeyError as error:
            raise UnknownExperimentalCapabilityError(
                f"La capacité expérimentale {capability_key!r} n'est pas configurée."
            ) from error
        validated_latent = validate_intrinsic_latent(u_intrinsic)
        return CapabilityPerformanceObservation(
            id=performance_id,
            agent_id=agent_id,
            trial_id=trial_id,
            cycle_id=cycle_id,
            sequence_index=sequence_index,
            capability_key=capability_key,
            intrinsic_success=validated_latent < true_success_probability,
            observed_at=observed_at,
            source_type=SourceType.DIRECT_ENVIRONMENT,
        )
