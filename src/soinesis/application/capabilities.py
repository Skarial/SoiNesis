"""Règles pures d'estimation et de décision pour la tranche P3 DEV."""

from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityDecision,
    CapabilityEstimate,
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    EstimateSource,
    MetacognitiveCapabilityState,
    VersionedMetacognitiveCapabilityState,
)
from soinesis.domain.models import SourceType
from soinesis.ports.capabilities import CapabilityUnitOfWork, CapabilityUnitOfWorkFactory

DEV_PRIOR_ALPHA: Final = 3.0
DEV_PRIOR_BETA: Final = 2.0
FIXED_BASELINE_ESTIMATE: Final = 0.60
HELP_VERIFY_BOUNDARY: Final = 0.50
VERIFY_DIRECT_BOUNDARY: Final = 0.80
ALLOWED_SELF_PERFORMANCE_SOURCE: Final = SourceType.DIRECT_ENVIRONMENT


class MetacognitiveUpdateStatus(StrEnum):
    """Issues auditables du traitement d'une preuve intrinsèque persistée."""

    APPLIED = "APPLIED"
    ALREADY_PROCESSED = "ALREADY_PROCESSED"


class MetacognitiveCapabilityUpdateResult(BaseModel):
    """Résultat public minimal d'une tentative de mise à jour métacognitive."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    performance_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    capability_key: str = Field(min_length=1)
    status: MetacognitiveUpdateStatus
    previous_version: int = Field(ge=1, strict=True)
    resulting_version: int = Field(ge=1, strict=True)
    previous_estimated_success: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)
    resulting_estimated_success: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)


class CapabilityPerformanceNotFoundError(LookupError):
    """Signaler qu'aucune preuve persistée ne correspond à l'identifiant demandé."""


class CapabilityPerformanceProvenanceError(ValueError):
    """Refuser une provenance qui ne constitue pas une performance propre admise."""


class CapabilityPerformanceOrderError(ValueError):
    """Refuser une preuve ancienne ou un saut dans l'ordre causal d'une capacité."""


class MetacognitiveLambdaMismatchError(ValueError):
    """Refuser de poursuivre un état avec un facteur d'oubli différent."""


class MetacognitiveStateIntegrityError(ValueError):
    """Refuser un prior ou un curseur persistant incohérent avec les preuves."""


def is_admissible_self_performance(
    observation: CapabilityPerformanceObservation,
) -> bool:
    """Indiquer si une observation constitue une preuve de performance propre."""
    return observation.source_type is ALLOWED_SELF_PERFORMANCE_SOURCE


class CapabilityPerformanceProvenancePolicy:
    """Vérifier la provenance déclarée des preuves admises pour l'apprentissage.

    ``DIRECT_ENVIRONMENT`` est nécessaire dans cette tranche, mais cette étiquette
    ne constitue pas une preuve cryptographique du producteur. Le futur module de
    capacité expérimental devra être le producteur de confiance.
    """

    def validate(self, observation: CapabilityPerformanceObservation) -> None:
        """Refuser toute observation qui ne provient pas de la voie autorisée."""
        if not is_admissible_self_performance(observation):
            raise CapabilityPerformanceProvenanceError(
                "Seule une performance DIRECT_ENVIRONMENT peut alimenter la métacognition."
            )


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
            if observation.agent_id == agent_id
            and observation.capability_key == capability_key
            and is_admissible_self_performance(observation)
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


class MetacognitiveCapabilityUpdateService:
    """Incorporer exactement une fois une performance intrinsèque persistée."""

    def __init__(
        self,
        *,
        unit_of_work_factory: CapabilityUnitOfWorkFactory,
        estimator: DecayedBetaEstimator,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._estimator = estimator
        self._provenance_policy = CapabilityPerformanceProvenancePolicy()

    def process(self, *, performance_id: str) -> MetacognitiveCapabilityUpdateResult:
        """Traiter une preuve persistée sans saut, double incorporation ni futur."""
        with self._unit_of_work_factory() as unit_of_work:
            performance = unit_of_work.capability_performances.get(performance_id)
            if performance is None:
                raise CapabilityPerformanceNotFoundError(
                    f"La performance persistée {performance_id!r} n'existe pas."
                )
            self._provenance_policy.validate(performance)

            current = unit_of_work.metacognitive_states.get_current(
                agent_id=performance.agent_id,
                capability_key=performance.capability_key,
            )
            if current is None:
                current = VersionedMetacognitiveCapabilityState(
                    agent_id=performance.agent_id,
                    capability_key=performance.capability_key,
                    version=1,
                    state=self._estimator.initial_state(),
                )
                unit_of_work.metacognitive_states.replace_current(
                    state=current,
                    expected_version=None,
                )

            if current.state.lambda_ != self._estimator.lambda_:
                raise MetacognitiveLambdaMismatchError(
                    "Le facteur lambda du service diffère de celui de l'état persistant."
                )
            self._validate_persisted_state(unit_of_work=unit_of_work, current=current)

            if current.last_processed_performance_id == performance.id:
                if current.last_processed_sequence_index != performance.sequence_index:
                    raise CapabilityPerformanceOrderError(
                        "Le curseur persistant est incohérent avec la performance traitée."
                    )
                return self._already_processed_result(
                    performance=performance,
                    current=current,
                )

            last_sequence_index = current.last_processed_sequence_index
            if last_sequence_index is not None:
                if performance.sequence_index < last_sequence_index:
                    return self._already_processed_result(
                        performance=performance,
                        current=current,
                    )
                if performance.sequence_index == last_sequence_index:
                    raise CapabilityPerformanceOrderError(
                        "Deux performances distinctes partagent l'index du curseur."
                    )

            prior_history = unit_of_work.capability_performances.list_before(
                boundary=CapabilityHistoryBoundary(
                    agent_id=performance.agent_id,
                    capability_key=performance.capability_key,
                    trial_id=performance.trial_id,
                    cycle_id=performance.cycle_id,
                    sequence_index=performance.sequence_index,
                )
            )
            has_unprocessed_prior = any(
                is_admissible_self_performance(observation)
                and (
                    last_sequence_index is None or observation.sequence_index > last_sequence_index
                )
                for observation in prior_history
            )
            if has_unprocessed_prior:
                raise CapabilityPerformanceOrderError(
                    "Une performance antérieure de la même capacité reste à traiter."
                )

            next_statistical_state = self._estimator.update(
                current.state,
                performance.intrinsic_success,
            )
            resulting = VersionedMetacognitiveCapabilityState(
                agent_id=current.agent_id,
                capability_key=current.capability_key,
                version=current.version + 1,
                state=next_statistical_state,
                last_processed_performance_id=performance.id,
                last_processed_sequence_index=performance.sequence_index,
            )
            unit_of_work.metacognitive_states.replace_current(
                state=resulting,
                expected_version=current.version,
            )
            unit_of_work.commit()

        return MetacognitiveCapabilityUpdateResult(
            performance_id=performance.id,
            agent_id=performance.agent_id,
            capability_key=performance.capability_key,
            status=MetacognitiveUpdateStatus.APPLIED,
            previous_version=current.version,
            resulting_version=resulting.version,
            previous_estimated_success=current.state.estimated_success,
            resulting_estimated_success=resulting.state.estimated_success,
        )

    @staticmethod
    def _already_processed_result(
        *,
        performance: CapabilityPerformanceObservation,
        current: VersionedMetacognitiveCapabilityState,
    ) -> MetacognitiveCapabilityUpdateResult:
        estimated_success = current.state.estimated_success
        return MetacognitiveCapabilityUpdateResult(
            performance_id=performance.id,
            agent_id=performance.agent_id,
            capability_key=performance.capability_key,
            status=MetacognitiveUpdateStatus.ALREADY_PROCESSED,
            previous_version=current.version,
            resulting_version=current.version,
            previous_estimated_success=estimated_success,
            resulting_estimated_success=estimated_success,
        )

    def _validate_persisted_state(
        self,
        *,
        unit_of_work: CapabilityUnitOfWork,
        current: VersionedMetacognitiveCapabilityState,
    ) -> None:
        if current.version == 1:
            if current.state != self._estimator.initial_state():
                raise MetacognitiveStateIntegrityError(
                    "La version métacognitive 1 ne correspond pas au prior DEV attendu."
                )
            return

        cursor_id = current.last_processed_performance_id
        cursor_sequence_index = current.last_processed_sequence_index
        if cursor_id is None or cursor_sequence_index is None:
            raise MetacognitiveStateIntegrityError(
                "L'état métacognitif persistant ne possède pas de curseur complet."
            )
        cursor_performance = unit_of_work.capability_performances.get(cursor_id)
        if (
            cursor_performance is None
            or cursor_performance.agent_id != current.agent_id
            or cursor_performance.capability_key != current.capability_key
            or cursor_performance.sequence_index != cursor_sequence_index
            or not is_admissible_self_performance(cursor_performance)
        ):
            raise MetacognitiveStateIntegrityError(
                "Le curseur métacognitif ne correspond pas à une preuve propre persistée."
            )
