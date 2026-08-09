import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import TracebackType
from typing import Self

import pytest
from pydantic import ValidationError

from soinesis.application.capabilities import (
    CapabilityPerformanceProvenanceError,
    CapabilityPerformanceRecordingIntegrityError,
    CapabilityPerformanceRecordingResult,
    CapabilityPerformanceRecordingService,
    CapabilityPerformanceRecordingStatus,
)
from soinesis.domain.capabilities import CapabilityPerformanceObservation
from soinesis.domain.models import SourceType
from soinesis.infrastructure.sqlite import SQLiteCapabilityUnitOfWorkFactory, SQLiteDatabase
from soinesis.ports.capabilities import (
    CapabilityPerformanceRepository,
    CapabilitySelfAttributeRepository,
    CapabilityUnitOfWork,
    MetacognitiveStateRepository,
    SelfModelVersionRepository,
)
from soinesis.ports.repositories import JournalRepository, MemoryRepository, ObservationRepository

OBSERVED_AT = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
PRIVATE_FIELDS = {
    "dataset",
    "final_success",
    "oracle",
    "phase",
    "seed",
    "true_success_probability",
    "u_correction",
    "u_intrinsic",
}


def build_observation(
    *,
    identifier: str = "performance-1",
    agent_id: str = "agent-1",
    trial_id: str = "trial-1",
    cycle_id: str = "cycle-1",
    sequence_index: int = 0,
    capability_key: str = "ALPHA",
    intrinsic_success: bool = True,
    observed_at: datetime = OBSERVED_AT,
    source_type: SourceType = SourceType.DIRECT_ENVIRONMENT,
) -> CapabilityPerformanceObservation:
    return CapabilityPerformanceObservation(
        id=identifier,
        agent_id=agent_id,
        trial_id=trial_id,
        cycle_id=cycle_id,
        sequence_index=sequence_index,
        capability_key=capability_key,
        intrinsic_success=intrinsic_success,
        observed_at=observed_at,
        source_type=source_type,
    )


@dataclass
class RecordingCounts:
    factory_calls: int = 0
    uow_enters: int = 0
    uow_exits: int = 0
    get_calls: int = 0
    add_calls: int = 0
    commit_calls: int = 0


class CapabilityPerformanceRepositoryProbe:
    def __init__(
        self,
        *,
        counts: RecordingCounts,
        existing: CapabilityPerformanceObservation | None = None,
        add_error: Exception | None = None,
    ) -> None:
        self._counts = counts
        self._existing = existing
        self._add_error = add_error
        self.added: list[CapabilityPerformanceObservation] = []

    def add(self, observation: CapabilityPerformanceObservation) -> None:
        self._counts.add_calls += 1
        if self._add_error is not None:
            raise self._add_error
        self.added.append(observation)

    def get(self, observation_id: str) -> CapabilityPerformanceObservation | None:
        self._counts.get_calls += 1
        if self._existing is None or self._existing.id != observation_id:
            return None
        return self._existing

    def list_before(self, *, boundary: object) -> list[CapabilityPerformanceObservation]:
        raise AssertionError(f"La lecture d'historique est interdite: {boundary!r}")


class RecordingUnitOfWorkProbe:
    def __init__(
        self,
        *,
        counts: RecordingCounts,
        performances: CapabilityPerformanceRepositoryProbe,
        commit_error: Exception | None = None,
    ) -> None:
        self._counts = counts
        self._performances = performances
        self._commit_error = commit_error

    @property
    def observations(self) -> ObservationRepository:
        raise AssertionError("Le repository historique d'observations est interdit.")

    @property
    def memories(self) -> MemoryRepository:
        raise AssertionError("Le repository de mémoires est interdit.")

    @property
    def journal(self) -> JournalRepository:
        raise AssertionError("Le journal est interdit.")

    @property
    def capability_performances(self) -> CapabilityPerformanceRepository:
        return self._performances

    @property
    def metacognitive_states(self) -> MetacognitiveStateRepository:
        raise AssertionError("Le MetaState est interdit.")

    @property
    def self_model_versions(self) -> SelfModelVersionRepository:
        raise AssertionError("Le SelfModel est interdit.")

    @property
    def capability_self_attributes(self) -> CapabilitySelfAttributeRepository:
        raise AssertionError("Le SelfAttribute est interdit.")

    def __enter__(self) -> Self:
        self._counts.uow_enters += 1
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._counts.uow_exits += 1

    def commit(self) -> None:
        self._counts.commit_calls += 1
        if self._commit_error is not None:
            raise self._commit_error


class RecordingUnitOfWorkFactoryProbe:
    def __init__(self, *, counts: RecordingCounts, unit_of_work: RecordingUnitOfWorkProbe) -> None:
        self._counts = counts
        self._unit_of_work = unit_of_work

    def __call__(self) -> CapabilityUnitOfWork:
        self._counts.factory_calls += 1
        return self._unit_of_work


def build_unit_service(
    *,
    existing: CapabilityPerformanceObservation | None = None,
    add_error: Exception | None = None,
    commit_error: Exception | None = None,
) -> tuple[
    CapabilityPerformanceRecordingService,
    RecordingCounts,
    CapabilityPerformanceRepositoryProbe,
]:
    counts = RecordingCounts()
    repository = CapabilityPerformanceRepositoryProbe(
        counts=counts,
        existing=existing,
        add_error=add_error,
    )
    unit_of_work = RecordingUnitOfWorkProbe(
        counts=counts,
        performances=repository,
        commit_error=commit_error,
    )
    factory = RecordingUnitOfWorkFactoryProbe(counts=counts, unit_of_work=unit_of_work)
    return CapabilityPerformanceRecordingService(unit_of_work_factory=factory), counts, repository


def test_new_observation_is_added_and_committed_exactly_once() -> None:
    observation = build_observation()
    service, counts, repository = build_unit_service()

    result = service.record(observation=observation)

    assert result.status is CapabilityPerformanceRecordingStatus.RECORDED
    assert result.performance_id == observation.id
    assert repository.added == [observation]
    assert counts == RecordingCounts(
        factory_calls=1,
        uow_enters=1,
        uow_exits=1,
        get_calls=1,
        add_calls=1,
        commit_calls=1,
    )


def test_exact_retry_is_already_recorded_without_add_or_commit() -> None:
    observation = build_observation()
    service, counts, repository = build_unit_service(existing=observation)

    result = service.record(observation=observation)

    assert result.status is CapabilityPerformanceRecordingStatus.ALREADY_RECORDED
    assert repository.added == []
    assert counts.add_calls == 0
    assert counts.commit_calls == 0


@pytest.mark.parametrize(
    "changed_fields",
    (
        {"agent_id": "agent-2"},
        {"trial_id": "trial-2"},
        {"cycle_id": "cycle-2"},
        {"sequence_index": 1},
        {"capability_key": "BETA"},
        {"intrinsic_success": False},
        {"observed_at": OBSERVED_AT + timedelta(seconds=1)},
        {"source_type": SourceType.IMAGINATION},
    ),
)
def test_same_id_with_different_public_content_is_an_integrity_error(
    changed_fields: dict[str, object],
) -> None:
    existing = build_observation()
    incoming = existing.model_copy(update=changed_fields)
    service, counts, repository = build_unit_service(existing=existing)

    with pytest.raises(CapabilityPerformanceRecordingIntegrityError, match="contenu différent"):
        service.record(observation=incoming)

    assert repository.added == []
    assert counts.add_calls == 0
    assert counts.commit_calls == 0


def test_non_admissible_provenance_is_rejected_without_repository_mutation() -> None:
    observation = build_observation(source_type=SourceType.IMAGINATION)
    service, counts, repository = build_unit_service()

    with pytest.raises(CapabilityPerformanceProvenanceError, match="DIRECT_ENVIRONMENT"):
        service.record(observation=observation)

    assert repository.added == []
    assert counts.get_calls == 1
    assert counts.add_calls == 0
    assert counts.commit_calls == 0


def test_exact_retry_of_a_persisted_non_admissible_observation_is_never_blessed() -> None:
    corrupted = build_observation(source_type=SourceType.IMAGINATION)
    service, counts, repository = build_unit_service(existing=corrupted)

    with pytest.raises(CapabilityPerformanceProvenanceError, match="DIRECT_ENVIRONMENT"):
        service.record(observation=corrupted)

    assert repository.added == []
    assert counts.get_calls == 1
    assert counts.add_calls == 0
    assert counts.commit_calls == 0


def test_add_failure_propagates_without_commit_or_success_result() -> None:
    service, counts, _ = build_unit_service(add_error=RuntimeError("échec add"))

    with pytest.raises(RuntimeError, match="échec add"):
        service.record(observation=build_observation())

    assert counts.add_calls == 1
    assert counts.commit_calls == 0


def test_commit_failure_propagates_without_success_result() -> None:
    service, counts, _ = build_unit_service(commit_error=RuntimeError("échec commit"))

    with pytest.raises(RuntimeError, match="échec commit"):
        service.record(observation=build_observation())

    assert counts.add_calls == 1
    assert counts.commit_calls == 1


def test_public_result_contains_only_auditable_recording_fields() -> None:
    service, _, _ = build_unit_service()

    result = service.record(observation=build_observation())

    assert type(result) is CapabilityPerformanceRecordingResult
    assert set(CapabilityPerformanceRecordingResult.model_fields) == {
        "agent_id",
        "capability_key",
        "performance_id",
        "sequence_index",
        "status",
    }
    assert PRIVATE_FIELDS.isdisjoint(CapabilityPerformanceRecordingResult.model_fields)
    assert PRIVATE_FIELDS.isdisjoint(CapabilityPerformanceObservation.model_fields)
    with pytest.raises(ValidationError):
        CapabilityPerformanceRecordingResult.model_validate(
            {**result.model_dump(), "unknown": "value"}
        )
    with pytest.raises(ValidationError):
        result.status = CapabilityPerformanceRecordingStatus.ALREADY_RECORDED  # type: ignore[misc]


def build_database(path: Path) -> SQLiteDatabase:
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    return database


def row_count(database: SQLiteDatabase) -> int:
    with database.connect() as connection:
        return int(connection.execute("SELECT COUNT(*) FROM capability_performances").fetchone()[0])


def test_sqlite_record_retry_and_next_index_are_durable(tmp_path: Path) -> None:
    database = build_database(tmp_path / "recording.db")
    service = CapabilityPerformanceRecordingService(
        unit_of_work_factory=SQLiteCapabilityUnitOfWorkFactory(database)
    )
    first = build_observation(sequence_index=0)
    second = build_observation(
        identifier="performance-2",
        trial_id="trial-2",
        cycle_id="cycle-2",
        sequence_index=1,
    )

    first_result = service.record(observation=first)
    retry_result = service.record(observation=first)
    second_result = service.record(observation=second)

    assert first_result.status is CapabilityPerformanceRecordingStatus.RECORDED
    assert retry_result.status is CapabilityPerformanceRecordingStatus.ALREADY_RECORDED
    assert second_result.status is CapabilityPerformanceRecordingStatus.RECORDED
    assert row_count(database) == 2
    with SQLiteCapabilityUnitOfWorkFactory(database)() as unit_of_work:
        assert unit_of_work.capability_performances.get(first.id) == first
        assert unit_of_work.capability_performances.get(second.id) == second


def test_sqlite_rejects_retroactive_new_performance_after_later_index(tmp_path: Path) -> None:
    database = build_database(tmp_path / "retroactive.db")
    service = CapabilityPerformanceRecordingService(
        unit_of_work_factory=SQLiteCapabilityUnitOfWorkFactory(database)
    )
    service.record(observation=build_observation(identifier="performance-2", sequence_index=2))
    late = build_observation(
        identifier="performance-1",
        trial_id="trial-late",
        cycle_id="cycle-late",
        sequence_index=1,
    )

    with pytest.raises(sqlite3.IntegrityError):
        service.record(observation=late)

    assert row_count(database) == 1


def test_sqlite_rejects_two_ids_at_the_same_agent_sequence_index(tmp_path: Path) -> None:
    database = build_database(tmp_path / "same-index.db")
    service = CapabilityPerformanceRecordingService(
        unit_of_work_factory=SQLiteCapabilityUnitOfWorkFactory(database)
    )
    service.record(observation=build_observation(identifier="performance-1", sequence_index=0))
    conflicting = build_observation(
        identifier="performance-2",
        trial_id="trial-2",
        cycle_id="cycle-2",
        sequence_index=0,
    )

    with pytest.raises(sqlite3.IntegrityError):
        service.record(observation=conflicting)

    assert row_count(database) == 1


def test_sqlite_agents_have_independent_chronologies(tmp_path: Path) -> None:
    database = build_database(tmp_path / "agents.db")
    service = CapabilityPerformanceRecordingService(
        unit_of_work_factory=SQLiteCapabilityUnitOfWorkFactory(database)
    )
    first = build_observation(identifier="agent-1-performance", agent_id="agent-1")
    second = build_observation(
        identifier="agent-2-performance",
        agent_id="agent-2",
        trial_id="agent-2-trial",
        cycle_id="agent-2-cycle",
    )

    assert service.record(observation=first).status is CapabilityPerformanceRecordingStatus.RECORDED
    assert (
        service.record(observation=second).status is CapabilityPerformanceRecordingStatus.RECORDED
    )
    assert row_count(database) == 2
