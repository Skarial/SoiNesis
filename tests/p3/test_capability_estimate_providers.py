import inspect
from datetime import UTC, datetime

from soinesis.application.capabilities import (
    DecayedBetaEstimator,
    FixedCapabilityEstimateProvider,
    RawHistoryCapabilityEstimateProvider,
    SelfAttributeCapabilityEstimateProvider,
)
from soinesis.domain.capabilities import (
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    EstimateSource,
)
from soinesis.domain.models import SourceType


def build_observation(
    *,
    identifier: str,
    agent_id: str = "agent-1",
    capability_key: str = "ALPHA",
    intrinsic_success: bool,
) -> CapabilityPerformanceObservation:
    return CapabilityPerformanceObservation(
        id=identifier,
        agent_id=agent_id,
        trial_id=f"trial-{identifier}",
        cycle_id=f"cycle-{identifier}",
        capability_key=capability_key,
        intrinsic_success=intrinsic_success,
        observed_at=datetime(2026, 8, 8, tzinfo=UTC),
        source_type=SourceType.DIRECT_ENVIRONMENT,
    )


def test_fixed_provider_always_returns_point_six() -> None:
    provider = FixedCapabilityEstimateProvider()

    first = provider.estimate(agent_id="agent-1", capability_key="ALPHA")
    second = provider.estimate(agent_id="agent-2", capability_key="GAMMA")

    assert first.estimated_success == 0.60
    assert second.estimated_success == 0.60
    assert first.source is EstimateSource.FIXED_BASELINE
    assert second.source is EstimateSource.FIXED_BASELINE
    assert vars(provider) == {}


def test_raw_history_provider_replays_only_the_requested_agent_and_capability() -> None:
    estimator = DecayedBetaEstimator(lambda_=0.90)
    provider = RawHistoryCapabilityEstimateProvider(estimator=estimator)
    history = (
        build_observation(identifier="1", intrinsic_success=True),
        build_observation(identifier="2", capability_key="BETA", intrinsic_success=False),
        build_observation(identifier="3", agent_id="agent-2", intrinsic_success=False),
        build_observation(identifier="4", intrinsic_success=False),
    )

    estimate = provider.estimate(
        agent_id="agent-1",
        capability_key="ALPHA",
        history=history,
    )
    expected_state = estimator.replay((True, False))

    assert estimate.estimated_success == expected_state.estimated_success
    assert estimate.source is EstimateSource.RAW_HISTORY


def test_raw_history_provider_reconstructs_without_persisting_state() -> None:
    provider = RawHistoryCapabilityEstimateProvider(estimator=DecayedBetaEstimator(lambda_=0.95))
    successful_history = (build_observation(identifier="1", intrinsic_success=True),)
    initial_provider_state = vars(provider).copy()

    first = provider.estimate(
        agent_id="agent-1",
        capability_key="ALPHA",
        history=successful_history,
    )
    empty = provider.estimate(
        agent_id="agent-1",
        capability_key="ALPHA",
        history=(),
    )
    repeated = provider.estimate(
        agent_id="agent-1",
        capability_key="ALPHA",
        history=successful_history,
    )

    assert first.estimated_success > 0.60
    assert empty.estimated_success == 0.60
    assert repeated == first
    assert vars(provider) == initial_provider_state
    assert successful_history[0].intrinsic_success is True


def test_self_attribute_provider_uses_only_the_consolidated_attribute() -> None:
    provider = SelfAttributeCapabilityEstimateProvider()
    attribute = CapabilitySelfAttribute(
        id="self-attribute-1",
        agent_id="agent-1",
        capability_key="GAMMA",
        estimated_success=0.73,
    )

    estimate = provider.estimate(attribute=attribute)

    assert estimate.agent_id == attribute.agent_id
    assert estimate.capability_key == attribute.capability_key
    assert estimate.estimated_success == attribute.estimated_success
    assert estimate.source is EstimateSource.SELF_ATTRIBUTE


def test_self_attribute_provider_has_no_history_or_metacognitive_dependency() -> None:
    provider = SelfAttributeCapabilityEstimateProvider()

    assert tuple(inspect.signature(SelfAttributeCapabilityEstimateProvider).parameters) == ()
    assert tuple(inspect.signature(provider.estimate).parameters) == ("attribute",)
    assert vars(provider) == {}
