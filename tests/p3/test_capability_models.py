from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityDecision,
    CapabilityEstimate,
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    EstimateSource,
    MetacognitiveCapabilityState,
    SelfAttributeType,
    SelfModelVersion,
    VersionedMetacognitiveCapabilityState,
)
from soinesis.domain.models import SourceType

FORBIDDEN_PUBLIC_FIELDS = {
    "dataset_id",
    "final_success",
    "future_probability",
    "official_dataset_id",
    "oracle",
    "phase",
    "replication",
    "seed",
    "true_success_probability",
    "u_correction",
}


def build_observation() -> CapabilityPerformanceObservation:
    return CapabilityPerformanceObservation(
        id="performance-1",
        agent_id="agent-1",
        trial_id="trial-1",
        cycle_id="cycle-1",
        sequence_index=0,
        capability_key="ALPHA",
        intrinsic_success=True,
        observed_at=datetime(2026, 8, 8, tzinfo=UTC),
        source_type=SourceType.DIRECT_ENVIRONMENT,
    )


def test_performance_observation_is_intrinsic_immutable_evidence() -> None:
    observation = build_observation()

    assert observation.intrinsic_success is True
    assert observation.trial_id == "trial-1"
    assert observation.source_type is SourceType.DIRECT_ENVIRONMENT
    with pytest.raises(ValidationError):
        observation.intrinsic_success = False


@pytest.mark.parametrize("sequence_index", (-1, 1.0, "1", True))
def test_performance_observation_requires_a_non_negative_strict_sequence_index(
    sequence_index: object,
) -> None:
    invalid_observation = build_observation().model_dump()
    invalid_observation["sequence_index"] = sequence_index

    with pytest.raises(ValidationError):
        CapabilityPerformanceObservation.model_validate(invalid_observation)


def test_history_boundary_is_public_scoped_and_contains_no_outcome() -> None:
    boundary = CapabilityHistoryBoundary(
        agent_id="agent-1",
        capability_key="ALPHA",
        trial_id="trial-2",
        cycle_id="cycle-2",
        sequence_index=1,
    )

    assert boundary.sequence_index == 1
    assert {"intrinsic_success", "observed_at"}.isdisjoint(CapabilityHistoryBoundary.model_fields)

    with pytest.raises(ValidationError):
        CapabilityHistoryBoundary.model_validate(
            {
                **boundary.model_dump(),
                "phase": 2,
            }
        )

    with pytest.raises(ValidationError):
        CapabilityHistoryBoundary.model_validate(
            {
                **boundary.model_dump(),
                "sequence_index": -1,
            }
        )


def test_observation_preserves_provenance_for_future_service_authorization() -> None:
    observation = CapabilityPerformanceObservation.model_validate(
        {
            **build_observation().model_dump(),
            "source_type": SourceType.IMAGINATION,
        }
    )

    # Le futur service applicatif devra refuser cette provenance comme preuve propre.
    assert observation.source_type is SourceType.IMAGINATION


def test_domain_models_reject_empty_identifiers_and_extra_truth() -> None:
    with pytest.raises(ValidationError):
        CapabilityPerformanceObservation.model_validate(
            {
                "id": "",
                "agent_id": "agent-1",
                "trial_id": "trial-1",
                "cycle_id": "cycle-1",
                "sequence_index": 0,
                "capability_key": "ALPHA",
                "intrinsic_success": True,
                "observed_at": datetime(2026, 8, 8, tzinfo=UTC),
                "source_type": SourceType.DIRECT_ENVIRONMENT,
            }
        )

    with pytest.raises(ValidationError):
        CapabilityPerformanceObservation.model_validate(
            {
                **build_observation().model_dump(),
                "true_success_probability": 0.65,
            }
        )


@pytest.mark.parametrize("coerced_success", (1, 0, "true", "false"))
def test_performance_observation_requires_a_strict_boolean(coerced_success: object) -> None:
    invalid_observation = build_observation().model_dump()
    invalid_observation["intrinsic_success"] = coerced_success

    with pytest.raises(ValidationError):
        CapabilityPerformanceObservation.model_validate(invalid_observation)


def test_public_cognitive_models_expose_no_private_experimental_fields() -> None:
    public_models = (
        CapabilityPerformanceObservation,
        CapabilityHistoryBoundary,
        MetacognitiveCapabilityState,
        VersionedMetacognitiveCapabilityState,
        CapabilitySelfAttribute,
        SelfModelVersion,
        CapabilityEstimate,
        CapabilityDecision,
    )

    for model in public_models:
        assert FORBIDDEN_PUBLIC_FIELDS.isdisjoint(model.model_fields)


def test_metacognitive_state_validates_parameters_and_lambda_bounds() -> None:
    valid_state = MetacognitiveCapabilityState(alpha=3.0, beta=2.0, lambda_=1.0)
    assert valid_state.estimated_success == 0.60

    invalid_states = (
        {"alpha": 0.0, "beta": 2.0, "lambda_": 0.9},
        {"alpha": 3.0, "beta": 0.0, "lambda_": 0.9},
        {"alpha": 3.0, "beta": 2.0, "lambda_": 0.0},
        {"alpha": 3.0, "beta": 2.0, "lambda_": -0.1},
        {"alpha": 3.0, "beta": 2.0, "lambda_": 1.01},
        {"alpha": 3.0, "beta": 2.0, "lambda_": float("nan")},
        {"alpha": 3.0, "beta": 2.0, "lambda_": float("inf")},
    )
    for invalid_state in invalid_states:
        with pytest.raises(ValidationError):
            MetacognitiveCapabilityState.model_validate(invalid_state)


def test_versioned_metacognitive_state_scopes_and_versions_the_statistical_state() -> None:
    statistical_state = MetacognitiveCapabilityState(alpha=3.0, beta=2.0, lambda_=0.9)
    versioned_state = VersionedMetacognitiveCapabilityState(
        agent_id="agent-1",
        capability_key="ALPHA",
        version=1,
        state=statistical_state,
    )

    assert versioned_state.state == statistical_state
    assert versioned_state.version == 1

    with pytest.raises(ValidationError):
        VersionedMetacognitiveCapabilityState(
            agent_id="agent-1",
            capability_key="ALPHA",
            version=0,
            state=statistical_state,
        )


def test_self_attribute_contains_only_a_consolidated_capability_estimate() -> None:
    attribute = CapabilitySelfAttribute(
        id="self-attribute-1",
        agent_id="agent-1",
        capability_key="BETA",
        estimated_success=0.73,
        self_model_version_id="self-model-version-1",
        attribute_version=1,
        created_at=datetime(2026, 8, 8, tzinfo=UTC),
    )

    assert attribute.attribute_type is SelfAttributeType.CAPABILITY
    assert {"alpha", "beta", "lambda_"}.isdisjoint(CapabilitySelfAttribute.model_fields)

    with pytest.raises(ValidationError):
        CapabilitySelfAttribute.model_validate(
            {
                **attribute.model_dump(),
                "alpha": 3.0,
            }
        )

    with pytest.raises(ValidationError):
        CapabilitySelfAttribute.model_validate(
            {
                **attribute.model_dump(),
                "attribute_type": "OTHER",
            }
        )


def test_self_attribute_version_chain_is_append_only() -> None:
    first = CapabilitySelfAttribute(
        id="self-attribute-1",
        agent_id="agent-1",
        capability_key="ALPHA",
        estimated_success=0.60,
        self_model_version_id="self-model-version-1",
        attribute_version=1,
        created_at=datetime(2026, 8, 8, tzinfo=UTC),
    )
    second = CapabilitySelfAttribute(
        id="self-attribute-2",
        agent_id="agent-1",
        capability_key="ALPHA",
        estimated_success=0.70,
        self_model_version_id="self-model-version-2",
        attribute_version=2,
        previous_attribute_id=first.id,
        created_at=datetime(2026, 8, 9, tzinfo=UTC),
    )

    assert second.previous_attribute_id == first.id

    invalid_chains = (
        {**first.model_dump(), "previous_attribute_id": "unexpected"},
        {**second.model_dump(), "previous_attribute_id": None},
        {**second.model_dump(), "previous_attribute_id": second.id},
    )
    for invalid_chain in invalid_chains:
        with pytest.raises(ValidationError):
            CapabilitySelfAttribute.model_validate(invalid_chain)


def test_self_model_version_chain_is_append_only() -> None:
    first = SelfModelVersion(
        id="self-model-version-1",
        agent_id="agent-1",
        version=1,
        created_at=datetime(2026, 8, 8, tzinfo=UTC),
    )
    second = SelfModelVersion(
        id="self-model-version-2",
        agent_id="agent-1",
        version=2,
        previous_version_id=first.id,
        created_at=datetime(2026, 8, 9, tzinfo=UTC),
    )

    assert second.previous_version_id == first.id

    invalid_chains = (
        {**first.model_dump(), "previous_version_id": "unexpected"},
        {**second.model_dump(), "previous_version_id": None},
        {**second.model_dump(), "previous_version_id": second.id},
    )
    for invalid_chain in invalid_chains:
        with pytest.raises(ValidationError):
            SelfModelVersion.model_validate(invalid_chain)


@pytest.mark.parametrize("estimated_success", (-0.01, 1.01, float("nan"), float("inf")))
def test_self_attribute_estimate_probability_is_bounded(estimated_success: float) -> None:
    with pytest.raises(ValidationError):
        CapabilitySelfAttribute(
            id="self-attribute-1",
            agent_id="agent-1",
            capability_key="ALPHA",
            estimated_success=estimated_success,
            self_model_version_id="self-model-version-1",
            attribute_version=1,
            created_at=datetime(2026, 8, 8, tzinfo=UTC),
        )


@pytest.mark.parametrize("estimated_success", (-0.01, 1.01, float("nan"), float("inf")))
def test_capability_estimate_probability_is_bounded(estimated_success: float) -> None:
    with pytest.raises(ValidationError):
        CapabilityEstimate(
            agent_id="agent-1",
            capability_key="ALPHA",
            estimated_success=estimated_success,
            source=EstimateSource.FIXED_BASELINE,
        )


def test_capability_enum_values_are_explicit() -> None:
    assert tuple(CapabilityAction) == (
        CapabilityAction.DIRECT,
        CapabilityAction.VERIFY,
        CapabilityAction.HELP,
    )
    assert tuple(EstimateSource) == (
        EstimateSource.FIXED_BASELINE,
        EstimateSource.RAW_HISTORY,
        EstimateSource.SELF_ATTRIBUTE,
    )
