import inspect
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from soinesis.application.capabilities import CapabilityPerformanceRecordingService
from soinesis.domain.capabilities import EstimateSource
from soinesis.experiments.p3 import (
    ExperimentalCondition,
    ExperimentalConditionConfiguration,
    ExperimentalConditionReplicationRunner,
    ExperimentalConditionReplicationRunResult,
    ExperimentalConditionRuntimeComposer,
    ExperimentalCycleCheckpointService,
    ExperimentalCycleRunnerError,
    ExperimentalCycleStartContext,
    ExperimentalExecutionConditionConfigurationService,
    ExperimentalExecutionGenerationProvenanceService,
    ExperimentalExecutionPlanBindingService,
    ExperimentalPairedConditionExecutionIntegrityError,
    ExperimentalPairedConditionExecutionResult,
    ExperimentalPairedConditionExecutionRunner,
    ExperimentalPairedConditionGroup,
    ExperimentalPairedConditionGroupService,
    ExperimentalPairedConditionNotFoundError,
    ExperimentalReplicationCycleContext,
    ExperimentalReplicationExecutionManifest,
    ExperimentalReplicationManifestService,
    ExperimentalReplicationPlanGenerator,
    ExperimentalReplicationPlanIdentity,
    ExperimentalReplicationRunResult,
    SQLiteExperimentalAgentCognitiveStateInspector,
    SQLiteExperimentalCycleCheckpointRepository,
    SQLiteExperimentalExecutionConditionConfigurationRepository,
    SQLiteExperimentalExecutionGenerationProvenanceRepository,
    SQLiteExperimentalExecutionPlanBindingRepository,
    SQLiteExperimentalPairedConditionGroupRepository,
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


class PairingReaderProbe:
    def __init__(self, pairing: ExperimentalPairedConditionGroup | None) -> None:
        self._pairing = pairing
        self.calls: list[str] = []

    def get(self, *, pairing_id: str) -> ExperimentalPairedConditionGroup | None:
        self.calls.append(pairing_id)
        return self._pairing


class ConditionRunnerProbe:
    def __init__(
        self,
        results: dict[str, ExperimentalConditionReplicationRunResult],
        *,
        fail_on: str | None = None,
    ) -> None:
        self._results = results
        self._fail_on = fail_on
        self.calls: list[str] = []

    def run(self, *, execution_id: str) -> ExperimentalConditionReplicationRunResult:
        self.calls.append(execution_id)
        if execution_id == self._fail_on:
            raise ExperimentalCycleRunnerError("interruption simulée")
        return self._results[execution_id]


class FailBeforeExecutionRunner:
    def __init__(
        self,
        delegate: ExperimentalConditionReplicationRunner,
        *,
        fail_on: str,
    ) -> None:
        self._delegate = delegate
        self._fail_on = fail_on
        self.calls: list[str] = []

    def run(self, *, execution_id: str) -> ExperimentalConditionReplicationRunResult:
        self.calls.append(execution_id)
        if execution_id == self._fail_on:
            raise ExperimentalCycleRunnerError("interruption simulée")
        return self._delegate.run(execution_id=execution_id)


def plan_identity(*, fingerprint: str = "a" * 64) -> ExperimentalReplicationPlanIdentity:
    return ExperimentalReplicationPlanIdentity(
        scheme="p3-plan-fingerprint-v1",
        fingerprint=fingerprint,
    )


def pairing() -> ExperimentalPairedConditionGroup:
    return ExperimentalPairedConditionGroup(
        pairing_id="pairing-1",
        execution_a="execution-A",
        execution_b="execution-B",
        execution_c="execution-C",
        plan_identity=plan_identity(),
        estimator_lambda=Decimal("0.94"),
    )


def condition_result(
    *,
    execution_id: str,
    condition: ExperimentalCondition,
    agent_id: str,
    identity: ExperimentalReplicationPlanIdentity | None = None,
    cycle_count: int = 180,
) -> ExperimentalConditionReplicationRunResult:
    replication = ExperimentalReplicationRunResult.model_construct(
        execution_id=execution_id,
        plan_identity=identity or plan_identity(),
        cycle_results=tuple(object() for _ in range(cycle_count)),
    )
    return ExperimentalConditionReplicationRunResult.model_construct(
        execution_id=execution_id,
        condition=condition,
        agent_id=agent_id,
        replication_result=replication,
    )


def probe_results() -> dict[str, ExperimentalConditionReplicationRunResult]:
    return {
        "execution-A": condition_result(
            execution_id="execution-A", condition=ExperimentalCondition.A, agent_id="agent-A"
        ),
        "execution-B": condition_result(
            execution_id="execution-B", condition=ExperimentalCondition.B, agent_id="agent-B"
        ),
        "execution-C": condition_result(
            execution_id="execution-C", condition=ExperimentalCondition.C, agent_id="agent-C"
        ),
    }


def test_runner_reads_pairing_then_calls_3t_exactly_in_a_b_c_order() -> None:
    certified_pairing = pairing()
    pairing_reader = PairingReaderProbe(certified_pairing)
    expected_results = probe_results()
    condition_runner = ConditionRunnerProbe(expected_results)

    result = ExperimentalPairedConditionExecutionRunner(
        pairing_service=pairing_reader,
        condition_runner=condition_runner,
    ).run(pairing_id="pairing-1")

    assert pairing_reader.calls == ["pairing-1"]
    assert condition_runner.calls == ["execution-A", "execution-B", "execution-C"]
    assert result.pairing == certified_pairing
    assert result.result_a == expected_results["execution-A"]
    assert result.result_b == expected_results["execution-B"]
    assert result.result_c == expected_results["execution-C"]
    assert set(ExperimentalPairedConditionExecutionResult.model_fields) == {
        "pairing",
        "result_a",
        "result_b",
        "result_c",
    }
    with pytest.raises(ValidationError):
        result.result_a = result.result_b  # type: ignore[misc]


def test_missing_pairing_fails_before_any_3t_call() -> None:
    pairing_reader = PairingReaderProbe(None)
    condition_runner = ConditionRunnerProbe(probe_results())

    with pytest.raises(ExperimentalPairedConditionNotFoundError, match="pairing 3U"):
        ExperimentalPairedConditionExecutionRunner(
            pairing_service=pairing_reader,
            condition_runner=condition_runner,
        ).run(pairing_id="missing")

    assert pairing_reader.calls == ["missing"]
    assert condition_runner.calls == []


def test_condition_failure_is_propagated_and_no_partial_result_is_returned() -> None:
    condition_runner = ConditionRunnerProbe(probe_results(), fail_on="execution-B")
    runner = ExperimentalPairedConditionExecutionRunner(
        pairing_service=PairingReaderProbe(pairing()),
        condition_runner=condition_runner,
    )

    with pytest.raises(ExperimentalCycleRunnerError, match="interruption simulée"):
        runner.run(pairing_id="pairing-1")

    assert condition_runner.calls == ["execution-A", "execution-B"]


@pytest.mark.parametrize(
    ("corrupted_execution", "expected_calls"),
    (
        ("execution-A", ["execution-A"]),
        ("execution-B", ["execution-A", "execution-B"]),
    ),
)
def test_incoherent_a_or_b_result_fails_before_the_next_condition(
    corrupted_execution: str,
    expected_calls: list[str],
) -> None:
    results = probe_results()
    expected_condition = (
        ExperimentalCondition.B if corrupted_execution == "execution-A" else ExperimentalCondition.C
    )
    results[corrupted_execution] = condition_result(
        execution_id=corrupted_execution,
        condition=expected_condition,
        agent_id=f"agent-{corrupted_execution[-1]}",
    )
    condition_runner = ConditionRunnerProbe(results)

    with pytest.raises(ExperimentalPairedConditionExecutionIntegrityError):
        ExperimentalPairedConditionExecutionRunner(
            pairing_service=PairingReaderProbe(pairing()),
            condition_runner=condition_runner,
        ).run(pairing_id="pairing-1")

    assert condition_runner.calls == expected_calls


@pytest.mark.parametrize(
    "changed_results",
    (
        {
            "result_a": condition_result(
                execution_id="execution-A", condition=ExperimentalCondition.B, agent_id="agent-A"
            )
        },
        {
            "result_a": condition_result(
                execution_id="other", condition=ExperimentalCondition.A, agent_id="agent-A"
            )
        },
        {
            "result_a": condition_result(
                execution_id="execution-A",
                condition=ExperimentalCondition.A,
                agent_id="agent-A",
                identity=plan_identity(fingerprint="b" * 64),
            )
        },
        {
            "result_b": condition_result(
                execution_id="execution-B", condition=ExperimentalCondition.B, agent_id="agent-A"
            )
        },
        {
            "result_c": condition_result(
                execution_id="execution-C",
                condition=ExperimentalCondition.C,
                agent_id="agent-C",
                cycle_count=179,
            )
        },
    ),
)
def test_result_rejects_wrong_role_scope_plan_agent_or_cycle_count(
    changed_results: dict[str, ExperimentalConditionReplicationRunResult],
) -> None:
    results = probe_results() | changed_results
    with pytest.raises(ValidationError):
        ExperimentalPairedConditionExecutionResult(
            pairing=pairing(),
            result_a=results["execution-A"] if "result_a" not in results else results["result_a"],
            result_b=results["execution-B"] if "result_b" not in results else results["result_b"],
            result_c=results["execution-C"] if "result_c" not in results else results["result_c"],
        )


@dataclass(frozen=True)
class EndToEndHarness:
    path: Path
    database: SQLiteDatabase
    factory: SQLiteCapabilityUnitOfWorkFactory
    inspector: SQLiteExperimentalAgentCognitiveStateInspector
    pairing_service: ExperimentalPairedConditionGroupService
    paired_runner: ExperimentalPairedConditionExecutionRunner
    condition_runner: ExperimentalConditionReplicationRunner
    checkpoint_service: ExperimentalCycleCheckpointService
    generator: ExperimentalReplicationPlanGenerator
    binding_service: ExperimentalExecutionPlanBindingService
    provenance_service: ExperimentalExecutionGenerationProvenanceService
    manifest_service: ExperimentalReplicationManifestService
    configuration_service: ExperimentalExecutionConditionConfigurationService


def build_end_to_end_harness(path: Path) -> EndToEndHarness:
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    binding_repository = SQLiteExperimentalExecutionPlanBindingRepository(database)
    provenance_repository = SQLiteExperimentalExecutionGenerationProvenanceRepository(database)
    manifest_repository = SQLiteExperimentalReplicationManifestRepository(database)
    configuration_repository = SQLiteExperimentalExecutionConditionConfigurationRepository(database)
    pairing_repository = SQLiteExperimentalPairedConditionGroupRepository(database)
    checkpoint_repository = SQLiteExperimentalCycleCheckpointRepository(database)
    binding_repository.initialize_schema()
    provenance_repository.initialize_schema()
    manifest_repository.initialize_schema()
    configuration_repository.initialize_schema()
    pairing_repository.initialize_schema()
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
    generator = ExperimentalReplicationPlanGenerator()
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    inspector = SQLiteExperimentalAgentCognitiveStateInspector(database)
    checkpoint_service = ExperimentalCycleCheckpointService(checkpoint_repository)
    composer = ExperimentalConditionRuntimeComposer(
        configuration_service=configuration_service,
        manifest_service=manifest_service,
        cognitive_state_inspector=inspector,
        unit_of_work_factory=factory,
        revision_clock=FixedClock(START_TIME + timedelta(days=1)),
        identifiers=SequentialIdentifiers(),
    )
    recording_service = CapabilityPerformanceRecordingService(unit_of_work_factory=factory)
    condition_runner = ExperimentalConditionReplicationRunner(
        configuration_service=configuration_service,
        manifest_service=manifest_service,
        binding_service=binding_service,
        provenance_service=provenance_service,
        plan_generator=generator,
        cognitive_state_inspector=inspector,
        checkpoint_service=checkpoint_service,
        runtime_composer=composer,
        recording_service=recording_service,
    )
    pairing_service = ExperimentalPairedConditionGroupService(
        repository=pairing_repository,
        configuration_service=configuration_service,
        binding_service=binding_service,
        provenance_service=provenance_service,
        manifest_service=manifest_service,
        plan_generator=generator,
    )
    return EndToEndHarness(
        path=path,
        database=database,
        factory=factory,
        inspector=inspector,
        pairing_service=pairing_service,
        paired_runner=ExperimentalPairedConditionExecutionRunner(
            pairing_service=pairing_service,
            condition_runner=condition_runner,
        ),
        condition_runner=condition_runner,
        checkpoint_service=checkpoint_service,
        generator=generator,
        binding_service=binding_service,
        provenance_service=provenance_service,
        manifest_service=manifest_service,
        configuration_service=configuration_service,
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


def prepare_certified_pairing(harness: EndToEndHarness) -> ExperimentalPairedConditionGroup:
    generated = harness.generator.generate_with_provenance(seed=12345)
    for condition in ExperimentalCondition:
        execution_id = f"execution-{condition.value}"
        harness.binding_service.bind(
            execution_id=execution_id,
            plan_identity=generated.plan.identity(),
        )
        harness.provenance_service.register(
            execution_id=execution_id,
            generation_provenance=generated.provenance,
        )
        harness.manifest_service.register(
            manifest=build_manifest(execution_id=execution_id, agent_id=f"agent-{condition.value}")
        )
        harness.configuration_service.register(
            execution_id=execution_id,
            configuration=ExperimentalConditionConfiguration(
                scheme="p3-condition-config-v1",
                condition=condition,
                estimator_lambda=(
                    None if condition is ExperimentalCondition.A else Decimal("0.94")
                ),
            ),
        )
    return harness.pairing_service.register(
        pairing_id="pairing-1",
        execution_a="execution-A",
        execution_b="execution-B",
        execution_c="execution-C",
    )


def inspect_states(harness: EndToEndHarness) -> tuple[object, object, object]:
    return tuple(harness.inspector.inspect(agent_id=f"agent-{role}") for role in "ABC")  # type: ignore[return-value]


def checkpoint_count(harness: EndToEndHarness, *, execution_id: str) -> int:
    with harness.database.connect() as connection:
        return int(
            connection.execute(
                "SELECT COUNT(*) FROM p3_dev_cycle_checkpoints WHERE execution_id = ?",
                (execution_id,),
            ).fetchone()[0]
        )


def test_real_pairing_runs_resumes_and_remains_idempotent_end_to_end(tmp_path: Path) -> None:
    harness = build_end_to_end_harness(tmp_path / "paired-execution.db")
    certified_pairing = prepare_certified_pairing(harness)
    failing_condition_runner = FailBeforeExecutionRunner(
        harness.condition_runner,
        fail_on="execution-B",
    )
    interrupted_runner = ExperimentalPairedConditionExecutionRunner(
        pairing_service=harness.pairing_service,
        condition_runner=failing_condition_runner,
    )

    with pytest.raises(ExperimentalCycleRunnerError, match="interruption simulée"):
        interrupted_runner.run(pairing_id="pairing-1")
    assert failing_condition_runner.calls == ["execution-A", "execution-B"]
    assert len(harness.inspector.inspect(agent_id="agent-A").performances) == 180
    assert len(harness.inspector.inspect(agent_id="agent-B").performances) == 0
    assert len(harness.inspector.inspect(agent_id="agent-C").performances) == 0

    first = harness.paired_runner.run(pairing_id="pairing-1")
    states_after_first = inspect_states(harness)
    checkpoints_after_first = tuple(
        checkpoint_count(harness, execution_id=f"execution-{role}") for role in "ABC"
    )
    second = harness.paired_runner.run(pairing_id="pairing-1")

    assert first.pairing == certified_pairing
    assert second == first
    assert inspect_states(harness) == states_after_first
    assert checkpoints_after_first == (180, 180, 180)
    assert (
        tuple(checkpoint_count(harness, execution_id=f"execution-{role}") for role in "ABC")
        == checkpoints_after_first
    )
    results = (first.result_a, first.result_b, first.result_c)
    assert all(len(result.replication_result.cycle_results) == 180 for result in results)
    assert all(
        result.replication_result.plan_identity == certified_pairing.plan_identity
        for result in results
    )
    expected_sources = (
        EstimateSource.FIXED_BASELINE,
        EstimateSource.RAW_HISTORY,
        EstimateSource.SELF_ATTRIBUTE,
    )
    assert all(
        all(
            cycle.checkpoint.decision.estimate.source is expected_source
            for cycle in result.replication_result.cycle_results
        )
        for result, expected_source in zip(results, expected_sources, strict=True)
    )
    intrinsic_worlds = tuple(
        tuple(
            (cycle.performance.capability_key, cycle.performance.intrinsic_success)
            for cycle in result.replication_result.cycle_results
        )
        for result in results
    )
    assert intrinsic_worlds[0] == intrinsic_worlds[1] == intrinsic_worlds[2]


def test_3v_source_has_no_cycles_private_plan_cognitive_access_metrics_or_persistence() -> None:
    assert list(inspect.signature(ExperimentalPairedConditionExecutionRunner.run).parameters) == [
        "self",
        "pairing_id",
    ]
    source = Path("src/soinesis/experiments/p3/paired_execution.py").read_text(encoding="utf-8")
    assert source.count("self._condition_runner.run(") == 3
    assert "range(" not in source
    for forbidden in (
        "ExperimentalReplicationPlan",
        "ExperimentalReplicationPlanGenerator",
        "ExperimentalReplicationRunner",
        "ExperimentalCycleRunner",
        "provenance",
        "seed",
        "u_intrinsic",
        "u_correction",
        "true_success_probability",
        "schedule",
        "capability_performances",
        "metacognitive_states",
        "MetaState",
        "SelfModel",
        "SelfAttribute",
        "journal",
        "checkpoint",
        "MAE",
        "Brier",
        "regret",
        "reward",
        "adaptation",
        "SELF-ABL",
        "META-ABL",
        "VALIDATION",
        "OFFICIAL",
    ):
        assert forbidden not in source
