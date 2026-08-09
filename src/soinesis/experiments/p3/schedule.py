"""Calendrier temporel privé des capacités synthétiques P3 DEV."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import datetime

from soinesis.domain.capabilities import CapabilityPerformanceObservation
from soinesis.experiments.p3.capability import ExperimentalCapabilityModule

_TOTAL_CYCLES = 180
_SEGMENT_LENGTH = 60
_CAPABILITIES_PER_SEGMENT = 20
_CAPABILITY_KEYS = frozenset({"ALPHA", "BETA", "GAMMA"})
_PRIVATE_SEGMENT_PROBABILITIES = (
    {"ALPHA": 0.65, "BETA": 0.85, "GAMMA": 0.35},
    {"ALPHA": 0.65, "BETA": 0.40, "GAMMA": 0.75},
    {"ALPHA": 0.65, "BETA": 0.40, "GAMMA": 0.75},
)


class InvalidExperimentalCapabilityScheduleError(ValueError):
    """Signaler un ordre de capacités incompatible avec le calendrier DEV P3."""


class ExperimentalCapabilitySchedule:
    """Ordonner les capacités et sélectionner leur module privé pour un cycle."""

    def __init__(self, *, capability_order: Sequence[str]) -> None:
        copied_order = tuple(capability_order)
        _validate_capability_order(copied_order)
        self._capability_order = copied_order
        self._segment_modules = tuple(
            ExperimentalCapabilityModule(true_success_probabilities=probabilities)
            for probabilities in _PRIVATE_SEGMENT_PROBABILITIES
        )

    def capability_key_for_sequence(self, sequence_index: int) -> str:
        """Retourner uniquement la capacité publique du cycle demandé."""
        validated_index = _validate_sequence_index(sequence_index)
        return self._capability_order[validated_index]

    def attempt(
        self,
        *,
        performance_id: str,
        agent_id: str,
        trial_id: str,
        cycle_id: str,
        sequence_index: int,
        observed_at: datetime,
        u_intrinsic: float,
    ) -> CapabilityPerformanceObservation:
        """Produire la preuve publique du cycle sans accepter de capacité injectée."""
        validated_index = _validate_sequence_index(sequence_index)
        capability_key = self._capability_order[validated_index]
        module = self._segment_modules[validated_index // _SEGMENT_LENGTH]
        return module.attempt(
            performance_id=performance_id,
            agent_id=agent_id,
            trial_id=trial_id,
            cycle_id=cycle_id,
            sequence_index=validated_index,
            capability_key=capability_key,
            observed_at=observed_at,
            u_intrinsic=u_intrinsic,
        )


def _validate_capability_order(capability_order: tuple[str, ...]) -> None:
    if len(capability_order) != _TOTAL_CYCLES:
        raise InvalidExperimentalCapabilityScheduleError(
            f"Le calendrier DEV P3 doit contenir exactement {_TOTAL_CYCLES} cycles."
        )
    unknown_capabilities = set(capability_order) - _CAPABILITY_KEYS
    if unknown_capabilities:
        raise InvalidExperimentalCapabilityScheduleError(
            "Le calendrier DEV P3 contient une capability_key inconnue."
        )
    expected_counts = Counter(
        {capability_key: _CAPABILITIES_PER_SEGMENT for capability_key in _CAPABILITY_KEYS}
    )
    for segment_start in range(0, _TOTAL_CYCLES, _SEGMENT_LENGTH):
        segment = capability_order[segment_start : segment_start + _SEGMENT_LENGTH]
        if Counter(segment) != expected_counts:
            raise InvalidExperimentalCapabilityScheduleError(
                "Chaque segment DEV P3 doit contenir exactement 20 ALPHA, 20 BETA et 20 GAMMA."
            )


def _validate_sequence_index(sequence_index: object) -> int:
    if isinstance(sequence_index, bool) or not isinstance(sequence_index, int):
        raise TypeError("sequence_index doit être un entier strict.")
    if not 0 <= sequence_index < _TOTAL_CYCLES:
        raise IndexError("sequence_index doit être compris entre 0 inclus et 180 exclu.")
    return sequence_index
