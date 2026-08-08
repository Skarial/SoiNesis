from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityDecision,
    CapabilityEstimate,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    EstimateSource,
    MetacognitiveCapabilityState,
    SelfAttributeType,
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


def test_domain_models_reject_empty_identifiers_and_extra_truth() -> None:
    with pytest.raises(ValidationError):
        CapabilityPerformanceObservation.model_validate(
            {
                "id": "",
                "agent_id": "agent-1",
                "trial_id": "trial-1",
                "cycle_id": "cycle-1",
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
        MetacognitiveCapabilityState,
        CapabilitySelfAttribute,
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


def test_self_attribute_contains_only_a_consolidated_capability_estimate() -> None:
    attribute = CapabilitySelfAttribute(
        id="self-attribute-1",
        agent_id="agent-1",
        capability_key="BETA",
        estimated_success=0.73,
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


@pytest.mark.parametrize("estimated_success", (-0.01, 1.01, float("nan"), float("inf")))
def test_self_attribute_estimate_probability_is_bounded(estimated_success: float) -> None:
    with pytest.raises(ValidationError):
        CapabilitySelfAttribute(
            id="self-attribute-1",
            agent_id="agent-1",
            capability_key="ALPHA",
            estimated_success=estimated_success,
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
