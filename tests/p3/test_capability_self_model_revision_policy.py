import inspect

import pytest

from soinesis.application.capabilities import (
    CapabilityDecisionPolicy,
    SignificantSelfRevisionPolicy,
)
from soinesis.domain.capabilities import CapabilityAction


@pytest.mark.parametrize(
    ("estimated_success", "expected_action"),
    (
        (0.49, CapabilityAction.HELP),
        (0.50, CapabilityAction.VERIFY),
        (0.79, CapabilityAction.VERIFY),
        (0.80, CapabilityAction.DIRECT),
    ),
)
def test_decision_policy_classifies_the_exact_revision_boundaries(
    estimated_success: float,
    expected_action: CapabilityAction,
) -> None:
    action = CapabilityDecisionPolicy().action_for_estimated_success(estimated_success)

    assert action is expected_action


@pytest.mark.parametrize(
    (
        "previous_estimated_success",
        "candidate_estimated_success",
        "expected_previous_action",
        "expected_resulting_action",
        "expected_significance",
    ),
    (
        (0.60, 0.70, CapabilityAction.VERIFY, CapabilityAction.VERIFY, False),
        (0.60, 0.80, CapabilityAction.VERIFY, CapabilityAction.DIRECT, True),
        (0.80, 0.79, CapabilityAction.DIRECT, CapabilityAction.VERIFY, True),
        (0.60, 0.49, CapabilityAction.VERIFY, CapabilityAction.HELP, True),
        (0.40, 0.30, CapabilityAction.HELP, CapabilityAction.HELP, False),
    ),
)
def test_revision_is_significant_exactly_when_the_decision_band_changes(
    previous_estimated_success: float,
    candidate_estimated_success: float,
    expected_previous_action: CapabilityAction,
    expected_resulting_action: CapabilityAction,
    expected_significance: bool,
) -> None:
    policy = SignificantSelfRevisionPolicy(decision_policy=CapabilityDecisionPolicy())

    assessment = policy.assess(
        previous_estimated_success=previous_estimated_success,
        candidate_estimated_success=candidate_estimated_success,
    )

    assert assessment.previous_action is expected_previous_action
    assert assessment.resulting_action is expected_resulting_action
    assert assessment.is_significant is expected_significance


def test_revision_policy_has_no_delta_threshold_or_evolving_state() -> None:
    decision_policy = CapabilityDecisionPolicy()
    policy = SignificantSelfRevisionPolicy(decision_policy=decision_policy)
    initial_policy_state = vars(policy).copy()

    first = policy.assess(
        previous_estimated_success=0.60,
        candidate_estimated_success=0.80,
    )
    repeated = policy.assess(
        previous_estimated_success=0.60,
        candidate_estimated_success=0.80,
    )

    assert first == repeated
    assert vars(policy) == initial_policy_state
    assert tuple(inspect.signature(SignificantSelfRevisionPolicy).parameters) == (
        "decision_policy",
    )
    assert tuple(inspect.signature(SignificantSelfRevisionPolicy.assess).parameters) == (
        "self",
        "previous_estimated_success",
        "candidate_estimated_success",
    )
