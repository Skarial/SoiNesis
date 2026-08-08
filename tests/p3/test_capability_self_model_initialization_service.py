import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from soinesis.application.capabilities import (
    CapabilitySelfModelInitializationError,
    CapabilitySelfModelInitializationService,
    CapabilitySelfModelInitializationStatus,
    CapabilitySelfModelIntegrityError,
    DecayedBetaEstimator,
    MetacognitiveCapabilityUpdateService,
)
from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    SelfModelVersion,
    VersionedMetacognitiveCapabilityState,
)
from soinesis.domain.models import EventType, SourceType
from soinesis.infrastructure.sqlite import (
    SQLiteCapabilityUnitOfWorkFactory,
    SQLiteDatabase,
)

DEV_LAMBDA = 0.9
INITIALIZATION_TARGET_TYPE = "CapabilitySelfAttribute"
PRIVATE_JOURNAL_FIELDS = {
    "alpha",
    "beta",
    "dataset_id",
    "decay_lambda",
    "final_success",
    "lambda_",
    "official_dataset_id",
    "oracle",
    "phase",
    "replication",
    "seed",
    "true_success_probability",
    "u_correction",
}


class RecordingClock:
    def __init__(self) -> None:
        self.calls = 0
        self.value = datetime(2026, 8, 8, 20, 30, tzinfo=UTC)

    def now(self) -> datetime:
        self.calls += 1
        return self.value


class SequentialIdentifiers:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self._counts: dict[str, int] = {}

    def new(self, prefix: str) -> str:
        self.calls.append(prefix)
        next_value = self._counts.get(prefix, 0) + 1
        self._counts[prefix] = next_value
        return f"{prefix}-{next_value}"


def build_database(path: Path) -> SQLiteDatabase:
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    return database


def build_initialization_service(
    factory: SQLiteCapabilityUnitOfWorkFactory,
    *,
    clock: RecordingClock | None = None,
    identifiers: SequentialIdentifiers | None = None,
) -> tuple[
    CapabilitySelfModelInitializationService,
    RecordingClock,
    SequentialIdentifiers,
]:
    selected_clock = clock or RecordingClock()
    selected_identifiers = identifiers or SequentialIdentifiers()
    return (
        CapabilitySelfModelInitializationService(
            unit_of_work_factory=factory,
            estimator=DecayedBetaEstimator(lambda_=DEV_LAMBDA),
            clock=selected_clock,
            identifiers=selected_identifiers,
        ),
        selected_clock,
        selected_identifiers,
    )


def build_performance() -> CapabilityPerformanceObservation:
    return CapabilityPerformanceObservation(
        id="performance-1",
        agent_id="agent-1",
        trial_id="trial-1",
        cycle_id="cycle-1",
        sequence_index=0,
        capability_key="ALPHA",
        intrinsic_success=True,
        observed_at=datetime(2026, 8, 8, 20, tzinfo=UTC),
        source_type=SourceType.DIRECT_ENVIRONMENT,
    )


def test_initialization_persists_prior_model_attribute_and_auditable_journal(
    tmp_path: Path,
) -> None:
    database = build_database(tmp_path / "initialization.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    service, clock, identifiers = build_initialization_service(factory)
    estimator = DecayedBetaEstimator(lambda_=DEV_LAMBDA)

    result = service.initialize(agent_id="agent-1", capability_key="ALPHA")

    with factory() as unit_of_work:
        state = unit_of_work.metacognitive_states.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
        model = unit_of_work.self_model_versions.get_current(agent_id="agent-1")
        attribute = unit_of_work.capability_self_attributes.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
        assert attribute is not None
        events = unit_of_work.journal.list_for_target(
            target_entity_type=INITIALIZATION_TARGET_TYPE,
            target_entity_id=attribute.id,
        )

    assert state == VersionedMetacognitiveCapabilityState(
        agent_id="agent-1",
        capability_key="ALPHA",
        version=1,
        state=estimator.initial_state(),
    )
    assert model is not None
    assert model.version == 1
    assert model.previous_version_id is None
    assert attribute.estimated_success == 0.60
    assert attribute.attribute_version == 1
    assert attribute.previous_attribute_id is None
    assert attribute.self_model_version_id == model.id
    assert result.status is CapabilitySelfModelInitializationStatus.INITIALIZED
    assert result.estimated_success == 0.60
    assert result.action is CapabilityAction.VERIFY
    assert result.self_model_version == 1
    assert result.attribute_version == 1
    assert clock.calls == 1
    assert identifiers.calls == [
        "self-model-version",
        "capability-self-attribute",
        "event",
    ]

    assert len(events) == 1
    event = events[0]
    assert event.event_type is EventType.CAPABILITY_SELF_ATTRIBUTE_INITIALIZED
    assert event.target_entity_id == attribute.id
    assert event.reason == "INITIALIZATION"
    assert event.new_value["capability_key"] == "ALPHA"
    assert event.new_value["previous_estimated_success"] is None
    assert event.new_value["resulting_estimated_success"] == 0.60
    assert event.new_value["previous_action"] is None
    assert event.new_value["resulting_action"] == CapabilityAction.VERIFY.value
    assert event.new_value["metacognitive_state_version"] == 1
    assert event.new_value["evidence_through_performance_id"] is None
    assert event.new_value["evidence_through_sequence_index"] is None
    assert event.new_value["evidence_source_type"] is None
    assert event.new_value["source_type"] == SourceType.SYSTEM_RULE.value
    assert event.new_value["self_model_version"] == 1
    assert event.new_value["attribute_version"] == 1
    assert event.new_value["reason"] == "INITIALIZATION"
    assert PRIVATE_JOURNAL_FIELDS.isdisjoint(event.new_value)


def test_repeated_initialization_and_reopen_are_idempotent(tmp_path: Path) -> None:
    database_path = tmp_path / "idempotent.db"
    database = build_database(database_path)
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    service, clock, identifiers = build_initialization_service(factory)
    first = service.initialize(agent_id="agent-1", capability_key="ALPHA")
    calls_after_first = tuple(identifiers.calls)

    repeated = service.initialize(agent_id="agent-1", capability_key="ALPHA")
    reopened_database = SQLiteDatabase(database_path)
    reopened_database.initialize_capability_schema()
    reopened_factory = SQLiteCapabilityUnitOfWorkFactory(reopened_database)
    reopened_service, _, _ = build_initialization_service(
        reopened_factory,
        clock=clock,
        identifiers=identifiers,
    )
    reopened = reopened_service.initialize(agent_id="agent-1", capability_key="ALPHA")

    with reopened_factory() as unit_of_work:
        models = unit_of_work.self_model_versions.list_versions(agent_id="agent-1")
        attributes = unit_of_work.capability_self_attributes.list_versions(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
        events = unit_of_work.journal.list_for_target(
            target_entity_type=INITIALIZATION_TARGET_TYPE,
            target_entity_id=attributes[0].id,
        )

    assert first.status is CapabilitySelfModelInitializationStatus.INITIALIZED
    assert repeated.status is CapabilitySelfModelInitializationStatus.ALREADY_INITIALIZED
    assert reopened.status is CapabilitySelfModelInitializationStatus.ALREADY_INITIALIZED
    assert len(models) == 1
    assert len(attributes) == 1
    assert len(events) == 1
    assert clock.calls == 1
    assert tuple(identifiers.calls) == calls_after_first


def test_repeated_initialization_rejects_a_non_prior_initial_attribute(
    tmp_path: Path,
) -> None:
    database = build_database(tmp_path / "invalid-initial-estimate.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    estimator = DecayedBetaEstimator(lambda_=DEV_LAMBDA)
    model = SelfModelVersion(
        id="self-model-corrupt",
        agent_id="agent-1",
        version=1,
        previous_version_id=None,
        created_at=datetime(2026, 8, 8, 20, tzinfo=UTC),
    )
    attribute = CapabilitySelfAttribute(
        id="attribute-corrupt",
        agent_id="agent-1",
        capability_key="ALPHA",
        estimated_success=0.70,
        self_model_version_id=model.id,
        attribute_version=1,
        previous_attribute_id=None,
        created_at=model.created_at,
    )
    state = VersionedMetacognitiveCapabilityState(
        agent_id="agent-1",
        capability_key="ALPHA",
        version=1,
        state=estimator.initial_state(),
    )
    with factory() as unit_of_work:
        unit_of_work.metacognitive_states.replace_current(
            state=state,
            expected_version=None,
        )
        unit_of_work.self_model_versions.add(model)
        unit_of_work.capability_self_attributes.add(attribute)
        unit_of_work.commit()
    service, clock, identifiers = build_initialization_service(factory)

    with pytest.raises(CapabilitySelfModelIntegrityError, match="prior DEV"):
        service.initialize(agent_id="agent-1", capability_key="ALPHA")

    with factory() as unit_of_work:
        assert (
            unit_of_work.metacognitive_states.get_current(
                agent_id="agent-1",
                capability_key="ALPHA",
            )
            == state
        )
        assert unit_of_work.self_model_versions.list_versions(agent_id="agent-1") == [model]
        assert unit_of_work.capability_self_attributes.list_versions(
            agent_id="agent-1",
            capability_key="ALPHA",
        ) == [attribute]
    assert clock.calls == 0
    assert identifiers.calls == []


def test_two_capabilities_share_one_coherent_global_self_model_chain(tmp_path: Path) -> None:
    database = build_database(tmp_path / "two-capabilities.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    service, _, _ = build_initialization_service(factory)

    alpha_result = service.initialize(agent_id="agent-1", capability_key="ALPHA")
    beta_result = service.initialize(agent_id="agent-1", capability_key="BETA")

    with factory() as unit_of_work:
        models = unit_of_work.self_model_versions.list_versions(agent_id="agent-1")
        alpha = unit_of_work.capability_self_attributes.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
        beta = unit_of_work.capability_self_attributes.get_current(
            agent_id="agent-1",
            capability_key="BETA",
        )
        alpha_meta = unit_of_work.metacognitive_states.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
        beta_meta = unit_of_work.metacognitive_states.get_current(
            agent_id="agent-1",
            capability_key="BETA",
        )

    assert [model.version for model in models] == [1, 2]
    assert models[0].previous_version_id is None
    assert models[1].previous_version_id == models[0].id
    assert alpha is not None
    assert beta is not None
    assert alpha.self_model_version_id == models[0].id
    assert beta.self_model_version_id == models[1].id
    assert alpha.attribute_version == beta.attribute_version == 1
    assert alpha_meta is not None and alpha_meta.version == 1
    assert beta_meta is not None and beta_meta.version == 1
    assert alpha_result.self_model_version == 1
    assert beta_result.self_model_version == 2


def test_agents_have_independent_global_self_model_chains(tmp_path: Path) -> None:
    database = build_database(tmp_path / "agents.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    service, _, _ = build_initialization_service(factory)

    first = service.initialize(agent_id="agent-1", capability_key="ALPHA")
    second = service.initialize(agent_id="agent-2", capability_key="ALPHA")

    with factory() as unit_of_work:
        first_models = unit_of_work.self_model_versions.list_versions(agent_id="agent-1")
        second_models = unit_of_work.self_model_versions.list_versions(agent_id="agent-2")
        first_attribute = unit_of_work.capability_self_attributes.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
        second_attribute = unit_of_work.capability_self_attributes.get_current(
            agent_id="agent-2",
            capability_key="ALPHA",
        )

    assert first.status is CapabilitySelfModelInitializationStatus.INITIALIZED
    assert second.status is CapabilitySelfModelInitializationStatus.INITIALIZED
    assert first.self_model_version == second.self_model_version == 1
    assert len(first_models) == len(second_models) == 1
    assert first_models[0].previous_version_id is None
    assert second_models[0].previous_version_id is None
    assert first_models[0].id != second_models[0].id
    assert first_attribute is not None
    assert second_attribute is not None
    assert first_attribute.agent_id == "agent-1"
    assert second_attribute.agent_id == "agent-2"


def test_late_initialization_after_metacognitive_learning_is_rejected(
    tmp_path: Path,
) -> None:
    database = build_database(tmp_path / "late-initialization.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    estimator = DecayedBetaEstimator(lambda_=DEV_LAMBDA)
    performance = build_performance()
    with factory() as unit_of_work:
        unit_of_work.capability_performances.add(performance)
        unit_of_work.commit()
    MetacognitiveCapabilityUpdateService(
        unit_of_work_factory=factory,
        estimator=estimator,
    ).process(performance_id=performance.id)
    service, clock, identifiers = build_initialization_service(factory)

    with pytest.raises(CapabilitySelfModelInitializationError, match="tardivement"):
        service.initialize(agent_id="agent-1", capability_key="ALPHA")

    with factory() as unit_of_work:
        state = unit_of_work.metacognitive_states.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
        models = unit_of_work.self_model_versions.list_versions(agent_id="agent-1")
        attributes = unit_of_work.capability_self_attributes.list_versions(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
    with database.connect() as connection:
        journal_count = int(
            connection.execute("SELECT COUNT(*) AS count FROM journal_events").fetchone()["count"]
        )

    assert state is not None and state.version == 2
    assert models == []
    assert attributes == []
    assert journal_count == 0
    assert clock.calls == 0
    assert identifiers.calls == []


def test_initialization_rolls_back_every_write_when_journal_append_fails(
    tmp_path: Path,
) -> None:
    database = build_database(tmp_path / "journal-rollback.db")
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    with database.connect() as connection:
        connection.execute(
            """
            CREATE TRIGGER fail_capability_initialization_journal
            BEFORE INSERT ON journal_events
            WHEN NEW.event_type = 'CAPABILITY_SELF_ATTRIBUTE_INITIALIZED'
            BEGIN
                SELECT RAISE(ABORT, 'échec journal P3 injecté');
            END
            """
        )
    service, _, _ = build_initialization_service(factory)

    with pytest.raises(sqlite3.IntegrityError, match="journal P3"):
        service.initialize(agent_id="agent-1", capability_key="ALPHA")

    with factory() as unit_of_work:
        state = unit_of_work.metacognitive_states.get_current(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
        models = unit_of_work.self_model_versions.list_versions(agent_id="agent-1")
        attributes = unit_of_work.capability_self_attributes.list_versions(
            agent_id="agent-1",
            capability_key="ALPHA",
        )
    with database.connect() as connection:
        journal_count = int(
            connection.execute("SELECT COUNT(*) AS count FROM journal_events").fetchone()["count"]
        )

    assert state is None
    assert models == []
    assert attributes == []
    assert journal_count == 0
