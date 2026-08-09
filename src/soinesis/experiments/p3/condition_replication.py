"""Intégration DEV d'une condition persistante avec le runner de réplication P3."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from soinesis.application.capabilities import (
    CapabilityDecisionPolicy,
    CapabilityPerformanceRecordingService,
)
from soinesis.domain.capabilities import EstimateSource
from soinesis.experiments.p3.checkpoint import (
    ExperimentalCycleCheckpoint,
    ExperimentalCycleCheckpointService,
    ExperimentalCycleCheckpointStatus,
)
from soinesis.experiments.p3.condition_config import (
    ExperimentalCondition,
    ExperimentalExecutionConditionConfiguration,
)
from soinesis.experiments.p3.condition_runtime import (
    ExperimentalAgentCognitiveState,
    ExperimentalAgentCognitiveStateInspector,
    ExperimentalConditionRuntime,
)
from soinesis.experiments.p3.execution_binding import (
    ExperimentalExecutionPlanBinding,
    ExperimentalExecutionPlanBindingService,
)
from soinesis.experiments.p3.generation import ExperimentalReplicationPlanGenerator
from soinesis.experiments.p3.plan import ExperimentalReplicationPlan
from soinesis.experiments.p3.provenance import (
    ExperimentalExecutionGenerationProvenance,
)
from soinesis.experiments.p3.replication_manifest import (
    ExperimentalReplicationExecutionManifest,
)
from soinesis.experiments.p3.replication_runner import (
    ExperimentalReplicationRunner,
    ExperimentalReplicationRunResult,
)

_TOTAL_CYCLES = 180
_FIXED_BASELINE_ESTIMATE = 0.60
_DECISION_SOURCE_BY_CONDITION = {
    ExperimentalCondition.A: EstimateSource.FIXED_BASELINE,
    ExperimentalCondition.B: EstimateSource.RAW_HISTORY,
    ExperimentalCondition.C: EstimateSource.SELF_ATTRIBUTE,
}


class ExperimentalConditionReplicationRunResult(BaseModel):
    """Résultat minimal d'une réplication DEV exécutée sous sa condition 3R."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(min_length=1)
    condition: ExperimentalCondition
    agent_id: str = Field(min_length=1)
    replication_result: ExperimentalReplicationRunResult

    @model_validator(mode="after")
    def validate_execution_scope(self) -> ExperimentalConditionReplicationRunResult:
        if self.replication_result.execution_id != self.execution_id:
            raise ValueError("Le résultat 3Q appartient à une autre exécution.")
        return self


class ExperimentalConditionReplicationError(RuntimeError):
    """Erreur de base de l'intégration condition/réplication P3 DEV."""


class ExperimentalConditionReplicationIntegrityError(ExperimentalConditionReplicationError):
    """Refuser un passé ou des artefacts incompatibles avant toute exécution."""


class _ConditionConfigurationReader(Protocol):
    def get(self, *, execution_id: str) -> ExperimentalExecutionConditionConfiguration | None: ...


class _ManifestReader(Protocol):
    def get(self, *, execution_id: str) -> ExperimentalReplicationExecutionManifest | None: ...


class _GenerationProvenanceReader(Protocol):
    def get(self, *, execution_id: str) -> ExperimentalExecutionGenerationProvenance | None: ...


class _RuntimeComposer(Protocol):
    def compose(self, *, execution_id: str) -> ExperimentalConditionRuntime: ...


class ExperimentalConditionReplicationRunner:
    """Prévalider le passé puis déléguer une unique exécution aux couches 3S et 3Q."""

    def __init__(
        self,
        *,
        configuration_service: _ConditionConfigurationReader,
        manifest_service: _ManifestReader,
        binding_service: ExperimentalExecutionPlanBindingService,
        provenance_service: _GenerationProvenanceReader,
        plan_generator: ExperimentalReplicationPlanGenerator,
        cognitive_state_inspector: ExperimentalAgentCognitiveStateInspector,
        checkpoint_service: ExperimentalCycleCheckpointService,
        runtime_composer: _RuntimeComposer,
        recording_service: CapabilityPerformanceRecordingService,
    ) -> None:
        self._configuration_service = configuration_service
        self._manifest_service = manifest_service
        self._binding_service = binding_service
        self._provenance_service = provenance_service
        self._plan_generator = plan_generator
        self._cognitive_state_inspector = cognitive_state_inspector
        self._checkpoint_service = checkpoint_service
        self._runtime_composer = runtime_composer
        self._recording_service = recording_service

    def run(self, *, execution_id: str) -> ExperimentalConditionReplicationRunResult:
        """Exécuter une condition uniquement après un préflight privé et read-only."""
        configuration = self._require_configuration(execution_id=execution_id)
        manifest = self._require_manifest(execution_id=execution_id)
        binding = self._require_binding(execution_id=execution_id)
        provenance = self._require_provenance(execution_id=execution_id)
        self._validate_artifact_scopes(
            execution_id=execution_id,
            configuration=configuration,
            manifest=manifest,
            binding=binding,
            provenance=provenance,
        )
        plan = self._plan_generator.reproduce(provenance=provenance.generation_provenance)
        if plan.identity() != binding.plan_identity:
            raise ExperimentalConditionReplicationIntegrityError(
                "Le plan reproduit ne correspond pas au binding 3N."
            )
        agent_id = self._manifest_agent_id(manifest)
        cognitive_state = self._cognitive_state_inspector.inspect(agent_id=agent_id)
        if cognitive_state.agent_id != agent_id:
            raise ExperimentalConditionReplicationIntegrityError(
                "L'inspection cognitive a retourné un autre agent."
            )
        self._validate_historical_performances(
            manifest=manifest,
            cognitive_state=cognitive_state,
            plan=plan,
        )
        checkpoints = self._read_checkpoint_prefix(execution_id=execution_id)
        self._validate_checkpoints(
            execution_id=execution_id,
            condition=configuration.configuration.condition,
            agent_id=agent_id,
            manifest=manifest,
            cognitive_state=cognitive_state,
            plan=plan,
            checkpoints=checkpoints,
        )

        runtime = self._runtime_composer.compose(execution_id=execution_id)
        if (
            runtime.execution_id != execution_id
            or runtime.condition is not configuration.configuration.condition
            or runtime.agent_id != agent_id
        ):
            raise ExperimentalConditionReplicationIntegrityError(
                "Le runtime 3S diverge des artefacts prévalidés."
            )
        replication_result = ExperimentalReplicationRunner(
            manifest_service=self._manifest_service,
            binding_service=self._binding_service,
            provenance_service=self._provenance_service,
            plan_generator=self._plan_generator,
            checkpoint_service=self._checkpoint_service,
            decision_service=runtime.decision_service,
            recording_service=self._recording_service,
            post_performance_processor=runtime.post_performance_processor,
        ).run(execution_id=execution_id)
        return ExperimentalConditionReplicationRunResult(
            execution_id=execution_id,
            condition=configuration.configuration.condition,
            agent_id=agent_id,
            replication_result=replication_result,
        )

    def _require_configuration(
        self, *, execution_id: str
    ) -> ExperimentalExecutionConditionConfiguration:
        configuration = self._configuration_service.get(execution_id=execution_id)
        if configuration is None:
            raise ExperimentalConditionReplicationIntegrityError(
                "Une configuration 3R persistante est requise."
            )
        return configuration

    def _require_manifest(self, *, execution_id: str) -> ExperimentalReplicationExecutionManifest:
        manifest = self._manifest_service.get(execution_id=execution_id)
        if manifest is None:
            raise ExperimentalConditionReplicationIntegrityError(
                "Un manifeste 3P persistant est requis."
            )
        return manifest

    def _require_binding(self, *, execution_id: str) -> ExperimentalExecutionPlanBinding:
        binding = self._binding_service.get(execution_id=execution_id)
        if binding is None:
            raise ExperimentalConditionReplicationIntegrityError(
                "Un binding 3N persistant est requis."
            )
        return binding

    def _require_provenance(
        self, *, execution_id: str
    ) -> ExperimentalExecutionGenerationProvenance:
        provenance = self._provenance_service.get(execution_id=execution_id)
        if provenance is None:
            raise ExperimentalConditionReplicationIntegrityError(
                "Une provenance 3O persistante est requise."
            )
        return provenance

    @staticmethod
    def _validate_artifact_scopes(
        *,
        execution_id: str,
        configuration: ExperimentalExecutionConditionConfiguration,
        manifest: ExperimentalReplicationExecutionManifest,
        binding: ExperimentalExecutionPlanBinding,
        provenance: ExperimentalExecutionGenerationProvenance,
    ) -> None:
        if (
            configuration.execution_id != execution_id
            or manifest.execution_id != execution_id
            or binding.execution_id != execution_id
            or provenance.execution_id != execution_id
        ):
            raise ExperimentalConditionReplicationIntegrityError(
                "Les artefacts 3N à 3R appartiennent à des exécutions différentes."
            )
        if binding.plan_identity != provenance.generation_provenance.plan_identity:
            raise ExperimentalConditionReplicationIntegrityError(
                "Le binding 3N et la provenance 3O sont incohérents."
            )

    @staticmethod
    def _manifest_agent_id(manifest: ExperimentalReplicationExecutionManifest) -> str:
        agent_ids = {context.start_context.agent_id for context in manifest.cycle_contexts}
        if len(agent_ids) != 1:
            raise ExperimentalConditionReplicationIntegrityError(
                "Le manifeste doit décrire exactement un agent."
            )
        return next(iter(agent_ids))

    @staticmethod
    def _validate_historical_performances(
        *,
        manifest: ExperimentalReplicationExecutionManifest,
        cognitive_state: ExperimentalAgentCognitiveState,
        plan: ExperimentalReplicationPlan,
    ) -> None:
        indices = tuple(
            sorted(performance.sequence_index for performance in cognitive_state.performances)
        )
        if len(indices) > _TOTAL_CYCLES or indices != tuple(range(len(indices))):
            raise ExperimentalConditionReplicationIntegrityError(
                "Les performances historiques doivent former un préfixe causal contigu."
            )
        for performance in cognitive_state.performances:
            context = manifest.cycle_contexts[performance.sequence_index]
            start = context.start_context
            expected = plan.attempt(
                performance_id=start.performance_id,
                agent_id=start.agent_id,
                trial_id=start.trial_id,
                cycle_id=start.cycle_id,
                sequence_index=context.sequence_index,
                observed_at=start.observed_at,
            )
            if performance != expected:
                raise ExperimentalConditionReplicationIntegrityError(
                    "Une performance historique diverge du plan privé reproduit."
                )

    def _read_checkpoint_prefix(
        self, *, execution_id: str
    ) -> tuple[ExperimentalCycleCheckpoint, ...]:
        checkpoints = tuple(
            checkpoint
            for sequence_index in range(_TOTAL_CYCLES)
            if (
                checkpoint := self._checkpoint_service.get(
                    execution_id=execution_id,
                    sequence_index=sequence_index,
                )
            )
            is not None
        )
        indices = tuple(checkpoint.sequence_index for checkpoint in checkpoints)
        if indices != tuple(range(len(indices))):
            raise ExperimentalConditionReplicationIntegrityError(
                "Les checkpoints historiques doivent former un préfixe causal contigu."
            )
        return checkpoints

    @staticmethod
    def _validate_checkpoints(
        *,
        execution_id: str,
        condition: ExperimentalCondition,
        agent_id: str,
        manifest: ExperimentalReplicationExecutionManifest,
        cognitive_state: ExperimentalAgentCognitiveState,
        plan: ExperimentalReplicationPlan,
        checkpoints: tuple[ExperimentalCycleCheckpoint, ...],
    ) -> None:
        expected_source = _DECISION_SOURCE_BY_CONDITION[condition]
        policy = CapabilityDecisionPolicy()
        performances_by_index = {
            performance.sequence_index: performance for performance in cognitive_state.performances
        }
        for position, checkpoint in enumerate(checkpoints):
            context = manifest.cycle_contexts[position]
            start = context.start_context
            if (
                checkpoint.execution_id != execution_id
                or checkpoint.sequence_index != position
                or checkpoint.performance_id != start.performance_id
                or checkpoint.agent_id != agent_id
                or checkpoint.agent_id != start.agent_id
                or checkpoint.trial_id != start.trial_id
                or checkpoint.cycle_id != start.cycle_id
                or checkpoint.observed_at != start.observed_at
                or checkpoint.capability_key != plan.capability_key_for_sequence(position)
            ):
                raise ExperimentalConditionReplicationIntegrityError(
                    "Un checkpoint historique diverge du manifeste ou du plan."
                )
            if checkpoint.decision.estimate.source is not expected_source:
                raise ExperimentalConditionReplicationIntegrityError(
                    "Un checkpoint utilise une source de décision incompatible avec 3R."
                )
            if policy.decide(checkpoint.decision.estimate) != checkpoint.decision:
                raise ExperimentalConditionReplicationIntegrityError(
                    "La décision d'un checkpoint diverge de la politique commune."
                )
            if (
                condition is ExperimentalCondition.A
                and checkpoint.decision.estimate.estimated_success != _FIXED_BASELINE_ESTIMATE
            ):
                raise ExperimentalConditionReplicationIntegrityError(
                    "Un checkpoint A doit conserver l'estimation fixe 0,60."
                )
            has_performance = position in performances_by_index
            if (
                checkpoint.status is ExperimentalCycleCheckpointStatus.COMPLETED
                and not has_performance
            ):
                raise ExperimentalConditionReplicationIntegrityError(
                    "Un checkpoint COMPLETED doit posséder sa performance."
                )
            if (
                checkpoint.status is ExperimentalCycleCheckpointStatus.STARTED
                and position != len(checkpoints) - 1
            ):
                raise ExperimentalConditionReplicationIntegrityError(
                    "Un checkpoint STARTED doit être le dernier du préfixe."
                )
        checkpoint_indices = {checkpoint.sequence_index for checkpoint in checkpoints}
        if any(index not in checkpoint_indices for index in performances_by_index):
            raise ExperimentalConditionReplicationIntegrityError(
                "Toute performance historique doit posséder son checkpoint."
            )
