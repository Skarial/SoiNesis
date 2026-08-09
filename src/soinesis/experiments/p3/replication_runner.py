"""Orchestration reprenable d'une réplication P3 DEV complète."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from soinesis.domain.capabilities import (
    CapabilityDecision,
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
)
from soinesis.experiments.p3.checkpoint import (
    ExperimentalCycleCheckpoint,
    ExperimentalCycleCheckpointStatus,
)
from soinesis.experiments.p3.execution_binding import ExperimentalExecutionPlanBinding
from soinesis.experiments.p3.plan import (
    ExperimentalReplicationPlan,
    ExperimentalReplicationPlanIdentity,
)
from soinesis.experiments.p3.provenance import (
    ExperimentalExecutionGenerationProvenance,
    ExperimentalPlanGenerationProvenance,
)
from soinesis.experiments.p3.replication_manifest import (
    ExperimentalReplicationExecutionManifest,
)
from soinesis.experiments.p3.runner import (
    ExperimentalCycleRunner,
    ExperimentalCycleRunResult,
)

_TOTAL_CYCLES = 180


class ExperimentalReplicationRunResult(BaseModel):
    """Résultat déterministe complet reconstruit depuis les checkpoints individuels."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(min_length=1)
    plan_identity: ExperimentalReplicationPlanIdentity
    cycle_results: tuple[ExperimentalCycleRunResult, ...] = Field(
        min_length=_TOTAL_CYCLES,
        max_length=_TOTAL_CYCLES,
    )

    @model_validator(mode="after")
    def validate_complete_replication(self) -> ExperimentalReplicationRunResult:
        checkpoints = tuple(result.checkpoint for result in self.cycle_results)
        if tuple(checkpoint.sequence_index for checkpoint in checkpoints) != tuple(
            range(_TOTAL_CYCLES)
        ):
            raise ValueError("Les résultats doivent suivre exactement les cycles 0 à 179.")
        if any(
            checkpoint.execution_id != self.execution_id
            or checkpoint.status is not ExperimentalCycleCheckpointStatus.COMPLETED
            for checkpoint in checkpoints
        ):
            raise ValueError("Chaque cycle doit être COMPLETED et appartenir à l'exécution.")
        performance_ids = tuple(result.performance.id for result in self.cycle_results)
        if len(set(performance_ids)) != _TOTAL_CYCLES:
            raise ValueError("Chaque résultat doit posséder un performance_id unique.")
        return self


class ExperimentalReplicationRunnerError(RuntimeError):
    """Erreur de base de l'orchestrateur d'une réplication P3 DEV."""


class ExperimentalReplicationRunnerIntegrityError(ExperimentalReplicationRunnerError):
    """Refuser un préflight incomplet ou incohérent avant tout cycle."""


class _ReplicationManifestReader(Protocol):
    def get(self, *, execution_id: str) -> ExperimentalReplicationExecutionManifest | None: ...


class _ExecutionPlanBindingService(Protocol):
    def get(self, *, execution_id: str) -> ExperimentalExecutionPlanBinding | None: ...

    def bind(
        self,
        *,
        execution_id: str,
        plan_identity: ExperimentalReplicationPlanIdentity,
    ) -> ExperimentalExecutionPlanBinding: ...


class _ExecutionGenerationProvenanceReader(Protocol):
    def get(self, *, execution_id: str) -> ExperimentalExecutionGenerationProvenance | None: ...


class _ReplicationPlanReproducer(Protocol):
    def reproduce(
        self, *, provenance: ExperimentalPlanGenerationProvenance
    ) -> ExperimentalReplicationPlan: ...


class _CapabilityDecisionService(Protocol):
    def decide(self, *, boundary: CapabilityHistoryBoundary) -> CapabilityDecision: ...


class _CapabilityPerformanceRecordingService(Protocol):
    def record(self, *, observation: CapabilityPerformanceObservation) -> object: ...


class _PostPerformanceProcessor(Protocol):
    def process(self, *, performance_id: str) -> object: ...


class _ExperimentalCycleCheckpointService(Protocol):
    def get(
        self, *, execution_id: str, sequence_index: int
    ) -> ExperimentalCycleCheckpoint | None: ...

    def begin(
        self,
        *,
        execution_id: str,
        sequence_index: int,
        performance_id: str,
        agent_id: str,
        trial_id: str,
        cycle_id: str,
        capability_key: str,
        observed_at: datetime,
        decision: CapabilityDecision,
    ) -> ExperimentalCycleCheckpoint: ...

    def complete(
        self, *, execution_id: str, sequence_index: int
    ) -> ExperimentalCycleCheckpoint: ...


class ExperimentalReplicationRunner:
    """Reproduire le plan puis déléguer séquentiellement les 180 cycles à 3M."""

    def __init__(
        self,
        *,
        manifest_service: _ReplicationManifestReader,
        binding_service: _ExecutionPlanBindingService,
        provenance_service: _ExecutionGenerationProvenanceReader,
        plan_generator: _ReplicationPlanReproducer,
        checkpoint_service: _ExperimentalCycleCheckpointService,
        decision_service: _CapabilityDecisionService,
        recording_service: _CapabilityPerformanceRecordingService,
        post_performance_processor: _PostPerformanceProcessor | None = None,
    ) -> None:
        self._manifest_service = manifest_service
        self._binding_service = binding_service
        self._provenance_service = provenance_service
        self._plan_generator = plan_generator
        self._checkpoint_service = checkpoint_service
        self._decision_service = decision_service
        self._recording_service = recording_service
        self._post_performance_processor = post_performance_processor

    def run(self, *, execution_id: str) -> ExperimentalReplicationRunResult:
        """Prévalider l'exécution puis parcourir son manifeste sans recalcul de contexte."""
        manifest = self._manifest_service.get(execution_id=execution_id)
        if manifest is None:
            raise ExperimentalReplicationRunnerIntegrityError(
                "Un manifeste 3P persistant est requis avant la réplication."
            )
        binding = self._binding_service.get(execution_id=execution_id)
        if binding is None:
            raise ExperimentalReplicationRunnerIntegrityError(
                "Un binding 3N persistant est requis avant la réplication."
            )
        stored_provenance = self._provenance_service.get(execution_id=execution_id)
        if stored_provenance is None:
            raise ExperimentalReplicationRunnerIntegrityError(
                "Une provenance 3O persistante est requise avant la réplication."
            )
        self._validate_preflight_scope(
            execution_id=execution_id,
            manifest=manifest,
            binding=binding,
            stored_provenance=stored_provenance,
        )
        plan = self._plan_generator.reproduce(provenance=stored_provenance.generation_provenance)
        if plan.identity() != binding.plan_identity:
            raise ExperimentalReplicationRunnerIntegrityError(
                "Le plan reproduit ne correspond pas au binding 3N."
            )

        cycle_runner = ExperimentalCycleRunner(
            plan=plan,
            checkpoint_service=self._checkpoint_service,
            execution_plan_binding_service=self._binding_service,
            decision_service=self._decision_service,
            recording_service=self._recording_service,
            post_performance_processor=self._post_performance_processor,
        )
        cycle_results = tuple(
            cycle_runner.run(
                execution_id=execution_id,
                sequence_index=context.sequence_index,
                start_context=context.start_context,
            )
            for context in manifest.cycle_contexts
        )
        return ExperimentalReplicationRunResult(
            execution_id=execution_id,
            plan_identity=plan.identity(),
            cycle_results=cycle_results,
        )

    @staticmethod
    def _validate_preflight_scope(
        *,
        execution_id: str,
        manifest: ExperimentalReplicationExecutionManifest,
        binding: ExperimentalExecutionPlanBinding,
        stored_provenance: ExperimentalExecutionGenerationProvenance,
    ) -> None:
        if (
            manifest.execution_id != execution_id
            or binding.execution_id != execution_id
            or stored_provenance.execution_id != execution_id
        ):
            raise ExperimentalReplicationRunnerIntegrityError(
                "Les artefacts du préflight appartiennent à une autre exécution."
            )
        if binding.plan_identity != stored_provenance.generation_provenance.plan_identity:
            raise ExperimentalReplicationRunnerIntegrityError(
                "Le binding 3N et la provenance 3O sont incohérents."
            )
