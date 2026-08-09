"""Règles pures d'estimation et de décision pour la tranche P3 DEV."""

from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from math import isfinite
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
    SelfModelVersion,
    VersionedMetacognitiveCapabilityState,
)
from soinesis.domain.models import EventType, JournalEvent, SourceType
from soinesis.ports.capabilities import CapabilityUnitOfWork, CapabilityUnitOfWorkFactory
from soinesis.ports.system import Clock, IdentifierGenerator

DEV_PRIOR_ALPHA: Final = 3.0
DEV_PRIOR_BETA: Final = 2.0
DEV_PRIOR_ESTIMATED_SUCCESS: Final = DEV_PRIOR_ALPHA / (DEV_PRIOR_ALPHA + DEV_PRIOR_BETA)
FIXED_BASELINE_ESTIMATE: Final = 0.60
HELP_VERIFY_BOUNDARY: Final = 0.50
VERIFY_DIRECT_BOUNDARY: Final = 0.80
ALLOWED_SELF_PERFORMANCE_SOURCE: Final = SourceType.DIRECT_ENVIRONMENT
CAPABILITY_SELF_ATTRIBUTE_TARGET_TYPE: Final = "CapabilitySelfAttribute"
CAPABILITY_SELF_MODEL_INITIALIZATION_CYCLE_ID: Final = "system-capability-self-model-initialization"
CAPABILITY_SELF_MODEL_INITIALIZATION_REASON: Final = "INITIALIZATION"
CAPABILITY_SELF_MODEL_REVISION_REASON: Final = "ACTION_BAND_CROSSING"


class MetacognitiveUpdateStatus(StrEnum):
    """Issues auditables du traitement d'une preuve intrinsèque persistée."""

    APPLIED = "APPLIED"
    ALREADY_PROCESSED = "ALREADY_PROCESSED"


class CapabilityPerformanceRecordingStatus(StrEnum):
    """Issues auditables de la persistance canonique d'une preuve intrinsèque."""

    RECORDED = "RECORDED"
    ALREADY_RECORDED = "ALREADY_RECORDED"


class CapabilitySelfModelInitializationStatus(StrEnum):
    """Issues publiques de l'initialisation d'une capacité dans le SelfModel."""

    INITIALIZED = "INITIALIZED"
    ALREADY_INITIALIZED = "ALREADY_INITIALIZED"


class CapabilitySelfModelRevisionStatus(StrEnum):
    """Issues publiques d'une tentative de consolidation métacognitive."""

    REVISED = "REVISED"
    NO_REVISION = "NO_REVISION"


class CapabilityPostPerformanceRevisionStatus(StrEnum):
    """Issue de révision propre à la façade post-performance."""

    REVISED = "REVISED"
    NO_REVISION = "NO_REVISION"
    SKIPPED_OLD_DUPLICATE = "SKIPPED_OLD_DUPLICATE"


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


class CapabilityPerformanceRecordingResult(BaseModel):
    """Résultat public minimal de l'enregistrement durable d'une performance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    performance_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    capability_key: str = Field(min_length=1)
    sequence_index: int = Field(ge=0, strict=True)
    status: CapabilityPerformanceRecordingStatus


class SignificantSelfRevisionAssessment(BaseModel):
    """Comparaison pure des bandes décisionnelles avant et après consolidation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    previous_action: CapabilityAction
    resulting_action: CapabilityAction

    @property
    def is_significant(self) -> bool:
        """Une révision est significative exactement lors d'un changement de bande."""
        return self.previous_action is not self.resulting_action


class CapabilitySelfModelInitializationResult(BaseModel):
    """Résultat minimal et auditable du bootstrap d'une capacité."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str = Field(min_length=1)
    capability_key: str = Field(min_length=1)
    status: CapabilitySelfModelInitializationStatus
    estimated_success: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)
    action: CapabilityAction
    self_model_version: int = Field(ge=1, strict=True)
    attribute_version: int = Field(ge=1, strict=True)


class CapabilitySelfModelRevisionResult(BaseModel):
    """Résultat minimal d'une tentative de révision significative."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str = Field(min_length=1)
    capability_key: str = Field(min_length=1)
    status: CapabilitySelfModelRevisionStatus
    previous_estimated_success: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)
    resulting_estimated_success: float = Field(ge=0.0, le=1.0, allow_inf_nan=False)
    previous_action: CapabilityAction
    resulting_action: CapabilityAction
    previous_self_model_version: int = Field(ge=1, strict=True)
    resulting_self_model_version: int = Field(ge=1, strict=True)
    previous_attribute_version: int = Field(ge=1, strict=True)
    resulting_attribute_version: int = Field(ge=1, strict=True)
    triggering_performance_id: str | None = Field(default=None, min_length=1)


class CapabilityPostPerformanceProcessingResult(BaseModel):
    """Résultat auditable du traitement post-performance complet de C."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    performance_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    capability_key: str = Field(min_length=1)
    metacognitive_status: MetacognitiveUpdateStatus
    self_model_revision_status: CapabilityPostPerformanceRevisionStatus
    metacognitive_version_before: int = Field(ge=1, strict=True)
    metacognitive_version_after: int = Field(ge=1, strict=True)
    self_model_version_before: int = Field(ge=1, strict=True)
    self_model_version_after: int = Field(ge=1, strict=True)
    attribute_version_before: int = Field(ge=1, strict=True)
    attribute_version_after: int = Field(ge=1, strict=True)
    resulting_action: CapabilityAction


class CapabilityPerformanceNotFoundError(LookupError):
    """Signaler qu'aucune preuve persistée ne correspond à l'identifiant demandé."""


class CapabilityPerformanceProvenanceError(ValueError):
    """Refuser une provenance qui ne constitue pas une performance propre admise."""


class CapabilityPerformanceOrderError(ValueError):
    """Refuser une preuve ancienne ou un saut dans l'ordre causal d'une capacité."""


class CapabilityPerformanceRecordingIntegrityError(ValueError):
    """Refuser la réutilisation d'un identifiant pour une performance différente."""


class MetacognitiveLambdaMismatchError(ValueError):
    """Refuser de poursuivre un état avec un facteur d'oubli différent."""


class MetacognitiveStateIntegrityError(ValueError):
    """Refuser un prior ou un curseur persistant incohérent avec les preuves."""


class CapabilitySelfModelInitializationError(ValueError):
    """Refuser un bootstrap tardif ou incompatible avec l'état déjà persistant."""


class CapabilitySelfModelIntegrityError(ValueError):
    """Refuser une chaîne SelfModel, SelfAttribute ou métacognitive incohérente."""


class CapabilitySelfModelNotInitializedError(CapabilitySelfModelIntegrityError):
    """Refuser un chemin qui exige une représentation de capacité initialisée."""


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


class CapabilityPerformanceRecordingService:
    """Enregistrer durablement une preuve intrinsèque par une voie idempotente unique."""

    def __init__(self, *, unit_of_work_factory: CapabilityUnitOfWorkFactory) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._provenance_policy = CapabilityPerformanceProvenancePolicy()

    def record(
        self,
        *,
        observation: CapabilityPerformanceObservation,
    ) -> CapabilityPerformanceRecordingResult:
        """Ajouter une preuve neuve ou reconnaître un retry strictement identique."""
        with self._unit_of_work_factory() as unit_of_work:
            try:
                self._provenance_policy.validate(observation)
            except CapabilityPerformanceProvenanceError as provenance_error:
                existing = unit_of_work.capability_performances.get(observation.id)
                if existing is not None and existing != observation:
                    raise CapabilityPerformanceRecordingIntegrityError(
                        "Le performance_id existe déjà avec un contenu différent."
                    ) from provenance_error
                raise
            existing = unit_of_work.capability_performances.get(observation.id)
            if existing is not None:
                if existing != observation:
                    raise CapabilityPerformanceRecordingIntegrityError(
                        "Le performance_id existe déjà avec un contenu différent."
                    )
                return _capability_performance_recording_result(
                    observation=observation,
                    status=CapabilityPerformanceRecordingStatus.ALREADY_RECORDED,
                )

            unit_of_work.capability_performances.add(observation)
            unit_of_work.commit()
            return _capability_performance_recording_result(
                observation=observation,
                status=CapabilityPerformanceRecordingStatus.RECORDED,
            )


def _capability_performance_recording_result(
    *,
    observation: CapabilityPerformanceObservation,
    status: CapabilityPerformanceRecordingStatus,
) -> CapabilityPerformanceRecordingResult:
    return CapabilityPerformanceRecordingResult(
        performance_id=observation.id,
        agent_id=observation.agent_id,
        capability_key=observation.capability_key,
        sequence_index=observation.sequence_index,
        status=status,
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

    def action_for_estimated_success(self, estimated_success: float) -> CapabilityAction:
        """Classer une estimation dans l'unique définition des bandes P3."""
        if not isfinite(estimated_success) or not 0.0 <= estimated_success <= 1.0:
            raise ValueError("L'estimation de succès doit être finie et comprise entre 0 et 1.")
        if estimated_success < HELP_VERIFY_BOUNDARY:
            return CapabilityAction.HELP
        if estimated_success < VERIFY_DIRECT_BOUNDARY:
            return CapabilityAction.VERIFY
        return CapabilityAction.DIRECT

    def decide(self, estimate: CapabilityEstimate) -> CapabilityDecision:
        """Choisir une action avec les règles de départage exactes du protocole."""
        estimated_success = estimate.estimated_success
        direct_utility = 20.0 * estimated_success - 10.0
        verify_utility = 10.0 * estimated_success - 2.0
        help_utility = 2.0 * estimated_success + 2.0
        action = self.action_for_estimated_success(estimated_success)

        return CapabilityDecision(
            estimate=estimate,
            action=action,
            direct_utility=direct_utility,
            verify_utility=verify_utility,
            help_utility=help_utility,
        )


class SignificantSelfRevisionPolicy:
    """Politique DEV pure : réviser uniquement lors d'un changement de bande."""

    def __init__(self, *, decision_policy: CapabilityDecisionPolicy) -> None:
        self._decision_policy = decision_policy

    def assess(
        self,
        *,
        previous_estimated_success: float,
        candidate_estimated_success: float,
    ) -> SignificantSelfRevisionAssessment:
        """Comparer les actions sans introduire de seuil de delta parallèle."""
        return SignificantSelfRevisionAssessment(
            previous_action=self._decision_policy.action_for_estimated_success(
                previous_estimated_success
            ),
            resulting_action=self._decision_policy.action_for_estimated_success(
                candidate_estimated_success
            ),
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


class FixedCapabilityDecisionService:
    """Décider pour A depuis la seule estimation fixe, sans ouvrir de UoW."""

    def __init__(
        self,
        *,
        estimate_provider: FixedCapabilityEstimateProvider,
        decision_policy: CapabilityDecisionPolicy,
    ) -> None:
        self._estimate_provider = estimate_provider
        self._decision_policy = decision_policy

    def decide(self, *, boundary: CapabilityHistoryBoundary) -> CapabilityDecision:
        """Produire la décision fixe depuis le contexte public courant."""
        estimate = self._estimate_provider.estimate(
            agent_id=boundary.agent_id,
            capability_key=boundary.capability_key,
        )
        return self._decision_policy.decide(estimate)


class RawHistoryCapabilityDecisionService:
    """Chemin décisionnel brut unique destiné à B et à la future SELF-ABL."""

    def __init__(
        self,
        *,
        unit_of_work_factory: CapabilityUnitOfWorkFactory,
        estimate_provider: RawHistoryCapabilityEstimateProvider,
        decision_policy: CapabilityDecisionPolicy,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._estimate_provider = estimate_provider
        self._decision_policy = decision_policy

    def decide(self, *, boundary: CapabilityHistoryBoundary) -> CapabilityDecision:
        """Reconstruire uniquement depuis les performances strictement antérieures."""
        with self._unit_of_work_factory() as unit_of_work:
            history = unit_of_work.capability_performances.list_before(boundary=boundary)
        estimate = self._estimate_provider.estimate(
            agent_id=boundary.agent_id,
            capability_key=boundary.capability_key,
            history=history,
        )
        return self._decision_policy.decide(estimate)


class SelfAttributeCapabilityDecisionService:
    """Décider pour C depuis le seul CapabilitySelfAttribute courant."""

    def __init__(
        self,
        *,
        unit_of_work_factory: CapabilityUnitOfWorkFactory,
        estimate_provider: SelfAttributeCapabilityEstimateProvider,
        decision_policy: CapabilityDecisionPolicy,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._estimate_provider = estimate_provider
        self._decision_policy = decision_policy

    def decide(self, *, boundary: CapabilityHistoryBoundary) -> CapabilityDecision:
        """Lire l'attribut consolidé ou refuser une capacité non initialisée."""
        with self._unit_of_work_factory() as unit_of_work:
            attribute = unit_of_work.capability_self_attributes.get_current(
                agent_id=boundary.agent_id,
                capability_key=boundary.capability_key,
            )
        if attribute is None:
            raise CapabilitySelfModelNotInitializedError(
                "La capacité doit être initialisée avant toute décision depuis le SelfModel."
            )
        if (
            attribute.agent_id != boundary.agent_id
            or attribute.capability_key != boundary.capability_key
        ):
            raise CapabilitySelfModelIntegrityError(
                "Le CapabilitySelfAttribute courant appartient à un autre périmètre."
            )
        estimate = self._estimate_provider.estimate(attribute=attribute)
        return self._decision_policy.decide(estimate)


def _validate_metacognitive_state(
    *,
    unit_of_work: CapabilityUnitOfWork,
    current: VersionedMetacognitiveCapabilityState,
    estimator: DecayedBetaEstimator,
) -> CapabilityPerformanceObservation | None:
    """Valider le prior ou relire la preuve exacte désignée par le curseur."""
    if current.state.lambda_ != estimator.lambda_:
        raise MetacognitiveLambdaMismatchError(
            "Le facteur lambda du service diffère de celui de l'état persistant."
        )
    if current.version == 1:
        if current.state != estimator.initial_state():
            raise MetacognitiveStateIntegrityError(
                "La version métacognitive 1 ne correspond pas au prior DEV attendu."
            )
        return None

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
    return cursor_performance


def _validate_self_model_history(
    *,
    agent_id: str,
    current: SelfModelVersion | None,
    versions: list[SelfModelVersion],
) -> None:
    """Vérifier la chaîne globale append-only relue depuis la persistance."""
    if current is None:
        if versions:
            raise CapabilitySelfModelIntegrityError(
                "L'historique SelfModel existe sans version globale courante."
            )
        return
    if not versions or versions[-1] != current:
        raise CapabilitySelfModelIntegrityError(
            "La version SelfModel courante ne correspond pas à la fin de l'historique."
        )

    previous_id: str | None = None
    seen_ids: set[str] = set()
    for expected_version, version in enumerate(versions, start=1):
        if (
            version.agent_id != agent_id
            or version.version != expected_version
            or version.previous_version_id != previous_id
            or version.id in seen_ids
        ):
            raise CapabilitySelfModelIntegrityError(
                "La chaîne globale des versions SelfModel est incohérente."
            )
        seen_ids.add(version.id)
        previous_id = version.id


def _validate_capability_attribute_history(
    *,
    agent_id: str,
    capability_key: str,
    current: CapabilitySelfAttribute | None,
    versions: list[CapabilitySelfAttribute],
    self_model_versions: list[SelfModelVersion],
    expected_initial_estimated_success: float,
) -> None:
    """Vérifier la chaîne d'attribut et ses liens vers les snapshots globaux."""
    if current is None:
        if versions:
            raise CapabilitySelfModelIntegrityError(
                "L'historique d'attribut existe sans CapabilitySelfAttribute courant."
            )
        return
    if not versions or versions[-1] != current:
        raise CapabilitySelfModelIntegrityError(
            "Le CapabilitySelfAttribute courant ne termine pas son historique."
        )
    if versions[0].estimated_success != expected_initial_estimated_success:
        raise CapabilitySelfModelIntegrityError(
            "Le CapabilitySelfAttribute initial ne correspond pas au prior DEV attendu."
        )

    model_versions_by_id = {version.id: version.version for version in self_model_versions}
    previous_id: str | None = None
    previous_model_version = 0
    seen_ids: set[str] = set()
    for expected_version, attribute in enumerate(versions, start=1):
        linked_model_version = model_versions_by_id.get(attribute.self_model_version_id)
        if (
            attribute.agent_id != agent_id
            or attribute.capability_key != capability_key
            or attribute.attribute_version != expected_version
            or attribute.previous_attribute_id != previous_id
            or attribute.id in seen_ids
            or linked_model_version is None
            or linked_model_version <= previous_model_version
        ):
            raise CapabilitySelfModelIntegrityError(
                "La chaîne du CapabilitySelfAttribute ou son lien SelfModel est incohérent."
            )
        seen_ids.add(attribute.id)
        previous_id = attribute.id
        previous_model_version = linked_model_version


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

            _validate_metacognitive_state(
                unit_of_work=unit_of_work,
                current=current,
                estimator=self._estimator,
            )

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


class CapabilitySelfModelInitializationService:
    """Initialiser atomiquement le prior et la représentation d'une capacité."""

    def __init__(
        self,
        *,
        unit_of_work_factory: CapabilityUnitOfWorkFactory,
        estimator: DecayedBetaEstimator,
        clock: Clock,
        identifiers: IdentifierGenerator,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._estimator = estimator
        self._clock = clock
        self._identifiers = identifiers
        self._decision_policy = CapabilityDecisionPolicy()

    def initialize(
        self,
        *,
        agent_id: str,
        capability_key: str,
    ) -> CapabilitySelfModelInitializationResult:
        """Créer une représentation initiale ou confirmer son existence cohérente."""
        with self._unit_of_work_factory() as unit_of_work:
            current_meta = unit_of_work.metacognitive_states.get_current(
                agent_id=agent_id,
                capability_key=capability_key,
            )
            current_attribute = unit_of_work.capability_self_attributes.get_current(
                agent_id=agent_id,
                capability_key=capability_key,
            )
            attribute_versions = unit_of_work.capability_self_attributes.list_versions(
                agent_id=agent_id,
                capability_key=capability_key,
            )
            current_model = unit_of_work.self_model_versions.get_current(agent_id=agent_id)
            model_versions = unit_of_work.self_model_versions.list_versions(agent_id=agent_id)
            _validate_self_model_history(
                agent_id=agent_id,
                current=current_model,
                versions=model_versions,
            )
            _validate_capability_attribute_history(
                agent_id=agent_id,
                capability_key=capability_key,
                current=current_attribute,
                versions=attribute_versions,
                self_model_versions=model_versions,
                expected_initial_estimated_success=(
                    self._estimator.initial_state().estimated_success
                ),
            )

            if current_attribute is not None:
                if current_meta is None or current_model is None:
                    raise CapabilitySelfModelIntegrityError(
                        "Une capacité initialisée doit posséder un état méta et un SelfModel."
                    )
                if (
                    current_meta.agent_id != agent_id
                    or current_meta.capability_key != capability_key
                ):
                    raise CapabilitySelfModelIntegrityError(
                        "L'état métacognitif courant appartient à un autre périmètre."
                    )
                _validate_metacognitive_state(
                    unit_of_work=unit_of_work,
                    current=current_meta,
                    estimator=self._estimator,
                )
                return CapabilitySelfModelInitializationResult(
                    agent_id=agent_id,
                    capability_key=capability_key,
                    status=CapabilitySelfModelInitializationStatus.ALREADY_INITIALIZED,
                    estimated_success=current_attribute.estimated_success,
                    action=self._decision_policy.action_for_estimated_success(
                        current_attribute.estimated_success
                    ),
                    self_model_version=current_model.version,
                    attribute_version=current_attribute.attribute_version,
                )

            if current_meta is None:
                current_meta = VersionedMetacognitiveCapabilityState(
                    agent_id=agent_id,
                    capability_key=capability_key,
                    version=1,
                    state=self._estimator.initial_state(),
                )
                create_meta = True
            else:
                create_meta = False
                if (
                    current_meta.agent_id != agent_id
                    or current_meta.capability_key != capability_key
                ):
                    raise CapabilitySelfModelInitializationError(
                        "L'état métacognitif à initialiser appartient à un autre périmètre."
                    )
                _validate_metacognitive_state(
                    unit_of_work=unit_of_work,
                    current=current_meta,
                    estimator=self._estimator,
                )
                if current_meta.version > 1:
                    raise CapabilitySelfModelInitializationError(
                        "Une capacité déjà apprise ne peut pas être initialisée tardivement."
                    )

            now = self._clock.now()
            new_model = SelfModelVersion(
                id=self._identifiers.new("self-model-version"),
                agent_id=agent_id,
                version=1 if current_model is None else current_model.version + 1,
                previous_version_id=None if current_model is None else current_model.id,
                created_at=now,
            )
            initial_estimate = current_meta.state.estimated_success
            initial_action = self._decision_policy.action_for_estimated_success(initial_estimate)
            new_attribute = CapabilitySelfAttribute(
                id=self._identifiers.new("capability-self-attribute"),
                agent_id=agent_id,
                capability_key=capability_key,
                estimated_success=initial_estimate,
                self_model_version_id=new_model.id,
                attribute_version=1,
                previous_attribute_id=None,
                created_at=now,
            )
            event = JournalEvent(
                id=self._identifiers.new("event"),
                agent_id=agent_id,
                cycle_id=CAPABILITY_SELF_MODEL_INITIALIZATION_CYCLE_ID,
                event_type=EventType.CAPABILITY_SELF_ATTRIBUTE_INITIALIZED,
                target_entity_type=CAPABILITY_SELF_ATTRIBUTE_TARGET_TYPE,
                target_entity_id=new_attribute.id,
                occurred_at=now,
                reason=CAPABILITY_SELF_MODEL_INITIALIZATION_REASON,
                new_value={
                    "capability_key": capability_key,
                    "previous_estimated_success": None,
                    "resulting_estimated_success": initial_estimate,
                    "previous_action": None,
                    "resulting_action": initial_action.value,
                    "metacognitive_state_version": current_meta.version,
                    "evidence_through_performance_id": None,
                    "evidence_through_sequence_index": None,
                    "evidence_source_type": None,
                    "source_type": SourceType.SYSTEM_RULE.value,
                    "self_model_version": new_model.version,
                    "attribute_version": new_attribute.attribute_version,
                    "reason": CAPABILITY_SELF_MODEL_INITIALIZATION_REASON,
                },
            )
            result = CapabilitySelfModelInitializationResult(
                agent_id=agent_id,
                capability_key=capability_key,
                status=CapabilitySelfModelInitializationStatus.INITIALIZED,
                estimated_success=initial_estimate,
                action=initial_action,
                self_model_version=new_model.version,
                attribute_version=new_attribute.attribute_version,
            )

            if create_meta:
                unit_of_work.metacognitive_states.replace_current(
                    state=current_meta,
                    expected_version=None,
                )
            unit_of_work.self_model_versions.add(new_model)
            unit_of_work.capability_self_attributes.add(new_attribute)
            unit_of_work.journal.append(event)
            unit_of_work.commit()
            return result


class CapabilitySelfModelRevisionService:
    """Consolider atomiquement un changement de bande métacognitif persistant."""

    def __init__(
        self,
        *,
        unit_of_work_factory: CapabilityUnitOfWorkFactory,
        estimator: DecayedBetaEstimator,
        revision_policy: SignificantSelfRevisionPolicy,
        clock: Clock,
        identifiers: IdentifierGenerator,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._estimator = estimator
        self._revision_policy = revision_policy
        self._clock = clock
        self._identifiers = identifiers

    def revise(
        self,
        *,
        agent_id: str,
        capability_key: str,
    ) -> CapabilitySelfModelRevisionResult:
        """Réviser depuis la persistance ou retourner explicitement NO_REVISION."""
        with self._unit_of_work_factory() as unit_of_work:
            current_meta = unit_of_work.metacognitive_states.get_current(
                agent_id=agent_id,
                capability_key=capability_key,
            )
            current_attribute = unit_of_work.capability_self_attributes.get_current(
                agent_id=agent_id,
                capability_key=capability_key,
            )
            current_model = unit_of_work.self_model_versions.get_current(agent_id=agent_id)
            if current_meta is None or current_attribute is None or current_model is None:
                raise CapabilitySelfModelNotInitializedError(
                    "La capacité doit être initialisée avant toute révision du SelfModel."
                )
            if current_meta.agent_id != agent_id or current_meta.capability_key != capability_key:
                raise CapabilitySelfModelIntegrityError(
                    "L'état métacognitif courant appartient à un autre périmètre."
                )

            model_versions = unit_of_work.self_model_versions.list_versions(agent_id=agent_id)
            attribute_versions = unit_of_work.capability_self_attributes.list_versions(
                agent_id=agent_id,
                capability_key=capability_key,
            )
            _validate_self_model_history(
                agent_id=agent_id,
                current=current_model,
                versions=model_versions,
            )
            _validate_capability_attribute_history(
                agent_id=agent_id,
                capability_key=capability_key,
                current=current_attribute,
                versions=attribute_versions,
                self_model_versions=model_versions,
                expected_initial_estimated_success=(
                    self._estimator.initial_state().estimated_success
                ),
            )
            cursor_performance = _validate_metacognitive_state(
                unit_of_work=unit_of_work,
                current=current_meta,
                estimator=self._estimator,
            )
            if current_meta.version == 1:
                raise CapabilitySelfModelIntegrityError(
                    "Une révision exige une preuve métacognitive réellement incorporée."
                )
            assessment = self._revision_policy.assess(
                previous_estimated_success=current_attribute.estimated_success,
                candidate_estimated_success=current_meta.state.estimated_success,
            )

            if not assessment.is_significant:
                return CapabilitySelfModelRevisionResult(
                    agent_id=agent_id,
                    capability_key=capability_key,
                    status=CapabilitySelfModelRevisionStatus.NO_REVISION,
                    previous_estimated_success=current_attribute.estimated_success,
                    resulting_estimated_success=current_attribute.estimated_success,
                    previous_action=assessment.previous_action,
                    resulting_action=assessment.previous_action,
                    previous_self_model_version=current_model.version,
                    resulting_self_model_version=current_model.version,
                    previous_attribute_version=current_attribute.attribute_version,
                    resulting_attribute_version=current_attribute.attribute_version,
                    triggering_performance_id=None,
                )

            if cursor_performance is None:
                raise CapabilitySelfModelIntegrityError(
                    "Une révision significative exige une preuve métacognitive persistée."
                )

            now = self._clock.now()
            new_model = SelfModelVersion(
                id=self._identifiers.new("self-model-version"),
                agent_id=agent_id,
                version=current_model.version + 1,
                previous_version_id=current_model.id,
                created_at=now,
            )
            new_attribute = CapabilitySelfAttribute(
                id=self._identifiers.new("capability-self-attribute"),
                agent_id=agent_id,
                capability_key=capability_key,
                estimated_success=current_meta.state.estimated_success,
                self_model_version_id=new_model.id,
                attribute_version=current_attribute.attribute_version + 1,
                previous_attribute_id=current_attribute.id,
                created_at=now,
            )
            event = JournalEvent(
                id=self._identifiers.new("event"),
                agent_id=agent_id,
                cycle_id=cursor_performance.cycle_id,
                event_type=EventType.CAPABILITY_SELF_ATTRIBUTE_REVISED,
                target_entity_type=CAPABILITY_SELF_ATTRIBUTE_TARGET_TYPE,
                target_entity_id=new_attribute.id,
                occurred_at=now,
                reason=CAPABILITY_SELF_MODEL_REVISION_REASON,
                new_value={
                    "capability_key": capability_key,
                    "previous_estimated_success": current_attribute.estimated_success,
                    "resulting_estimated_success": new_attribute.estimated_success,
                    "previous_action": assessment.previous_action.value,
                    "resulting_action": assessment.resulting_action.value,
                    "metacognitive_state_version": current_meta.version,
                    "evidence_through_performance_id": cursor_performance.id,
                    "evidence_through_sequence_index": cursor_performance.sequence_index,
                    "evidence_source_type": cursor_performance.source_type.value,
                    "source_type": SourceType.INTERNAL_STATE.value,
                    "self_model_version": new_model.version,
                    "attribute_version": new_attribute.attribute_version,
                    "reason": CAPABILITY_SELF_MODEL_REVISION_REASON,
                },
            )
            result = CapabilitySelfModelRevisionResult(
                agent_id=agent_id,
                capability_key=capability_key,
                status=CapabilitySelfModelRevisionStatus.REVISED,
                previous_estimated_success=current_attribute.estimated_success,
                resulting_estimated_success=new_attribute.estimated_success,
                previous_action=assessment.previous_action,
                resulting_action=assessment.resulting_action,
                previous_self_model_version=current_model.version,
                resulting_self_model_version=new_model.version,
                previous_attribute_version=current_attribute.attribute_version,
                resulting_attribute_version=new_attribute.attribute_version,
                triggering_performance_id=cursor_performance.id,
            )

            unit_of_work.self_model_versions.add(new_model)
            unit_of_work.capability_self_attributes.add(new_attribute)
            unit_of_work.journal.append(event)
            unit_of_work.commit()
            return result


class CapabilityPostPerformanceProcessingService:
    """Enchaîner pour C l'apprentissage puis la révision dans deux transactions."""

    def __init__(
        self,
        *,
        unit_of_work_factory: CapabilityUnitOfWorkFactory,
        metacognitive_update_service: MetacognitiveCapabilityUpdateService,
        self_model_revision_service: CapabilitySelfModelRevisionService,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._metacognitive_update_service = metacognitive_update_service
        self._self_model_revision_service = self_model_revision_service
        self._decision_policy = CapabilityDecisionPolicy()

    def process(self, *, performance_id: str) -> CapabilityPostPerformanceProcessingResult:
        """Traiter une preuve persistée seulement si sa capacité est déjà initialisée."""
        performance = self._ensure_capability_is_initialized(performance_id=performance_id)

        metacognitive_result = self._metacognitive_update_service.process(
            performance_id=performance_id
        )
        if metacognitive_result.status is MetacognitiveUpdateStatus.ALREADY_PROCESSED:
            current_meta, current_model, current_attribute = self._read_current_cognitive_state(
                agent_id=metacognitive_result.agent_id,
                capability_key=metacognitive_result.capability_key,
            )
            if current_meta.last_processed_performance_id != performance.id:
                cursor_sequence_index = current_meta.last_processed_sequence_index
                if (
                    cursor_sequence_index is None
                    or performance.sequence_index >= cursor_sequence_index
                ):
                    raise MetacognitiveStateIntegrityError(
                        "Le vieux doublon ne précède pas strictement le curseur métacognitif."
                    )
                return CapabilityPostPerformanceProcessingResult(
                    performance_id=metacognitive_result.performance_id,
                    agent_id=metacognitive_result.agent_id,
                    capability_key=metacognitive_result.capability_key,
                    metacognitive_status=metacognitive_result.status,
                    self_model_revision_status=(
                        CapabilityPostPerformanceRevisionStatus.SKIPPED_OLD_DUPLICATE
                    ),
                    metacognitive_version_before=metacognitive_result.previous_version,
                    metacognitive_version_after=metacognitive_result.resulting_version,
                    self_model_version_before=current_model.version,
                    self_model_version_after=current_model.version,
                    attribute_version_before=current_attribute.attribute_version,
                    attribute_version_after=current_attribute.attribute_version,
                    resulting_action=self._decision_policy.action_for_estimated_success(
                        current_attribute.estimated_success
                    ),
                )
        revision_result = self._self_model_revision_service.revise(
            agent_id=metacognitive_result.agent_id,
            capability_key=metacognitive_result.capability_key,
        )
        return CapabilityPostPerformanceProcessingResult(
            performance_id=metacognitive_result.performance_id,
            agent_id=metacognitive_result.agent_id,
            capability_key=metacognitive_result.capability_key,
            self_model_revision_status=CapabilityPostPerformanceRevisionStatus(
                revision_result.status.value
            ),
            metacognitive_status=metacognitive_result.status,
            metacognitive_version_before=metacognitive_result.previous_version,
            metacognitive_version_after=metacognitive_result.resulting_version,
            self_model_version_before=revision_result.previous_self_model_version,
            self_model_version_after=revision_result.resulting_self_model_version,
            attribute_version_before=revision_result.previous_attribute_version,
            attribute_version_after=revision_result.resulting_attribute_version,
            resulting_action=revision_result.resulting_action,
        )

    def _ensure_capability_is_initialized(
        self,
        *,
        performance_id: str,
    ) -> CapabilityPerformanceObservation:
        """Refuser avant apprentissage une preuve absente ou un bootstrap incomplet."""
        with self._unit_of_work_factory() as unit_of_work:
            performance = unit_of_work.capability_performances.get(performance_id)
            if performance is None:
                raise CapabilityPerformanceNotFoundError(
                    f"La performance persistée {performance_id!r} n'existe pas."
                )
            current_attribute = unit_of_work.capability_self_attributes.get_current(
                agent_id=performance.agent_id,
                capability_key=performance.capability_key,
            )
            attribute_versions = unit_of_work.capability_self_attributes.list_versions(
                agent_id=performance.agent_id,
                capability_key=performance.capability_key,
            )
            current_meta = unit_of_work.metacognitive_states.get_current(
                agent_id=performance.agent_id,
                capability_key=performance.capability_key,
            )
            current_model = unit_of_work.self_model_versions.get_current(
                agent_id=performance.agent_id
            )
        if current_attribute is None:
            raise CapabilitySelfModelNotInitializedError(
                "La capacité doit être initialisée avant sa première performance traitée par C."
            )
        if not attribute_versions or attribute_versions[-1] != current_attribute:
            raise CapabilitySelfModelIntegrityError(
                "Le CapabilitySelfAttribute courant ne termine pas son historique."
            )
        initial_attribute = attribute_versions[0]
        if (
            initial_attribute.agent_id != performance.agent_id
            or initial_attribute.capability_key != performance.capability_key
            or initial_attribute.attribute_version != 1
            or initial_attribute.previous_attribute_id is not None
            or initial_attribute.estimated_success != DEV_PRIOR_ESTIMATED_SUCCESS
        ):
            raise CapabilitySelfModelIntegrityError(
                "Le premier CapabilitySelfAttribute ne représente pas le prior DEV initial."
            )
        if initial_attribute.created_at > performance.observed_at:
            raise CapabilitySelfModelNotInitializedError(
                "L'initialisation de la capacité doit précéder la performance traitée par C."
            )
        if current_meta is None or current_model is None:
            raise CapabilitySelfModelIntegrityError(
                "Une capacité initialisée doit posséder un MetaState et un SelfModel courants."
            )
        if (
            current_attribute.agent_id != performance.agent_id
            or current_attribute.capability_key != performance.capability_key
            or current_meta.agent_id != performance.agent_id
            or current_meta.capability_key != performance.capability_key
            or current_model.agent_id != performance.agent_id
        ):
            raise CapabilitySelfModelIntegrityError(
                "La précondition d'initialisation appartient à un autre périmètre."
            )
        return performance

    def _read_current_cognitive_state(
        self,
        *,
        agent_id: str,
        capability_key: str,
    ) -> tuple[
        VersionedMetacognitiveCapabilityState,
        SelfModelVersion,
        CapabilitySelfAttribute,
    ]:
        """Relire l'état public courant servant à classifier un ALREADY_PROCESSED."""
        with self._unit_of_work_factory() as unit_of_work:
            current_meta = unit_of_work.metacognitive_states.get_current(
                agent_id=agent_id,
                capability_key=capability_key,
            )
            current_model = unit_of_work.self_model_versions.get_current(agent_id=agent_id)
            current_attribute = unit_of_work.capability_self_attributes.get_current(
                agent_id=agent_id,
                capability_key=capability_key,
            )
        if current_meta is None or current_model is None or current_attribute is None:
            raise CapabilitySelfModelIntegrityError(
                "L'état cognitif courant a disparu après le traitement métacognitif."
            )
        if (
            current_meta.agent_id != agent_id
            or current_meta.capability_key != capability_key
            or current_model.agent_id != agent_id
            or current_attribute.agent_id != agent_id
            or current_attribute.capability_key != capability_key
        ):
            raise CapabilitySelfModelIntegrityError(
                "L'état cognitif courant relu appartient à un autre périmètre."
            )
        return current_meta, current_model, current_attribute
