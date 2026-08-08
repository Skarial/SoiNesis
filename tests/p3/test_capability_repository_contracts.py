import inspect
from datetime import UTC, datetime

import pytest

from soinesis.domain.capabilities import (
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
)
from soinesis.domain.models import SourceType
from soinesis.ports.capabilities import (
    CapabilityPerformanceRepository,
    CapabilitySelfAttributeRepository,
    CapabilityUnitOfWork,
    CapabilityUnitOfWorkFactory,
    MetacognitiveStateRepository,
    SelfModelVersionRepository,
)
from soinesis.ports.repositories import UnitOfWork, UnitOfWorkFactory


class InMemoryCapabilityPerformanceContractProbe:
    """Double local documentant les garanties exigées du futur adapter."""

    def __init__(self) -> None:
        self._observations: list[CapabilityPerformanceObservation] = []

    def add(self, observation: CapabilityPerformanceObservation) -> None:
        if any(
            persisted.agent_id == observation.agent_id
            and persisted.sequence_index >= observation.sequence_index
            for persisted in self._observations
        ):
            raise ValueError("La chronologie publique de l'agent doit être strictement croissante.")
        self._observations.append(observation)

    def get(self, observation_id: str) -> CapabilityPerformanceObservation | None:
        return next(
            (observation for observation in self._observations if observation.id == observation_id),
            None,
        )

    def list_before(
        self,
        *,
        boundary: CapabilityHistoryBoundary,
    ) -> list[CapabilityPerformanceObservation]:
        matching_past = (
            observation
            for observation in self._observations
            if observation.agent_id == boundary.agent_id
            and observation.capability_key == boundary.capability_key
            and observation.sequence_index < boundary.sequence_index
        )
        return sorted(
            matching_past,
            key=lambda observation: (
                observation.sequence_index,
                observation.observed_at,
                observation.id,
            ),
        )


class NeverCalledCapabilityUnitOfWorkFactory:
    """Double servant uniquement à vérifier le sous-typage structurel."""

    def __call__(self) -> CapabilityUnitOfWork:
        raise AssertionError("Ce double de typage ne doit pas ouvrir de transaction.")


def build_observation(
    *,
    identifier: str,
    sequence_index: int,
    minute: int = 0,
    agent_id: str = "agent-1",
    capability_key: str = "ALPHA",
    intrinsic_success: bool = True,
) -> CapabilityPerformanceObservation:
    return CapabilityPerformanceObservation(
        id=identifier,
        agent_id=agent_id,
        trial_id=f"trial-{identifier}",
        cycle_id=f"cycle-{identifier}",
        sequence_index=sequence_index,
        capability_key=capability_key,
        intrinsic_success=intrinsic_success,
        observed_at=datetime(2026, 8, 8, 12, minute, tzinfo=UTC),
        source_type=SourceType.DIRECT_ENVIRONMENT,
    )


def test_performance_history_contract_excludes_current_future_and_other_scopes() -> None:
    repository: CapabilityPerformanceRepository = InMemoryCapabilityPerformanceContractProbe()
    observations = (
        build_observation(identifier="past-0", sequence_index=0, minute=2),
        build_observation(identifier="other-agent", sequence_index=0, agent_id="agent-2"),
        build_observation(identifier="past-1", sequence_index=1, minute=1),
        build_observation(identifier="other-capability", sequence_index=2, capability_key="BETA"),
        build_observation(identifier="past-3", sequence_index=3, minute=2),
        build_observation(identifier="current", sequence_index=4, intrinsic_success=False),
        build_observation(identifier="future", sequence_index=5),
    )
    for observation in observations:
        repository.add(observation)

    boundary = CapabilityHistoryBoundary(
        agent_id="agent-1",
        capability_key="ALPHA",
        trial_id="trial-current",
        cycle_id="cycle-current",
        sequence_index=4,
    )

    first_read = repository.list_before(boundary=boundary)
    second_read = repository.list_before(boundary=boundary)

    assert [observation.id for observation in first_read] == [
        "past-0",
        "past-1",
        "past-3",
    ]
    assert second_read == first_read
    assert all(observation.agent_id == boundary.agent_id for observation in first_read)
    assert all(observation.capability_key == boundary.capability_key for observation in first_read)
    assert all(observation.sequence_index < boundary.sequence_index for observation in first_read)


def test_performance_add_contract_is_monotonic_globally_per_agent() -> None:
    repository: CapabilityPerformanceRepository = InMemoryCapabilityPerformanceContractProbe()
    first = build_observation(identifier="agent-1-alpha-0", sequence_index=0)
    third = build_observation(
        identifier="agent-1-beta-2",
        sequence_index=2,
        capability_key="BETA",
    )
    late = build_observation(identifier="agent-1-alpha-1", sequence_index=1)
    other_agent = build_observation(
        identifier="agent-2-alpha-0",
        sequence_index=0,
        agent_id="agent-2",
    )

    repository.add(first)
    repository.add(third)
    with pytest.raises(ValueError, match="strictement croissante"):
        repository.add(late)
    repository.add(other_agent)

    assert repository.get(first.id) == first
    assert repository.get(third.id) == third
    assert repository.get(late.id) is None
    assert repository.get(other_agent.id) == other_agent


def test_performance_history_port_exposes_only_a_nominal_causal_boundary() -> None:
    parameters = inspect.signature(CapabilityPerformanceRepository.list_before).parameters

    assert tuple(parameters) == ("self", "boundary")
    assert parameters["boundary"].kind is inspect.Parameter.KEYWORD_ONLY


def test_performance_repository_reads_only_a_persisted_identifier() -> None:
    repository: CapabilityPerformanceRepository = InMemoryCapabilityPerformanceContractProbe()
    observation = build_observation(identifier="performance-1", sequence_index=0)
    repository.add(observation)

    assert repository.get(observation.id) == observation
    assert repository.get("missing") is None
    assert tuple(inspect.signature(CapabilityPerformanceRepository.get).parameters) == (
        "self",
        "observation_id",
    )


def test_metacognitive_replace_contract_requires_an_expected_version() -> None:
    parameters = inspect.signature(MetacognitiveStateRepository.replace_current).parameters

    assert tuple(parameters) == ("self", "state", "expected_version")
    assert parameters["state"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["expected_version"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["expected_version"].default is inspect.Parameter.empty


def test_snapshot_repositories_are_append_only_and_scope_their_reads() -> None:
    assert set(SelfModelVersionRepository.__dict__).isdisjoint({"update", "replace", "delete"})
    assert set(CapabilitySelfAttributeRepository.__dict__).isdisjoint(
        {"update", "replace", "delete"}
    )
    assert tuple(inspect.signature(SelfModelVersionRepository.get_current).parameters) == (
        "self",
        "agent_id",
    )
    assert tuple(inspect.signature(CapabilitySelfAttributeRepository.get_current).parameters) == (
        "self",
        "agent_id",
        "capability_key",
    )


def test_capability_uow_is_additive_and_leaves_the_legacy_contract_unchanged() -> None:
    p3_repository_properties = {
        "capability_performances",
        "metacognitive_states",
        "self_model_versions",
        "capability_self_attributes",
    }

    assert p3_repository_properties.isdisjoint(UnitOfWork.__dict__)
    assert p3_repository_properties.issubset(CapabilityUnitOfWork.__dict__)


def test_capability_uow_factory_remains_assignable_to_the_legacy_factory() -> None:
    specialized: CapabilityUnitOfWorkFactory = NeverCalledCapabilityUnitOfWorkFactory()
    legacy: UnitOfWorkFactory = specialized

    assert legacy is specialized
