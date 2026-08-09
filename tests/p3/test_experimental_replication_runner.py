import inspect
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from soinesis.application.capabilities import (
    CapabilityDecisionPolicy,
    CapabilityPerformanceRecordingService,
    FixedCapabilityDecisionService,
    FixedCapabilityEstimateProvider,
)
from soinesis.domain.capabilities import (
    CapabilityDecision,
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
)
from soinesis.experiments.p3 import (
    ExperimentalCycleCheckpoint,
    ExperimentalCycleCheckpointService,
    ExperimentalCycleStartContext,
    ExperimentalExecutionGenerationProvenance,
    ExperimentalExecutionGenerationProvenanceService,
    ExperimentalExecutionPlanBindingService,
    ExperimentalPlanGenerationEnvironmentError,
    ExperimentalReplicationCycleContext,
    ExperimentalReplicationExecutionManifest,
    ExperimentalReplicationManifestService,
    ExperimentalReplicationPlanGenerator,
    ExperimentalReplicationRunner,
    ExperimentalReplicationRunnerIntegrityError,
    ExperimentalReplicationRunResult,
    SQLiteExperimentalCycleCheckpointRepository,
    SQLiteExperimentalExecutionGenerationProvenanceRepository,
    SQLiteExperimentalExecutionPlanBindingRepository,
    SQLiteExperimentalReplicationManifestRepository,
)
from soinesis.infrastructure.sqlite import SQLiteCapabilityUnitOfWorkFactory, SQLiteDatabase

OBSERVED_AT = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)


class SimulatedCycleError(RuntimeError):
    pass


def build_manifest(
    *, execution_id: str = "execution-1"
) -> ExperimentalReplicationExecutionManifest:
    return ExperimentalReplicationExecutionManifest(
        execution_id=execution_id,
        cycle_contexts=tuple(
            ExperimentalReplicationCycleContext(
                sequence_index=sequence_index,
                start_context=ExperimentalCycleStartContext(
                    performance_id=f"performance-{sequence_index}",
                    agent_id="agent-1",
                    trial_id=f"trial-{sequence_index}",
                    cycle_id=f"cycle-{sequence_index}",
                    observed_at=OBSERVED_AT + timedelta(minutes=sequence_index),
                ),
            )
            for sequence_index in range(180)
        ),
    )


class DecisionProbe:
    def __init__(self, *, fail_at: int | None = None) -> None:
        self._delegate = FixedCapabilityDecisionService(
            estimate_provider=FixedCapabilityEstimateProvider(),
            decision_policy=CapabilityDecisionPolicy(),
        )
        self.fail_at = fail_at
        self.boundaries: list[CapabilityHistoryBoundary] = []

    def decide(self, *, boundary: CapabilityHistoryBoundary) -> CapabilityDecision:
        self.boundaries.append(boundary)
        if boundary.sequence_index == self.fail_at:
            raise SimulatedCycleError(f"decision failure at {boundary.sequence_index}")
        return self._delegate.decide(boundary=boundary)


class RecordingProbe:
    def __init__(self, delegate: CapabilityPerformanceRecordingService) -> None:
        self._delegate = delegate
        self.performance_ids: list[str] = []

    def record(self, *, observation: CapabilityPerformanceObservation) -> object:
        self.performance_ids.append(observation.id)
        return self._delegate.record(observation=observation)


class PostProcessorProbe:
    def __init__(self, *, fail_once_at: str | None = None) -> None:
        self.fail_once_at = fail_once_at
        self.failed = False
        self.performance_ids: list[str] = []

    def process(self, *, performance_id: str) -> object:
        self.performance_ids.append(performance_id)
        if performance_id == self.fail_once_at and not self.failed:
            self.failed = True
            raise SimulatedCycleError(f"post failure for {performance_id}")
        return None


class CheckpointServiceProbe:
    def __init__(self, delegate: ExperimentalCycleCheckpointService) -> None:
        self._delegate = delegate
        self.get_indices: list[int] = []
        self.begin_indices: list[int] = []
        self.complete_indices: list[int] = []

    def get(self, *, execution_id: str, sequence_index: int) -> ExperimentalCycleCheckpoint | None:
        self.get_indices.append(sequence_index)
        return self._delegate.get(execution_id=execution_id, sequence_index=sequence_index)

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
    ) -> ExperimentalCycleCheckpoint:
        self.begin_indices.append(sequence_index)
        return self._delegate.begin(
            execution_id=execution_id,
            sequence_index=sequence_index,
            performance_id=performance_id,
            agent_id=agent_id,
            trial_id=trial_id,
            cycle_id=cycle_id,
            capability_key=capability_key,
            observed_at=observed_at,
            decision=decision,
        )

    def complete(self, *, execution_id: str, sequence_index: int) -> ExperimentalCycleCheckpoint:
        self.complete_indices.append(sequence_index)
        return self._delegate.complete(
            execution_id=execution_id,
            sequence_index=sequence_index,
        )


@dataclass(frozen=True)
class Storage:
    path: Path
    database: SQLiteDatabase
    binding_repository: SQLiteExperimentalExecutionPlanBindingRepository
    provenance_repository: SQLiteExperimentalExecutionGenerationProvenanceRepository
    manifest_repository: SQLiteExperimentalReplicationManifestRepository
    checkpoint_service: ExperimentalCycleCheckpointService
    binding_service: ExperimentalExecutionPlanBindingService
    provenance_service: ExperimentalExecutionGenerationProvenanceService
    manifest_service: ExperimentalReplicationManifestService


@dataclass(frozen=True)
class Runtime:
    runner: ExperimentalReplicationRunner
    decision: DecisionProbe
    recording: RecordingProbe
    post: PostProcessorProbe
    checkpoint: CheckpointServiceProbe
    generator: ExperimentalReplicationPlanGenerator


def build_storage(path: Path) -> Storage:
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    binding_repository = SQLiteExperimentalExecutionPlanBindingRepository(database)
    binding_repository.initialize_schema()
    provenance_repository = SQLiteExperimentalExecutionGenerationProvenanceRepository(database)
    provenance_repository.initialize_schema()
    manifest_repository = SQLiteExperimentalReplicationManifestRepository(database)
    manifest_repository.initialize_schema()
    checkpoint_repository = SQLiteExperimentalCycleCheckpointRepository(database)
    checkpoint_repository.initialize_schema()
    checkpoint_service = ExperimentalCycleCheckpointService(checkpoint_repository)
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
    return Storage(
        path=path,
        database=database,
        binding_repository=binding_repository,
        provenance_repository=provenance_repository,
        manifest_repository=manifest_repository,
        checkpoint_service=checkpoint_service,
        binding_service=binding_service,
        provenance_service=provenance_service,
        manifest_service=manifest_service,
    )


def prepare_execution(storage: Storage, *, execution_id: str = "execution-1") -> None:
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)
    storage.binding_service.bind(
        execution_id=execution_id,
        plan_identity=generated.plan.identity(),
    )
    storage.provenance_service.register(
        execution_id=execution_id,
        generation_provenance=generated.provenance,
    )
    storage.manifest_service.register(manifest=build_manifest(execution_id=execution_id))


def build_runtime(
    storage: Storage,
    *,
    decision_fail_at: int | None = None,
    post_fail_once_at: str | None = None,
) -> Runtime:
    decision = DecisionProbe(fail_at=decision_fail_at)
    recording = RecordingProbe(
        CapabilityPerformanceRecordingService(
            unit_of_work_factory=SQLiteCapabilityUnitOfWorkFactory(storage.database)
        )
    )
    post = PostProcessorProbe(fail_once_at=post_fail_once_at)
    checkpoint = CheckpointServiceProbe(storage.checkpoint_service)
    generator = ExperimentalReplicationPlanGenerator()
    runner = ExperimentalReplicationRunner(
        manifest_service=storage.manifest_service,
        binding_service=storage.binding_service,
        provenance_service=storage.provenance_service,
        plan_generator=generator,
        checkpoint_service=checkpoint,
        decision_service=decision,
        recording_service=recording,
        post_performance_processor=post,
    )
    return Runtime(
        runner=runner,
        decision=decision,
        recording=recording,
        post=post,
        checkpoint=checkpoint,
        generator=generator,
    )


def count_rows(path: Path, table: str, *, execution_id: str | None = None) -> int:
    query = f"SELECT COUNT(*) FROM {table}"
    parameters: tuple[str, ...] = ()
    if execution_id is not None:
        query += " WHERE execution_id = ?"
        parameters = (execution_id,)
    with sqlite3.connect(path) as connection:
        row = connection.execute(query, parameters).fetchone()
    assert row is not None
    return int(row[0])


def checkpoint_statuses(path: Path) -> dict[int, str]:
    with sqlite3.connect(path) as connection:
        rows = connection.execute(
            """
            SELECT sequence_index, checkpoint_status FROM p3_dev_cycle_checkpoints
            WHERE execution_id = 'execution-1'
            ORDER BY sequence_index
            """
        ).fetchall()
    return {int(index): str(status) for index, status in rows}


def test_complete_sqlite_replication_is_stable_and_second_run_has_no_effects(
    tmp_path: Path,
) -> None:
    path = tmp_path / "complete.db"
    storage = build_storage(path)
    prepare_execution(storage)
    first = build_runtime(storage)

    first_result = first.runner.run(execution_id="execution-1")

    assert len(first_result.cycle_results) == 180
    assert set(checkpoint_statuses(path).values()) == {"COMPLETED"}
    assert count_rows(path, "p3_dev_cycle_checkpoints", execution_id="execution-1") == 180
    assert count_rows(path, "capability_performances") == 180
    assert first.checkpoint.begin_indices == list(range(180))
    assert first.checkpoint.complete_indices == list(range(180))
    assert [boundary.sequence_index for boundary in first.decision.boundaries] == list(range(180))

    reopened = build_storage(path)
    second = build_runtime(reopened)
    second_result = second.runner.run(execution_id="execution-1")

    assert second_result == first_result
    assert second.decision.boundaries == []
    assert second.recording.performance_ids == []
    assert second.post.performance_ids == []
    assert second.checkpoint.begin_indices == []
    assert second.checkpoint.complete_indices == []
    assert second.checkpoint.get_indices == list(range(180))
    assert count_rows(path, "capability_performances") == 180
    assert set(ExperimentalReplicationRunResult.model_fields) == {
        "execution_id",
        "plan_identity",
        "cycle_results",
    }
    with pytest.raises(ValidationError):
        second_result.execution_id = "another"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        ExperimentalReplicationRunResult.model_validate(
            {**second_result.model_dump(), "seed": 12345}
        )


def test_crash_on_started_cycle_73_resumes_without_redecision_or_duplicate_performance(
    tmp_path: Path,
) -> None:
    path = tmp_path / "crash-73.db"
    storage = build_storage(path)
    prepare_execution(storage)
    first = build_runtime(storage, post_fail_once_at="performance-73")

    with pytest.raises(SimulatedCycleError, match="performance-73"):
        first.runner.run(execution_id="execution-1")

    statuses = checkpoint_statuses(path)
    assert statuses == {**{index: "COMPLETED" for index in range(73)}, 73: "STARTED"}
    assert count_rows(path, "capability_performances") == 74
    assert [boundary.sequence_index for boundary in first.decision.boundaries] == list(range(74))

    reopened = build_storage(path)
    retry = build_runtime(reopened)
    result = retry.runner.run(execution_id="execution-1")

    assert len(result.cycle_results) == 180
    assert [boundary.sequence_index for boundary in retry.decision.boundaries] == list(
        range(74, 180)
    )
    assert retry.recording.performance_ids == [f"performance-{index}" for index in range(73, 180)]
    assert retry.post.performance_ids == [f"performance-{index}" for index in range(73, 180)]
    assert retry.checkpoint.complete_indices == list(range(73, 180))
    assert set(checkpoint_statuses(path).values()) == {"COMPLETED"}
    assert count_rows(path, "p3_dev_cycle_checkpoints", execution_id="execution-1") == 180
    assert count_rows(path, "capability_performances") == 180


def test_failure_deciding_cycle_74_stops_before_begin_and_retry_continues(
    tmp_path: Path,
) -> None:
    path = tmp_path / "between-cycles.db"
    storage = build_storage(path)
    prepare_execution(storage)
    first = build_runtime(storage, decision_fail_at=74)

    with pytest.raises(SimulatedCycleError, match="decision failure at 74"):
        first.runner.run(execution_id="execution-1")

    assert checkpoint_statuses(path) == {index: "COMPLETED" for index in range(74)}
    assert 74 not in first.checkpoint.begin_indices
    assert count_rows(path, "capability_performances") == 74

    reopened = build_storage(path)
    retry = build_runtime(reopened)
    result = retry.runner.run(execution_id="execution-1")

    assert len(result.cycle_results) == 180
    assert [boundary.sequence_index for boundary in retry.decision.boundaries] == list(
        range(74, 180)
    )
    assert set(checkpoint_statuses(path).values()) == {"COMPLETED"}
    assert count_rows(path, "capability_performances") == 180


@pytest.mark.parametrize("missing", ("manifest", "binding", "provenance"))
def test_missing_preflight_artifact_refuses_before_any_cycle(
    tmp_path: Path,
    missing: str,
) -> None:
    path = tmp_path / f"missing-{missing}.db"
    storage = build_storage(path)
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)
    manifest = build_manifest()
    if missing != "binding":
        storage.binding_service.bind(
            execution_id="execution-1",
            plan_identity=generated.plan.identity(),
        )
    if missing != "provenance":
        storage.provenance_repository.register(
            ExperimentalExecutionGenerationProvenance(
                execution_id="execution-1",
                generation_provenance=generated.provenance,
            )
        )
    if missing != "manifest":
        storage.manifest_repository.register(manifest)
    runtime = build_runtime(storage)

    with pytest.raises(ExperimentalReplicationRunnerIntegrityError):
        runtime.runner.run(execution_id="execution-1")

    assert runtime.decision.boundaries == []
    assert runtime.recording.performance_ids == []
    assert runtime.post.performance_ids == []
    assert runtime.checkpoint.get_indices == []
    assert count_rows(path, "capability_performances") == 0


def test_binding_provenance_mismatch_refuses_before_reproduction_or_cycle(tmp_path: Path) -> None:
    path = tmp_path / "identity-mismatch.db"
    storage = build_storage(path)
    bound = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)
    other = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=54321)
    storage.binding_service.bind(
        execution_id="execution-1",
        plan_identity=bound.plan.identity(),
    )
    storage.provenance_repository.register(
        ExperimentalExecutionGenerationProvenance(
            execution_id="execution-1",
            generation_provenance=other.provenance,
        )
    )
    storage.manifest_repository.register(build_manifest())
    runtime = build_runtime(storage)

    with pytest.raises(ExperimentalReplicationRunnerIntegrityError, match="incohérents"):
        runtime.runner.run(execution_id="execution-1")

    assert runtime.checkpoint.get_indices == []
    assert runtime.decision.boundaries == []
    assert count_rows(path, "capability_performances") == 0


@pytest.mark.parametrize(
    ("changed_field", "changed_value"),
    (
        ("generator_version", "p3-dev-plan-v1"),
        ("python_implementation", "pypy"),
        ("python_version", "0.0.1"),
    ),
)
def test_incompatible_generation_environment_refuses_before_any_cycle(
    tmp_path: Path,
    changed_field: str,
    changed_value: str,
) -> None:
    path = tmp_path / f"environment-{changed_field}.db"
    storage = build_storage(path)
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)
    incompatible = generated.provenance.model_copy(update={changed_field: changed_value})
    storage.binding_service.bind(
        execution_id="execution-1",
        plan_identity=generated.plan.identity(),
    )
    storage.provenance_repository.register(
        ExperimentalExecutionGenerationProvenance(
            execution_id="execution-1",
            generation_provenance=incompatible,
        )
    )
    storage.manifest_repository.register(build_manifest())
    runtime = build_runtime(storage)

    with pytest.raises(ExperimentalPlanGenerationEnvironmentError):
        runtime.runner.run(execution_id="execution-1")

    assert runtime.checkpoint.get_indices == []
    assert runtime.decision.boundaries == []
    assert runtime.recording.performance_ids == []
    assert count_rows(path, "capability_performances") == 0


def test_replication_runner_public_api_and_source_have_no_condition_or_context_generation() -> None:
    assert list(inspect.signature(ExperimentalReplicationRunner.run).parameters) == [
        "self",
        "execution_id",
    ]
    source = Path("src/soinesis/experiments/p3/replication_runner.py").read_text(encoding="utf-8")
    assert ".generate(" not in source
    assert ".generate_with_provenance(" not in source
    assert "for context in manifest.cycle_contexts" in source
    assert "range(180)" not in source
    assert "if condition" not in source
    assert "run_all" not in source
    assert "CapabilitySelfModelInitializationService" not in source
    assert "datetime.now" not in source
