import inspect
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
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
    ExperimentalCycleCheckpoint,
    ExperimentalCycleCheckpointService,
    ExperimentalCycleCheckpointStatus,
    ExperimentalCycleRunner,
    ExperimentalCycleRunnerIntegrityError,
    ExperimentalCycleRunResult,
    ExperimentalCycleStartContext,
    ExperimentalCycleStartContextRequiredError,
    ExperimentalReplicationPlan,
    ExperimentalTrialOutcome,
    SQLiteExperimentalCycleCheckpointRepository,
)
from soinesis.infrastructure.sqlite import SQLiteCapabilityUnitOfWorkFactory, SQLiteDatabase

OBSERVED_AT = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
CAPABILITY_BLOCK = ["ALPHA"] * 20 + ["BETA"] * 20 + ["GAMMA"] * 20


class ExpectedTestError(RuntimeError):
    pass


def build_plan(
    *, log: list[str] | None = None, outcome_error: Exception | None = None
) -> LoggingPlan:
    return LoggingPlan(
        capability_order=CAPABILITY_BLOCK * 3,
        u_intrinsic_by_sequence=[0.25] * 180,
        u_correction_by_sequence=[0.75] * 180,
        log=log if log is not None else [],
        outcome_error=outcome_error,
    )


def build_context(**changes: object) -> ExperimentalCycleStartContext:
    values: dict[str, object] = {
        "performance_id": "performance-0",
        "agent_id": "agent-1",
        "trial_id": "trial-0",
        "cycle_id": "cycle-0",
        "observed_at": OBSERVED_AT,
    }
    values.update(changes)
    return ExperimentalCycleStartContext.model_validate(values)


class LoggingPlan(ExperimentalReplicationPlan):
    def __init__(
        self,
        *,
        capability_order: list[str],
        u_intrinsic_by_sequence: list[float],
        u_correction_by_sequence: list[float],
        log: list[str],
        outcome_error: Exception | None = None,
    ) -> None:
        super().__init__(
            capability_order=capability_order,
            u_intrinsic_by_sequence=u_intrinsic_by_sequence,
            u_correction_by_sequence=u_correction_by_sequence,
        )
        self.log = log
        self.outcome_error = outcome_error
        self._resolving_outcome = False
        self.performances: list[CapabilityPerformanceObservation] = []
        self.outcomes: list[ExperimentalTrialOutcome] = []

    def attempt(
        self,
        *,
        performance_id: str,
        agent_id: str,
        trial_id: str,
        cycle_id: str,
        sequence_index: int,
        observed_at: datetime,
    ) -> CapabilityPerformanceObservation:
        if not self._resolving_outcome:
            self.log.append("plan.attempt")
        performance = super().attempt(
            performance_id=performance_id,
            agent_id=agent_id,
            trial_id=trial_id,
            cycle_id=cycle_id,
            sequence_index=sequence_index,
            observed_at=observed_at,
        )
        if not self._resolving_outcome:
            self.performances.append(performance)
        return performance

    def resolve_outcome(
        self,
        *,
        decision: CapabilityDecision,
        performance: CapabilityPerformanceObservation,
    ) -> ExperimentalTrialOutcome:
        self.log.append("plan.resolve_outcome")
        if self.outcome_error is not None:
            raise self.outcome_error
        self._resolving_outcome = True
        try:
            outcome = super().resolve_outcome(decision=decision, performance=performance)
        finally:
            self._resolving_outcome = False
        self.outcomes.append(outcome)
        return outcome


class DecisionServiceProbe:
    def __init__(self, *, log: list[str], error: Exception | None = None) -> None:
        self.log = log
        self.error = error
        self.boundaries: list[CapabilityHistoryBoundary] = []

    def decide(self, *, boundary: CapabilityHistoryBoundary) -> CapabilityDecision:
        self.log.append("decision.decide")
        self.boundaries.append(boundary)
        if self.error is not None:
            raise self.error
        return CapabilityDecisionPolicy().decide(
            CapabilityEstimate(
                agent_id=boundary.agent_id,
                capability_key=boundary.capability_key,
                estimated_success=0.60,
                source=EstimateSource.FIXED_BASELINE,
            )
        )


class CheckpointServiceProbe:
    def __init__(self, *, delegate: ExperimentalCycleCheckpointService, log: list[str]) -> None:
        self.delegate = delegate
        self.log = log

    def get(self, *, execution_id: str, sequence_index: int) -> ExperimentalCycleCheckpoint | None:
        self.log.append("checkpoint.get")
        return self.delegate.get(execution_id=execution_id, sequence_index=sequence_index)

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
        self.log.append("checkpoint.begin")
        return self.delegate.begin(
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
        self.log.append("checkpoint.complete")
        return self.delegate.complete(execution_id=execution_id, sequence_index=sequence_index)


class RecordingServiceProbe:
    def __init__(
        self,
        *,
        delegate: CapabilityPerformanceRecordingService,
        log: list[str],
        error: Exception | None = None,
    ) -> None:
        self.delegate = delegate
        self.log = log
        self.error = error
        self.observations: list[CapabilityPerformanceObservation] = []

    def record(self, *, observation: CapabilityPerformanceObservation) -> object:
        self.log.append("recording.record")
        self.observations.append(observation)
        if self.error is not None:
            raise self.error
        return self.delegate.record(observation=observation)


class PostProcessorProbe:
    def __init__(
        self,
        *,
        log: list[str],
        effects: list[str] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.log = log
        self.effects = effects if effects is not None else []
        self.error = error
        self.performance_ids: list[str] = []

    def process(self, *, performance_id: str) -> object:
        self.log.append("post.process")
        self.performance_ids.append(performance_id)
        self.effects.append(performance_id)
        if self.error is not None:
            raise self.error
        return performance_id


@dataclass
class RunnerHarness:
    database: SQLiteDatabase
    checkpoint_repository: SQLiteExperimentalCycleCheckpointRepository
    checkpoint_service: ExperimentalCycleCheckpointService
    plan: LoggingPlan
    decision: DecisionServiceProbe
    recording: RecordingServiceProbe
    post: PostProcessorProbe | None
    runner: ExperimentalCycleRunner


def build_harness(
    path: Path,
    *,
    log: list[str] | None = None,
    decision_error: Exception | None = None,
    recording_error: Exception | None = None,
    outcome_error: Exception | None = None,
    post: PostProcessorProbe | None = None,
) -> RunnerHarness:
    operation_log = log if log is not None else []
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    checkpoint_repository = SQLiteExperimentalCycleCheckpointRepository(database)
    checkpoint_repository.initialize_schema()
    checkpoint_service = ExperimentalCycleCheckpointService(checkpoint_repository)
    recording_delegate = CapabilityPerformanceRecordingService(
        unit_of_work_factory=SQLiteCapabilityUnitOfWorkFactory(database)
    )
    plan = build_plan(log=operation_log, outcome_error=outcome_error)
    decision = DecisionServiceProbe(log=operation_log, error=decision_error)
    recording = RecordingServiceProbe(
        delegate=recording_delegate,
        log=operation_log,
        error=recording_error,
    )
    runner = ExperimentalCycleRunner(
        plan=plan,
        checkpoint_service=CheckpointServiceProbe(
            delegate=checkpoint_service,
            log=operation_log,
        ),
        decision_service=decision,
        recording_service=recording,
        post_performance_processor=post,
    )
    return RunnerHarness(
        database=database,
        checkpoint_repository=checkpoint_repository,
        checkpoint_service=checkpoint_service,
        plan=plan,
        decision=decision,
        recording=recording,
        post=post,
        runner=runner,
    )


def performance_count(database: SQLiteDatabase, performance_id: str) -> int:
    with database.connect() as connection:
        row = connection.execute(
            "SELECT COUNT(*) FROM capability_performances WHERE id = ?",
            (performance_id,),
        ).fetchone()
    assert row is not None
    return int(row[0])


def test_new_cycle_has_the_exact_causal_order_and_minimal_inputs(tmp_path: Path) -> None:
    log: list[str] = []
    post = PostProcessorProbe(log=log)
    harness = build_harness(tmp_path / "causal.db", log=log, post=post)

    result = harness.runner.run(
        execution_id="execution-1",
        sequence_index=0,
        start_context=build_context(),
    )

    assert log == [
        "checkpoint.get",
        "decision.decide",
        "checkpoint.begin",
        "plan.attempt",
        "plan.resolve_outcome",
        "recording.record",
        "post.process",
        "checkpoint.complete",
    ]
    assert result.checkpoint.status is ExperimentalCycleCheckpointStatus.COMPLETED
    assert harness.decision.boundaries == [
        CapabilityHistoryBoundary(
            agent_id="agent-1",
            capability_key="ALPHA",
            trial_id="trial-0",
            cycle_id="cycle-0",
            sequence_index=0,
        )
    ]
    assert harness.recording.observations == [result.performance]
    assert post.performance_ids == [result.performance.id]
    assert result.performance.observed_at == OBSERVED_AT
    assert result.outcome.action is result.checkpoint.decision.action


def test_completed_retry_is_stable_and_has_no_cognitive_or_persistent_effect(
    tmp_path: Path,
) -> None:
    log: list[str] = []
    post = PostProcessorProbe(log=log)
    harness = build_harness(tmp_path / "completed.db", log=log, post=post)
    result_1 = harness.runner.run(
        execution_id="execution-1",
        sequence_index=0,
        start_context=build_context(),
    )
    log.clear()
    decision_calls = len(harness.decision.boundaries)
    recording_calls = len(harness.recording.observations)
    post_calls = len(post.performance_ids)

    result_2 = harness.runner.run(
        execution_id="execution-1",
        sequence_index=0,
        start_context=None,
    )

    assert result_2 == result_1
    assert log == ["checkpoint.get", "plan.attempt", "plan.resolve_outcome"]
    assert len(harness.decision.boundaries) == decision_calls
    assert len(harness.recording.observations) == recording_calls
    assert len(post.performance_ids) == post_calls
    assert performance_count(harness.database, "performance-0") == 1


def test_cycle_without_post_processor_records_then_completes_without_metacognition(
    tmp_path: Path,
) -> None:
    log: list[str] = []
    harness = build_harness(tmp_path / "without-post.db", log=log)

    result = harness.runner.run(
        execution_id="execution-1",
        sequence_index=0,
        start_context=build_context(),
    )

    assert "post.process" not in log
    assert log[-2:] == ["recording.record", "checkpoint.complete"]
    assert result.checkpoint.status is ExperimentalCycleCheckpointStatus.COMPLETED
    assert performance_count(harness.database, "performance-0") == 1


def test_crash_after_record_reuses_frozen_decision_and_completes_on_retry(
    tmp_path: Path,
) -> None:
    path = tmp_path / "crash-after-record.db"
    first_log: list[str] = []
    durable_effects: list[str] = []
    failing_post = PostProcessorProbe(
        log=first_log,
        effects=durable_effects,
        error=ExpectedTestError("post failure"),
    )
    first = build_harness(path, log=first_log, post=failing_post)

    with pytest.raises(ExpectedTestError, match="post failure"):
        first.runner.run(
            execution_id="execution-1",
            sequence_index=0,
            start_context=build_context(),
        )

    frozen = first.checkpoint_service.get(execution_id="execution-1", sequence_index=0)
    assert frozen is not None
    assert frozen.status is ExperimentalCycleCheckpointStatus.STARTED
    assert performance_count(first.database, "performance-0") == 1
    first_performance = first.plan.performances[-1]
    first_outcome = first.plan.outcomes[-1]
    assert durable_effects == ["performance-0"]

    retry_log: list[str] = []
    succeeding_post = PostProcessorProbe(log=retry_log, effects=durable_effects)
    retry = build_harness(
        path,
        log=retry_log,
        decision_error=ExpectedTestError("decision must not run"),
        post=succeeding_post,
    )
    result = retry.runner.run(
        execution_id="execution-1",
        sequence_index=0,
        start_context=None,
    )

    assert retry_log == [
        "checkpoint.get",
        "plan.attempt",
        "plan.resolve_outcome",
        "recording.record",
        "post.process",
        "checkpoint.complete",
    ]
    assert retry.decision.boundaries == []
    assert result.performance == first_performance
    assert result.outcome == first_outcome
    assert result.checkpoint.status is ExperimentalCycleCheckpointStatus.COMPLETED
    assert performance_count(retry.database, "performance-0") == 1
    assert durable_effects == ["performance-0", "performance-0"]


def test_record_failure_stops_post_processing_and_completion(tmp_path: Path) -> None:
    log: list[str] = []
    post = PostProcessorProbe(log=log)
    harness = build_harness(
        tmp_path / "record-failure.db",
        log=log,
        recording_error=ExpectedTestError("record failure"),
        post=post,
    )

    with pytest.raises(ExpectedTestError, match="record failure"):
        harness.runner.run(
            execution_id="execution-1",
            sequence_index=0,
            start_context=build_context(),
        )

    assert log[-1] == "recording.record"
    assert "post.process" not in log
    assert "checkpoint.complete" not in log
    checkpoint = harness.checkpoint_service.get(execution_id="execution-1", sequence_index=0)
    assert checkpoint is not None
    assert checkpoint.status is ExperimentalCycleCheckpointStatus.STARTED


def test_outcome_failure_stops_recording_post_processing_and_completion(tmp_path: Path) -> None:
    log: list[str] = []
    post = PostProcessorProbe(log=log)
    harness = build_harness(
        tmp_path / "outcome-failure.db",
        log=log,
        outcome_error=ExpectedTestError("outcome failure"),
        post=post,
    )

    with pytest.raises(ExpectedTestError, match="outcome failure"):
        harness.runner.run(
            execution_id="execution-1",
            sequence_index=0,
            start_context=build_context(),
        )

    assert log[-1] == "plan.resolve_outcome"
    assert "recording.record" not in log
    assert "post.process" not in log
    assert "checkpoint.complete" not in log
    checkpoint = harness.checkpoint_service.get(execution_id="execution-1", sequence_index=0)
    assert checkpoint is not None
    assert checkpoint.status is ExperimentalCycleCheckpointStatus.STARTED


def test_new_cycle_without_start_context_is_refused_after_checkpoint_get(tmp_path: Path) -> None:
    log: list[str] = []
    harness = build_harness(tmp_path / "missing-context.db", log=log)

    with pytest.raises(ExperimentalCycleStartContextRequiredError):
        harness.runner.run(execution_id="execution-1", sequence_index=0)

    assert log == ["checkpoint.get"]
    assert harness.decision.boundaries == []


@pytest.mark.parametrize(
    "changed_context",
    (
        {"performance_id": "another-performance"},
        {"agent_id": "another-agent"},
        {"trial_id": "another-trial"},
        {"cycle_id": "another-cycle"},
        {"observed_at": OBSERVED_AT + timedelta(seconds=1)},
    ),
)
def test_existing_checkpoint_rejects_a_different_start_context_without_deciding(
    tmp_path: Path,
    changed_context: dict[str, object],
) -> None:
    harness = build_harness(tmp_path / f"context-{next(iter(changed_context))}.db")
    harness.runner.run(
        execution_id="execution-1",
        sequence_index=0,
        start_context=build_context(),
    )
    decision_calls = len(harness.decision.boundaries)

    with pytest.raises(ExperimentalCycleRunnerIntegrityError):
        harness.runner.run(
            execution_id="execution-1",
            sequence_index=0,
            start_context=build_context(**changed_context),
        )

    assert len(harness.decision.boundaries) == decision_calls


def test_retry_refuses_a_different_plan_before_attempt_or_cognitive_effects(tmp_path: Path) -> None:
    path = tmp_path / "plan-mismatch.db"
    first = build_harness(path)
    first.runner.run(
        execution_id="execution-1",
        sequence_index=0,
        start_context=build_context(),
    )
    log: list[str] = []
    mismatched_plan = LoggingPlan(
        capability_order=(["BETA"] * 20 + ["ALPHA"] * 20 + ["GAMMA"] * 20) * 3,
        u_intrinsic_by_sequence=[0.25] * 180,
        u_correction_by_sequence=[0.75] * 180,
        log=log,
    )
    decision = DecisionServiceProbe(log=log, error=ExpectedTestError("must not decide"))
    recording = RecordingServiceProbe(
        delegate=CapabilityPerformanceRecordingService(
            unit_of_work_factory=SQLiteCapabilityUnitOfWorkFactory(first.database)
        ),
        log=log,
    )
    runner = ExperimentalCycleRunner(
        plan=mismatched_plan,
        checkpoint_service=CheckpointServiceProbe(delegate=first.checkpoint_service, log=log),
        decision_service=decision,
        recording_service=recording,
    )

    with pytest.raises(ExperimentalCycleRunnerIntegrityError):
        runner.run(execution_id="execution-1", sequence_index=0)

    assert log == ["checkpoint.get"]
    assert decision.boundaries == []
    assert recording.observations == []


def test_public_models_and_runner_signature_expose_only_the_expected_context() -> None:
    assert set(ExperimentalCycleStartContext.model_fields) == {
        "performance_id",
        "agent_id",
        "trial_id",
        "cycle_id",
        "observed_at",
    }
    assert set(ExperimentalCycleRunResult.model_fields) == {
        "checkpoint",
        "performance",
        "outcome",
    }
    assert list(inspect.signature(ExperimentalCycleRunner.run).parameters) == [
        "self",
        "execution_id",
        "sequence_index",
        "start_context",
    ]
    with pytest.raises(ValidationError):
        ExperimentalCycleStartContext.model_validate(
            {**build_context().model_dump(), "final_success": True}
        )


def test_runner_module_has_no_condition_branch_or_multi_cycle_loop() -> None:
    source = Path("src/soinesis/experiments/p3/runner.py").read_text(encoding="utf-8")
    assert "if condition" not in source
    assert "for sequence" not in source
    assert "while " not in source
    assert "OFFICIAL" not in source
    assert "true_success_probability" not in source
