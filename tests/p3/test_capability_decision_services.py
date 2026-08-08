import inspect
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import TracebackType
from typing import Self

import pytest

from soinesis.application.capabilities import (
    CapabilityDecisionPolicy,
    CapabilitySelfModelNotInitializedError,
    DecayedBetaEstimator,
    FixedCapabilityDecisionService,
    FixedCapabilityEstimateProvider,
    RawHistoryCapabilityDecisionService,
    RawHistoryCapabilityEstimateProvider,
    SelfAttributeCapabilityDecisionService,
    SelfAttributeCapabilityEstimateProvider,
)
from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityDecision,
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    EstimateSource,
)
from soinesis.domain.models import SourceType
from soinesis.infrastructure.sqlite import SQLiteCapabilityUnitOfWorkFactory, SQLiteDatabase
from soinesis.ports.capabilities import (
    CapabilityPerformanceRepository,
    CapabilitySelfAttributeRepository,
    CapabilityUnitOfWork,
    MetacognitiveStateRepository,
    SelfModelVersionRepository,
)
from soinesis.ports.repositories import (
    JournalRepository,
    MemoryRepository,
    ObservationRepository,
)


@dataclass
class AccessCounts:
    factory_calls: int = 0
    uow_enters: int = 0
    uow_exits: int = 0
    commit_calls: int = 0
    performance_repository_accesses: int = 0
    performance_add_calls: int = 0
    performance_get_calls: int = 0
    performance_list_before_calls: int = 0
    metacognitive_repository_accesses: int = 0
    self_model_repository_accesses: int = 0
    self_attribute_repository_accesses: int = 0
    self_attribute_add_calls: int = 0
    self_attribute_get_current_calls: int = 0
    self_attribute_list_versions_calls: int = 0
    observation_repository_accesses: int = 0
    memory_repository_accesses: int = 0
    journal_repository_accesses: int = 0


class CapabilityPerformanceRepositoryProbe:
    def __init__(
        self,
        *,
        counts: AccessCounts,
        observations: tuple[CapabilityPerformanceObservation, ...] = (),
    ) -> None:
        self._counts = counts
        self._observations = observations
        self.boundaries: list[CapabilityHistoryBoundary] = []

    def add(self, observation: CapabilityPerformanceObservation) -> None:
        self._counts.performance_add_calls += 1
        raise AssertionError(
            f"Écriture de performance interdite pendant la décision: {observation.id}"
        )

    def get(self, observation_id: str) -> CapabilityPerformanceObservation | None:
        self._counts.performance_get_calls += 1
        raise AssertionError(f"Lecture directe de performance interdite: {observation_id}")

    def list_before(
        self,
        *,
        boundary: CapabilityHistoryBoundary,
    ) -> list[CapabilityPerformanceObservation]:
        self._counts.performance_list_before_calls += 1
        self.boundaries.append(boundary)
        return sorted(
            (
                observation
                for observation in self._observations
                if observation.agent_id == boundary.agent_id
                and observation.capability_key == boundary.capability_key
                and observation.sequence_index < boundary.sequence_index
            ),
            key=lambda observation: (
                observation.sequence_index,
                observation.observed_at,
                observation.id,
            ),
        )


class CapabilitySelfAttributeRepositoryProbe:
    def __init__(
        self,
        *,
        counts: AccessCounts,
        current: CapabilitySelfAttribute | None,
    ) -> None:
        self._counts = counts
        self._current = current

    def add(self, attribute: CapabilitySelfAttribute) -> None:
        self._counts.self_attribute_add_calls += 1
        raise AssertionError(f"Écriture de SelfAttribute interdite: {attribute.id}")

    def get_current(
        self,
        *,
        agent_id: str,
        capability_key: str,
    ) -> CapabilitySelfAttribute | None:
        self._counts.self_attribute_get_current_calls += 1
        if (
            self._current is None
            or self._current.agent_id != agent_id
            or self._current.capability_key != capability_key
        ):
            return None
        return self._current

    def list_versions(
        self,
        *,
        agent_id: str,
        capability_key: str,
    ) -> list[CapabilitySelfAttribute]:
        self._counts.self_attribute_list_versions_calls += 1
        raise AssertionError(
            f"Lecture de versions interdite pendant la décision: {agent_id}/{capability_key}"
        )


class CapabilityDecisionUnitOfWorkProbe:
    def __init__(
        self,
        *,
        counts: AccessCounts,
        performances: CapabilityPerformanceRepositoryProbe,
        self_attributes: CapabilitySelfAttributeRepositoryProbe,
    ) -> None:
        self._counts = counts
        self._performances = performances
        self._self_attributes = self_attributes

    @property
    def observations(self) -> ObservationRepository:
        self._counts.observation_repository_accesses += 1
        raise AssertionError("Le repository d'observations historique est interdit.")

    @property
    def memories(self) -> MemoryRepository:
        self._counts.memory_repository_accesses += 1
        raise AssertionError("Le repository de mémoires historique est interdit.")

    @property
    def journal(self) -> JournalRepository:
        self._counts.journal_repository_accesses += 1
        raise AssertionError("Le journal est interdit pendant la décision.")

    @property
    def capability_performances(self) -> CapabilityPerformanceRepository:
        self._counts.performance_repository_accesses += 1
        return self._performances

    @property
    def metacognitive_states(self) -> MetacognitiveStateRepository:
        self._counts.metacognitive_repository_accesses += 1
        raise AssertionError("Le MetaState est interdit pendant la décision.")

    @property
    def self_model_versions(self) -> SelfModelVersionRepository:
        self._counts.self_model_repository_accesses += 1
        raise AssertionError("Les SelfModelVersion sont interdites pendant la décision.")

    @property
    def capability_self_attributes(self) -> CapabilitySelfAttributeRepository:
        self._counts.self_attribute_repository_accesses += 1
        return self._self_attributes

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
        raise AssertionError("Une décision ne doit jamais committer.")


class CapabilityDecisionUnitOfWorkFactoryProbe:
    def __init__(
        self,
        *,
        counts: AccessCounts,
        unit_of_work: CapabilityDecisionUnitOfWorkProbe,
    ) -> None:
        self._counts = counts
        self._unit_of_work = unit_of_work

    def __call__(self) -> CapabilityUnitOfWork:
        self._counts.factory_calls += 1
        return self._unit_of_work


def build_boundary(*, sequence_index: int = 4) -> CapabilityHistoryBoundary:
    return CapabilityHistoryBoundary(
        agent_id="agent-1",
        capability_key="ALPHA",
        trial_id="trial-current",
        cycle_id="cycle-current",
        sequence_index=sequence_index,
    )


def build_observation(
    *,
    identifier: str,
    sequence_index: int,
    intrinsic_success: bool,
    agent_id: str = "agent-1",
    capability_key: str = "ALPHA",
    source_type: SourceType = SourceType.DIRECT_ENVIRONMENT,
) -> CapabilityPerformanceObservation:
    return CapabilityPerformanceObservation(
        id=identifier,
        agent_id=agent_id,
        trial_id=f"trial-{identifier}",
        cycle_id=f"cycle-{identifier}",
        sequence_index=sequence_index,
        capability_key=capability_key,
        intrinsic_success=intrinsic_success,
        observed_at=datetime(2026, 8, 8, 12, tzinfo=UTC) + timedelta(minutes=sequence_index),
        source_type=source_type,
    )


def build_attribute(estimated_success: float) -> CapabilitySelfAttribute:
    return CapabilitySelfAttribute(
        id="attribute-1",
        agent_id="agent-1",
        capability_key="ALPHA",
        estimated_success=estimated_success,
        self_model_version_id="self-model-version-1",
        attribute_version=1,
        created_at=datetime(2026, 8, 8, tzinfo=UTC),
    )


def build_access_probe(
    *,
    observations: tuple[CapabilityPerformanceObservation, ...] = (),
    attribute: CapabilitySelfAttribute | None = None,
) -> tuple[
    AccessCounts,
    CapabilityPerformanceRepositoryProbe,
    CapabilityDecisionUnitOfWorkFactoryProbe,
]:
    counts = AccessCounts()
    performance_repository = CapabilityPerformanceRepositoryProbe(
        counts=counts,
        observations=observations,
    )
    unit_of_work = CapabilityDecisionUnitOfWorkProbe(
        counts=counts,
        performances=performance_repository,
        self_attributes=CapabilitySelfAttributeRepositoryProbe(
            counts=counts,
            current=attribute,
        ),
    )
    return (
        counts,
        performance_repository,
        CapabilityDecisionUnitOfWorkFactoryProbe(
            counts=counts,
            unit_of_work=unit_of_work,
        ),
    )


def assert_no_forbidden_repository_access(counts: AccessCounts) -> None:
    assert counts.performance_add_calls == 0
    assert counts.performance_get_calls == 0
    assert counts.metacognitive_repository_accesses == 0
    assert counts.self_model_repository_accesses == 0
    assert counts.self_attribute_add_calls == 0
    assert counts.self_attribute_list_versions_calls == 0
    assert counts.observation_repository_accesses == 0
    assert counts.memory_repository_accesses == 0
    assert counts.journal_repository_accesses == 0
    assert counts.commit_calls == 0


def test_fixed_decision_service_uses_point_six_without_opening_any_repository() -> None:
    counts, _, _factory = build_access_probe()
    service = FixedCapabilityDecisionService(
        estimate_provider=FixedCapabilityEstimateProvider(),
        decision_policy=CapabilityDecisionPolicy(),
    )

    decision = service.decide(boundary=build_boundary())

    assert isinstance(decision, CapabilityDecision)
    assert decision.estimate.estimated_success == 0.60
    assert decision.estimate.source is EstimateSource.FIXED_BASELINE
    assert decision.action is CapabilityAction.VERIFY
    assert counts == AccessCounts()
    assert (
        "unit_of_work_factory" not in inspect.signature(FixedCapabilityDecisionService).parameters
    )


def test_raw_history_decision_service_is_the_single_b_and_future_self_abl_path() -> None:
    estimator = DecayedBetaEstimator(lambda_=0.5)
    observations = (
        build_observation(identifier="past-success", sequence_index=0, intrinsic_success=True),
        build_observation(
            identifier="ignored-imagination",
            sequence_index=1,
            intrinsic_success=False,
            source_type=SourceType.IMAGINATION,
        ),
        build_observation(
            identifier="other-capability",
            sequence_index=2,
            capability_key="BETA",
            intrinsic_success=True,
        ),
        build_observation(identifier="past-failure", sequence_index=3, intrinsic_success=False),
        build_observation(identifier="current", sequence_index=4, intrinsic_success=True),
        build_observation(identifier="future", sequence_index=5, intrinsic_success=True),
    )
    counts, repository, factory = build_access_probe(observations=observations)
    boundary = build_boundary()
    shared_b_and_future_self_abl_service = RawHistoryCapabilityDecisionService(
        unit_of_work_factory=factory,
        estimate_provider=RawHistoryCapabilityEstimateProvider(estimator=estimator),
        decision_policy=CapabilityDecisionPolicy(),
    )

    decision = shared_b_and_future_self_abl_service.decide(boundary=boundary)

    expected = estimator.replay((True, False)).estimated_success
    reverse = estimator.replay((False, True)).estimated_success
    assert isinstance(decision, CapabilityDecision)
    assert decision.estimate.estimated_success == expected
    assert decision.estimate.estimated_success != reverse
    assert decision.estimate.source is EstimateSource.RAW_HISTORY
    assert repository.boundaries == [boundary]
    assert repository.boundaries[0] is boundary
    assert counts.factory_calls == 1
    assert counts.uow_enters == 1
    assert counts.uow_exits == 1
    assert counts.performance_repository_accesses == 1
    assert counts.performance_list_before_calls == 1
    assert counts.self_attribute_repository_accesses == 0
    assert_no_forbidden_repository_access(counts)
    assert "B et à la future SELF-ABL" in (RawHistoryCapabilityDecisionService.__doc__ or "")


def test_raw_history_decision_service_uses_the_prior_for_an_empty_history() -> None:
    counts, _, factory = build_access_probe()
    service = RawHistoryCapabilityDecisionService(
        unit_of_work_factory=factory,
        estimate_provider=RawHistoryCapabilityEstimateProvider(
            estimator=DecayedBetaEstimator(lambda_=0.9)
        ),
        decision_policy=CapabilityDecisionPolicy(),
    )

    decision = service.decide(boundary=build_boundary(sequence_index=0))

    assert decision.estimate.estimated_success == 0.60
    assert decision.action is CapabilityAction.VERIFY
    assert counts.performance_list_before_calls == 1
    assert counts.self_attribute_repository_accesses == 0
    assert_no_forbidden_repository_access(counts)


def test_raw_history_decision_service_excludes_current_and_future_in_sqlite(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "raw-history-decision.db")
    database.initialize_capability_schema()
    factory = SQLiteCapabilityUnitOfWorkFactory(database)
    observations = (
        build_observation(identifier="past", sequence_index=0, intrinsic_success=True),
        build_observation(identifier="current", sequence_index=1, intrinsic_success=False),
        build_observation(identifier="future", sequence_index=2, intrinsic_success=False),
    )
    with factory() as unit_of_work:
        for observation in observations:
            unit_of_work.capability_performances.add(observation)
        unit_of_work.commit()
    estimator = DecayedBetaEstimator(lambda_=0.5)
    service = RawHistoryCapabilityDecisionService(
        unit_of_work_factory=factory,
        estimate_provider=RawHistoryCapabilityEstimateProvider(estimator=estimator),
        decision_policy=CapabilityDecisionPolicy(),
    )

    decision = service.decide(boundary=build_boundary(sequence_index=1))

    assert decision.estimate.estimated_success == estimator.replay((True,)).estimated_success
    with factory() as unit_of_work:
        assert (
            unit_of_work.metacognitive_states.get_current(
                agent_id="agent-1",
                capability_key="ALPHA",
            )
            is None
        )
        assert unit_of_work.self_model_versions.get_current(agent_id="agent-1") is None
        assert (
            unit_of_work.capability_self_attributes.get_current(
                agent_id="agent-1",
                capability_key="ALPHA",
            )
            is None
        )


@pytest.mark.parametrize(
    ("estimated_success", "expected_action"),
    (
        (0.49, CapabilityAction.HELP),
        (0.50, CapabilityAction.VERIFY),
        (0.79, CapabilityAction.VERIFY),
        (0.80, CapabilityAction.DIRECT),
    ),
)
def test_self_attribute_decision_service_reads_only_the_current_attribute(
    estimated_success: float,
    expected_action: CapabilityAction,
) -> None:
    counts, _, factory = build_access_probe(attribute=build_attribute(estimated_success))
    service = SelfAttributeCapabilityDecisionService(
        unit_of_work_factory=factory,
        estimate_provider=SelfAttributeCapabilityEstimateProvider(),
        decision_policy=CapabilityDecisionPolicy(),
    )

    decision = service.decide(boundary=build_boundary())

    assert isinstance(decision, CapabilityDecision)
    assert decision.estimate.estimated_success == estimated_success
    assert decision.estimate.source is EstimateSource.SELF_ATTRIBUTE
    assert decision.action is expected_action
    assert counts.factory_calls == 1
    assert counts.uow_enters == 1
    assert counts.uow_exits == 1
    assert counts.self_attribute_repository_accesses == 1
    assert counts.self_attribute_get_current_calls == 1
    assert counts.performance_repository_accesses == 0
    assert counts.performance_list_before_calls == 0
    assert_no_forbidden_repository_access(counts)


def test_self_attribute_decision_service_refuses_an_uninitialized_capability() -> None:
    counts, _, factory = build_access_probe(attribute=None)
    service = SelfAttributeCapabilityDecisionService(
        unit_of_work_factory=factory,
        estimate_provider=SelfAttributeCapabilityEstimateProvider(),
        decision_policy=CapabilityDecisionPolicy(),
    )

    with pytest.raises(CapabilitySelfModelNotInitializedError, match="initialisée"):
        service.decide(boundary=build_boundary())

    assert counts.self_attribute_repository_accesses == 1
    assert counts.self_attribute_get_current_calls == 1
    assert counts.performance_repository_accesses == 0
    assert_no_forbidden_repository_access(counts)


def test_decision_services_accept_only_the_public_boundary_at_decision_time() -> None:
    for service_type in (
        FixedCapabilityDecisionService,
        RawHistoryCapabilityDecisionService,
        SelfAttributeCapabilityDecisionService,
    ):
        parameters = inspect.signature(service_type.decide).parameters

        assert tuple(parameters) == ("self", "boundary")
        assert parameters["boundary"].kind is inspect.Parameter.KEYWORD_ONLY

    raw_constructor = inspect.signature(RawHistoryCapabilityDecisionService).parameters
    self_attribute_constructor = inspect.signature(
        SelfAttributeCapabilityDecisionService
    ).parameters
    assert {"estimator", "lambda_", "history"}.isdisjoint(raw_constructor)
    assert {
        "performance",
        "history",
        "metacognitive_state",
        "self_model_version",
        "alpha",
        "beta",
        "lambda_",
    }.isdisjoint(self_attribute_constructor)
