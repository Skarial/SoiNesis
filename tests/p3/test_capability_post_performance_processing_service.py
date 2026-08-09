import inspect
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import pytest
from pydantic import ValidationError

from soinesis.application.capabilities import (
    CapabilityDecisionPolicy,
    CapabilityPerformanceNotFoundError,
    CapabilityPerformanceOrderError,
    CapabilityPerformanceProvenanceError,
    CapabilityPostPerformanceProcessingResult,
    CapabilityPostPerformanceProcessingService,
    CapabilityPostPerformanceRevisionStatus,
    CapabilitySelfModelInitializationService,
    CapabilitySelfModelIntegrityError,
    CapabilitySelfModelNotInitializedError,
    CapabilitySelfModelRevisionResult,
    CapabilitySelfModelRevisionService,
    CapabilitySelfModelRevisionStatus,
    DecayedBetaEstimator,
    MetacognitiveCapabilityUpdateResult,
    MetacognitiveCapabilityUpdateService,
    MetacognitiveUpdateStatus,
    SelfAttributeCapabilityDecisionService,
    SelfAttributeCapabilityEstimateProvider,
    SignificantSelfRevisionPolicy,
)
from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityHistoryBoundary,
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
FIXED_TIME = datetime(2026, 8, 8, 20, 0, tzinfo=UTC)


class MutableClock:
    def __init__(self) -> None:
        self._current = FIXED_TIME

    def now(self) -> datetime:
        return self._current

    def set(self, current: datetime) -> None:
        self._current = current


class SequentialIdentifiers:
    def __init__(self) -> None:
        self._counters: dict[str, int] = {}

    def new(self, prefix: str) -> str:
        next_value = self._counters.get(prefix, 0) + 1
        self._counters[prefix] = next_value
        return f"{prefix}-{next_value}"


@dataclass(frozen=True)
class ProcessingHarness:
    database: SQLiteDatabase
    factory: SQLiteCapabilityUnitOfWorkFactory
    clock: MutableClock
    identifiers: SequentialIdentifiers
    initializer: CapabilitySelfModelInitializationService
    updater: MetacognitiveCapabilityUpdateService
    facade: CapabilityPostPerformanceProcessingService
    decision_service: SelfAttributeCapabilityDecisionService


@dataclass(frozen=True)
class PersistedSnapshot:
    models: tuple[SelfModelVersion, ...]
    attributes: tuple[CapabilitySelfAttribute, ...]
    metacognitive_state: VersionedMetacognitiveCapabilityState | None
    events: tuple[JournalEvent, ...]


class MetacognitiveUpdateProbe:
    def __init__(
        self,
        *,
        calls: list[tuple[str, ...]],
        result: MetacognitiveCapabilityUpdateResult,
    ) -> None:
        self._calls = calls
        self._result = result

    def process(self, *, performance_id: str) -> MetacognitiveCapabilityUpdateResult:
        self._calls.append(("update", performance_id))
        return self._result


class FailingMetacognitiveUpdateProbe:
    def __init__(
        self,
        *,
        calls: list[tuple[str, ...]],
        error: Exception,
    ) -> None:
        self._calls = calls
        self._error = error

    def process(self, *, performance_id: str) -> MetacognitiveCapabilityUpdateResult:
        self._calls.append(("update", performance_id))
        raise self._error


class SelfModelRevisionProbe:
    def __init__(
        self,
        *,
        calls: list[tuple[str, ...]],
        result: CapabilitySelfModelRevisionResult,
    ) -> None:
        self._calls = calls
        self._result = result

    def revise(
        self,
        *,
        agent_id: str,
        capability_key: str,
    ) -> CapabilitySelfModelRevisionResult:
        self._calls.append(("revise", agent_id, capability_key))
        return self._result


def build_harness(
    path: Path,
    *,
    identifiers: SequentialIdentifiers | None = None,
) -> ProcessingHarness:
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    estimator = DecayedBetaEstimator(lambda_=DEV_LAMBDA)
    clock = MutableClock()
    identifier_generator = identifiers or SequentialIdentifiers()
    decision_policy = CapabilityDecisionPolicy()
    initializer = CapabilitySelfModelInitializationService(
        unit_of_work_factory=factory,
        estimator=estimator,
        clock=clock,
        identifiers=identifier_generator,
    )
    updater = MetacognitiveCapabilityUpdateService(
        unit_of_work_factory=factory,
        estimator=estimator,
    )
    revision_service = CapabilitySelfModelRevisionService(
        unit_of_work_factory=factory,
        estimator=estimator,
        revision_policy=SignificantSelfRevisionPolicy(
            decision_policy=decision_policy,
        ),
        clock=clock,
        identifiers=identifier_generator,
    )
    return ProcessingHarness(
        database=database,
        factory=factory,
        clock=clock,
        identifiers=identifier_generator,
        initializer=initializer,
        updater=updater,
        facade=CapabilityPostPerformanceProcessingService(
            unit_of_work_factory=factory,
            metacognitive_update_service=updater,
            self_model_revision_service=revision_service,
        ),
        decision_service=SelfAttributeCapabilityDecisionService(
            unit_of_work_factory=factory,
            estimate_provider=SelfAttributeCapabilityEstimateProvider(),
            decision_policy=decision_policy,
        ),
    )


def build_performance(
    *,
    sequence_index: int,
    intrinsic_success: bool,
    source_type: SourceType = SourceType.DIRECT_ENVIRONMENT,
    observed_at: datetime | None = None,
) -> CapabilityPerformanceObservation:
    return CapabilityPerformanceObservation(
        id=f"performance-{sequence_index}",
        agent_id=AGENT_ID,
        trial_id=f"trial-{sequence_index}",
        cycle_id=f"cycle-{sequence_index}",
        sequence_index=sequence_index,
        capability_key=CAPABILITY_KEY,
        intrinsic_success=intrinsic_success,
        observed_at=(
            observed_at
            if observed_at is not None
            else FIXED_TIME + timedelta(minutes=sequence_index + 1)
        ),
        source_type=source_type,
    )


def persist_performance(
    harness: ProcessingHarness,
    *,
    sequence_index: int,
    intrinsic_success: bool,
    source_type: SourceType = SourceType.DIRECT_ENVIRONMENT,
    observed_at: datetime | None = None,
) -> CapabilityPerformanceObservation:
    performance = build_performance(
        sequence_index=sequence_index,
        intrinsic_success=intrinsic_success,
        source_type=source_type,
        observed_at=observed_at,
    )
    with harness.factory() as unit_of_work:
        unit_of_work.capability_performances.add(performance)
        unit_of_work.commit()
    return performance


def read_snapshot(harness: ProcessingHarness) -> PersistedSnapshot:
    with harness.factory() as unit_of_work:
        models = tuple(unit_of_work.self_model_versions.list_versions(agent_id=AGENT_ID))
        attributes = tuple(
            unit_of_work.capability_self_attributes.list_versions(
                agent_id=AGENT_ID,
                capability_key=CAPABILITY_KEY,
            )
        )
        metacognitive_state = unit_of_work.metacognitive_states.get_current(
            agent_id=AGENT_ID,
            capability_key=CAPABILITY_KEY,
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


def build_update_result(
    status: MetacognitiveUpdateStatus,
) -> MetacognitiveCapabilityUpdateResult:
    previous_version = 1 if status is MetacognitiveUpdateStatus.APPLIED else 2
    return MetacognitiveCapabilityUpdateResult(
        performance_id="performance-0",
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
        status=status,
        previous_version=previous_version,
        resulting_version=2,
        previous_estimated_success=0.60,
        resulting_estimated_success=2.0 / 3.0,
    )


def build_revision_result() -> CapabilitySelfModelRevisionResult:
    return CapabilitySelfModelRevisionResult(
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
        status=CapabilitySelfModelRevisionStatus.NO_REVISION,
        previous_estimated_success=0.60,
        resulting_estimated_success=0.60,
        previous_action=CapabilityAction.VERIFY,
        resulting_action=CapabilityAction.VERIFY,
        previous_self_model_version=1,
        resulting_self_model_version=1,
        previous_attribute_version=1,
        resulting_attribute_version=1,
    )


def build_facade_with_revision_probe(
    harness: ProcessingHarness,
    revision_probe: SelfModelRevisionProbe,
) -> CapabilityPostPerformanceProcessingService:
    return CapabilityPostPerformanceProcessingService(
        unit_of_work_factory=harness.factory,
        metacognitive_update_service=harness.updater,
        self_model_revision_service=cast(
            CapabilitySelfModelRevisionService,
            revision_probe,
        ),
    )


@pytest.mark.parametrize(
    "status",
    (MetacognitiveUpdateStatus.APPLIED, MetacognitiveUpdateStatus.ALREADY_PROCESSED),
)
def test_facade_calls_update_then_revision_even_when_already_processed(
    tmp_path: Path,
    status: MetacognitiveUpdateStatus,
) -> None:
    harness = build_harness(tmp_path / f"order-{status.value}.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    persist_performance(harness, sequence_index=0, intrinsic_success=True)
    if status is MetacognitiveUpdateStatus.ALREADY_PROCESSED:
        harness.updater.process(performance_id="performance-0")
    calls: list[tuple[str, ...]] = []
    update_probe = MetacognitiveUpdateProbe(calls=calls, result=build_update_result(status))
    revision_probe = SelfModelRevisionProbe(calls=calls, result=build_revision_result())
    service = CapabilityPostPerformanceProcessingService(
        unit_of_work_factory=harness.factory,
        metacognitive_update_service=cast(
            MetacognitiveCapabilityUpdateService,
            update_probe,
        ),
        self_model_revision_service=cast(
            CapabilitySelfModelRevisionService,
            revision_probe,
        ),
    )

    result = service.process(performance_id="performance-0")

    assert calls == [
        ("update", "performance-0"),
        ("revise", AGENT_ID, CAPABILITY_KEY),
    ]
    assert result.metacognitive_status is status
    assert result.self_model_revision_status is CapabilityPostPerformanceRevisionStatus.NO_REVISION
    assert result.metacognitive_version_before == build_update_result(status).previous_version
    assert result.metacognitive_version_after == 2
    assert result.self_model_version_before == result.self_model_version_after == 1
    assert result.attribute_version_before == result.attribute_version_after == 1
    assert result.resulting_action is CapabilityAction.VERIFY


def test_public_contract_is_minimal_immutable_and_contains_no_private_field(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "public-contract.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    performance = persist_performance(harness, sequence_index=0, intrinsic_success=True)

    result = harness.facade.process(performance_id=performance.id)

    parameters = inspect.signature(CapabilityPostPerformanceProcessingService.process).parameters
    assert tuple(parameters) == ("self", "performance_id")
    assert parameters["performance_id"].kind is inspect.Parameter.KEYWORD_ONLY
    assert set(CapabilityPostPerformanceProcessingResult.model_fields) == {
        "performance_id",
        "agent_id",
        "capability_key",
        "metacognitive_status",
        "self_model_revision_status",
        "metacognitive_version_before",
        "metacognitive_version_after",
        "self_model_version_before",
        "self_model_version_after",
        "attribute_version_before",
        "attribute_version_after",
        "resulting_action",
    }
    forbidden_fields = {
        "true_success_probability",
        "phase",
        "seed",
        "replication",
        "dataset",
        "official_dataset_id",
        "oracle",
        "u_correction",
        "final_success",
    }
    assert forbidden_fields.isdisjoint(CapabilityPostPerformanceProcessingResult.model_fields)
    frozen_field = "resulting_action"
    with pytest.raises(ValidationError):
        setattr(result, frozen_field, CapabilityAction.DIRECT)


def test_update_error_prevents_revision_call(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "update-error-probe.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    persist_performance(harness, sequence_index=0, intrinsic_success=True)
    calls: list[tuple[str, ...]] = []
    update_probe = FailingMetacognitiveUpdateProbe(
        calls=calls,
        error=CapabilityPerformanceOrderError("ordre causal invalide"),
    )
    revision_probe = SelfModelRevisionProbe(calls=calls, result=build_revision_result())
    service = CapabilityPostPerformanceProcessingService(
        unit_of_work_factory=harness.factory,
        metacognitive_update_service=cast(
            MetacognitiveCapabilityUpdateService,
            update_probe,
        ),
        self_model_revision_service=cast(
            CapabilitySelfModelRevisionService,
            revision_probe,
        ),
    )

    with pytest.raises(CapabilityPerformanceOrderError):
        service.process(performance_id="performance-0")

    assert calls == [("update", "performance-0")]


def test_same_band_updates_meta_without_revising_self_model(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "same-band.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    before = read_snapshot(harness)
    performance = persist_performance(harness, sequence_index=0, intrinsic_success=True)

    result = harness.facade.process(performance_id=performance.id)

    after = read_snapshot(harness)
    assert before.attributes[0].attribute_version == 1
    assert before.attributes[0].estimated_success == 0.60
    assert before.attributes[0].created_at <= performance.observed_at
    assert result.metacognitive_status is MetacognitiveUpdateStatus.APPLIED
    assert result.self_model_revision_status is CapabilityPostPerformanceRevisionStatus.NO_REVISION
    assert result.metacognitive_version_before == 1
    assert result.metacognitive_version_after == 2
    assert result.self_model_version_before == result.self_model_version_after == 1
    assert result.attribute_version_before == result.attribute_version_after == 1
    assert result.resulting_action is CapabilityAction.VERIFY
    assert after.models == before.models
    assert after.attributes == before.attributes
    assert after.events == before.events
    assert after.metacognitive_state is not None
    assert after.metacognitive_state.version == 2


def test_crossing_is_revised_immediately_with_the_triggering_performance(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "immediate-crossing.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    results: list[CapabilityPostPerformanceProcessingResult] = []
    performances: list[CapabilityPerformanceObservation] = []

    for sequence_index in range(5):
        performance = persist_performance(
            harness,
            sequence_index=sequence_index,
            intrinsic_success=True,
        )
        performances.append(performance)
        results.append(harness.facade.process(performance_id=performance.id))

    assert all(
        result.self_model_revision_status is CapabilityPostPerformanceRevisionStatus.NO_REVISION
        for result in results[:-1]
    )
    crossing = results[-1]
    assert crossing.metacognitive_status is MetacognitiveUpdateStatus.APPLIED
    assert crossing.self_model_revision_status is CapabilityPostPerformanceRevisionStatus.REVISED
    assert crossing.resulting_action is CapabilityAction.DIRECT
    assert crossing.self_model_version_before == 1
    assert crossing.self_model_version_after == 2
    assert crossing.attribute_version_before == 1
    assert crossing.attribute_version_after == 2
    snapshot = read_snapshot(harness)
    assert snapshot.metacognitive_state is not None
    assert snapshot.metacognitive_state.state.estimated_success == 0.80
    assert len(snapshot.models) == len(snapshot.attributes) == len(snapshot.events) == 2
    revised_attribute = snapshot.attributes[-1]
    assert revised_attribute.estimated_success == 0.80
    revision_event = snapshot.events[-1]
    assert revision_event.event_type is EventType.CAPABILITY_SELF_ATTRIBUTE_REVISED
    assert revision_event.target_entity_id == revised_attribute.id
    assert revision_event.cycle_id == performances[-1].cycle_id
    assert revision_event.new_value["evidence_through_performance_id"] == performances[-1].id
    assert revision_event.new_value["evidence_through_sequence_index"] == 4


def test_completed_processing_is_idempotent_and_survives_reopen(tmp_path: Path) -> None:
    database_path = tmp_path / "idempotence-reopen.db"
    harness = build_harness(database_path)
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    performance = persist_performance(harness, sequence_index=0, intrinsic_success=True)
    first = harness.facade.process(performance_id=performance.id)
    persisted = read_snapshot(harness)

    repeated = harness.facade.process(performance_id=performance.id)
    reopened = build_harness(database_path, identifiers=harness.identifiers)
    after_reopen = reopened.facade.process(performance_id=performance.id)

    assert first.metacognitive_status is MetacognitiveUpdateStatus.APPLIED
    assert repeated.metacognitive_status is MetacognitiveUpdateStatus.ALREADY_PROCESSED
    assert after_reopen.metacognitive_status is MetacognitiveUpdateStatus.ALREADY_PROCESSED
    assert (
        repeated.self_model_revision_status is CapabilityPostPerformanceRevisionStatus.NO_REVISION
    )
    assert (
        after_reopen.self_model_revision_status
        is CapabilityPostPerformanceRevisionStatus.NO_REVISION
    )
    assert repeated.metacognitive_version_before == repeated.metacognitive_version_after == 2
    assert (
        after_reopen.metacognitive_version_before == after_reopen.metacognitive_version_after == 2
    )
    assert read_snapshot(reopened) == persisted


def test_revision_failure_keeps_meta_and_retry_completes_from_already_processed(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "revision-recovery.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    for sequence_index in range(4):
        performance = persist_performance(
            harness,
            sequence_index=sequence_index,
            intrinsic_success=True,
        )
        harness.facade.process(performance_id=performance.id)
    triggering_performance = persist_performance(
        harness,
        sequence_index=4,
        intrinsic_success=True,
    )
    before = read_snapshot(harness)
    with harness.database.connect() as connection:
        connection.execute(
            """
            CREATE TRIGGER fail_post_performance_revision
            BEFORE INSERT ON journal_events
            WHEN NEW.event_type = 'CAPABILITY_SELF_ATTRIBUTE_REVISED'
            BEGIN
                SELECT RAISE(ABORT, 'injected post-performance revision failure');
            END
            """
        )

    with pytest.raises(sqlite3.IntegrityError, match="injected post-performance revision failure"):
        harness.facade.process(performance_id=triggering_performance.id)

    after_failure = read_snapshot(harness)
    assert after_failure.metacognitive_state is not None
    assert before.metacognitive_state is not None
    assert after_failure.metacognitive_state.version == before.metacognitive_state.version + 1 == 6
    assert (
        after_failure.metacognitive_state.last_processed_performance_id == triggering_performance.id
    )
    assert after_failure.models == before.models
    assert after_failure.attributes == before.attributes
    assert after_failure.events == before.events
    with harness.database.connect() as connection:
        connection.execute("DROP TRIGGER fail_post_performance_revision")

    retry = harness.facade.process(performance_id=triggering_performance.id)

    final = read_snapshot(harness)
    assert retry.metacognitive_status is MetacognitiveUpdateStatus.ALREADY_PROCESSED
    assert retry.self_model_revision_status is CapabilityPostPerformanceRevisionStatus.REVISED
    assert retry.metacognitive_version_before == retry.metacognitive_version_after == 6
    assert len(final.models) == len(before.models) + 1 == 2
    assert len(final.attributes) == len(before.attributes) + 1 == 2
    assert len(final.events) == len(before.events) + 1 == 2
    assert final.events[-1].new_value["evidence_through_performance_id"] == (
        triggering_performance.id
    )


def test_old_duplicate_cannot_trigger_the_pending_revision_of_a_later_performance(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "old-duplicate-vs-recovery.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    first_performance = persist_performance(
        harness,
        sequence_index=0,
        intrinsic_success=False,
    )
    first_result = harness.facade.process(performance_id=first_performance.id)
    assert first_result.self_model_revision_status is (
        CapabilityPostPerformanceRevisionStatus.NO_REVISION
    )
    second_performance = persist_performance(
        harness,
        sequence_index=1,
        intrinsic_success=False,
    )
    with harness.database.connect() as connection:
        connection.execute(
            """
            CREATE TRIGGER fail_pending_later_revision
            BEFORE INSERT ON journal_events
            WHEN NEW.event_type = 'CAPABILITY_SELF_ATTRIBUTE_REVISED'
            BEGIN
                SELECT RAISE(ABORT, 'injected pending later revision failure');
            END
            """
        )

    with pytest.raises(sqlite3.IntegrityError, match="injected pending later revision failure"):
        harness.facade.process(performance_id=second_performance.id)

    after_second_failure = read_snapshot(harness)
    assert after_second_failure.metacognitive_state is not None
    assert after_second_failure.metacognitive_state.version == 3
    assert (
        after_second_failure.metacognitive_state.last_processed_performance_id
        == second_performance.id
    )

    old_duplicate = harness.facade.process(performance_id=first_performance.id)

    assert old_duplicate.metacognitive_status is MetacognitiveUpdateStatus.ALREADY_PROCESSED
    assert old_duplicate.self_model_revision_status is (
        CapabilityPostPerformanceRevisionStatus.SKIPPED_OLD_DUPLICATE
    )
    assert (
        old_duplicate.metacognitive_version_before == old_duplicate.metacognitive_version_after == 3
    )
    assert old_duplicate.self_model_version_before == old_duplicate.self_model_version_after == 1
    assert old_duplicate.attribute_version_before == old_duplicate.attribute_version_after == 1
    assert old_duplicate.resulting_action is CapabilityAction.VERIFY
    assert read_snapshot(harness) == after_second_failure
    with harness.database.connect() as connection:
        connection.execute("DROP TRIGGER fail_pending_later_revision")

    retry = harness.facade.process(performance_id=second_performance.id)

    final = read_snapshot(harness)
    assert retry.metacognitive_status is MetacognitiveUpdateStatus.ALREADY_PROCESSED
    assert retry.self_model_revision_status is CapabilityPostPerformanceRevisionStatus.REVISED
    assert retry.resulting_action is CapabilityAction.HELP
    revision_events = tuple(
        event
        for event in final.events
        if event.event_type is EventType.CAPABILITY_SELF_ATTRIBUTE_REVISED
    )
    assert len(revision_events) == 1
    assert revision_events[0].new_value["evidence_through_performance_id"] == (
        second_performance.id
    )
    assert revision_events[0].new_value["evidence_through_performance_id"] != (first_performance.id)


def test_meta_failures_never_call_revision_or_change_self_model(tmp_path: Path) -> None:
    missing_harness = build_harness(tmp_path / "missing.db")
    missing_harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    missing_calls: list[tuple[str, ...]] = []
    missing_probe = SelfModelRevisionProbe(
        calls=missing_calls,
        result=build_revision_result(),
    )
    missing_service = build_facade_with_revision_probe(missing_harness, missing_probe)
    missing_before = read_snapshot(missing_harness)
    with pytest.raises(CapabilityPerformanceNotFoundError):
        missing_service.process(performance_id="missing-performance")
    assert missing_calls == []
    assert read_snapshot(missing_harness) == missing_before

    provenance_harness = build_harness(tmp_path / "provenance.db")
    provenance_harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    forbidden = persist_performance(
        provenance_harness,
        sequence_index=0,
        intrinsic_success=True,
        source_type=SourceType.IMAGINATION,
    )
    provenance_calls: list[tuple[str, ...]] = []
    provenance_probe = SelfModelRevisionProbe(
        calls=provenance_calls,
        result=build_revision_result(),
    )
    provenance_service = build_facade_with_revision_probe(
        provenance_harness,
        provenance_probe,
    )
    provenance_before = read_snapshot(provenance_harness)
    with pytest.raises(CapabilityPerformanceProvenanceError):
        provenance_service.process(performance_id=forbidden.id)
    assert provenance_calls == []
    assert read_snapshot(provenance_harness) == provenance_before

    order_harness = build_harness(tmp_path / "order.db")
    order_harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    persist_performance(order_harness, sequence_index=0, intrinsic_success=True)
    future = persist_performance(order_harness, sequence_index=1, intrinsic_success=True)
    order_calls: list[tuple[str, ...]] = []
    order_probe = SelfModelRevisionProbe(calls=order_calls, result=build_revision_result())
    order_service = build_facade_with_revision_probe(order_harness, order_probe)
    order_before = read_snapshot(order_harness)
    with pytest.raises(CapabilityPerformanceOrderError):
        order_service.process(performance_id=future.id)
    assert order_calls == []
    assert read_snapshot(order_harness) == order_before


def test_uninitialized_capability_is_rejected_before_any_learning(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "uninitialized.db")
    performance = persist_performance(harness, sequence_index=0, intrinsic_success=True)

    with pytest.raises(CapabilitySelfModelNotInitializedError):
        harness.facade.process(performance_id=performance.id)

    snapshot = read_snapshot(harness)
    assert snapshot.metacognitive_state is None
    assert snapshot.models == ()
    assert snapshot.attributes == ()
    assert snapshot.events == ()
    with harness.factory() as unit_of_work:
        assert unit_of_work.capability_performances.get(performance.id) == performance


def test_initialization_after_the_observed_performance_is_rejected(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "late-initialization.db")
    performance = persist_performance(
        harness,
        sequence_index=0,
        intrinsic_success=True,
        observed_at=FIXED_TIME - timedelta(minutes=1),
    )
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    after_late_initialization = read_snapshot(harness)

    with pytest.raises(CapabilitySelfModelNotInitializedError, match="doit précéder"):
        harness.facade.process(performance_id=performance.id)

    assert read_snapshot(harness) == after_late_initialization
    assert after_late_initialization.metacognitive_state is not None
    assert after_late_initialization.metacognitive_state.version == 1


def test_temporal_guard_uses_initial_attribute_not_newer_current_revision(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "initial-attribute-time.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    for sequence_index in range(4):
        performance = persist_performance(
            harness,
            sequence_index=sequence_index,
            intrinsic_success=True,
        )
        harness.facade.process(performance_id=performance.id)
    harness.clock.set(FIXED_TIME + timedelta(hours=2))
    crossing_performance = persist_performance(
        harness,
        sequence_index=4,
        intrinsic_success=True,
    )

    crossing = harness.facade.process(performance_id=crossing_performance.id)

    after_crossing = read_snapshot(harness)
    initial_attribute, current_attribute = after_crossing.attributes
    assert crossing.self_model_revision_status is CapabilityPostPerformanceRevisionStatus.REVISED
    assert initial_attribute.attribute_version == 1
    assert initial_attribute.estimated_success == 0.60
    assert initial_attribute.created_at <= crossing_performance.observed_at
    assert crossing_performance.observed_at < current_attribute.created_at

    repeated = harness.facade.process(performance_id=crossing_performance.id)

    assert repeated.metacognitive_status is MetacognitiveUpdateStatus.ALREADY_PROCESSED
    assert repeated.self_model_revision_status is (
        CapabilityPostPerformanceRevisionStatus.NO_REVISION
    )
    assert read_snapshot(harness) == after_crossing


def test_incomplete_bootstrap_is_rejected_before_meta_creation(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "incomplete-bootstrap.db")
    model = SelfModelVersion(
        id="self-model-version-partial",
        agent_id=AGENT_ID,
        version=1,
        created_at=FIXED_TIME,
    )
    attribute = CapabilitySelfAttribute(
        id="capability-self-attribute-partial",
        agent_id=AGENT_ID,
        capability_key=CAPABILITY_KEY,
        estimated_success=0.60,
        self_model_version_id=model.id,
        attribute_version=1,
        created_at=FIXED_TIME,
    )
    with harness.factory() as unit_of_work:
        unit_of_work.self_model_versions.add(model)
        unit_of_work.capability_self_attributes.add(attribute)
        unit_of_work.commit()
    performance = persist_performance(harness, sequence_index=0, intrinsic_success=True)

    with pytest.raises(CapabilitySelfModelIntegrityError, match="MetaState"):
        harness.facade.process(performance_id=performance.id)

    snapshot = read_snapshot(harness)
    assert snapshot.metacognitive_state is None
    assert snapshot.models == (model,)
    assert snapshot.attributes == (attribute,)
    assert snapshot.events == ()


def test_next_c_decision_sees_the_attribute_revised_by_the_same_facade_call(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "decision-causality.db")
    harness.initializer.initialize(agent_id=AGENT_ID, capability_key=CAPABILITY_KEY)
    initial_decision = harness.decision_service.decide(
        boundary=CapabilityHistoryBoundary(
            agent_id=AGENT_ID,
            capability_key=CAPABILITY_KEY,
            trial_id="trial-before",
            cycle_id="cycle-before",
            sequence_index=0,
        )
    )
    assert initial_decision.action is CapabilityAction.VERIFY

    for sequence_index in range(4):
        performance = persist_performance(
            harness,
            sequence_index=sequence_index,
            intrinsic_success=True,
        )
        result = harness.facade.process(performance_id=performance.id)
        assert (
            result.self_model_revision_status is CapabilityPostPerformanceRevisionStatus.NO_REVISION
        )
    decision_before_crossing = harness.decision_service.decide(
        boundary=CapabilityHistoryBoundary(
            agent_id=AGENT_ID,
            capability_key=CAPABILITY_KEY,
            trial_id="trial-crossing",
            cycle_id="cycle-crossing",
            sequence_index=4,
        )
    )
    assert decision_before_crossing.action is CapabilityAction.VERIFY
    crossing_performance = persist_performance(
        harness,
        sequence_index=4,
        intrinsic_success=True,
    )

    crossing = harness.facade.process(performance_id=crossing_performance.id)
    next_decision = harness.decision_service.decide(
        boundary=CapabilityHistoryBoundary(
            agent_id=AGENT_ID,
            capability_key=CAPABILITY_KEY,
            trial_id="trial-after",
            cycle_id="cycle-after",
            sequence_index=5,
        )
    )

    assert crossing.self_model_revision_status is CapabilityPostPerformanceRevisionStatus.REVISED
    assert crossing.resulting_action is CapabilityAction.DIRECT
    assert next_decision.action is CapabilityAction.DIRECT
    assert next_decision.estimate.estimated_success == 0.80
