"""Résolution pure et privée du résultat final d'un essai P3 DEV."""

from collections.abc import Mapping
from types import MappingProxyType

from pydantic import ConfigDict, Field

from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityDecision,
    CapabilityPerformanceObservation,
)
from soinesis.domain.models import DomainModel
from soinesis.experiments.p3._validation import validate_correction_latent

_ACTION_COSTS: Mapping[CapabilityAction, int] = MappingProxyType(
    {
        CapabilityAction.DIRECT: 0,
        CapabilityAction.VERIFY: 2,
        CapabilityAction.HELP: 6,
    }
)
_CORRECTION_THRESHOLDS: Mapping[CapabilityAction, float] = MappingProxyType(
    {
        CapabilityAction.VERIFY: 0.50,
        CapabilityAction.HELP: 0.90,
    }
)
_SUCCESS_REWARD = 10
_FAILURE_REWARD = -10


class ExperimentalTrialContextMismatchError(ValueError):
    """Refuser une décision qui ne concerne pas la performance fournie."""


class ExperimentalTrialOutcome(DomainModel):
    """Trace expérimentale privée séparant succès intrinsèque et succès final."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    performance_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    trial_id: str = Field(min_length=1)
    cycle_id: str = Field(min_length=1)
    sequence_index: int = Field(ge=0)
    capability_key: str = Field(min_length=1)
    action: CapabilityAction
    intrinsic_success: bool
    u_correction: float = Field(ge=0.0, lt=1.0, allow_inf_nan=False)
    correction_applied: bool
    final_success: bool
    action_cost: int = Field(ge=0)
    outcome_reward: int
    realized_reward: int


class ExperimentalTrialOutcomeResolver:
    """Appliquer une action déjà décidée sans RNG, persistance ou état interne."""

    def resolve(
        self,
        *,
        decision: CapabilityDecision,
        performance: CapabilityPerformanceObservation,
        u_correction: float,
    ) -> ExperimentalTrialOutcome:
        """Calculer le résultat final sans altérer la preuve intrinsèque."""
        validated_latent = validate_correction_latent(u_correction)
        _validate_trial_context(decision=decision, performance=performance)

        action = decision.action
        if performance.intrinsic_success:
            correction_applied = False
            final_success = True
        elif action is CapabilityAction.DIRECT:
            correction_applied = False
            final_success = False
        else:
            correction_applied = validated_latent < _CORRECTION_THRESHOLDS[action]
            final_success = correction_applied

        action_cost = _ACTION_COSTS[action]
        outcome_reward = _SUCCESS_REWARD if final_success else _FAILURE_REWARD
        return ExperimentalTrialOutcome(
            performance_id=performance.id,
            agent_id=performance.agent_id,
            trial_id=performance.trial_id,
            cycle_id=performance.cycle_id,
            sequence_index=performance.sequence_index,
            capability_key=performance.capability_key,
            action=action,
            intrinsic_success=performance.intrinsic_success,
            u_correction=validated_latent,
            correction_applied=correction_applied,
            final_success=final_success,
            action_cost=action_cost,
            outcome_reward=outcome_reward,
            realized_reward=outcome_reward - action_cost,
        )


def _validate_trial_context(
    *,
    decision: CapabilityDecision,
    performance: CapabilityPerformanceObservation,
) -> None:
    if decision.estimate.agent_id != performance.agent_id:
        raise ExperimentalTrialContextMismatchError(
            "La décision et la performance doivent concerner le même agent."
        )
    if decision.estimate.capability_key != performance.capability_key:
        raise ExperimentalTrialContextMismatchError(
            "La décision et la performance doivent concerner la même capability_key."
        )
