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
from soinesis.domain.models import SourceType
from soinesis.infrastructure.sqlite import (
    MetacognitiveStateConflictError,
    SQLiteCapabilityUnitOfWorkFactory,
    SQLiteDatabase,
)


def build_database(path: Path) -> SQLiteDatabase:
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    return database


def build_observation(
    *,
    identifier: str,
    sequence_index: int,
    agent_id: str = "agent-1",
    capability_key: str = "ALPHA",
    trial_id: str | None = None,
    intrinsic_success: bool = True,
    minute: int = 0,
) -> CapabilityPerformanceObservation:
    return CapabilityPerformanceObservation(
        id=identifier,
        agent_id=agent_id,
        trial_id=trial_id or f"trial-{identifier}",
        cycle_id=f"cycle-{identifier}",
        sequence_index=sequence_index,
        capability_key=capability_key,
        intrinsic_success=intrinsic_success,
        observed_at=datetime(2026, 8, 8, 12, minute, tzinfo=UTC),
        source_type=SourceType.DIRECT_ENVIRONMENT,
    )


def build_metacognitive_state(
    *,
    version: int,
    agent_id: str = "agent-1",
    capability_key: str = "ALPHA",
    alpha: float = 3.0,
    beta: float = 2.0,
    last_processed_performance_id: str | None = None,
    last_processed_sequence_index: int | None = None,
) -> VersionedMetacognitiveCapabilityState:
    if version > 1:
        last_processed_performance_id = (
            last_processed_performance_id or f"performance-{version - 1}"
        )
        if last_processed_sequence_index is None:
            last_processed_sequence_index = version - 2
    return VersionedMetacognitiveCapabilityState(
        agent_id=agent_id,
        capability_key=capability_key,
        version=version,
        state=MetacognitiveCapabilityState(alpha=alpha, beta=beta, lambda_=0.9),
        last_processed_performance_id=last_processed_performance_id,
        last_processed_sequence_index=last_processed_sequence_index,
    )


def build_self_model_version(
    *,
    identifier: str,
    version: int,
    agent_id: str = "agent-1",
    previous_version_id: str | None = None,
    created_at: datetime | None = None,
) -> SelfModelVersion:
    return SelfModelVersion(
        id=identifier,
        agent_id=agent_id,
        version=version,
        previous_version_id=previous_version_id,
        created_at=created_at or datetime(2026, 8, 8, tzinfo=UTC),
    )


def build_self_attribute(
    *,
    identifier: str,
    self_model_version_id: str,
    attribute_version: int,
    agent_id: str = "agent-1",
    capability_key: str = "ALPHA",
    previous_attribute_id: str | None = None,
    estimated_success: float = 0.6,
    created_at: datetime | None = None,
) -> CapabilitySelfAttribute:
    return CapabilitySelfAttribute(
        id=identifier,
        agent_id=agent_id,
        capability_key=capability_key,
        estimated_success=estimated_success,
        self_model_version_id=self_model_version_id,
        attribute_version=attribute_version,
        previous_attribute_id=previous_attribute_id,
        created_at=created_at or datetime(2026, 8, 8, tzinfo=UTC),
    )


def test_performance_add_and_read_round_trip(tmp_path: Path) -> None:
    database = build_database(tmp_path / "performance.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    observation = build_observation(
        identifier="performance-1",
        sequence_index=0,
        intrinsic_success=False,
    )

    with factory() as unit_of_work:
        unit_of_work.capability_performances.add(observation)
        unit_of_work.commit()

    with factory() as unit_of_work:
        persisted = unit_of_work.capability_performances.get(observation.id)
        missing = unit_of_work.capability_performances.get("missing")
        history = unit_of_work.capability_performances.list_before(
            boundary=CapabilityHistoryBoundary(
                agent_id="agent-1",
                capability_key="ALPHA",
                trial_id="trial-current",
                cycle_id="cycle-current",
                sequence_index=1,
            )
        )

    assert persisted == observation
    assert missing is None
    assert history == [observation]


@pytest.mark.parametrize("conflict", ("id", "trial", "sequence"))
def test_performance_rejects_ambiguous_duplicates(tmp_path: Path, conflict: str) -> None:
    database = build_database(tmp_path / f"performance-{conflict}.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    original = build_observation(identifier="original", sequence_index=0)
    conflicting = build_observation(
        identifier="original" if conflict == "id" else "conflicting",
        trial_id=original.trial_id if conflict == "trial" else None,
        sequence_index=original.sequence_index if conflict == "sequence" else 1,
    )

    with factory() as unit_of_work:
        unit_of_work.capability_performances.add(original)
        unit_of_work.commit()

    with pytest.raises(sqlite3.IntegrityError), factory() as unit_of_work:
        unit_of_work.capability_performances.add(conflicting)


def test_performance_is_immutable_in_sqlite(tmp_path: Path) -> None:
    database = build_database(tmp_path / "performance-immutable.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    observation = build_observation(identifier="immutable", sequence_index=0)
    with factory() as unit_of_work:
        unit_of_work.capability_performances.add(observation)
        unit_of_work.commit()

    with pytest.raises(sqlite3.IntegrityError, match="immuable"), database.connect() as connection:
        connection.execute(
            "UPDATE capability_performances SET intrinsic_success = 0 WHERE id = ?",
            (observation.id,),
        )
    with (
        pytest.raises(
            sqlite3.IntegrityError,
            match="append-only",
        ),
        database.connect() as connection,
    ):
        connection.execute(
            "DELETE FROM capability_performances WHERE id = ?",
            (observation.id,),
        )


def test_list_before_filters_scope_and_excludes_current_and_future(tmp_path: Path) -> None:
    database = build_database(tmp_path / "performance-history.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    observations = (
        build_observation(identifier="future", sequence_index=6),
        build_observation(identifier="past-3", sequence_index=3, minute=3),
        build_observation(identifier="other-agent", sequence_index=2, agent_id="agent-2"),
        build_observation(
            identifier="other-capability",
            sequence_index=1,
            capability_key="BETA",
        ),
        build_observation(identifier="current", sequence_index=5),
        build_observation(identifier="past-0", sequence_index=0, minute=5),
    )
    with factory() as unit_of_work:
        for observation in observations:
            unit_of_work.capability_performances.add(observation)
        unit_of_work.commit()

    boundary = CapabilityHistoryBoundary(
        agent_id="agent-1",
        capability_key="ALPHA",
        trial_id="trial-current",
        cycle_id="cycle-current",
        sequence_index=5,
    )
    with factory() as unit_of_work:
        first = unit_of_work.capability_performances.list_before(boundary=boundary)
        second = unit_of_work.capability_performances.list_before(boundary=boundary)

    assert [observation.id for observation in first] == ["past-0", "past-3"]
    assert second == first
    assert all(observation.agent_id == boundary.agent_id for observation in first)
    assert all(observation.capability_key == boundary.capability_key for observation in first)
    assert all(observation.sequence_index < boundary.sequence_index for observation in first)


def test_metacognitive_state_creation_and_update_are_versioned(tmp_path: Path) -> None:
    database = build_database(tmp_path / "metacognitive.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first = build_metacognitive_state(version=1)
    second = build_metacognitive_state(version=2, alpha=4.0, beta=2.5)

    with factory() as unit_of_work:
        unit_of_work.metacognitive_states.replace_current(
            state=first,
            expected_version=None,
        )
        unit_of_work.commit()
    with factory() as unit_of_work:
        unit_of_work.metacognitive_states.replace_current(
            state=second,
            expected_version=1,
        )
        unit_of_work.commit()
    with factory() as unit_of_work:
        current = unit_of_work.metacognitive_states.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )

    assert current is not None
    assert current == second
    assert current.last_processed_performance_id == "performance-1"
    assert current.last_processed_sequence_index == 0


def test_metacognitive_state_rejects_invalid_initial_and_version_jump(tmp_path: Path) -> None:
    database = build_database(tmp_path / "metacognitive-jump.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)

    with pytest.raises(ValueError, match="version 1"), factory() as unit_of_work:
        unit_of_work.metacognitive_states.replace_current(
            state=build_metacognitive_state(version=2),
            expected_version=None,
        )

    with factory() as unit_of_work:
        unit_of_work.metacognitive_states.replace_current(
            state=build_metacognitive_state(version=1),
            expected_version=None,
        )
        unit_of_work.commit()

    with pytest.raises(ValueError, match="suivre"), factory() as unit_of_work:
        unit_of_work.metacognitive_states.replace_current(
            state=build_metacognitive_state(version=3),
            expected_version=1,
        )


def test_metacognitive_state_rejects_concurrent_creation(tmp_path: Path) -> None:
    database = build_database(tmp_path / "metacognitive-create-conflict.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first = build_metacognitive_state(version=1)
    with factory() as unit_of_work:
        unit_of_work.metacognitive_states.replace_current(
            state=first,
            expected_version=None,
        )
        unit_of_work.commit()

    with (
        pytest.raises(
            MetacognitiveStateConflictError,
            match="existe déjà",
        ),
        factory() as unit_of_work,
    ):
        unit_of_work.metacognitive_states.replace_current(
            state=first,
            expected_version=None,
        )


def test_metacognitive_state_rejects_stale_expected_version_without_overwrite(
    tmp_path: Path,
) -> None:
    database = build_database(tmp_path / "metacognitive-stale.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first = build_metacognitive_state(version=1)
    second = build_metacognitive_state(version=2, alpha=4.0)
    stale_second = build_metacognitive_state(version=2, beta=3.0)
    with factory() as unit_of_work:
        unit_of_work.metacognitive_states.replace_current(
            state=first,
            expected_version=None,
        )
        unit_of_work.commit()
    with factory() as unit_of_work:
        unit_of_work.metacognitive_states.replace_current(
            state=second,
            expected_version=1,
        )
        unit_of_work.commit()

    with (
        pytest.raises(
            MetacognitiveStateConflictError,
            match="version attendue",
        ),
        factory() as unit_of_work,
    ):
        unit_of_work.metacognitive_states.replace_current(
            state=stale_second,
            expected_version=1,
        )

    with factory() as unit_of_work:
        current = unit_of_work.metacognitive_states.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
    assert current == second


def test_current_state_and_snapshot_reads_are_scoped(tmp_path: Path) -> None:
    database = build_database(tmp_path / "scoped-reads.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    state = build_metacognitive_state(version=1)
    model = build_self_model_version(identifier="self-model-1", version=1)
    attribute = build_self_attribute(
        identifier="attribute-1",
        self_model_version_id=model.id,
        attribute_version=1,
    )
    with factory() as unit_of_work:
        unit_of_work.metacognitive_states.replace_current(
            state=state,
            expected_version=None,
        )
        unit_of_work.self_model_versions.add(model)
        unit_of_work.capability_self_attributes.add(attribute)
        unit_of_work.commit()

    with factory() as unit_of_work:
        assert (
            unit_of_work.metacognitive_states.get_current(
                agent_id="agent-2",
                capability_key="ALPHA",
            )
            is None
        )
        assert (
            unit_of_work.metacognitive_states.get_current(
                agent_id="agent-1",
                capability_key="BETA",
            )
            is None
        )
        assert unit_of_work.self_model_versions.get_current(agent_id="agent-2") is None
        assert unit_of_work.self_model_versions.list_versions(agent_id="agent-2") == []
        assert (
            unit_of_work.capability_self_attributes.get_current(
                agent_id="agent-1",
                capability_key="BETA",
            )
            is None
        )
        assert (
            unit_of_work.capability_self_attributes.list_versions(
                agent_id="agent-2",
                capability_key="ALPHA",
            )
            == []
        )


def test_self_model_is_append_only_and_ordered_by_version(tmp_path: Path) -> None:
    database = build_database(tmp_path / "self-model.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first = build_self_model_version(
        identifier="self-model-1",
        version=1,
        created_at=datetime(2026, 8, 9, tzinfo=UTC),
    )
    second = build_self_model_version(
        identifier="self-model-2",
        version=2,
        previous_version_id=first.id,
        created_at=datetime(2026, 8, 8, tzinfo=UTC),
    )
    with factory() as unit_of_work:
        unit_of_work.self_model_versions.add(first)
        unit_of_work.self_model_versions.add(second)
        unit_of_work.commit()

    with factory() as unit_of_work:
        current = unit_of_work.self_model_versions.get_current(agent_id="agent-1")
        history = unit_of_work.self_model_versions.list_versions(agent_id="agent-1")

    assert current == second
    assert history == [first, second]


@pytest.mark.parametrize(
    "invalid_version",
    (
        build_self_model_version(
            identifier="wrong-predecessor",
            version=2,
            previous_version_id="not-current",
        ),
        build_self_model_version(
            identifier="version-jump",
            version=3,
            previous_version_id="self-model-1",
        ),
        build_self_model_version(
            identifier="other-agent-predecessor",
            agent_id="agent-2",
            version=2,
            previous_version_id="self-model-1",
        ),
    ),
)
def test_self_model_rejects_invalid_chain(
    tmp_path: Path,
    invalid_version: SelfModelVersion,
) -> None:
    database = build_database(tmp_path / f"{invalid_version.id}.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    with factory() as unit_of_work:
        unit_of_work.self_model_versions.add(
            build_self_model_version(identifier="self-model-1", version=1)
        )
        unit_of_work.commit()

    with pytest.raises(ValueError, match=r"version|prolonger"), factory() as unit_of_work:
        unit_of_work.self_model_versions.add(invalid_version)


def test_self_model_rejects_duplicate_id_and_version(tmp_path: Path) -> None:
    database = build_database(tmp_path / "self-model-duplicates.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first = build_self_model_version(identifier="shared-id", version=1)
    with factory() as unit_of_work:
        unit_of_work.self_model_versions.add(first)
        unit_of_work.commit()

    with pytest.raises(ValueError), factory() as unit_of_work:
        unit_of_work.self_model_versions.add(
            build_self_model_version(identifier="duplicate-version", version=1)
        )
    with pytest.raises(sqlite3.IntegrityError), factory() as unit_of_work:
        unit_of_work.self_model_versions.add(
            build_self_model_version(identifier="shared-id", agent_id="agent-2", version=1)
        )


def test_self_attribute_is_append_only_scoped_and_ordered(tmp_path: Path) -> None:
    database = build_database(tmp_path / "self-attribute.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first_model = build_self_model_version(identifier="self-model-1", version=1)
    second_model = build_self_model_version(
        identifier="self-model-2",
        version=2,
        previous_version_id=first_model.id,
    )
    first = build_self_attribute(
        identifier="attribute-1",
        self_model_version_id=first_model.id,
        attribute_version=1,
        created_at=datetime(2026, 8, 9, tzinfo=UTC),
    )
    second = build_self_attribute(
        identifier="attribute-2",
        self_model_version_id=second_model.id,
        attribute_version=2,
        previous_attribute_id=first.id,
        estimated_success=0.7,
        created_at=datetime(2026, 8, 8, tzinfo=UTC),
    )
    with factory() as unit_of_work:
        unit_of_work.self_model_versions.add(first_model)
        unit_of_work.self_model_versions.add(second_model)
        unit_of_work.capability_self_attributes.add(first)
        unit_of_work.capability_self_attributes.add(second)
        unit_of_work.commit()

    with factory() as unit_of_work:
        current = unit_of_work.capability_self_attributes.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
        history = unit_of_work.capability_self_attributes.list_versions(
            agent_id="agent-1",
            capability_key="ALPHA",
        )

    assert current == second
    assert history == [first, second]


def test_self_attribute_rejects_wrong_model_owner_and_missing_model(tmp_path: Path) -> None:
    database = build_database(tmp_path / "attribute-model-owner.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    with factory() as unit_of_work:
        unit_of_work.self_model_versions.add(
            build_self_model_version(identifier="agent-1-model", version=1)
        )
        unit_of_work.commit()

    invalid_attributes = (
        build_self_attribute(
            identifier="wrong-owner",
            agent_id="agent-2",
            self_model_version_id="agent-1-model",
            attribute_version=1,
        ),
        build_self_attribute(
            identifier="missing-model",
            self_model_version_id="missing",
            attribute_version=1,
        ),
    )
    for attribute in invalid_attributes:
        with pytest.raises(ValueError, match="même agent"), factory() as unit_of_work:
            unit_of_work.capability_self_attributes.add(attribute)


def test_self_attribute_rejects_a_predecessor_from_another_capability(
    tmp_path: Path,
) -> None:
    database = build_database(tmp_path / "attribute-other-capability.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first_model = build_self_model_version(identifier="self-model-1", version=1)
    second_model = build_self_model_version(
        identifier="self-model-2",
        version=2,
        previous_version_id=first_model.id,
    )
    alpha = build_self_attribute(
        identifier="alpha-1",
        self_model_version_id=first_model.id,
        attribute_version=1,
    )
    beta = build_self_attribute(
        identifier="beta-1",
        self_model_version_id=first_model.id,
        attribute_version=1,
        capability_key="BETA",
    )
    invalid_alpha = build_self_attribute(
        identifier="alpha-2",
        self_model_version_id=second_model.id,
        attribute_version=2,
        previous_attribute_id=beta.id,
    )
    with factory() as unit_of_work:
        unit_of_work.self_model_versions.add(first_model)
        unit_of_work.self_model_versions.add(second_model)
        unit_of_work.capability_self_attributes.add(alpha)
        unit_of_work.capability_self_attributes.add(beta)
        unit_of_work.commit()

    with pytest.raises(ValueError, match="prolonger"), factory() as unit_of_work:
        unit_of_work.capability_self_attributes.add(invalid_alpha)


@pytest.mark.parametrize(
    "invalid_attribute",
    (
        build_self_attribute(
            identifier="wrong-predecessor",
            self_model_version_id="self-model-2",
            attribute_version=2,
            previous_attribute_id="not-current",
        ),
        build_self_attribute(
            identifier="attribute-jump",
            self_model_version_id="self-model-2",
            attribute_version=3,
            previous_attribute_id="attribute-1",
        ),
        build_self_attribute(
            identifier="duplicate-version",
            self_model_version_id="self-model-2",
            attribute_version=1,
        ),
    ),
)
def test_self_attribute_rejects_invalid_chain(
    tmp_path: Path,
    invalid_attribute: CapabilitySelfAttribute,
) -> None:
    database = build_database(tmp_path / f"{invalid_attribute.id}.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    first_model = build_self_model_version(identifier="self-model-1", version=1)
    second_model = build_self_model_version(
        identifier="self-model-2",
        version=2,
        previous_version_id=first_model.id,
    )
    first_attribute = build_self_attribute(
        identifier="attribute-1",
        self_model_version_id=first_model.id,
        attribute_version=1,
    )
    with factory() as unit_of_work:
        unit_of_work.self_model_versions.add(first_model)
        unit_of_work.self_model_versions.add(second_model)
        unit_of_work.capability_self_attributes.add(first_attribute)
        unit_of_work.commit()

    with pytest.raises(ValueError, match=r"version|prolonger"), factory() as unit_of_work:
        unit_of_work.capability_self_attributes.add(invalid_attribute)


def test_self_model_and_attribute_rows_reject_update_and_delete(tmp_path: Path) -> None:
    database = build_database(tmp_path / "append-only.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    model = build_self_model_version(identifier="self-model-1", version=1)
    attribute = build_self_attribute(
        identifier="attribute-1",
        self_model_version_id=model.id,
        attribute_version=1,
    )
    with factory() as unit_of_work:
        unit_of_work.self_model_versions.add(model)
        unit_of_work.capability_self_attributes.add(attribute)
        unit_of_work.commit()

    statements = (
        ("UPDATE self_model_versions SET created_at = created_at WHERE id = ?", model.id),
        ("DELETE FROM self_model_versions WHERE id = ?", model.id),
        (
            "UPDATE capability_self_attributes SET created_at = created_at WHERE id = ?",
            attribute.id,
        ),
        ("DELETE FROM capability_self_attributes WHERE id = ?", attribute.id),
    )
    for statement, identifier in statements:
        with pytest.raises(sqlite3.IntegrityError), database.connect() as connection:
            connection.execute(statement, (identifier,))


def test_sqlite_rejects_replace_for_all_persistent_capability_rows(tmp_path: Path) -> None:
    database = build_database(tmp_path / "no-replace.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    performance = build_observation(identifier="performance-1", sequence_index=0)
    state = build_metacognitive_state(version=1)
    model = build_self_model_version(identifier="self-model-1", version=1)
    attribute = build_self_attribute(
        identifier="attribute-1",
        self_model_version_id=model.id,
        attribute_version=1,
    )
    with factory() as unit_of_work:
        unit_of_work.capability_performances.add(performance)
        unit_of_work.metacognitive_states.replace_current(
            state=state,
            expected_version=None,
        )
        unit_of_work.self_model_versions.add(model)
        unit_of_work.capability_self_attributes.add(attribute)
        unit_of_work.commit()

    replacement_statements = (
        (
            """
            INSERT OR REPLACE INTO capability_performances (
                id, agent_id, trial_id, cycle_id, sequence_index,
                capability_key, intrinsic_success, observed_at, source_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                performance.id,
                performance.agent_id,
                performance.trial_id,
                performance.cycle_id,
                performance.sequence_index,
                performance.capability_key,
                0,
                performance.observed_at.isoformat(),
                performance.source_type.value,
            ),
        ),
        (
            """
            INSERT OR REPLACE INTO metacognitive_states (
                agent_id, capability_key, version, alpha, beta, decay_lambda
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("agent-1", "ALPHA", 1, 9.0, 2.0, 0.9),
        ),
        (
            """
            INSERT OR REPLACE INTO self_model_versions (
                id, agent_id, version, previous_version_id, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (model.id, model.agent_id, 1, None, "2026-08-09T00:00:00+00:00"),
        ),
        (
            """
            INSERT OR REPLACE INTO capability_self_attributes (
                id, agent_id, attribute_type, capability_key, estimated_success,
                self_model_version_id, attribute_version, previous_attribute_id,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attribute.id,
                attribute.agent_id,
                attribute.attribute_type.value,
                attribute.capability_key,
                0.9,
                attribute.self_model_version_id,
                1,
                None,
                attribute.created_at.isoformat(),
            ),
        ),
    )
    for statement, parameters in replacement_statements:
        with pytest.raises(sqlite3.IntegrityError), database.connect() as connection:
            connection.execute(statement, parameters)

    with factory() as unit_of_work:
        persisted_performances = unit_of_work.capability_performances.list_before(
            boundary=CapabilityHistoryBoundary(
                agent_id="agent-1",
                capability_key="ALPHA",
                trial_id="trial-boundary",
                cycle_id="cycle-boundary",
                sequence_index=1,
            )
        )
        persisted_state = unit_of_work.metacognitive_states.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
        persisted_model = unit_of_work.self_model_versions.get_current(agent_id="agent-1")
        persisted_attribute = unit_of_work.capability_self_attributes.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )

    assert persisted_performances == [performance]
    assert persisted_state == state
    assert persisted_model == model
    assert persisted_attribute == attribute
