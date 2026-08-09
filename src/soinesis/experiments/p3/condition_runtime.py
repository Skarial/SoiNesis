"""Composition contrôlée des runtimes cognitifs A, B et C de P3 DEV."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final, Protocol

from soinesis.application.capabilities import (
    CAPABILITY_SELF_ATTRIBUTE_TARGET_TYPE,
    CapabilityDecisionPolicy,
    CapabilityPostPerformanceProcessingService,
    CapabilitySelfModelInitializationService,
    CapabilitySelfModelRevisionService,
    DecayedBetaEstimator,
    FixedCapabilityDecisionService,
    FixedCapabilityEstimateProvider,
    MetacognitiveCapabilityUpdateService,
    RawHistoryCapabilityDecisionService,
    RawHistoryCapabilityEstimateProvider,
    SelfAttributeCapabilityDecisionService,
    SelfAttributeCapabilityEstimateProvider,
    SignificantSelfRevisionPolicy,
)
from soinesis.domain.capabilities import (
    CapabilityDecision,
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    SelfModelVersion,
    VersionedMetacognitiveCapabilityState,
)
from soinesis.domain.models import EventType, JournalEvent
from soinesis.experiments.p3.condition_config import (
    ExperimentalCondition,
    ExperimentalExecutionConditionConfigurationService,
)
from soinesis.experiments.p3.replication_manifest import (
    ExperimentalReplicationExecutionManifest,
    ExperimentalReplicationManifestService,
)
from soinesis.ports.capabilities import CapabilityUnitOfWorkFactory
from soinesis.ports.system import Clock, IdentifierGenerator

P3_PUBLIC_CAPABILITY_KEYS: Final = ("ALPHA", "BETA", "GAMMA")
_INITIAL_ESTIMATED_SUCCESS: Final = 0.60
_CAPABILITY_EVENT_TYPES: Final = {
    EventType.CAPABILITY_SELF_ATTRIBUTE_INITIALIZED,
    EventType.CAPABILITY_SELF_ATTRIBUTE_REVISED,
}


class _CapabilityDecisionService(Protocol):
    def decide(self, *, boundary: CapabilityHistoryBoundary) -> CapabilityDecision: ...


@dataclass(frozen=True, slots=True)
class ExperimentalAgentCognitiveState:
    """Snapshot expérimental en lecture seule de l'état cognitif d'un agent."""

    agent_id: str
    performances: tuple[CapabilityPerformanceObservation, ...]
    metacognitive_states: tuple[VersionedMetacognitiveCapabilityState, ...]
    self_model_versions: tuple[SelfModelVersion, ...]
    capability_self_attributes: tuple[CapabilitySelfAttribute, ...]
    capability_journal_events: tuple[JournalEvent, ...]


class ExperimentalAgentCognitiveStateInspector(Protocol):
    """Inspecter un agent sans étendre les ports cognitifs généraux."""

    def inspect(self, *, agent_id: str) -> ExperimentalAgentCognitiveState: ...


@dataclass(frozen=True, slots=True)
class ExperimentalConditionRuntime:
    """Services cognitifs composés pour une exécution, sans l'exécuter."""

    execution_id: str
    condition: ExperimentalCondition
    agent_id: str
    decision_service: _CapabilityDecisionService
    post_performance_processor: CapabilityPostPerformanceProcessingService | None


class ExperimentalConditionRuntimeError(RuntimeError):
    """Erreur de base de la composition expérimentale P3 DEV."""


class ExperimentalConditionRuntimeIntegrityError(ExperimentalConditionRuntimeError):
    """Refuser une configuration ou un état cognitif incompatible avec l'exécution."""


@dataclass(frozen=True, slots=True)
class _ManifestBootstrapClock:
    value: datetime

    def now(self) -> datetime:
        return self.value


class ExperimentalConditionRuntimeComposer:
    """Construire A, B ou C depuis 3R et 3P sans lancer de cycle."""

    def __init__(
        self,
        *,
        configuration_service: ExperimentalExecutionConditionConfigurationService,
        manifest_service: ExperimentalReplicationManifestService,
        cognitive_state_inspector: ExperimentalAgentCognitiveStateInspector,
        unit_of_work_factory: CapabilityUnitOfWorkFactory,
        revision_clock: Clock,
        identifiers: IdentifierGenerator,
    ) -> None:
        self._configuration_service = configuration_service
        self._manifest_service = manifest_service
        self._cognitive_state_inspector = cognitive_state_inspector
        self._unit_of_work_factory = unit_of_work_factory
        self._revision_clock = revision_clock
        self._identifiers = identifiers

    def compose(self, *, execution_id: str) -> ExperimentalConditionRuntime:
        """Composer uniquement depuis la configuration et le manifeste persistants."""
        stored_configuration = self._configuration_service.get(execution_id=execution_id)
        if stored_configuration is None:
            raise ExperimentalConditionRuntimeIntegrityError(
                "Une configuration de condition 3R persistante est requise."
            )
        manifest = self._manifest_service.get(execution_id=execution_id)
        if manifest is None:
            raise ExperimentalConditionRuntimeIntegrityError(
                "Un manifeste 3P persistant est requis."
            )
        if (
            stored_configuration.execution_id != execution_id
            or manifest.execution_id != execution_id
        ):
            raise ExperimentalConditionRuntimeIntegrityError(
                "La configuration 3R ou le manifeste 3P appartient à une autre exécution."
            )
        agent_ids = {context.start_context.agent_id for context in manifest.cycle_contexts}
        if len(agent_ids) != 1:
            raise ExperimentalConditionRuntimeIntegrityError(
                "Le manifeste persistant doit décrire exactement un agent."
            )
        agent_id = next(iter(agent_ids))
        cognitive_state = self._cognitive_state_inspector.inspect(agent_id=agent_id)
        if cognitive_state.agent_id != agent_id:
            raise ExperimentalConditionRuntimeIntegrityError(
                "L'inspection cognitive a retourné un autre agent."
            )
        self._validate_performances(cognitive_state=cognitive_state, manifest=manifest)

        configuration = stored_configuration.configuration
        decision_policy = CapabilityDecisionPolicy()
        if configuration.condition is ExperimentalCondition.A:
            self._require_no_persistent_self_state(cognitive_state)
            return ExperimentalConditionRuntime(
                execution_id=execution_id,
                condition=configuration.condition,
                agent_id=agent_id,
                decision_service=FixedCapabilityDecisionService(
                    estimate_provider=FixedCapabilityEstimateProvider(),
                    decision_policy=decision_policy,
                ),
                post_performance_processor=None,
            )

        lambda_value = configuration.estimator_lambda
        if lambda_value is None:
            raise ExperimentalConditionRuntimeIntegrityError(
                "La condition configurée exige un estimator_lambda 3R."
            )
        estimator = DecayedBetaEstimator(lambda_=float(lambda_value))
        if configuration.condition is ExperimentalCondition.B:
            self._require_no_persistent_self_state(cognitive_state)
            return ExperimentalConditionRuntime(
                execution_id=execution_id,
                condition=configuration.condition,
                agent_id=agent_id,
                decision_service=RawHistoryCapabilityDecisionService(
                    unit_of_work_factory=self._unit_of_work_factory,
                    estimate_provider=RawHistoryCapabilityEstimateProvider(estimator=estimator),
                    decision_policy=decision_policy,
                ),
                post_performance_processor=None,
            )
        if configuration.condition is not ExperimentalCondition.C:
            raise ExperimentalConditionRuntimeIntegrityError(
                "La condition expérimentale persistante n'est pas supportée."
            )
        return self._compose_c(
            execution_id=execution_id,
            agent_id=agent_id,
            manifest=manifest,
            cognitive_state=cognitive_state,
            estimator=estimator,
            decision_policy=decision_policy,
        )

    def _compose_c(
        self,
        *,
        execution_id: str,
        agent_id: str,
        manifest: ExperimentalReplicationExecutionManifest,
        cognitive_state: ExperimentalAgentCognitiveState,
        estimator: DecayedBetaEstimator,
        decision_policy: CapabilityDecisionPolicy,
    ) -> ExperimentalConditionRuntime:
        bootstrap_time = self._bootstrap_time(manifest)
        self._validate_c_state(
            cognitive_state=cognitive_state,
            estimator=estimator,
            bootstrap_time=bootstrap_time,
        )
        initializer = CapabilitySelfModelInitializationService(
            unit_of_work_factory=self._unit_of_work_factory,
            estimator=estimator,
            clock=_ManifestBootstrapClock(bootstrap_time),
            identifiers=self._identifiers,
        )
        for capability_key in P3_PUBLIC_CAPABILITY_KEYS:
            initializer.initialize(agent_id=agent_id, capability_key=capability_key)

        revision_service = CapabilitySelfModelRevisionService(
            unit_of_work_factory=self._unit_of_work_factory,
            estimator=estimator,
            revision_policy=SignificantSelfRevisionPolicy(decision_policy=decision_policy),
            clock=self._revision_clock,
            identifiers=self._identifiers,
        )
        return ExperimentalConditionRuntime(
            execution_id=execution_id,
            condition=ExperimentalCondition.C,
            agent_id=agent_id,
            decision_service=SelfAttributeCapabilityDecisionService(
                unit_of_work_factory=self._unit_of_work_factory,
                estimate_provider=SelfAttributeCapabilityEstimateProvider(),
                decision_policy=decision_policy,
            ),
            post_performance_processor=CapabilityPostPerformanceProcessingService(
                unit_of_work_factory=self._unit_of_work_factory,
                metacognitive_update_service=MetacognitiveCapabilityUpdateService(
                    unit_of_work_factory=self._unit_of_work_factory,
                    estimator=estimator,
                ),
                self_model_revision_service=revision_service,
            ),
        )

    @staticmethod
    def _validate_performances(
        *,
        cognitive_state: ExperimentalAgentCognitiveState,
        manifest: ExperimentalReplicationExecutionManifest,
    ) -> None:
        sequence_indices = tuple(
            sorted(performance.sequence_index for performance in cognitive_state.performances)
        )
        if sequence_indices != tuple(range(len(sequence_indices))):
            raise ExperimentalConditionRuntimeIntegrityError(
                "Les performances persistantes doivent former un préfixe causal contigu."
            )
        contexts_by_performance_id = {
            context.start_context.performance_id: context for context in manifest.cycle_contexts
        }
        for performance in cognitive_state.performances:
            context = contexts_by_performance_id.get(performance.id)
            if context is None:
                raise ExperimentalConditionRuntimeIntegrityError(
                    "Une performance de l'agent est étrangère au manifeste 3P."
                )
            start = context.start_context
            if (
                performance.agent_id != cognitive_state.agent_id
                or performance.agent_id != start.agent_id
                or performance.trial_id != start.trial_id
                or performance.cycle_id != start.cycle_id
                or performance.sequence_index != context.sequence_index
                or performance.observed_at != start.observed_at
            ):
                raise ExperimentalConditionRuntimeIntegrityError(
                    "Une performance persistante diverge de son contexte manifeste."
                )

    @staticmethod
    def _require_no_persistent_self_state(
        cognitive_state: ExperimentalAgentCognitiveState,
    ) -> None:
        if (
            cognitive_state.metacognitive_states
            or cognitive_state.self_model_versions
            or cognitive_state.capability_self_attributes
            or cognitive_state.capability_journal_events
        ):
            raise ExperimentalConditionRuntimeIntegrityError(
                "La condition A ou B ne peut reprendre aucun état métacognitif ou SelfModel."
            )

    @staticmethod
    def _bootstrap_time(manifest: ExperimentalReplicationExecutionManifest) -> datetime:
        try:
            return min(context.start_context.observed_at for context in manifest.cycle_contexts)
        except TypeError as error:
            raise ExperimentalConditionRuntimeIntegrityError(
                "Les timestamps du manifeste ne sont pas comparables."
            ) from error

    @staticmethod
    def _validate_c_state(
        *,
        cognitive_state: ExperimentalAgentCognitiveState,
        estimator: DecayedBetaEstimator,
        bootstrap_time: datetime,
    ) -> None:
        allowed_capabilities = set(P3_PUBLIC_CAPABILITY_KEYS)
        meta_by_capability = {
            state.capability_key: state for state in cognitive_state.metacognitive_states
        }
        attributes_by_capability: dict[str, list[CapabilitySelfAttribute]] = {}
        for attribute in cognitive_state.capability_self_attributes:
            attributes_by_capability.setdefault(attribute.capability_key, []).append(attribute)
        if (
            not set(meta_by_capability) <= allowed_capabilities
            or not set(attributes_by_capability) <= allowed_capabilities
            or set(meta_by_capability) != set(attributes_by_capability)
        ):
            raise ExperimentalConditionRuntimeIntegrityError(
                "L'état C contient une capacité étrangère ou un bootstrap incomplet."
            )
        for state in meta_by_capability.values():
            if state.state.lambda_ != estimator.lambda_:
                raise ExperimentalConditionRuntimeIntegrityError(
                    "Un état métacognitif utilise un lambda différent de 3R."
                )
        linked_model_ids = {
            attribute.self_model_version_id
            for attribute in cognitive_state.capability_self_attributes
        }
        model_ids = {version.id for version in cognitive_state.self_model_versions}
        if linked_model_ids != model_ids:
            raise ExperimentalConditionRuntimeIntegrityError(
                "Les versions du SelfModel ne correspondent pas exactement aux attributs C."
            )
        events_by_target = {
            event.target_entity_id: event for event in cognitive_state.capability_journal_events
        }
        attribute_ids = {attribute.id for attribute in cognitive_state.capability_self_attributes}
        if set(events_by_target) != attribute_ids:
            raise ExperimentalConditionRuntimeIntegrityError(
                "Le journal CAPABILITY ne correspond pas exactement aux attributs C."
            )
        if len(events_by_target) != len(cognitive_state.capability_journal_events):
            raise ExperimentalConditionRuntimeIntegrityError(
                "Plusieurs événements CAPABILITY ciblent le même attribut."
            )
        for attribute in cognitive_state.capability_self_attributes:
            event = events_by_target[attribute.id]
            expected_event_type = (
                EventType.CAPABILITY_SELF_ATTRIBUTE_INITIALIZED
                if attribute.attribute_version == 1
                else EventType.CAPABILITY_SELF_ATTRIBUTE_REVISED
            )
            if (
                event.event_type is not expected_event_type
                or event.agent_id != cognitive_state.agent_id
                or event.target_entity_type != CAPABILITY_SELF_ATTRIBUTE_TARGET_TYPE
                or event.new_value.get("capability_key") != attribute.capability_key
            ):
                raise ExperimentalConditionRuntimeIntegrityError(
                    "Un événement CAPABILITY ne correspond pas à sa version d'attribut."
                )

        has_performances = bool(cognitive_state.performances)
        initialized_capabilities = set(attributes_by_capability)
        if has_performances:
            if initialized_capabilities != allowed_capabilities:
                raise ExperimentalConditionRuntimeIntegrityError(
                    "Les trois capacités C doivent précéder toute performance."
                )
        else:
            ExperimentalConditionRuntimeComposer._validate_c_bootstrap_prefix(
                cognitive_state=cognitive_state,
                meta_by_capability=meta_by_capability,
                attributes_by_capability=attributes_by_capability,
                estimator=estimator,
            )
        for capability_key, attributes in attributes_by_capability.items():
            initial_attribute = min(
                attributes,
                key=lambda attribute: attribute.attribute_version,
            )
            if (
                initial_attribute.attribute_version != 1
                or initial_attribute.previous_attribute_id is not None
                or initial_attribute.estimated_success != _INITIAL_ESTIMATED_SUCCESS
                or initial_attribute.created_at > bootstrap_time
            ):
                raise ExperimentalConditionRuntimeIntegrityError(
                    f"Le bootstrap C de {capability_key} est invalide ou tardif."
                )

    @staticmethod
    def _validate_c_bootstrap_prefix(
        *,
        cognitive_state: ExperimentalAgentCognitiveState,
        meta_by_capability: dict[str, VersionedMetacognitiveCapabilityState],
        attributes_by_capability: dict[str, list[CapabilitySelfAttribute]],
        estimator: DecayedBetaEstimator,
    ) -> None:
        model_order = {
            version.id: version.version for version in cognitive_state.self_model_versions
        }
        capability_order = tuple(
            attribute.capability_key
            for attribute in sorted(
                cognitive_state.capability_self_attributes,
                key=lambda attribute: model_order[attribute.self_model_version_id],
            )
        )
        if capability_order != P3_PUBLIC_CAPABILITY_KEYS[: len(capability_order)]:
            raise ExperimentalConditionRuntimeIntegrityError(
                "Un bootstrap C interrompu doit suivre ALPHA, BETA, GAMMA."
            )
        expected_prior = estimator.initial_state()
        for capability_key in capability_order:
            state = meta_by_capability[capability_key]
            attributes = attributes_by_capability[capability_key]
            if (
                state.version != 1
                or state.last_processed_performance_id is not None
                or state.last_processed_sequence_index is not None
                or state.state != expected_prior
                or len(attributes) != 1
                or attributes[0].attribute_version != 1
            ):
                raise ExperimentalConditionRuntimeIntegrityError(
                    "Le préfixe de bootstrap C contient un apprentissage ou une révision."
                )
        if any(
            event.event_type is EventType.CAPABILITY_SELF_ATTRIBUTE_REVISED
            for event in cognitive_state.capability_journal_events
        ):
            raise ExperimentalConditionRuntimeIntegrityError(
                "Un bootstrap C sans performance ne peut contenir aucune révision."
            )
