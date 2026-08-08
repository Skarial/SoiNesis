import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from soinesis.application.capabilities import (
    CapabilityPerformanceNotFoundError,
    CapabilityPerformanceOrderError,
    CapabilityPerformanceProvenanceError,
    DecayedBetaEstimator,
    MetacognitiveCapabilityUpdateResult,
    MetacognitiveCapabilityUpdateService,
    MetacognitiveLambdaMismatchError,
    MetacognitiveStateIntegrityError,
    MetacognitiveUpdateStatus,
)
from soinesis.domain.capabilities import (
    CapabilityPerformanceObservation,
    MetacognitiveCapabilityState,
    VersionedMetacognitiveCapabilityState,
)
from soinesis.domain.models import SourceType
from soinesis.infrastructure.sqlite import (
    SQLiteCapabilityUnitOfWorkFactory,
    SQLiteDatabase,
)

DEV_LAMBDA = 0.9
FORBIDDEN_RESULT_FIELDS = {
    "dataset_id",
    "final_success",
    "official_dataset_id",
    "oracle",
    "phase",
    "replication",
    "seed",
    "true_success_probability",
    "u_correction",
}


def build_database(path: Path) -> SQLiteDatabase:
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    return database


def build_performance(
    *,
    identifier: str,
    sequence_index: int,
    intrinsic_success: bool = True,
    capability_key: str = "ALPHA",
    source_type: SourceType = SourceType.DIRECT_ENVIRONMENT,
) -> CapabilityPerformanceObservation:
    return CapabilityPerformanceObservation(
        id=identifier,
        agent_id="agent-1",
        trial_id=f"trial-{identifier}",
        cycle_id=f"cycle-{identifier}",
        sequence_index=sequence_index,
        capability_key=capability_key,
        intrinsic_success=intrinsic_success,
        observed_at=datetime(2026, 8, 8, 12, sequence_index, tzinfo=UTC),
        source_type=source_type,
    )


def persist_performances(
    factory: SQLiteCapabilityUnitOfWorkFactory,
    *performances: CapabilityPerformanceObservation,
) -> None:
    with factory() as unit_of_work:
        for performance in performances:
            unit_of_work.capability_performances.add(performance)
        unit_of_work.commit()


def get_current_state(
    factory: SQLiteCapabilityUnitOfWorkFactory,
    *,
    capability_key: str = "ALPHA",
) -> VersionedMetacognitiveCapabilityState | None:
    with factory() as unit_of_work:
        return unit_of_work.metacognitive_states.get_current(
            agent_id="agent-1",
            capability_key=capability_key,
        )


def build_service(
    factory: SQLiteCapabilityUnitOfWorkFactory,
    *,
    lambda_: float = DEV_LAMBDA,
) -> MetacognitiveCapabilityUpdateService:
    return MetacognitiveCapabilityUpdateService(
        unit_of_work_factory=factory,
        estimator=DecayedBetaEstimator(lambda_=lambda_),
    )


def test_metacognitive_update_result_exposes_no_private_experimental_fields() -> None:
    assert FORBIDDEN_RESULT_FIELDS.isdisjoint(MetacognitiveCapabilityUpdateResult.model_fields)


@pytest.mark.parametrize("intrinsic_success", (True, False))
def test_first_performance_updates_the_prior_to_version_two(
    tmp_path: Path,
    intrinsic_success: bool,
) -> None:
    database = build_database(tmp_path / f"first-{intrinsic_success}.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    performance = build_performance(
        identifier="performance-1",
        sequence_index=0,
        intrinsic_success=intrinsic_success,
    )
    persist_performances(factory, performance)
    estimator = DecayedBetaEstimator(lambda_=DEV_LAMBDA)

    result = MetacognitiveCapabilityUpdateService(
        unit_of_work_factory=factory,
        estimator=estimator,
    ).process(performance_id=performance.id)

    prior = estimator.initial_state()
    expected_state = estimator.update(prior, intrinsic_success)
    assert get_current_state(factory) == VersionedMetacognitiveCapabilityState(
        agent_id=performance.agent_id,
        capability_key=performance.capability_key,
        version=2,
        state=expected_state,
        last_processed_performance_id=performance.id,
        last_processed_sequence_index=performance.sequence_index,
    )
    assert result.performance_id == performance.id
    assert result.agent_id == performance.agent_id
    assert result.capability_key == performance.capability_key
    assert result.status is MetacognitiveUpdateStatus.APPLIED
    assert result.previous_version == 1
    assert result.resulting_version == 2
    assert result.previous_estimated_success == prior.estimated_success
    assert result.resulting_estimated_success == expected_state.estimated_success


def test_second_performance_reaches_version_three_and_matches_replay(tmp_path: Path) -> None:
    database = build_database(tmp_path / "second.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first = build_performance(
        identifier="performance-1",
        sequence_index=0,
        intrinsic_success=True,
    )
    second = build_performance(
        identifier="performance-2",
        sequence_index=1,
        intrinsic_success=False,
    )
    persist_performances(factory, first, second)
    estimator = DecayedBetaEstimator(lambda_=DEV_LAMBDA)
    service = MetacognitiveCapabilityUpdateService(
        unit_of_work_factory=factory,
        estimator=estimator,
    )

    service.process(performance_id=first.id)
    result = service.process(performance_id=second.id)

    expected_state = estimator.replay((True, False))
    current = get_current_state(factory)
    assert current == VersionedMetacognitiveCapabilityState(
        agent_id=second.agent_id,
        capability_key=second.capability_key,
        version=3,
        state=expected_state,
        last_processed_performance_id=second.id,
        last_processed_sequence_index=second.sequence_index,
    )
    assert result.status is MetacognitiveUpdateStatus.APPLIED
    assert result.previous_version == 2
    assert result.resulting_version == 3
    assert result.resulting_estimated_success == expected_state.estimated_success


def test_processing_the_current_cursor_twice_is_idempotent(tmp_path: Path) -> None:
    database = build_database(tmp_path / "duplicate.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    performance = build_performance(identifier="performance-1", sequence_index=0)
    persist_performances(factory, performance)
    service = build_service(factory)
    service.process(performance_id=performance.id)
    state_after_first_call = get_current_state(factory)
    assert state_after_first_call is not None

    result = service.process(performance_id=performance.id)

    assert get_current_state(factory) == state_after_first_call
    assert result.status is MetacognitiveUpdateStatus.ALREADY_PROCESSED
    assert result.previous_version == state_after_first_call.version
    assert result.resulting_version == state_after_first_call.version
    assert result.previous_estimated_success == state_after_first_call.state.estimated_success
    assert result.resulting_estimated_success == state_after_first_call.state.estimated_success


def test_a_previously_processed_performance_before_the_cursor_is_idempotent(
    tmp_path: Path,
) -> None:
    database = build_database(tmp_path / "older.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first = build_performance(identifier="performance-1", sequence_index=0)
    second = build_performance(identifier="performance-2", sequence_index=1)
    persist_performances(factory, first, second)
    service = build_service(factory)
    service.process(performance_id=first.id)
    service.process(performance_id=second.id)
    state_before_replay = get_current_state(factory)
    assert state_before_replay is not None

    result = service.process(performance_id=first.id)

    assert result.status is MetacognitiveUpdateStatus.ALREADY_PROCESSED
    assert result.previous_version == state_before_replay.version
    assert result.resulting_version == state_before_replay.version
    assert result.previous_estimated_success == state_before_replay.state.estimated_success
    assert result.resulting_estimated_success == state_before_replay.state.estimated_success
    assert get_current_state(factory) == state_before_replay


def test_skipping_an_earlier_performance_of_the_same_capability_is_rejected(
    tmp_path: Path,
) -> None:
    database = build_database(tmp_path / "same-capability-gap.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first = build_performance(identifier="performance-1", sequence_index=0)
    skipped = build_performance(identifier="performance-2", sequence_index=1)
    requested = build_performance(identifier="performance-3", sequence_index=2)
    persist_performances(factory, first, skipped, requested)
    service = build_service(factory)
    service.process(performance_id=first.id)
    state_before_rejection = get_current_state(factory)

    with pytest.raises(CapabilityPerformanceOrderError):
        service.process(performance_id=requested.id)

    assert get_current_state(factory) == state_before_rejection


def test_a_sequence_gap_used_only_by_another_capability_is_accepted(tmp_path: Path) -> None:
    database = build_database(tmp_path / "other-capability-gap.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first = build_performance(
        identifier="alpha-1",
        sequence_index=0,
        intrinsic_success=True,
    )
    other_capability = build_performance(
        identifier="beta-1",
        sequence_index=1,
        capability_key="BETA",
        intrinsic_success=False,
    )
    second = build_performance(
        identifier="alpha-2",
        sequence_index=2,
        intrinsic_success=False,
    )
    persist_performances(factory, first, other_capability, second)
    estimator = DecayedBetaEstimator(lambda_=DEV_LAMBDA)
    service = MetacognitiveCapabilityUpdateService(
        unit_of_work_factory=factory,
        estimator=estimator,
    )
    service.process(performance_id=first.id)

    result = service.process(performance_id=second.id)

    assert result.status is MetacognitiveUpdateStatus.APPLIED
    current = get_current_state(factory)
    assert current is not None
    assert current.version == 3
    assert current.state == estimator.replay((True, False))
    assert current.last_processed_performance_id == second.id
    assert current.last_processed_sequence_index == second.sequence_index
    assert get_current_state(factory, capability_key="BETA") is None


def test_unauthorized_provenance_between_valid_proofs_is_not_a_causal_gap(
    tmp_path: Path,
) -> None:
    database = build_database(tmp_path / "unauthorized-gap.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first = build_performance(
        identifier="performance-1",
        sequence_index=0,
        intrinsic_success=True,
    )
    unauthorized = build_performance(
        identifier="performance-2",
        sequence_index=1,
        intrinsic_success=True,
        source_type=SourceType.IMAGINATION,
    )
    second = build_performance(
        identifier="performance-3",
        sequence_index=2,
        intrinsic_success=False,
    )
    persist_performances(factory, first, unauthorized, second)
    estimator = DecayedBetaEstimator(lambda_=DEV_LAMBDA)
    service = MetacognitiveCapabilityUpdateService(
        unit_of_work_factory=factory,
        estimator=estimator,
    )
    service.process(performance_id=first.id)

    result = service.process(performance_id=second.id)

    current = get_current_state(factory)
    assert result.status is MetacognitiveUpdateStatus.APPLIED
    assert current is not None
    assert current.version == 3
    assert current.state == estimator.replay((True, False))
    assert current.last_processed_performance_id == second.id
    assert current.last_processed_sequence_index == second.sequence_index
    with factory() as unit_of_work:
        assert unit_of_work.capability_performances.get(unauthorized.id) == unauthorized


UNAUTHORIZED_SOURCE_TYPES = tuple(
    source_type for source_type in SourceType if source_type is not SourceType.DIRECT_ENVIRONMENT
)


@pytest.mark.parametrize("source_type", UNAUTHORIZED_SOURCE_TYPES)
def test_unauthorized_provenance_is_rejected_without_state_change(
    tmp_path: Path,
    source_type: SourceType,
) -> None:
    database = build_database(tmp_path / f"provenance-{source_type.value}.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    performance = build_performance(
        identifier="performance-1",
        sequence_index=0,
        source_type=source_type,
    )
    persist_performances(factory, performance)

    with pytest.raises(CapabilityPerformanceProvenanceError):
        build_service(factory).process(performance_id=performance.id)

    assert get_current_state(factory) is None
    with factory() as unit_of_work:
        assert unit_of_work.capability_performances.get(performance.id) == performance


def test_a_missing_persisted_performance_is_rejected(tmp_path: Path) -> None:
    database = build_database(tmp_path / "missing.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)

    with pytest.raises(CapabilityPerformanceNotFoundError):
        build_service(factory).process(performance_id="missing-performance")

    assert get_current_state(factory) is None


def test_an_existing_state_with_another_lambda_is_rejected_without_change(
    tmp_path: Path,
) -> None:
    database = build_database(tmp_path / "lambda-mismatch.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    performance = build_performance(identifier="performance-1", sequence_index=0)
    existing = VersionedMetacognitiveCapabilityState(
        agent_id=performance.agent_id,
        capability_key=performance.capability_key,
        version=1,
        state=MetacognitiveCapabilityState(alpha=3.0, beta=2.0, lambda_=0.8),
        last_processed_performance_id=None,
        last_processed_sequence_index=None,
    )
    with factory() as unit_of_work:
        unit_of_work.capability_performances.add(performance)
        unit_of_work.metacognitive_states.replace_current(
            state=existing,
            expected_version=None,
        )
        unit_of_work.commit()

    with pytest.raises(MetacognitiveLambdaMismatchError):
        build_service(factory).process(performance_id=performance.id)

    assert get_current_state(factory) == existing


def test_an_invalid_persisted_prior_is_rejected_without_change(tmp_path: Path) -> None:
    database = build_database(tmp_path / "invalid-prior.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    performance = build_performance(identifier="performance-1", sequence_index=0)
    invalid_prior = VersionedMetacognitiveCapabilityState(
        agent_id=performance.agent_id,
        capability_key=performance.capability_key,
        version=1,
        state=MetacognitiveCapabilityState(alpha=9.0, beta=2.0, lambda_=DEV_LAMBDA),
    )
    with factory() as unit_of_work:
        unit_of_work.capability_performances.add(performance)
        unit_of_work.metacognitive_states.replace_current(
            state=invalid_prior,
            expected_version=None,
        )
        unit_of_work.commit()

    with pytest.raises(MetacognitiveStateIntegrityError, match="prior DEV"):
        build_service(factory).process(performance_id=performance.id)

    assert get_current_state(factory) == invalid_prior


def test_a_cursor_from_another_capability_is_rejected_without_change(
    tmp_path: Path,
) -> None:
    database = build_database(tmp_path / "invalid-cursor-scope.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    other_capability = build_performance(
        identifier="beta-1",
        sequence_index=1,
        capability_key="BETA",
    )
    requested = build_performance(identifier="alpha-1", sequence_index=2)
    estimator = DecayedBetaEstimator(lambda_=DEV_LAMBDA)
    prior = VersionedMetacognitiveCapabilityState(
        agent_id=requested.agent_id,
        capability_key=requested.capability_key,
        version=1,
        state=estimator.initial_state(),
    )
    invalid_current = VersionedMetacognitiveCapabilityState(
        agent_id=requested.agent_id,
        capability_key=requested.capability_key,
        version=2,
        state=estimator.update(prior.state, True),
        last_processed_performance_id=other_capability.id,
        last_processed_sequence_index=other_capability.sequence_index,
    )
    with factory() as unit_of_work:
        unit_of_work.capability_performances.add(other_capability)
        unit_of_work.capability_performances.add(requested)
        unit_of_work.metacognitive_states.replace_current(
            state=prior,
            expected_version=None,
        )
        unit_of_work.metacognitive_states.replace_current(
            state=invalid_current,
            expected_version=prior.version,
        )
        unit_of_work.commit()

    with pytest.raises(MetacognitiveStateIntegrityError, match="preuve propre"):
        build_service(factory).process(performance_id=requested.id)

    assert get_current_state(factory) == invalid_current


def test_metacognitive_persistence_failure_rolls_back_the_created_prior(
    tmp_path: Path,
) -> None:
    database = build_database(tmp_path / "update-rollback.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    performance = build_performance(identifier="performance-1", sequence_index=0)
    persist_performances(factory, performance)
    with database.connect() as connection:
        connection.execute(
            """
            CREATE TRIGGER fail_metacognitive_version_two
            BEFORE UPDATE ON metacognitive_states
            WHEN NEW.version = 2
            BEGIN
                SELECT RAISE(ABORT, 'échec métacognitif injecté');
            END
            """
        )

    with pytest.raises(sqlite3.IntegrityError, match="inject"):
        build_service(factory).process(performance_id=performance.id)

    assert get_current_state(factory) is None
    with factory() as unit_of_work:
        assert unit_of_work.capability_performances.get(performance.id) == performance


def test_reopen_preserves_ignored_provenance_and_past_idempotence(tmp_path: Path) -> None:
    database_path = tmp_path / "reopen.db"
    database = build_database(database_path)
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first = build_performance(identifier="performance-1", sequence_index=0)
    unauthorized = build_performance(
        identifier="performance-2",
        sequence_index=1,
        source_type=SourceType.IMAGINATION,
    )
    second = build_performance(
        identifier="performance-3",
        sequence_index=2,
        intrinsic_success=False,
    )
    persist_performances(factory, first, unauthorized, second)
    build_service(factory).process(performance_id=first.id)

    reopened_database = SQLiteDatabase(database_path)
    reopened_database.initialize_capability_schema()
    reopened_factory = SQLiteCapabilityUnitOfWorkFactory(reopened_database)
    estimator = DecayedBetaEstimator(lambda_=DEV_LAMBDA)
    applied = build_service(reopened_factory).process(performance_id=second.id)
    state_after_second = get_current_state(reopened_factory)
    assert state_after_second is not None

    reopened_again = SQLiteDatabase(database_path)
    reopened_again.initialize_capability_schema()
    reopened_again_factory = SQLiteCapabilityUnitOfWorkFactory(reopened_again)
    replayed = build_service(reopened_again_factory).process(
        performance_id=first.id,
    )

    assert applied.status is MetacognitiveUpdateStatus.APPLIED
    assert state_after_second.version == 3
    assert state_after_second.state == estimator.replay((True, False))
    assert state_after_second.last_processed_performance_id == second.id
    assert state_after_second.last_processed_sequence_index == second.sequence_index
    assert replayed.status is MetacognitiveUpdateStatus.ALREADY_PROCESSED
    assert replayed.previous_version == state_after_second.version
    assert replayed.resulting_version == state_after_second.version
    assert get_current_state(reopened_again_factory) == state_after_second
    with reopened_again_factory() as unit_of_work:
        assert unit_of_work.capability_performances.get(unauthorized.id) == unauthorized
