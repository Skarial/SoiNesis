from math import isclose

import pytest

from soinesis.application.capabilities import CapabilityDecisionPolicy
from soinesis.domain.capabilities import CapabilityAction, CapabilityEstimate, EstimateSource


def build_estimate(estimated_success: float) -> CapabilityEstimate:
    return CapabilityEstimate(
        agent_id="agent-1",
        capability_key="ALPHA",
        estimated_success=estimated_success,
        source=EstimateSource.RAW_HISTORY,
    )


@pytest.mark.parametrize(
    ("estimated_success", "expected_action"),
    (
        (0.0, CapabilityAction.HELP),
        (0.499999, CapabilityAction.HELP),
        (0.50, CapabilityAction.VERIFY),
        (0.799999, CapabilityAction.VERIFY),
        (0.80, CapabilityAction.DIRECT),
        (1.0, CapabilityAction.DIRECT),
    ),
)
def test_policy_applies_exact_decision_boundaries(
    estimated_success: float,
    expected_action: CapabilityAction,
) -> None:
    decision = CapabilityDecisionPolicy().decide(build_estimate(estimated_success))

    assert decision.action is expected_action


@pytest.mark.parametrize(
    ("estimated_success", "direct", "verify", "help_"),
    (
        (0.0, -10.0, -2.0, 2.0),
        (0.50, 0.0, 3.0, 3.0),
        (0.60, 2.0, 4.0, 3.2),
        (0.80, 6.0, 6.0, 3.6),
        (1.0, 10.0, 8.0, 4.0),
    ),
)
def test_policy_computes_all_declared_utilities(
    estimated_success: float,
    direct: float,
    verify: float,
    help_: float,
) -> None:
    decision = CapabilityDecisionPolicy().decide(build_estimate(estimated_success))

    assert isclose(decision.direct_utility, direct)
    assert isclose(decision.verify_utility, verify)
    assert isclose(decision.help_utility, help_)


def test_policy_preserves_the_estimate_and_its_source() -> None:
    estimate = build_estimate(0.73)

    decision = CapabilityDecisionPolicy().decide(estimate)

    assert decision.estimate is estimate
    assert decision.estimate.source is EstimateSource.RAW_HISTORY
