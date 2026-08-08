"""Règles pures d'estimation et de décision pour la tranche P3 DEV."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Final

from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityDecision,
    CapabilityEstimate,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    EstimateSource,
    MetacognitiveCapabilityState,
)

DEV_PRIOR_ALPHA: Final = 3.0
DEV_PRIOR_BETA: Final = 2.0
FIXED_BASELINE_ESTIMATE: Final = 0.60
HELP_VERIFY_BOUNDARY: Final = 0.50
VERIFY_DIRECT_BOUNDARY: Final = 0.80


class DecayedBetaEstimator:
    """Estimateur Beta à oubli dont le facteur est fourni explicitement."""

    def __init__(self, *, lambda_: float) -> None:
        validated_state = MetacognitiveCapabilityState(
            alpha=DEV_PRIOR_ALPHA,
            beta=DEV_PRIOR_BETA,
            lambda_=lambda_,
        )
        self._lambda = validated_state.lambda_

    @property
    def lambda_(self) -> float:
        """Retourner le facteur d'oubli configuré pour cet estimateur."""
        return self._lambda

    def initial_state(self) -> MetacognitiveCapabilityState:
        """Créer un état neuf au prior de travail DEV."""
        return MetacognitiveCapabilityState(
            alpha=DEV_PRIOR_ALPHA,
            beta=DEV_PRIOR_BETA,
            lambda_=self._lambda,
        )

    def update(
        self,
        previous_state: MetacognitiveCapabilityState,
        intrinsic_success: bool,
    ) -> MetacognitiveCapabilityState:
        """Appliquer une preuve intrinsèque à un état statistique."""
        if previous_state.lambda_ != self._lambda:
            raise ValueError("L'état précédent utilise un facteur lambda différent.")

        outcome = 1.0 if intrinsic_success else 0.0
        return MetacognitiveCapabilityState(
            alpha=(
                DEV_PRIOR_ALPHA + self._lambda * (previous_state.alpha - DEV_PRIOR_ALPHA) + outcome
            ),
            beta=(
                DEV_PRIOR_BETA
                + self._lambda * (previous_state.beta - DEV_PRIOR_BETA)
                + (1.0 - outcome)
            ),
            lambda_=self._lambda,
        )

    def replay(self, history: Iterable[bool]) -> MetacognitiveCapabilityState:
        """Reconstruire un état neuf en repliant exactement ``update``."""
        state = self.initial_state()
        for intrinsic_success in history:
            state = self.update(state, intrinsic_success)
        return state


class CapabilityDecisionPolicy:
    """Politique commune calculant les utilités et l'action déclarées par P3."""

    def decide(self, estimate: CapabilityEstimate) -> CapabilityDecision:
        """Choisir une action avec les règles de départage exactes du protocole."""
        estimated_success = estimate.estimated_success
        direct_utility = 20.0 * estimated_success - 10.0
        verify_utility = 10.0 * estimated_success - 2.0
        help_utility = 2.0 * estimated_success + 2.0

        if estimated_success < HELP_VERIFY_BOUNDARY:
            action = CapabilityAction.HELP
        elif estimated_success < VERIFY_DIRECT_BOUNDARY:
            action = CapabilityAction.VERIFY
        else:
            action = CapabilityAction.DIRECT

        return CapabilityDecision(
            estimate=estimate,
            action=action,
            direct_utility=direct_utility,
            verify_utility=verify_utility,
            help_utility=help_utility,
        )


class FixedCapabilityEstimateProvider:
    """Provider sans état de la baseline fixe A."""

    def estimate(self, *, agent_id: str, capability_key: str) -> CapabilityEstimate:
        """Retourner l'estimation fixe indépendamment des performances."""
        return CapabilityEstimate(
            agent_id=agent_id,
            capability_key=capability_key,
            estimated_success=FIXED_BASELINE_ESTIMATE,
            source=EstimateSource.FIXED_BASELINE,
        )


class RawHistoryCapabilityEstimateProvider:
    """Provider générique de reconstruction brute pour B et la future SELF-ABL."""

    def __init__(self, *, estimator: DecayedBetaEstimator) -> None:
        self._estimator = estimator

    def estimate(
        self,
        *,
        agent_id: str,
        capability_key: str,
        history: Iterable[CapabilityPerformanceObservation],
    ) -> CapabilityEstimate:
        """Rejouer l'historique pertinent sans conserver l'état reconstruit."""
        relevant_history = tuple(
            observation
            for observation in history
            if observation.agent_id == agent_id and observation.capability_key == capability_key
        )
        state = self._estimator.replay(
            observation.intrinsic_success for observation in relevant_history
        )
        return CapabilityEstimate(
            agent_id=agent_id,
            capability_key=capability_key,
            estimated_success=state.estimated_success,
            source=EstimateSource.RAW_HISTORY,
        )


class SelfAttributeCapabilityEstimateProvider:
    """Provider sans dépendance donnant à C son seul accès décisionnel autorisé."""

    def estimate(self, *, attribute: CapabilitySelfAttribute) -> CapabilityEstimate:
        """Copier l'estimation consolidée sans consulter le brut ni l'état méta."""
        return CapabilityEstimate(
            agent_id=attribute.agent_id,
            capability_key=attribute.capability_key,
            estimated_success=attribute.estimated_success,
            source=EstimateSource.SELF_ATTRIBUTE,
        )
