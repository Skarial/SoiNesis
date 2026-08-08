import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

import pytest

from soinesis.application.capabilities import (
    CapabilityDecisionPolicy,
    CapabilitySelfModelInitializationService,
    CapabilitySelfModelIntegrityError,
    CapabilitySelfModelNotInitializedError,
    CapabilitySelfModelRevisionService,
    CapabilitySelfModelRevisionStatus,
    DecayedBetaEstimator,
    MetacognitiveCapabilityUpdateService,
    MetacognitiveStateIntegrityError,
    SignificantSelfRevisionPolicy,
)
from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    SelfModelVersion,
    VersionedMetacognitiveCapabilityState,
)
from soinesis.domain.models import EventType, JournalEvent, SourceType
from soinesis.infrastructure.sqlite import SQLiteCapabilityUnitOfWorkFactory, SQLiteDatabase

AGENT_ID = "agent-1"
CAPABILITY_KEY = "ALPHA"
DEV_LAMBDA = 1.0
FIXED_TIME = datetime(2026, 8, 8, 18, 0, tzinfo=UTC)


class FixedClock:
    def now(self) -> datetime:
        return FIXED_TIME


class SequentialIdentifiers:
    def __init__(self) -> None:
        self._counters: dict[str, int] = {}

    def new(self, prefix: str) -> str:
        next_value = self._counters.get(prefix, 0) + 1
        self._counters[prefix] = next_value
        return f"{prefix}-{next_value}"

    @property
    def issued_count(self) -> int:
        return sum(self._counters.values())


@dataclass(frozen=True)
class RevisionHarness:
    database: SQLiteDatabase
    factory: SQLiteCapabilityUnitOfWorkFactory
    estimator: DecayedBetaEstimator
    identifiers: SequentialIdentifiers
    initializer: CapabilitySelfModelInitializationService
    updater: MetacognitiveCapabilityUpdateService
    revision_service: CapabilitySelfModelRevisionService


@dataclass(frozen=True)
class PersistedSnapshot:
    models: tuple[SelfModelVersion, ...]
    attributes: tuple[CapabilitySelfAttribute, ...]
    metacognitive_state: VersionedMetacognitiveCapabilityState | None
    events: tuple[JournalEvent, ...]


def build_harness(
    path: Path,
    *,
    identifiers: SequentialIdentifiers | None = None,
) -> RevisionHarness:
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    estimator = DecayedBetaEstimator(lambda_=DEV_LAMBDA)
    identifier_generator = identifiers or SequentialIdentifiers()
    decision_policy = CapabilityDecisionPolicy()
    return RevisionHarness(
        database=database,
        factory=factory,
        estimator=estimator,
        identifiers=identifier_generator,
        initializer=CapabilitySelfModelInitializationService(
            unit_of_work_factory=factory,
            estimator=estimator,
            clock=FixedClock(),
            identifiers=identifier_generator,
        ),
        updater=MetacognitiveCapabilityUpdateService(
            unit_of_work_factory=factory,
            estimator=estimator,
        ),
        revision_service=CapabilitySelfModelRevisionService(
            unit_of_work_factory=factory,
            estimator=estimator,
            revision_policy=SignificantSelfRevisionPolicy(
                decision_policy=decision_policy,
            ),
            clock=FixedClock(),
            identifiers=identifier_generator,
        ),
    )


def build_performance(
    *,
    sequence_index: int,
    intrinsic_success: bool,
    agent_id: str = AGENT_ID,
    capability_key: str = CAPABILITY_KEY,
    source_type: SourceType = SourceType.DIRECT_ENVIRONMENT,
) -> CapabilityPerformanceObservation:
    identifier = f"performance-{agent_id.lower()}-{capability_key.lower()}-{sequence_index}"
    return CapabilityPerformanceObservation(
        id=identifier,
        agent_id=agent_id,
        trial_id=f"trial-{identifier}",
        cycle_id=f"cycle-{identifier}",
        sequence_index=sequence_index,
        capability_key=capability_key,
        intrinsic_success=intrinsic_success,
        observed_at=FIXED_TIME + timedelta(minutes=sequence_index + 1),
        source_type=source_type,
    )


def persist_and_process(
    harness: RevisionHarness,
    outcomes: tuple[bool, ...],
    *,
    capability_key: str = CAPABILITY_KEY,
    starting_sequence_index: int = 0,
) -> tuple[CapabilityPerformanceObservation, ...]:
    performances: list[CapabilityPerformanceObservation] = []
    for offset, intrinsic_success in enumerate(outcomes):
        performance = build_performance(
            sequence_index=starting_sequence_index + offset,
            intrinsic_success=intrinsic_success,
            capability_key=capability_key,
        )
        with harness.factory() as unit_of_work:
            unit_of_work.capability_performances.add(performance)
            unit_of_work.commit()
        harness.updater.process(performance_id=performance.id)
        performances.append(performance)
    return tuple(performances)


def snapshot(
    harness: RevisionHarness,
    *,
    capability_key: str = CAPABILITY_KEY,
) -> PersistedSnapshot:
    with harness.factory() as unit_of_work:
        models = tuple(unit_of_work.self_model_versions.list_versions(agent_id=AGENT_ID))
        attributes = tuple(
            unit_of_work.capability_self_attributes.list_versions(
                agent_id=AGENT_ID,
                capability_key=capability_key,
            )
        )
        metacognitive_state = unit_of_work.metacognitive_states.get_current(
            agent_id=AGENT_ID,
            capability_key=capability_key,
        )
        events = tuple(
            event
            for attribute in attributes
            for event in unit_of_work.journal.list_for_target(
                target_entity_type="CapabilitySelfAttribute",
                target_entity_id=attribute.id,
            )
        )
    return PersistedSnapshot(
        models=models,
        attributes=attributes,
        metacognitive_state=metacognitive_state,
        events=events,
    )


@pytest.mark.parametrize(
    ("outcomes", "expected_action"),
    (
        ((True, True, True, True, True), CapabilityAction.DIRECT),
        ((False, False), CapabilityAction.HELP),
    ),
)
def test_revision_crossing_creates_exact_linked_trio_with_evidence_payload(
    tmp_path: Path,
    outcomes: tuple[bool, ...],
    expected_action: CapabilityAction,
) -> None:
    harness = build_harness(tmp_path / f"crossing-{expected_action.value}.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    performances = persist_and_process(harness, outcomes)
    before = snapshot(harness)
    expected_state = harness.estimator.replay(outcomes)

    result = harness.revision_service.revise(
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
    )

    after = snapshot(harness)
    assert len(after.models) == len(before.models) + 1 == 2
    assert len(after.attributes) == len(before.attributes) + 1 == 2
    assert len(after.events) == len(before.events) + 1 == 2
    initial_model, revised_model = after.models
    initial_attribute, revised_attribute = after.attributes
    initialization_event, revision_event = after.events
    assert revised_model.version == 2
    assert revised_model.previous_version_id == initial_model.id
    assert revised_attribute.attribute_version == 2
    assert revised_attribute.previous_attribute_id == initial_attribute.id
    assert revised_attribute.self_model_version_id == revised_model.id
    assert revised_attribute.estimated_success == expected_state.estimated_success
    assert initialization_event.event_type is EventType.CAPABILITY_SELF_ATTRIBUTE_INITIALIZED
    assert revision_event.event_type is EventType.CAPABILITY_SELF_ATTRIBUTE_REVISED
    assert revision_event.target_entity_type == "CapabilitySelfAttribute"
    assert revision_event.target_entity_id == revised_attribute.id
    assert revision_event.agent_id == AGENT_ID
    assert revision_event.cycle_id == performances[-1].cycle_id
    assert revision_event.occurred_at == FIXED_TIME
    assert revision_event.reason == "ACTION_BAND_CROSSING"
    assert revision_event.new_value == {
        "capability_key": CAPABILITY_KEY,
        "previous_estimated_success": 0.6,
        "resulting_estimated_success": expected_state.estimated_success,
        "previous_action": CapabilityAction.VERIFY.value,
        "resulting_action": expected_action.value,
        "metacognitive_state_version": len(outcomes) + 1,
        "evidence_through_performance_id": performances[-1].id,
        "evidence_through_sequence_index": performances[-1].sequence_index,
        "evidence_source_type": SourceType.DIRECT_ENVIRONMENT.value,
        "source_type": SourceType.INTERNAL_STATE.value,
        "self_model_version": 2,
        "attribute_version": 2,
        "reason": "ACTION_BAND_CROSSING",
    }
    assert result.status is CapabilitySelfModelRevisionStatus.REVISED
    assert result.previous_estimated_success == 0.6
    assert result.resulting_estimated_success == expected_state.estimated_success
    assert result.previous_action is CapabilityAction.VERIFY
    assert result.resulting_action is expected_action
    assert result.previous_self_model_version == 1
    assert result.resulting_self_model_version == 2
    assert result.previous_attribute_version == 1
    assert result.resulting_attribute_version == 2
    assert result.triggering_performance_id == performances[-1].id
    assert after.metacognitive_state is not None
    assert after.metacognitive_state.state == expected_state


def test_same_decision_band_returns_no_revision_without_any_write(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "same-band.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    persist_and_process(harness, (True,))
    before = snapshot(harness)
    identifiers_before = harness.identifiers.issued_count

    result = harness.revision_service.revise(
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
    )

    assert snapshot(harness) == before
    assert harness.identifiers.issued_count == identifiers_before
    assert result.status is CapabilitySelfModelRevisionStatus.NO_REVISION
    assert result.previous_estimated_success == 0.6
    assert result.resulting_estimated_success == 0.6
    assert result.previous_action is CapabilityAction.VERIFY
    assert result.resulting_action is CapabilityAction.VERIFY
    assert result.previous_self_model_version == result.resulting_self_model_version == 1
    assert result.previous_attribute_version == result.resulting_attribute_version == 1
    assert result.triggering_performance_id is None


def test_prior_without_learning_is_rejected_without_any_write(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "prior-without-learning.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    before = snapshot(harness)
    identifiers_before = harness.identifiers.issued_count

    with pytest.raises(CapabilitySelfModelIntegrityError, match="preuve métacognitive"):
        harness.revision_service.revise(
            agent_id=AGENT_ID,
            capability_key=CAPABILITY_KEY,
        )

    assert snapshot(harness) == before
    assert harness.identifiers.issued_count == identifiers_before


def test_second_call_and_reopen_remain_no_revision(tmp_path: Path) -> None:
    database_path = tmp_path / "reopen-no-revision.db"
    harness = build_harness(database_path)
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    persist_and_process(harness, (True, True, True, True, True))
    first = harness.revision_service.revise(
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
    )
    persisted = snapshot(harness)
    identifiers_before = harness.identifiers.issued_count

    repeated = harness.revision_service.revise(
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
    )
    reopened = build_harness(database_path, identifiers=harness.identifiers)
    after_reopen = reopened.revision_service.revise(
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
    )

    assert first.status is CapabilitySelfModelRevisionStatus.REVISED
    assert repeated.status is CapabilitySelfModelRevisionStatus.NO_REVISION
    assert after_reopen.status is CapabilitySelfModelRevisionStatus.NO_REVISION
    assert repeated.previous_action is repeated.resulting_action is CapabilityAction.DIRECT
    assert after_reopen.previous_action is after_reopen.resulting_action is CapabilityAction.DIRECT
    assert repeated.triggering_performance_id is None
    assert after_reopen.triggering_performance_id is None
    assert snapshot(reopened) == persisted
    assert harness.identifiers.issued_count == identifiers_before


def test_inverse_crossing_creates_a_new_revision(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "inverse-crossing.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    persist_and_process(harness, (True, True, True, True, True))
    first = harness.revision_service.revise(
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
    )
    direct_snapshot = snapshot(harness)
    last_performance = persist_and_process(
        harness,
        (False,),
        starting_sequence_index=5,
    )[0]

    inverse = harness.revision_service.revise(
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
    )

    after = snapshot(harness)
    assert first.resulting_action is CapabilityAction.DIRECT
    assert inverse.status is CapabilitySelfModelRevisionStatus.REVISED
    assert inverse.previous_action is CapabilityAction.DIRECT
    assert inverse.resulting_action is CapabilityAction.VERIFY
    assert inverse.previous_self_model_version == 2
    assert inverse.resulting_self_model_version == 3
    assert inverse.previous_attribute_version == 2
    assert inverse.resulting_attribute_version == 3
    assert inverse.triggering_performance_id == last_performance.id
    assert len(after.models) == len(direct_snapshot.models) + 1 == 3
    assert len(after.attributes) == len(direct_snapshot.attributes) + 1 == 3
    assert len(after.events) == len(direct_snapshot.events) + 1 == 3
    assert after.models[-1].previous_version_id == direct_snapshot.models[-1].id
    assert after.attributes[-1].previous_attribute_id == direct_snapshot.attributes[-1].id
    assert after.attributes[-1].self_model_version_id == after.models[-1].id
    assert after.metacognitive_state is not None
    assert (
        after.attributes[-1].estimated_success == after.metacognitive_state.state.estimated_success
    )


@pytest.mark.parametrize("failure_target", ("attribute", "journal"))
def test_late_revision_failure_rolls_back_the_trio_and_preserves_meta_for_retry(
    tmp_path: Path,
    failure_target: Literal["attribute", "journal"],
) -> None:
    harness = build_harness(tmp_path / f"rollback-{failure_target}.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    persist_and_process(harness, (True, True, True, True, True))
    before = snapshot(harness)
    if failure_target == "attribute":
        trigger_statement = """
            CREATE TRIGGER fail_capability_revision
            BEFORE INSERT ON capability_self_attributes
            WHEN NEW.attribute_version = 2
            BEGIN
                SELECT RAISE(ABORT, 'injected revision failure');
            END
        """
    else:
        trigger_statement = """
            CREATE TRIGGER fail_capability_revision
            BEFORE INSERT ON journal_events
            WHEN NEW.event_type = 'CAPABILITY_SELF_ATTRIBUTE_REVISED'
            BEGIN
                SELECT RAISE(ABORT, 'injected revision failure');
            END
        """
    with harness.database.connect() as connection:
        connection.execute(trigger_statement)

    with pytest.raises(sqlite3.IntegrityError, match="injected revision failure"):
        harness.revision_service.revise(
            agent_id=AGENT_ID,
            capability_key=CAPABILITY_KEY,
        )

    after_failure = snapshot(harness)
    assert after_failure == before
    assert after_failure.metacognitive_state == before.metacognitive_state
    with harness.database.connect() as connection:
        connection.execute("DROP TRIGGER fail_capability_revision")

    retry = harness.revision_service.revise(
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
    )

    after_retry = snapshot(harness)
    assert retry.status is CapabilitySelfModelRevisionStatus.REVISED
    assert len(after_retry.models) == len(before.models) + 1
    assert len(after_retry.attributes) == len(before.attributes) + 1
    assert len(after_retry.events) == len(before.events) + 1
    assert after_retry.metacognitive_state == before.metacognitive_state


def test_revision_after_initializing_another_capability_extends_global_model_only(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "another-capability.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key="BETA")
    alpha_before = snapshot(harness)
    beta_before = snapshot(harness, capability_key="BETA")
    persist_and_process(harness, (True, True, True, True, True))

    result = harness.revision_service.revise(
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
    )

    alpha_after = snapshot(harness)
    beta_after = snapshot(harness, capability_key="BETA")
    assert result.status is CapabilitySelfModelRevisionStatus.REVISED
    assert result.previous_self_model_version == 2
    assert result.resulting_self_model_version == 3
    assert len(alpha_after.models) == len(alpha_before.models) + 1 == 3
    assert alpha_after.models[-1].previous_version_id == alpha_before.models[-1].id
    assert len(alpha_after.attributes) == len(alpha_before.attributes) + 1 == 2
    assert alpha_after.attributes[-1].previous_attribute_id == alpha_before.attributes[-1].id
    assert alpha_after.attributes[-1].self_model_version_id == alpha_after.models[-1].id
    assert beta_after.attributes == beta_before.attributes
    assert beta_after.events == beta_before.events
    assert beta_after.attributes[-1].self_model_version_id == alpha_before.models[-1].id


def test_uninitialized_capability_is_rejected_without_writes(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "uninitialized.db")
    before = snapshot(harness)

    with pytest.raises(CapabilitySelfModelNotInitializedError):
        harness.revision_service.revise(
            agent_id=AGENT_ID,
            capability_key=CAPABILITY_KEY,
        )

    assert snapshot(harness) == before
    assert harness.identifiers.issued_count == 0


def test_revision_rejects_a_non_prior_initial_attribute_without_writes(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "invalid-initial-estimate.db")
    model = SelfModelVersion(
        id="self-model-corrupt",
        agent_id=AGENT_ID,
        version=1,
        previous_version_id=None,
        created_at=FIXED_TIME,
    )
    attribute = CapabilitySelfAttribute(
        id="attribute-corrupt",
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
        estimated_success=0.70,
        self_model_version_id=model.id,
        attribute_version=1,
        previous_attribute_id=None,
        created_at=FIXED_TIME,
    )
    state = VersionedMetacognitiveCapabilityState(
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
        version=1,
        state=harness.estimator.initial_state(),
    )
    with harness.factory() as unit_of_work:
        unit_of_work.metacognitive_states.replace_current(
            state=state,
            expected_version=None,
        )
        unit_of_work.self_model_versions.add(model)
        unit_of_work.capability_self_attributes.add(attribute)
        unit_of_work.commit()
    before = snapshot(harness)

    with pytest.raises(CapabilitySelfModelIntegrityError, match="prior DEV"):
        harness.revision_service.revise(
            agent_id=AGENT_ID,
            capability_key=CAPABILITY_KEY,
        )

    assert snapshot(harness) == before
    assert harness.identifiers.issued_count == 0


@pytest.mark.parametrize(
    ("cursor_agent_id", "cursor_capability_key", "cursor_source_type", "persist_cursor"),
    (
        (AGENT_ID, "BETA", SourceType.DIRECT_ENVIRONMENT, True),
        ("agent-2", CAPABILITY_KEY, SourceType.DIRECT_ENVIRONMENT, True),
        (AGENT_ID, CAPABILITY_KEY, SourceType.IMAGINATION, True),
        (AGENT_ID, CAPABILITY_KEY, SourceType.DIRECT_ENVIRONMENT, False),
    ),
)
def test_invalid_cursor_is_rejected_without_revision(
    tmp_path: Path,
    cursor_agent_id: str,
    cursor_capability_key: str,
    cursor_source_type: SourceType,
    persist_cursor: bool,
) -> None:
    harness = build_harness(
        tmp_path
        / (
            "invalid-cursor-"
            f"{cursor_agent_id}-{cursor_capability_key}-{cursor_source_type.value}-{persist_cursor}.db"
        )
    )
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    initialized = snapshot(harness)
    prior = initialized.metacognitive_state
    assert prior is not None
    cursor = build_performance(
        sequence_index=0,
        intrinsic_success=True,
        agent_id=cursor_agent_id,
        capability_key=cursor_capability_key,
        source_type=cursor_source_type,
    )
    invalid_state = VersionedMetacognitiveCapabilityState(
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
        version=2,
        state=harness.estimator.update(prior.state, cursor.intrinsic_success),
        last_processed_performance_id=cursor.id,
        last_processed_sequence_index=cursor.sequence_index,
    )
    with harness.factory() as unit_of_work:
        if persist_cursor:
            unit_of_work.capability_performances.add(cursor)
        unit_of_work.metacognitive_states.replace_current(
            state=invalid_state,
            expected_version=prior.version,
        )
        unit_of_work.commit()
    before = snapshot(harness)
    identifiers_before = harness.identifiers.issued_count

    with pytest.raises(MetacognitiveStateIntegrityError):
        harness.revision_service.revise(
            agent_id=AGENT_ID,
            capability_key=CAPABILITY_KEY,
        )

    assert snapshot(harness) == before
    assert harness.identifiers.issued_count == identifiers_before
