import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from soinesis.domain.capabilities import (
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    MetacognitiveCapabilityState,
    SelfModelVersion,
    VersionedMetacognitiveCapabilityState,
)
from soinesis.domain.models import Observation, SourceType
from soinesis.infrastructure.sqlite import (
    SQLiteCapabilityUnitOfWorkFactory,
    SQLiteDatabase,
    SQLiteUnitOfWorkFactory,
)


def build_performance(
    identifier: str,
    sequence_index: int,
) -> CapabilityPerformanceObservation:
    return CapabilityPerformanceObservation(
        id=identifier,
        agent_id="agent-1",
        trial_id=f"trial-{identifier}",
        cycle_id=f"cycle-{identifier}",
        sequence_index=sequence_index,
        capability_key="ALPHA",
        intrinsic_success=True,
        observed_at=datetime(2026, 8, 8, tzinfo=UTC),
        source_type=SourceType.DIRECT_ENVIRONMENT,
    )


def build_snapshot() -> tuple[SelfModelVersion, CapabilitySelfAttribute]:
    model = SelfModelVersion(
        id="self-model-1",
        agent_id="agent-1",
        version=1,
        created_at=datetime(2026, 8, 8, tzinfo=UTC),
    )
    attribute = CapabilitySelfAttribute(
        id="attribute-1",
        agent_id="agent-1",
        capability_key="ALPHA",
        estimated_success=0.6,
        self_model_version_id=model.id,
        attribute_version=1,
        created_at=datetime(2026, 8, 8, tzinfo=UTC),
    )
    return model, attribute


def performance_history(database: SQLiteDatabase) -> list[CapabilityPerformanceObservation]:
    with SQLiteCapabilityUnitOfWorkFactory(database)() as unit_of_work:
        return unit_of_work.capability_performances.list_before(
            boundary=CapabilityHistoryBoundary(
                agent_id="agent-1",
                capability_key="ALPHA",
                trial_id="trial-boundary",
                cycle_id="cycle-boundary",
                sequence_index=100,
            )
        )


def test_capability_uow_commit_persists_multiple_p3_writes(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "commit.db")
    database.initialize_capability_schema()
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    performance = build_performance("performance-1", 0)
    model, attribute = build_snapshot()

    with factory() as unit_of_work:
        unit_of_work.capability_performances.add(performance)
        unit_of_work.self_model_versions.add(model)
        unit_of_work.capability_self_attributes.add(attribute)
        unit_of_work.commit()

    with factory() as unit_of_work:
        current_model = unit_of_work.self_model_versions.get_current(agent_id="agent-1")
        current_attribute = unit_of_work.capability_self_attributes.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )

    assert performance_history(database) == [performance]
    assert current_model == model
    assert current_attribute == attribute


def test_capability_uow_rolls_back_automatically_on_exception(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "exception-rollback.db")
    database.initialize_capability_schema()
    performance = build_performance("performance-1", 0)

    with (
        pytest.raises(
            RuntimeError,
            match="rollback",
        ),
        SQLiteCapabilityUnitOfWorkFactory(database)() as unit_of_work,
    ):
        unit_of_work.capability_performances.add(performance)
        raise RuntimeError("rollback demandé")

    assert performance_history(database) == []


def test_capability_uow_rolls_back_when_commit_is_omitted(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "implicit-rollback.db")
    database.initialize_capability_schema()
    performance = build_performance("performance-1", 0)

    with SQLiteCapabilityUnitOfWorkFactory(database)() as unit_of_work:
        unit_of_work.capability_performances.add(performance)

    assert performance_history(database) == []


def test_late_constraint_failure_rolls_back_all_p3_writes(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "atomic-rollback.db")
    database.initialize_capability_schema()
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    performance = build_performance("performance-1", 0)
    conflicting = build_performance("performance-2", 0)
    model, attribute = build_snapshot()

    with pytest.raises(sqlite3.IntegrityError), factory() as unit_of_work:
        unit_of_work.self_model_versions.add(model)
        unit_of_work.capability_self_attributes.add(attribute)
        unit_of_work.capability_performances.add(performance)
        unit_of_work.capability_performances.add(conflicting)

    with factory() as unit_of_work:
        current_model = unit_of_work.self_model_versions.get_current(agent_id="agent-1")
        current_attribute = unit_of_work.capability_self_attributes.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )

    assert performance_history(database) == []
    assert current_model is None
    assert current_attribute is None


def test_late_failure_rolls_back_metacognitive_state_creation(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "metacognitive-rollback.db")
    database.initialize_capability_schema()
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    state = VersionedMetacognitiveCapabilityState(
        agent_id="agent-1",
        capability_key="ALPHA",
        version=1,
        state=MetacognitiveCapabilityState(alpha=3.0, beta=2.0, lambda_=0.9),
    )
    performance = build_performance("performance-1", 0)
    conflicting = build_performance("performance-2", 0)

    with pytest.raises(sqlite3.IntegrityError), factory() as unit_of_work:
        unit_of_work.metacognitive_states.replace_current(
            state=state,
            expected_version=None,
        )
        unit_of_work.capability_performances.add(performance)
        unit_of_work.capability_performances.add(conflicting)

    with factory() as unit_of_work:
        current = unit_of_work.metacognitive_states.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )

    assert current is None
    assert performance_history(database) == []


def test_performance_can_commit_before_a_separate_failed_revision(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "separate-performance.db")
    database.initialize_capability_schema()
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    performance = build_performance("performance-1", 0)
    model, attribute = build_snapshot()
    with factory() as unit_of_work:
        unit_of_work.capability_performances.add(performance)
        unit_of_work.commit()

    with pytest.raises(RuntimeError, match="revision"), factory() as unit_of_work:
        unit_of_work.self_model_versions.add(model)
        unit_of_work.capability_self_attributes.add(attribute)
        raise RuntimeError("revision interrompue")

    with factory() as unit_of_work:
        assert unit_of_work.self_model_versions.get_current(agent_id="agent-1") is None
        assert (
            unit_of_work.capability_self_attributes.get_current(
                agent_id="agent-1",
                capability_key="ALPHA",
            )
            is None
        )
    assert performance_history(database) == [performance]


def test_historical_uow_and_initializer_remain_unchanged(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "historical.db")
    database.initialize_schema()
    observation = Observation(
        id="observation-1",
        agent_id="agent-1",
        cycle_id="cycle-1",
        source_type=SourceType.JORDAN_INPUT,
        raw_content="Information historique synthétique.",
        received_at=datetime(2026, 8, 8, tzinfo=UTC),
        confidence=1.0,
    )

    with SQLiteUnitOfWorkFactory(database)() as unit_of_work:
        unit_of_work.observations.add(observation)
        unit_of_work.commit()

    with database.connect() as connection:
        stored_id = connection.execute("SELECT id FROM observations").fetchone()["id"]
        capability_table = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'capability_performances'
            """
        ).fetchone()

    assert str(stored_id) == observation.id
    assert capability_table is None
