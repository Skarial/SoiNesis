from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from soinesis.application.capabilities import (
    CapabilitySelfModelInitializationService,
    DecayedBetaEstimator,
    MetacognitiveCapabilityUpdateService,
)
from soinesis.domain.capabilities import (
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
    EstimateSource,
)
from soinesis.domain.models import EventType, SourceType
from soinesis.experiments.p3 import (
    ExperimentalCondition,
    ExperimentalConditionConfiguration,
    ExperimentalConditionRuntimeComposer,
    ExperimentalConditionRuntimeIntegrityError,
    ExperimentalCycleStartContext,
    ExperimentalExecutionConditionConfiguration,
    ExperimentalExecutionConditionConfigurationService,
    ExperimentalExecutionGenerationProvenanceService,
    ExperimentalExecutionPlanBindingService,
    ExperimentalReplicationCycleContext,
    ExperimentalReplicationExecutionManifest,
    ExperimentalReplicationManifestService,
    ExperimentalReplicationPlanGenerator,
    SQLiteExperimentalAgentCognitiveStateInspector,
    SQLiteExperimentalExecutionConditionConfigurationRepository,
    SQLiteExperimentalExecutionGenerationProvenanceRepository,
    SQLiteExperimentalExecutionPlanBindingRepository,
    SQLiteExperimentalReplicationManifestRepository,
)
from soinesis.infrastructure.sqlite.capabilities import (
    SQLiteCapabilityUnitOfWorkFactory,
)
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

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
class RuntimeHarness:
    path: Path
    database: SQLiteDatabase
    factory: SQLiteCapabilityUnitOfWorkFactory
    inspector: SQLiteExperimentalAgentCognitiveStateInspector
    configuration_repository: SQLiteExperimentalExecutionConditionConfigurationRepository
    manifest_repository: SQLiteExperimentalReplicationManifestRepository
    binding_service: ExperimentalExecutionPlanBindingService
    provenance_service: ExperimentalExecutionGenerationProvenanceService
    manifest_service: ExperimentalReplicationManifestService
    configuration_service: ExperimentalExecutionConditionConfigurationService
    composer: ExperimentalConditionRuntimeComposer
    identifiers: SequentialIdentifiers


def build_harness(
    path: Path,
    *,
    identifiers: SequentialIdentifiers | None = None,
) -> RuntimeHarness:
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    binding_repository = SQLiteExperimentalExecutionPlanBindingRepository(database)
    provenance_repository = SQLiteExperimentalExecutionGenerationProvenanceRepository(database)
    manifest_repository = SQLiteExperimentalReplicationManifestRepository(database)
    configuration_repository = SQLiteExperimentalExecutionConditionConfigurationRepository(database)
    binding_repository.initialize_schema()
    provenance_repository.initialize_schema()
    manifest_repository.initialize_schema()
    configuration_repository.initialize_schema()
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
    selected_identifiers = identifiers or SequentialIdentifiers()
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    inspector = SQLiteExperimentalAgentCognitiveStateInspector(database)
    composer = ExperimentalConditionRuntimeComposer(
        configuration_service=configuration_service,
        manifest_service=manifest_service,
        cognitive_state_inspector=inspector,
        unit_of_work_factory=factory,
        revision_clock=FixedClock(START_TIME + timedelta(days=1)),
        identifiers=selected_identifiers,
    )
    return RuntimeHarness(
        path=path,
        database=database,
        factory=factory,
        inspector=inspector,
        configuration_repository=configuration_repository,
        manifest_repository=manifest_repository,
        binding_service=binding_service,
        provenance_service=provenance_service,
        manifest_service=manifest_service,
        configuration_service=configuration_service,
        composer=composer,
        identifiers=selected_identifiers,
    )


def build_manifest(
    *,
    execution_id: str,
    agent_id: str,
) -> ExperimentalReplicationExecutionManifest:
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
    harness: RuntimeHarness,
    *,
    execution_id: str,
    agent_id: str,
    condition: ExperimentalCondition,
    estimator_lambda: str | None,
) -> ExperimentalReplicationExecutionManifest:
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)
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
            estimator_lambda=(None if estimator_lambda is None else Decimal(estimator_lambda)),
        ),
    )
    return manifest


def persist_manifest_performance(
    harness: RuntimeHarness,
    manifest: ExperimentalReplicationExecutionManifest,
    *,
    sequence_index: int,
    capability_key: str,
    intrinsic_success: bool,
    changed_cycle_id: str | None = None,
) -> CapabilityPerformanceObservation:
    context = manifest.cycle_contexts[sequence_index]
    start = context.start_context
    performance = CapabilityPerformanceObservation(
        id=start.performance_id,
        agent_id=start.agent_id,
        trial_id=start.trial_id,
        cycle_id=changed_cycle_id or start.cycle_id,
        sequence_index=sequence_index,
        capability_key=capability_key,
        intrinsic_success=intrinsic_success,
        observed_at=start.observed_at,
        source_type=SourceType.DIRECT_ENVIRONMENT,
    )
    with harness.factory() as unit_of_work:
        unit_of_work.capability_performances.add(performance)
        unit_of_work.commit()
    return performance


def boundary(
    manifest: ExperimentalReplicationExecutionManifest,
    *,
    sequence_index: int,
    capability_key: str = "ALPHA",
) -> CapabilityHistoryBoundary:
    start = manifest.cycle_contexts[sequence_index].start_context
    return CapabilityHistoryBoundary(
        agent_id=start.agent_id,
        capability_key=capability_key,
        trial_id=start.trial_id,
        cycle_id=start.cycle_id,
        sequence_index=sequence_index,
    )


def initialize_capabilities(
    harness: RuntimeHarness,
    *,
    agent_id: str,
    capability_keys: tuple[str, ...],
    lambda_: float = 0.94,
) -> None:
    initializer = CapabilitySelfModelInitializationService(
        unit_of_work_factory=harness.factory,
        estimator=DecayedBetaEstimator(lambda_=lambda_),
        clock=FixedClock(START_TIME),
        identifiers=harness.identifiers,
    )
    for capability_key in capability_keys:
        initializer.initialize(agent_id=agent_id, capability_key=capability_key)


def test_compose_requires_stored_3r_then_stored_3p(tmp_path: Path) -> None:
    missing_configuration = build_harness(tmp_path / "missing-configuration.db")
    with pytest.raises(ExperimentalConditionRuntimeIntegrityError, match="3R"):
        missing_configuration.composer.compose(execution_id="execution-1")

    missing_manifest = build_harness(tmp_path / "missing-manifest.db")
    missing_manifest.configuration_repository.register(
        ExperimentalExecutionConditionConfiguration(
            execution_id="execution-1",
            configuration=ExperimentalConditionConfiguration(
                scheme="p3-condition-config-v1",
                condition=ExperimentalCondition.A,
                estimator_lambda=None,
            ),
        )
    )
    with pytest.raises(ExperimentalConditionRuntimeIntegrityError, match="3P"):
        missing_manifest.composer.compose(execution_id="execution-1")


def test_a_uses_only_fixed_baseline_and_tolerates_matching_raw_history(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "condition-a.db")
    manifest = prepare_execution(
        harness,
        execution_id="execution-a",
        agent_id="agent-A",
        condition=ExperimentalCondition.A,
        estimator_lambda=None,
    )
    persist_manifest_performance(
        harness,
        manifest,
        sequence_index=0,
        capability_key="ALPHA",
        intrinsic_success=False,
    )

    runtime = harness.composer.compose(execution_id="execution-a")
    decision = runtime.decision_service.decide(boundary=boundary(manifest, sequence_index=1))
    state = harness.inspector.inspect(agent_id="agent-A")

    assert runtime.condition is ExperimentalCondition.A
    assert runtime.agent_id == "agent-A"
    assert runtime.post_performance_processor is None
    assert decision.estimate.source is EstimateSource.FIXED_BASELINE
    assert decision.estimate.estimated_success == 0.60
    assert state.performances
    assert not state.metacognitive_states
    assert not state.self_model_versions
    assert not state.capability_self_attributes
    assert not state.capability_journal_events


def test_b_replays_matching_history_with_the_exact_lambda_of_each_execution(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "condition-b.db")
    manifests = {
        "execution-b94": prepare_execution(
            harness,
            execution_id="execution-b94",
            agent_id="agent-B94",
            condition=ExperimentalCondition.B,
            estimator_lambda="0.94",
        ),
        "execution-b97": prepare_execution(
            harness,
            execution_id="execution-b97",
            agent_id="agent-B97",
            condition=ExperimentalCondition.B,
            estimator_lambda="0.97",
        ),
    }
    for manifest in manifests.values():
        persist_manifest_performance(
            harness,
            manifest,
            sequence_index=0,
            capability_key="ALPHA",
            intrinsic_success=True,
        )
        persist_manifest_performance(
            harness,
            manifest,
            sequence_index=1,
            capability_key="ALPHA",
            intrinsic_success=False,
        )

    decisions = {
        execution_id: harness.composer.compose(execution_id=execution_id).decision_service.decide(
            boundary=boundary(manifest, sequence_index=2)
        )
        for execution_id, manifest in manifests.items()
    }

    for execution_id, lambda_ in (("execution-b94", 0.94), ("execution-b97", 0.97)):
        decision = decisions[execution_id]
        expected = DecayedBetaEstimator(lambda_=lambda_).replay((True, False))
        state = harness.inspector.inspect(
            agent_id=manifests[execution_id].cycle_contexts[0].start_context.agent_id
        )
        assert decision.estimate.source is EstimateSource.RAW_HISTORY
        assert decision.estimate.estimated_success == expected.estimated_success
        assert not state.metacognitive_states
        assert not state.self_model_versions
        assert not state.capability_self_attributes
    assert (
        decisions["execution-b94"].estimate.estimated_success
        != decisions["execution-b97"].estimate.estimated_success
    )


@pytest.mark.parametrize(
    ("condition", "indices"),
    (
        (ExperimentalCondition.A, (73,)),
        (ExperimentalCondition.B, (0, 2)),
    ),
)
def test_a_and_b_reject_sparse_performance_histories(
    tmp_path: Path,
    condition: ExperimentalCondition,
    indices: tuple[int, ...],
) -> None:
    harness = build_harness(tmp_path / f"sparse-{condition.value}.db")
    manifest = prepare_execution(
        harness,
        execution_id="execution-1",
        agent_id="agent-1",
        condition=condition,
        estimator_lambda=None if condition is ExperimentalCondition.A else "0.94",
    )
    for index in indices:
        persist_manifest_performance(
            harness,
            manifest,
            sequence_index=index,
            capability_key="ALPHA",
            intrinsic_success=True,
        )

    with pytest.raises(ExperimentalConditionRuntimeIntegrityError, match="préfixe causal"):
        harness.composer.compose(execution_id="execution-1")


def test_b_accepts_the_contiguous_zero_one_prefix_for_raw_history(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "contiguous-b.db")
    manifest = prepare_execution(
        harness,
        execution_id="execution-b",
        agent_id="agent-B",
        condition=ExperimentalCondition.B,
        estimator_lambda="0.94",
    )
    for index, success in enumerate((True, False)):
        persist_manifest_performance(
            harness,
            manifest,
            sequence_index=index,
            capability_key="ALPHA",
            intrinsic_success=success,
        )

    runtime = harness.composer.compose(execution_id="execution-b")
    decision = runtime.decision_service.decide(boundary=boundary(manifest, sequence_index=2))

    assert decision.estimate.source is EstimateSource.RAW_HISTORY
    assert (
        decision.estimate.estimated_success
        == DecayedBetaEstimator(lambda_=0.94).replay((True, False)).estimated_success
    )


@pytest.mark.parametrize("condition", (ExperimentalCondition.A, ExperimentalCondition.B))
def test_a_and_b_reject_preexisting_self_state(
    tmp_path: Path,
    condition: ExperimentalCondition,
) -> None:
    harness = build_harness(tmp_path / f"contaminated-{condition.value}.db")
    prepare_execution(
        harness,
        execution_id="execution-1",
        agent_id="agent-1",
        condition=condition,
        estimator_lambda=None if condition is ExperimentalCondition.A else "0.94",
    )
    initialize_capabilities(harness, agent_id="agent-1", capability_keys=("ALPHA",))

    with pytest.raises(ExperimentalConditionRuntimeIntegrityError, match="A ou B"):
        harness.composer.compose(execution_id="execution-1")


def test_c_bootstraps_all_capabilities_at_manifest_time_and_is_idempotent_after_reopen(
    tmp_path: Path,
) -> None:
    path = tmp_path / "condition-c.db"
    harness = build_harness(path)
    manifest = prepare_execution(
        harness,
        execution_id="execution-c",
        agent_id="agent-C",
        condition=ExperimentalCondition.C,
        estimator_lambda="0.94",
    )

    first_runtime = harness.composer.compose(execution_id="execution-c")
    first_state = harness.inspector.inspect(agent_id="agent-C")
    initial_decision = first_runtime.decision_service.decide(
        boundary=boundary(manifest, sequence_index=0)
    )
    reopened = build_harness(path, identifiers=harness.identifiers)
    second_runtime = reopened.composer.compose(execution_id="execution-c")
    second_state = reopened.inspector.inspect(agent_id="agent-C")
    repeated_decision = second_runtime.decision_service.decide(
        boundary=boundary(manifest, sequence_index=0)
    )

    assert first_runtime.post_performance_processor is not None
    assert len(first_state.metacognitive_states) == 3
    assert len(first_state.self_model_versions) == 3
    assert len(first_state.capability_self_attributes) == 3
    assert len(first_state.capability_journal_events) == 3
    assert not first_state.performances
    assert {state.capability_key for state in first_state.metacognitive_states} == {
        "ALPHA",
        "BETA",
        "GAMMA",
    }
    assert all(state.version == 1 for state in first_state.metacognitive_states)
    assert all(state.state.lambda_ == 0.94 for state in first_state.metacognitive_states)
    assert all(
        attribute.attribute_version == 1
        and attribute.estimated_success == 0.60
        and attribute.created_at == START_TIME
        for attribute in first_state.capability_self_attributes
    )
    assert all(
        event.event_type is EventType.CAPABILITY_SELF_ATTRIBUTE_INITIALIZED
        for event in first_state.capability_journal_events
    )
    assert initial_decision.estimate.source is EstimateSource.SELF_ATTRIBUTE
    assert initial_decision.estimate.estimated_success == 0.60
    assert repeated_decision.estimate.source is EstimateSource.SELF_ATTRIBUTE
    assert second_state == first_state


def test_c_resumes_a_valid_partial_bootstrap_without_duplication(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "partial-c.db")
    prepare_execution(
        harness,
        execution_id="execution-c",
        agent_id="agent-C",
        condition=ExperimentalCondition.C,
        estimator_lambda="0.94",
    )
    initialize_capabilities(harness, agent_id="agent-C", capability_keys=("ALPHA",))
    before = harness.inspector.inspect(agent_id="agent-C")

    harness.composer.compose(execution_id="execution-c")

    after = harness.inspector.inspect(agent_id="agent-C")
    assert before.capability_self_attributes[0] in after.capability_self_attributes
    assert len(after.metacognitive_states) == 3
    assert len(after.self_model_versions) == 3
    assert len(after.capability_self_attributes) == 3
    assert len(after.capability_journal_events) == 3


def test_c_refuses_late_bootstrap_after_a_manifest_performance(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "late-c.db")
    manifest = prepare_execution(
        harness,
        execution_id="execution-c",
        agent_id="agent-C",
        condition=ExperimentalCondition.C,
        estimator_lambda="0.94",
    )
    initialize_capabilities(
        harness,
        agent_id="agent-C",
        capability_keys=("ALPHA", "BETA"),
    )
    persist_manifest_performance(
        harness,
        manifest,
        sequence_index=0,
        capability_key="ALPHA",
        intrinsic_success=True,
    )
    before = harness.inspector.inspect(agent_id="agent-C")

    with pytest.raises(ExperimentalConditionRuntimeIntegrityError, match="trois capacités"):
        harness.composer.compose(execution_id="execution-c")

    assert harness.inspector.inspect(agent_id="agent-C") == before


def test_c_rejects_a_sparse_prefix_before_creating_any_bootstrap(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "sparse-c.db")
    manifest = prepare_execution(
        harness,
        execution_id="execution-c",
        agent_id="agent-C",
        condition=ExperimentalCondition.C,
        estimator_lambda="0.94",
    )
    for index in (*range(73), 74):
        persist_manifest_performance(
            harness,
            manifest,
            sequence_index=index,
            capability_key="ALPHA",
            intrinsic_success=True,
        )
    before = harness.inspector.inspect(agent_id="agent-C")

    with pytest.raises(ExperimentalConditionRuntimeIntegrityError, match="préfixe causal"):
        harness.composer.compose(execution_id="execution-c")

    after = harness.inspector.inspect(agent_id="agent-C")
    assert after == before
    assert not after.metacognitive_states
    assert not after.self_model_versions
    assert not after.capability_self_attributes
    assert not after.capability_journal_events


def test_c_rejects_an_unknown_capability_or_wrong_lambda_before_writing(
    tmp_path: Path,
) -> None:
    unknown = build_harness(tmp_path / "unknown-capability.db")
    prepare_execution(
        unknown,
        execution_id="execution-c",
        agent_id="agent-C",
        condition=ExperimentalCondition.C,
        estimator_lambda="0.94",
    )
    initialize_capabilities(unknown, agent_id="agent-C", capability_keys=("OTHER",))
    unknown_before = unknown.inspector.inspect(agent_id="agent-C")
    with pytest.raises(ExperimentalConditionRuntimeIntegrityError, match="étrangère"):
        unknown.composer.compose(execution_id="execution-c")
    assert unknown.inspector.inspect(agent_id="agent-C") == unknown_before

    wrong_lambda = build_harness(tmp_path / "wrong-lambda.db")
    prepare_execution(
        wrong_lambda,
        execution_id="execution-c",
        agent_id="agent-C",
        condition=ExperimentalCondition.C,
        estimator_lambda="0.97",
    )
    initialize_capabilities(
        wrong_lambda,
        agent_id="agent-C",
        capability_keys=("ALPHA", "BETA", "GAMMA"),
        lambda_=0.94,
    )
    wrong_before = wrong_lambda.inspector.inspect(agent_id="agent-C")
    with pytest.raises(ExperimentalConditionRuntimeIntegrityError, match="lambda"):
        wrong_lambda.composer.compose(execution_id="execution-c")
    assert wrong_lambda.inspector.inspect(agent_id="agent-C") == wrong_before


def test_compose_rejects_a_performance_whose_public_context_diverges(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "foreign-performance.db")
    manifest = prepare_execution(
        harness,
        execution_id="execution-a",
        agent_id="agent-A",
        condition=ExperimentalCondition.A,
        estimator_lambda=None,
    )
    persist_manifest_performance(
        harness,
        manifest,
        sequence_index=0,
        capability_key="ALPHA",
        intrinsic_success=True,
        changed_cycle_id="foreign-cycle",
    )

    with pytest.raises(ExperimentalConditionRuntimeIntegrityError, match="diverge"):
        harness.composer.compose(execution_id="execution-a")


def test_c_post_processor_updates_only_intrinsic_metacognition(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "post-c.db")
    manifest = prepare_execution(
        harness,
        execution_id="execution-c",
        agent_id="agent-C",
        condition=ExperimentalCondition.C,
        estimator_lambda="0.94",
    )
    runtime = harness.composer.compose(execution_id="execution-c")
    performance = persist_manifest_performance(
        harness,
        manifest,
        sequence_index=0,
        capability_key="ALPHA",
        intrinsic_success=True,
    )
    assert runtime.post_performance_processor is not None

    runtime.post_performance_processor.process(performance_id=performance.id)

    state = harness.inspector.inspect(agent_id="agent-C")
    alpha = next(meta for meta in state.metacognitive_states if meta.capability_key == "ALPHA")
    assert alpha.version == 2
    assert alpha.last_processed_performance_id == performance.id
    assert alpha.state.alpha == 4.0
    assert alpha.state.beta == 2.0

    resumed_runtime = harness.composer.compose(execution_id="execution-c")
    resumed_decision = resumed_runtime.decision_service.decide(
        boundary=boundary(manifest, sequence_index=1)
    )
    assert resumed_runtime.post_performance_processor is not None
    assert resumed_decision.estimate.source is EstimateSource.SELF_ATTRIBUTE


def test_c_compose_accepts_c1_c2_c3_resume_states_without_cognitive_writes(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "c-resume-states.db")
    manifest = prepare_execution(
        harness,
        execution_id="execution-c",
        agent_id="agent-C",
        condition=ExperimentalCondition.C,
        estimator_lambda="0.94",
    )
    initial_runtime = harness.composer.compose(execution_id="execution-c")
    first_performance = persist_manifest_performance(
        harness,
        manifest,
        sequence_index=0,
        capability_key="ALPHA",
        intrinsic_success=False,
    )
    assert initial_runtime.post_performance_processor is not None
    initial_runtime.post_performance_processor.process(performance_id=first_performance.id)
    performance = persist_manifest_performance(
        harness,
        manifest,
        sequence_index=1,
        capability_key="ALPHA",
        intrinsic_success=False,
    )

    c1_before = harness.inspector.inspect(agent_id="agent-C")
    c1_runtime = harness.composer.compose(execution_id="execution-c")
    assert harness.inspector.inspect(agent_id="agent-C") == c1_before
    assert c1_runtime.post_performance_processor is not None
    alpha_c1 = next(
        state for state in c1_before.metacognitive_states if state.capability_key == "ALPHA"
    )
    assert alpha_c1.version == 2
    assert alpha_c1.last_processed_performance_id == first_performance.id

    MetacognitiveCapabilityUpdateService(
        unit_of_work_factory=harness.factory,
        estimator=DecayedBetaEstimator(lambda_=0.94),
    ).process(performance_id=performance.id)
    c2_before = harness.inspector.inspect(agent_id="agent-C")
    c2_runtime = harness.composer.compose(execution_id="execution-c")
    assert harness.inspector.inspect(agent_id="agent-C") == c2_before
    assert c2_runtime.post_performance_processor is not None
    alpha_c2 = next(
        state for state in c2_before.metacognitive_states if state.capability_key == "ALPHA"
    )
    assert alpha_c2.version == 3
    assert alpha_c2.last_processed_performance_id == performance.id
    assert len(c2_before.capability_self_attributes) == 3

    initial_runtime.post_performance_processor.process(performance_id=performance.id)
    c3_before = harness.inspector.inspect(agent_id="agent-C")
    c3_runtime = harness.composer.compose(execution_id="execution-c")
    assert harness.inspector.inspect(agent_id="agent-C") == c3_before
    assert c3_runtime.post_performance_processor is not None
    alpha_c3 = next(
        state for state in c3_before.metacognitive_states if state.capability_key == "ALPHA"
    )
    assert alpha_c3.version == 3
    assert alpha_c3.last_processed_performance_id == performance.id
    assert len(c3_before.capability_self_attributes) == 4
    assert len(c3_before.self_model_versions) == 4
    assert len(c3_before.capability_journal_events) == 4


def test_c_rejects_incomparable_manifest_timestamps_before_bootstrap(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "incomparable-time.db")
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)
    harness.binding_service.bind(
        execution_id="execution-c",
        plan_identity=generated.plan.identity(),
    )
    harness.provenance_service.register(
        execution_id="execution-c",
        generation_provenance=generated.provenance,
    )
    contexts = list(build_manifest(execution_id="execution-c", agent_id="agent-C").cycle_contexts)
    start = contexts[73].start_context
    contexts[73] = contexts[73].model_copy(
        update={
            "start_context": start.model_copy(
                update={"observed_at": start.observed_at.replace(tzinfo=None)}
            )
        }
    )
    manifest = ExperimentalReplicationExecutionManifest(
        execution_id="execution-c",
        cycle_contexts=tuple(contexts),
    )
    harness.manifest_service.register(manifest=manifest)
    harness.configuration_service.register(
        execution_id="execution-c",
        configuration=ExperimentalConditionConfiguration(
            scheme="p3-condition-config-v1",
            condition=ExperimentalCondition.C,
            estimator_lambda=Decimal("0.94"),
        ),
    )

    with pytest.raises(ExperimentalConditionRuntimeIntegrityError, match="comparables"):
        harness.composer.compose(execution_id="execution-c")

    assert not harness.inspector.inspect(agent_id="agent-C").metacognitive_states
