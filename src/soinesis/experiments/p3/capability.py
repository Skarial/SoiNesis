"""Capacité synthétique P3 isolant la vérité expérimentale du système cognitif."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from math import isfinite
from types import MappingProxyType

from soinesis.domain.capabilities import CapabilityPerformanceObservation
from soinesis.domain.models import SourceType


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
            validated_probabilities[capability_key] = _validate_true_success_probability(
                probability
            )
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
        validated_latent = _validate_intrinsic_latent(u_intrinsic)
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


def _validate_true_success_probability(value: float) -> float:
    """Valider une probabilité privée fermée sur zéro et un."""
    validated_value = _as_strict_finite_float(value, parameter_name="true_success_probability")
    if not 0.0 <= validated_value <= 1.0:
        raise ValueError("true_success_probability doit être comprise entre 0 et 1.")
    return validated_value


def _validate_intrinsic_latent(value: float) -> float:
    """Valider un latent privé dans l'intervalle semi-ouvert [0, 1)."""
    validated_value = _as_strict_finite_float(value, parameter_name="u_intrinsic")
    if not 0.0 <= validated_value < 1.0:
        raise ValueError("u_intrinsic doit être compris entre 0 inclus et 1 exclu.")
    return validated_value


def _as_strict_finite_float(value: float, *, parameter_name: str) -> float:
    """Refuser les booléens, NaN et infinis."""
    if isinstance(value, bool):
        raise TypeError(f"{parameter_name} doit être un nombre réel.")
    validated_value = float(value)
    if not isfinite(validated_value):
        raise ValueError(f"{parameter_name} doit être fini.")
    return validated_value
