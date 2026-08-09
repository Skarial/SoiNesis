import inspect
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from soinesis.application.capabilities import (
    CapabilityDecisionPolicy,
    CapabilityPerformanceRecordingService,
)
from soinesis.domain.capabilities import (
    CapabilityDecision,
    CapabilityEstimate,
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
    EstimateSource,
)
from soinesis.experiments.p3 import (
    ExperimentalCondition,
    ExperimentalConditionConfiguration,
    ExperimentalConditionReplicationIntegrityError,
    ExperimentalConditionReplicationRunner,
    ExperimentalConditionReplicationRunResult,
    ExperimentalConditionRuntime,
    ExperimentalConditionRuntimeComposer,
    ExperimentalCycleCheckpoint,
    ExperimentalCycleCheckpointService,
    ExperimentalCycleCheckpointStatus,
    ExperimentalCycleStartContext,
    ExperimentalExecutionConditionConfiguration,
    ExperimentalExecutionConditionConfigurationService,
    ExperimentalExecutionGenerationProvenance,
    ExperimentalExecutionGenerationProvenanceService,
    ExperimentalExecutionPlanBinding,
    ExperimentalExecutionPlanBindingService,
    ExperimentalReplicationCycleContext,
    ExperimentalReplicationExecutionManifest,
    ExperimentalReplicationManifestService,
    ExperimentalReplicationPlan,
    ExperimentalReplicationPlanGenerator,
    ExperimentalReplicationRunner,
    SQLiteExperimentalAgentCognitiveStateInspector,
    SQLiteExperimentalCycleCheckpointRepository,
    SQLiteExperimentalExecutionConditionConfigurationRepository,
    SQLiteExperimentalExecutionGenerationProvenanceRepository,
    SQLiteExperimentalExecutionPlanBindingRepository,
    SQLiteExperimentalReplicationManifestRepository,
)
from soinesis.infrastructure.sqlite import SQLiteCapabilityUnitOfWorkFactory, SQLiteDatabase

START_TIME = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)


@dataclass
class SequentialIdentifiers:
    next_value: int = 1

    def new(self, prefix: str) -> str:
        value = self.next_value
        self.next_value += 1
        return f"{prefix}-{value}"


@dataclass(frozen=True)
class FixedClock:
    value: datetime

    def now(self) -> datetime:
        return self.value


@dataclass(frozen=True)
class Harness:
    path: Path
    database: SQLiteDatabase
    factory: SQLiteCapabilityUnitOfWorkFactory
    inspector: SQLiteExperimentalAgentCognitiveStateInspector
    binding_repository: SQLiteExperimentalExecutionPlanBindingRepository
    provenance_repository: SQLiteExperimentalExecutionGenerationProvenanceRepository
    manifest_repository: SQLiteExperimentalReplicationManifestRepository
    configuration_repository: SQLiteExperimentalExecutionConditionConfigurationRepository
    binding_service: ExperimentalExecutionPlanBindingService
    provenance_service: ExperimentalExecutionGenerationProvenanceService
    manifest_service: ExperimentalReplicationManifestService
    configuration_service: ExperimentalExecutionConditionConfigurationService
    checkpoint_service: ExperimentalCycleCheckpointService
    composer: ExperimentalConditionRuntimeComposer
    generator: ExperimentalReplicationPlanGenerator
    recording_service: CapabilityPerformanceRecordingService

    def condition_runner(
        self,
        *,
        composer: object | None = None,
    ) -> ExperimentalConditionReplicationRunner:
        selected_composer = self.composer if composer is None else composer
        assert hasattr(selected_composer, "compose")
        return ExperimentalConditionReplicationRunner(
            configuration_service=self.configuration_service,
            manifest_service=self.manifest_service,
            binding_service=self.binding_service,
            provenance_service=self.provenance_service,
            plan_generator=self.generator,
            cognitive_state_inspector=self.inspector,
            checkpoint_service=self.checkpoint_service,
            runtime_composer=selected_composer,  # type: ignore[arg-type]
            recording_service=self.recording_service,
        )


def build_harness(path: Path) -> Harness:
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    binding_repository = SQLiteExperimentalExecutionPlanBindingRepository(database)
    provenance_repository = SQLiteExperimentalExecutionGenerationProvenanceRepository(database)
    manifest_repository = SQLiteExperimentalReplicationManifestRepository(database)
    configuration_repository = SQLiteExperimentalExecutionConditionConfigurationRepository(database)
    checkpoint_repository = SQLiteExperimentalCycleCheckpointRepository(database)
    binding_repository.initialize_schema()
    provenance_repository.initialize_schema()
    manifest_repository.initialize_schema()
    configuration_repository.initialize_schema()
    checkpoint_repository.initialize_schema()
    binding_service = ExperimentalExecutionPlanBindingService(binding_repository)
    provenance_service = ExperimentalExecutionGenerationProvenanceService(
        repository=provenance_repository,
        binding_repository=binding_repository,
    )
    manifest_service = ExperimentalReplicationManifestService(
        repository=manifest_repository,
        binding_repository=binding_repository,
        provenance_repository=provenance_repository,
    )
    configuration_service = ExperimentalExecutionConditionConfigurationService(
        repository=configuration_repository,
        binding_repository=binding_repository,
        provenance_repository=provenance_repository,
        manifest_repository=manifest_repository,
    )
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    inspector = SQLiteExperimentalAgentCognitiveStateInspector(database)
    composer = ExperimentalConditionRuntimeComposer(
        configuration_service=configuration_service,
        manifest_service=manifest_service,
        cognitive_state_inspector=inspector,
        unit_of_work_factory=factory,
        revision_clock=FixedClock(START_TIME + timedelta(days=1)),
        identifiers=SequentialIdentifiers(),
    )
    return Harness(
        path=path,
        database=database,
        factory=factory,
        inspector=inspector,
        binding_repository=binding_repository,
        provenance_repository=provenance_repository,
        manifest_repository=manifest_repository,
        configuration_repository=configuration_repository,
        binding_service=binding_service,
        provenance_service=provenance_service,
        manifest_service=manifest_service,
        configuration_service=configuration_service,
        checkpoint_service=ExperimentalCycleCheckpointService(checkpoint_repository),
        composer=composer,
        generator=ExperimentalReplicationPlanGenerator(),
        recording_service=CapabilityPerformanceRecordingService(unit_of_work_factory=factory),
    )


def build_manifest(*, execution_id: str, agent_id: str) -> ExperimentalReplicationExecutionManifest:
    return ExperimentalReplicationExecutionManifest(
        execution_id=execution_id,
        cycle_contexts=tuple(
            ExperimentalReplicationCycleContext(
                sequence_index=index,
                start_context=ExperimentalCycleStartContext(
                    performance_id=f"{execution_id}-performance-{index}",
                    agent_id=agent_id,
                    trial_id=f"{execution_id}-trial-{index}",
                    cycle_id=f"{execution_id}-cycle-{index}",
                    observed_at=START_TIME + timedelta(minutes=index),
                ),
            )
            for index in range(180)
        ),
    )


def prepare_execution(
    harness: Harness,
    *,
    execution_id: str,
    agent_id: str,
    condition: ExperimentalCondition,
    seed: int = 12345,
) -> tuple[ExperimentalReplicationPlan, ExperimentalReplicationExecutionManifest]:
    generated = harness.generator.generate_with_provenance(seed=seed)
    harness.binding_service.bind(
        execution_id=execution_id,
        plan_identity=generated.plan.identity(),
    )
    harness.provenance_service.register(
        execution_id=execution_id,
        generation_provenance=generated.provenance,
    )
    manifest = build_manifest(execution_id=execution_id, agent_id=agent_id)
    harness.manifest_service.register(manifest=manifest)
    harness.configuration_service.register(
        execution_id=execution_id,
        configuration=ExperimentalConditionConfiguration(
            scheme="p3-condition-config-v1",
            condition=condition,
            estimator_lambda=(None if condition is ExperimentalCondition.A else Decimal("0.94")),
        ),
    )
    return generated.plan, manifest


def persist_performance(
    harness: Harness,
    observation: CapabilityPerformanceObservation,
) -> None:
    with harness.factory() as unit_of_work:
        unit_of_work.capability_performances.add(observation)
        unit_of_work.commit()


def checkpoint_decision(
    *,
    agent_id: str,
    capability_key: str,
    source: EstimateSource,
    estimated_success: float = 0.60,
) -> CapabilityDecision:
    return CapabilityDecisionPolicy().decide(
        CapabilityEstimate(
            agent_id=agent_id,
            capability_key=capability_key,
            estimated_success=estimated_success,
            source=source,
        )
    )


def begin_checkpoint(
    harness: Harness,
    *,
    manifest: ExperimentalReplicationExecutionManifest,
    plan: ExperimentalReplicationPlan,
    sequence_index: int,
    source: EstimateSource,
) -> ExperimentalCycleCheckpoint:
    start = manifest.cycle_contexts[sequence_index].start_context
    capability_key = plan.capability_key_for_sequence(sequence_index)
    return harness.checkpoint_service.begin(
        execution_id=manifest.execution_id,
        sequence_index=sequence_index,
        performance_id=start.performance_id,
        agent_id=start.agent_id,
        trial_id=start.trial_id,
        cycle_id=start.cycle_id,
        capability_key=capability_key,
        observed_at=start.observed_at,
        decision=checkpoint_decision(
            agent_id=start.agent_id,
            capability_key=capability_key,
            source=source,
        ),
    )


def test_3t_requires_configuration_before_manifest_without_writing(tmp_path: Path) -> None:
    missing_configuration = build_harness(tmp_path / "missing-configuration.db")
    with pytest.raises(ExperimentalConditionReplicationIntegrityError, match="3R"):
        missing_configuration.condition_runner().run(execution_id="execution-A")

    missing_manifest = build_harness(tmp_path / "missing-manifest.db")
    missing_manifest.configuration_repository.register(
        ExperimentalExecutionConditionConfiguration(
            execution_id="execution-A",
            configuration=ExperimentalConditionConfiguration(
                scheme="p3-condition-config-v1",
                condition=ExperimentalCondition.A,
                estimator_lambda=None,
            ),
        )
    )
    with pytest.raises(ExperimentalConditionReplicationIntegrityError, match="3P"):
        missing_manifest.condition_runner().run(execution_id="execution-A")

    assert not missing_configuration.inspector.inspect(agent_id="agent-A").metacognitive_states
    assert not missing_manifest.inspector.inspect(agent_id="agent-A").metacognitive_states


def test_binding_and_provenance_mismatch_is_rejected_before_c_bootstrap(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "binding-provenance-mismatch.db")
    bound = harness.generator.generate_with_provenance(seed=12345)
    foreign = harness.generator.generate_with_provenance(seed=54321)
    harness.binding_repository.bind(
        ExperimentalExecutionPlanBinding(
            execution_id="execution-C",
            plan_identity=bound.plan.identity(),
        )
    )
    harness.provenance_repository.register(
        ExperimentalExecutionGenerationProvenance(
            execution_id="execution-C",
            generation_provenance=foreign.provenance,
        )
    )
    harness.manifest_repository.register(
        build_manifest(execution_id="execution-C", agent_id="agent-C")
    )
    harness.configuration_repository.register(
        ExperimentalExecutionConditionConfiguration(
            execution_id="execution-C",
            configuration=ExperimentalConditionConfiguration(
                scheme="p3-condition-config-v1",
                condition=ExperimentalCondition.C,
                estimator_lambda=Decimal("0.94"),
            ),
        )
    )

    with pytest.raises(ExperimentalConditionReplicationIntegrityError, match="incohérents"):
        harness.condition_runner().run(execution_id="execution-C")

    state = harness.inspector.inspect(agent_id="agent-C")
    assert not state.metacognitive_states
    assert not state.self_model_versions
    assert not state.capability_self_attributes


def test_a_b_c_run_the_same_world_end_to_end_and_second_run_has_no_effects(
    tmp_path: Path,
) -> None:
    intrinsic_worlds: list[tuple[tuple[str, bool], ...]] = []
    for condition in ExperimentalCondition:
        execution_id = f"execution-{condition.value}"
        agent_id = f"agent-{condition.value}"
        harness = build_harness(tmp_path / f"condition-{condition.value}.db")
        prepare_execution(
            harness,
            execution_id=execution_id,
            agent_id=agent_id,
            condition=condition,
        )
        runner = harness.condition_runner()

        first = runner.run(execution_id=execution_id)
        first_state = harness.inspector.inspect(agent_id=agent_id)
        first_checkpoints = tuple(
            harness.checkpoint_service.get(
                execution_id=execution_id,
                sequence_index=index,
            )
            for index in range(180)
        )
        second = runner.run(execution_id=execution_id)

        assert second == first
        assert harness.inspector.inspect(agent_id=agent_id) == first_state
        assert len(first.replication_result.cycle_results) == 180
        assert all(
            checkpoint is not None
            and checkpoint.status is ExperimentalCycleCheckpointStatus.COMPLETED
            for checkpoint in first_checkpoints
        )
        expected_source = {
            ExperimentalCondition.A: EstimateSource.FIXED_BASELINE,
            ExperimentalCondition.B: EstimateSource.RAW_HISTORY,
            ExperimentalCondition.C: EstimateSource.SELF_ATTRIBUTE,
        }[condition]
        assert all(
            result.checkpoint.decision.estimate.source is expected_source
            for result in first.replication_result.cycle_results
        )
        intrinsic_worlds.append(
            tuple(
                (result.performance.capability_key, result.performance.intrinsic_success)
                for result in first.replication_result.cycle_results
            )
        )
        if condition is ExperimentalCondition.A:
            assert all(
                result.checkpoint.decision.estimate.estimated_success == 0.60
                for result in first.replication_result.cycle_results
            )
        if condition in (ExperimentalCondition.A, ExperimentalCondition.B):
            assert not first_state.metacognitive_states
            assert not first_state.self_model_versions
            assert not first_state.capability_self_attributes
            assert not first_state.capability_journal_events
        else:
            assert {state.capability_key for state in first_state.metacognitive_states} == {
                "ALPHA",
                "BETA",
                "GAMMA",
            }
            assert sum(state.version - 1 for state in first_state.metacognitive_states) == 180

    assert intrinsic_worlds[0] == intrinsic_worlds[1] == intrinsic_worlds[2]
    assert set(ExperimentalConditionReplicationRunResult.model_fields) == {
        "execution_id",
        "condition",
        "agent_id",
        "replication_result",
    }
    with pytest.raises(ValidationError):
        first.condition = ExperimentalCondition.A  # type: ignore[misc]


@pytest.mark.parametrize("changed_field", ("intrinsic_success", "capability_key"))
def test_corrupted_historical_performance_is_rejected_before_c_bootstrap(
    tmp_path: Path,
    changed_field: str,
) -> None:
    harness = build_harness(tmp_path / f"corrupt-{changed_field}.db")
    plan, manifest = prepare_execution(
        harness,
        execution_id="execution-C",
        agent_id="agent-C",
        condition=ExperimentalCondition.C,
    )
    start = manifest.cycle_contexts[0].start_context
    expected = plan.attempt(
        performance_id=start.performance_id,
        agent_id=start.agent_id,
        trial_id=start.trial_id,
        cycle_id=start.cycle_id,
        sequence_index=0,
        observed_at=start.observed_at,
    )
    changed_value: object = (
        not expected.intrinsic_success if changed_field == "intrinsic_success" else "OTHER"
    )
    persist_performance(harness, expected.model_copy(update={changed_field: changed_value}))

    with pytest.raises(ExperimentalConditionReplicationIntegrityError, match="plan privé"):
        harness.condition_runner().run(execution_id="execution-C")

    state = harness.inspector.inspect(agent_id="agent-C")
    assert len(state.performances) == 1
    assert not state.metacognitive_states
    assert not state.self_model_versions
    assert not state.capability_self_attributes
    assert not state.capability_journal_events
    assert harness.checkpoint_service.get(execution_id="execution-C", sequence_index=0) is None


def test_checkpoint_with_wrong_condition_source_is_rejected_before_c_bootstrap(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "wrong-source.db")
    plan, manifest = prepare_execution(
        harness,
        execution_id="execution-C",
        agent_id="agent-C",
        condition=ExperimentalCondition.C,
    )
    original = begin_checkpoint(
        harness,
        manifest=manifest,
        plan=plan,
        sequence_index=0,
        source=EstimateSource.RAW_HISTORY,
    )

    with pytest.raises(ExperimentalConditionReplicationIntegrityError, match="source"):
        harness.condition_runner().run(execution_id="execution-C")

    assert harness.checkpoint_service.get(execution_id="execution-C", sequence_index=0) == original
    state = harness.inspector.inspect(agent_id="agent-C")
    assert not state.metacognitive_states
    assert not state.self_model_versions
    assert not state.capability_self_attributes


def test_completed_checkpoint_without_performance_and_performance_without_checkpoint_are_refused(
    tmp_path: Path,
) -> None:
    completed = build_harness(tmp_path / "completed-without-performance.db")
    completed_plan, completed_manifest = prepare_execution(
        completed,
        execution_id="execution-A",
        agent_id="agent-A",
        condition=ExperimentalCondition.A,
    )
    begin_checkpoint(
        completed,
        manifest=completed_manifest,
        plan=completed_plan,
        sequence_index=0,
        source=EstimateSource.FIXED_BASELINE,
    )
    completed.checkpoint_service.complete(execution_id="execution-A", sequence_index=0)
    with pytest.raises(ExperimentalConditionReplicationIntegrityError, match="COMPLETED"):
        completed.condition_runner().run(execution_id="execution-A")

    orphan = build_harness(tmp_path / "performance-without-checkpoint.db")
    orphan_plan, orphan_manifest = prepare_execution(
        orphan,
        execution_id="execution-A",
        agent_id="agent-A",
        condition=ExperimentalCondition.A,
    )
    start = orphan_manifest.cycle_contexts[0].start_context
    persist_performance(
        orphan,
        orphan_plan.attempt(
            performance_id=start.performance_id,
            agent_id=start.agent_id,
            trial_id=start.trial_id,
            cycle_id=start.cycle_id,
            sequence_index=0,
            observed_at=start.observed_at,
        ),
    )
    with pytest.raises(ExperimentalConditionReplicationIntegrityError, match="checkpoint"):
        orphan.condition_runner().run(execution_id="execution-A")


class SimulatedPostFailure(RuntimeError):
    pass


class FailAtPerformancePostProcessor:
    def __init__(self, *, performance_id: str) -> None:
        self._performance_id = performance_id

    def process(self, *, performance_id: str) -> object:
        if performance_id == self._performance_id:
            raise SimulatedPostFailure(performance_id)
        return None


class DecisionProbe:
    def __init__(self, delegate: object) -> None:
        self._delegate = delegate
        self.boundaries: list[CapabilityHistoryBoundary] = []

    def decide(self, *, boundary: CapabilityHistoryBoundary) -> CapabilityDecision:
        self.boundaries.append(boundary)
        return self._delegate.decide(boundary=boundary)  # type: ignore[union-attr]


class RuntimeComposerProbe:
    def __init__(self, delegate: ExperimentalConditionRuntimeComposer) -> None:
        self._delegate = delegate
        self.decision_probe: DecisionProbe | None = None

    def compose(self, *, execution_id: str) -> ExperimentalConditionRuntime:
        runtime = self._delegate.compose(execution_id=execution_id)
        self.decision_probe = DecisionProbe(runtime.decision_service)
        return replace(runtime, decision_service=self.decision_probe)


def test_started_cycle_73_is_resumed_by_3q_without_redecision(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "resume-started.db")
    prepare_execution(
        harness,
        execution_id="execution-A",
        agent_id="agent-A",
        condition=ExperimentalCondition.A,
    )
    runtime = harness.composer.compose(execution_id="execution-A")
    failing_runner = ExperimentalReplicationRunner(
        manifest_service=harness.manifest_service,
        binding_service=harness.binding_service,
        provenance_service=harness.provenance_service,
        plan_generator=harness.generator,
        checkpoint_service=harness.checkpoint_service,
        decision_service=runtime.decision_service,
        recording_service=harness.recording_service,
        post_performance_processor=FailAtPerformancePostProcessor(
            performance_id="execution-A-performance-73"
        ),
    )
    with pytest.raises(SimulatedPostFailure):
        failing_runner.run(execution_id="execution-A")
    started = harness.checkpoint_service.get(execution_id="execution-A", sequence_index=73)
    assert started is not None
    assert started.status is ExperimentalCycleCheckpointStatus.STARTED

    composer_probe = RuntimeComposerProbe(harness.composer)
    result = harness.condition_runner(composer=composer_probe).run(execution_id="execution-A")

    assert composer_probe.decision_probe is not None
    assert [
        boundary.sequence_index for boundary in composer_probe.decision_probe.boundaries
    ] == list(range(74, 180))
    completed = result.replication_result.cycle_results[73].checkpoint
    assert completed.status is ExperimentalCycleCheckpointStatus.COMPLETED
    assert (
        completed.model_copy(update={"status": ExperimentalCycleCheckpointStatus.STARTED})
        == started
    )
    assert len(result.replication_result.cycle_results) == 180


def test_public_api_and_source_keep_3t_single_execution_without_metrics_or_ablation() -> None:
    assert list(inspect.signature(ExperimentalConditionReplicationRunner.run).parameters) == [
        "self",
        "execution_id",
    ]
    source = Path("src/soinesis/experiments/p3/condition_replication.py").read_text(
        encoding="utf-8"
    )
    assert ".generate(" not in source
    assert ".generate_with_provenance(" not in source
    assert "ExperimentalReplicationRunner(" in source
    assert "cycle_runner.run" not in source
    for forbidden in (
        "SELF-ABL",
        "META-ABL",
        "MAE",
        "Brier",
        "regret",
        "campaign",
        "OFFICIAL",
        "VALIDATION",
    ):
        assert forbidden not in source
