"""Validations numériques partagées et privées du banc expérimental P3."""

from math import isfinite


def validate_true_success_probability(value: float) -> float:
    """Valider une probabilité privée fermée sur zéro et un."""
    validated_value = as_strict_finite_float(
        value,
        parameter_name="true_success_probability",
    )
    if not 0.0 <= validated_value <= 1.0:
        raise ValueError("true_success_probability doit être comprise entre 0 et 1.")
    return validated_value


def validate_intrinsic_latent(value: float) -> float:
    """Valider un latent privé dans l'intervalle semi-ouvert [0, 1)."""
    validated_value = as_strict_finite_float(value, parameter_name="u_intrinsic")
    if not 0.0 <= validated_value < 1.0:
        raise ValueError("u_intrinsic doit être compris entre 0 inclus et 1 exclu.")
    return validated_value


def as_strict_finite_float(value: float, *, parameter_name: str) -> float:
    """Refuser les booléens, NaN et infinis."""
    if isinstance(value, bool):
        raise TypeError(f"{parameter_name} doit être un nombre réel.")
    validated_value = float(value)
    if not isfinite(validated_value):
        raise ValueError(f"{parameter_name} doit être fini.")
    return validated_value
