import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from soinesis.application.capabilities import CapabilityDecisionPolicy
from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityDecision,
    CapabilityEstimate,
    EstimateSource,
)
from soinesis.experiments.p3 import (
    ExperimentalCycleCheckpoint,
    ExperimentalCycleCheckpointIntegrityError,
    ExperimentalCycleCheckpointNotFoundError,
    ExperimentalCycleCheckpointOrderError,
    ExperimentalCycleCheckpointService,
    ExperimentalCycleCheckpointStatus,
    ExperimentalReplicationPlan,
    SQLiteExperimentalCycleCheckpointRepository,
)
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

PRIVATE_FIELDS = {
    "capability_order",
    "correction_applied",
    "dataset",
    "final_success",
    "intrinsic_success",
    "official_dataset_id",
    "oracle",
    "outcome",
    "phase",
    "realized_reward",
    "replication",
    "seed",
    "segment",
    "true_success_probability",
    "u_correction",
    "u_intrinsic",
}
OBSERVED_AT = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)


def build_decision(
    estimated_success: float = 0.60,
    *,
    agent_id: str = "agent-1",
    capability_key: str = "ALPHA",
) -> CapabilityDecision:
    return CapabilityDecisionPolicy().decide(
        CapabilityEstimate(
            agent_id=agent_id,
            capability_key=capability_key,
            estimated_success=estimated_success,
            source=EstimateSource.SELF_ATTRIBUTE,
        )
    )


def build_service(
    path: Path,
) -> tuple[ExperimentalCycleCheckpointService, SQLiteExperimentalCycleCheckpointRepository]:
    repository = SQLiteExperimentalCycleCheckpointRepository(SQLiteDatabase(path))
    repository.initialize_schema()
    return ExperimentalCycleCheckpointService(repository), repository


def begin(
    service: ExperimentalCycleCheckpointService,
    *,
    sequence_index: int = 0,
    performance_id: str = "performance-0",
    agent_id: str = "agent-1",
    trial_id: str = "trial-0",
    cycle_id: str = "cycle-0",
    capability_key: str = "ALPHA",
    observed_at: datetime = OBSERVED_AT,
    decision: CapabilityDecision | None = None,
    execution_id: str = "execution-1",
) -> ExperimentalCycleCheckpoint:
    return service.begin(
        execution_id=execution_id,
        sequence_index=sequence_index,
        performance_id=performance_id,
        agent_id=agent_id,
        trial_id=trial_id,
        cycle_id=cycle_id,
        capability_key=capability_key,
        observed_at=observed_at,
        decision=decision or build_decision(agent_id=agent_id, capability_key=capability_key),
    )


def row_count(path: Path, *, execution_id: str = "execution-1") -> int:
    with sqlite3.connect(path) as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) FROM p3_dev_cycle_checkpoints
            WHERE execution_id = ?
            """,
            (execution_id,),
        ).fetchone()
    assert row is not None
    return int(row[0])


def test_checkpoint_model_is_frozen_public_and_scope_consistent(tmp_path: Path) -> None:
    service, _ = build_service(tmp_path / "checkpoint.db")
    checkpoint = begin(service)

    assert checkpoint.status is ExperimentalCycleCheckpointStatus.STARTED
    assert set(ExperimentalCycleCheckpoint.model_fields) == {
        "execution_id",
        "sequence_index",
        "performance_id",
        "agent_id",
        "trial_id",
        "cycle_id",
        "capability_key",
        "observed_at",
        "decision",
        "status",
    }
    assert PRIVATE_FIELDS.isdisjoint(ExperimentalCycleCheckpoint.model_fields)
    with pytest.raises(ValidationError):
        checkpoint.sequence_index = 4  # type: ignore[misc]
    with pytest.raises(ValidationError):
        ExperimentalCycleCheckpoint(
            **checkpoint.model_dump(exclude={"decision"}),
            decision=build_decision(agent_id="another-agent"),
        )
    with pytest.raises(ValidationError):
        ExperimentalCycleCheckpoint.model_validate({**checkpoint.model_dump(), "phase": 1})


def test_experimental_schema_is_opt_in_and_contains_no_private_columns(tmp_path: Path) -> None:
    path = tmp_path / "opt-in.db"
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    with database.connect() as connection:
        absent = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'p3_dev_cycle_checkpoints'
            """
        ).fetchone()
    assert absent is None

    repository = SQLiteExperimentalCycleCheckpointRepository(database)
    repository.initialize_schema()
    with database.connect() as connection:
        columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(p3_dev_cycle_checkpoints)").fetchall()
        }
    assert PRIVATE_FIELDS.isdisjoint(columns)
    assert "observed_at" in columns


def test_first_checkpoint_must_be_zero_and_gaps_are_refused(tmp_path: Path) -> None:
    path = tmp_path / "order.db"
    service, repository = build_service(path)

    with pytest.raises(ExperimentalCycleCheckpointOrderError):
        begin(service, sequence_index=1, performance_id="performance-1")
    assert row_count(path) == 0

    first = begin(service)
    with pytest.raises(ExperimentalCycleCheckpointOrderError):
        begin(service, sequence_index=1, performance_id="performance-1")
    with pytest.raises(ExperimentalCycleCheckpointOrderError):
        begin(service, sequence_index=2, performance_id="performance-2")
    assert repository.get(execution_id="execution-1", sequence_index=0) == first
    assert row_count(path) == 1


def test_begin_and_complete_are_idempotent_without_starting_the_next_cycle(
    tmp_path: Path,
) -> None:
    path = tmp_path / "idempotent.db"
    service, repository = build_service(path)
    started = begin(service)

    assert begin(service) == started
    assert row_count(path) == 1

    completed = service.complete(execution_id="execution-1", sequence_index=0)
    assert completed.status is ExperimentalCycleCheckpointStatus.COMPLETED
    assert completed.decision == started.decision
    assert service.complete(execution_id="execution-1", sequence_index=0) == completed
    assert begin(service) == completed
    assert row_count(path) == 1
    assert repository.get(execution_id="execution-1", sequence_index=1) is None


def test_next_cycle_is_allowed_only_after_exactly_the_previous_one(tmp_path: Path) -> None:
    path = tmp_path / "contiguous.db"
    service, _ = build_service(path)
    begin(service)
    service.complete(execution_id="execution-1", sequence_index=0)

    second = begin(
        service,
        sequence_index=1,
        performance_id="performance-1",
        trial_id="trial-1",
        cycle_id="cycle-1",
        capability_key="BETA",
        decision=build_decision(capability_key="BETA"),
    )

    assert second.sequence_index == 1
    assert second.status is ExperimentalCycleCheckpointStatus.STARTED
    assert row_count(path) == 2


@pytest.mark.parametrize(
    ("override", "value"),
    (
        ("performance_id", "conflicting-performance"),
        ("cycle_id", "conflicting-cycle"),
        ("trial_id", "conflicting-trial"),
        ("decision", build_decision(0.70)),
        ("decision", build_decision(0.80)),
    ),
)
def test_same_position_with_different_context_or_decision_is_rejected(
    tmp_path: Path,
    override: str,
    value: str | CapabilityDecision,
) -> None:
    path = tmp_path / f"conflict-{override}-{str(value)[-8:]}.db"
    service, repository = build_service(path)
    original = begin(service)
    arguments: dict[str, str | CapabilityDecision] = {override: value}

    with pytest.raises(ExperimentalCycleCheckpointIntegrityError):
        begin(service, **arguments)  # type: ignore[arg-type]

    assert repository.get(execution_id="execution-1", sequence_index=0) == original
    assert row_count(path) == 1


def test_capability_conflict_is_rejected_even_with_a_coherent_new_decision(
    tmp_path: Path,
) -> None:
    path = tmp_path / "capability-conflict.db"
    service, repository = build_service(path)
    original = begin(service)

    with pytest.raises(ExperimentalCycleCheckpointIntegrityError):
        begin(
            service,
            capability_key="BETA",
            decision=build_decision(capability_key="BETA"),
        )

    assert repository.get(execution_id="execution-1", sequence_index=0) == original


def test_observed_at_conflict_is_rejected_without_modifying_the_checkpoint(
    tmp_path: Path,
) -> None:
    path = tmp_path / "observed-at-conflict.db"
    service, repository = build_service(path)
    original = begin(service, observed_at=OBSERVED_AT)

    with pytest.raises(ExperimentalCycleCheckpointIntegrityError):
        begin(service, observed_at=OBSERVED_AT + timedelta(seconds=1))

    assert repository.get(execution_id="execution-1", sequence_index=0) == original
    assert row_count(path) == 1


def test_started_snapshot_keeps_verify_after_external_decision_changes(tmp_path: Path) -> None:
    path = tmp_path / "frozen-decision.db"
    service, repository = build_service(path)
    started = begin(service)
    changed_decision = build_decision(0.80)

    reloaded = repository.get(execution_id="execution-1", sequence_index=0)

    assert started.decision.action is CapabilityAction.VERIFY
    assert changed_decision.action is CapabilityAction.DIRECT
    assert reloaded is not None
    assert reloaded.decision == started.decision
    assert reloaded.decision.action is CapabilityAction.VERIFY


def test_context_and_decision_are_immutable_during_completion(tmp_path: Path) -> None:
    path = tmp_path / "immutable.db"
    service, repository = build_service(path)
    started = begin(service)
    with sqlite3.connect(path) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            UPDATE p3_dev_cycle_checkpoints
            SET observed_at = '2026-08-09T12:00:01+00:00',
                checkpoint_status = 'COMPLETED'
            WHERE execution_id = 'execution-1' AND sequence_index = 0
            """
        )

    completed = service.complete(execution_id="execution-1", sequence_index=0)
    assert completed.model_copy(update={"status": started.status}) == started
    with sqlite3.connect(path) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                UPDATE p3_dev_cycle_checkpoints
                SET decision_action = 'DIRECT'
                WHERE execution_id = 'execution-1' AND sequence_index = 0
                """
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                DELETE FROM p3_dev_cycle_checkpoints
                WHERE execution_id = 'execution-1' AND sequence_index = 0
                """
            )
    assert repository.get(execution_id="execution-1", sequence_index=0) == completed


def test_missing_or_wrong_completion_is_refused_without_creation(tmp_path: Path) -> None:
    path = tmp_path / "missing.db"
    service, _ = build_service(path)

    with pytest.raises(ExperimentalCycleCheckpointNotFoundError):
        service.complete(execution_id="execution-1", sequence_index=0)
    begin(service)
    with pytest.raises(ExperimentalCycleCheckpointNotFoundError):
        service.complete(execution_id="execution-1", sequence_index=1)
    assert row_count(path) == 1


def test_crash_after_started_reloads_exact_snapshot_and_blocks_next_cycle(
    tmp_path: Path,
) -> None:
    path = tmp_path / "crash-started.db"
    first_service, _ = build_service(path)
    started = begin(first_service)

    reopened_service, reopened_repository = build_service(path)
    reloaded = reopened_service.get(execution_id="execution-1", sequence_index=0)

    assert reloaded == started
    assert reloaded is not None
    assert reloaded.status is ExperimentalCycleCheckpointStatus.STARTED
    assert reloaded.observed_at == OBSERVED_AT
    assert reloaded.decision.action is CapabilityAction.VERIFY
    assert reopened_repository.get(execution_id="execution-1", sequence_index=0) == started
    with pytest.raises(ExperimentalCycleCheckpointOrderError):
        begin(
            reopened_service,
            sequence_index=1,
            performance_id="performance-1",
            trial_id="trial-1",
            cycle_id="cycle-1",
        )
    assert row_count(path) == 1


def test_reopen_after_completion_allows_only_the_contiguous_next_cycle(tmp_path: Path) -> None:
    path = tmp_path / "crash-completed.db"
    first_service, _ = build_service(path)
    begin(first_service)
    first_service.complete(execution_id="execution-1", sequence_index=0)

    reopened_service, _ = build_service(path)
    completed_retry = begin(reopened_service)
    second = begin(
        reopened_service,
        sequence_index=1,
        performance_id="performance-1",
        trial_id="trial-1",
        cycle_id="cycle-1",
    )

    assert completed_retry.status is ExperimentalCycleCheckpointStatus.COMPLETED
    assert second.status is ExperimentalCycleCheckpointStatus.STARTED
    assert row_count(path) == 2


def test_checkpoint_reproduces_the_exact_plan_performance_after_reopening(
    tmp_path: Path,
) -> None:
    path = tmp_path / "reproducible-performance.db"
    capability_block = ["ALPHA"] * 20 + ["BETA"] * 20 + ["GAMMA"] * 20
    plan = ExperimentalReplicationPlan(
        capability_order=capability_block * 3,
        u_intrinsic_by_sequence=[0.25] * 180,
        u_correction_by_sequence=[0.75] * 180,
    )
    first_service, _ = build_service(path)
    checkpoint = begin(first_service, observed_at=OBSERVED_AT)
    performance_1 = plan.attempt(
        performance_id=checkpoint.performance_id,
        agent_id=checkpoint.agent_id,
        trial_id=checkpoint.trial_id,
        cycle_id=checkpoint.cycle_id,
        sequence_index=checkpoint.sequence_index,
        observed_at=checkpoint.observed_at,
    )

    reopened_service, _ = build_service(path)
    reloaded = reopened_service.get(execution_id="execution-1", sequence_index=0)
    assert reloaded is not None
    performance_2 = plan.attempt(
        performance_id=reloaded.performance_id,
        agent_id=reloaded.agent_id,
        trial_id=reloaded.trial_id,
        cycle_id=reloaded.cycle_id,
        sequence_index=reloaded.sequence_index,
        observed_at=reloaded.observed_at,
    )

    assert performance_1 == performance_2


def test_cognitive_modules_do_not_depend_on_experimental_checkpoint() -> None:
    for relative_path in (
        "src/soinesis/domain/capabilities.py",
        "src/soinesis/application/capabilities.py",
        "src/soinesis/ports/capabilities.py",
    ):
        source = Path(relative_path).read_text(encoding="utf-8")
        assert "soinesis.experiments.p3" not in source
        assert "execution_id" not in source
