import inspect
from math import isclose

import pytest
from pydantic import ValidationError

from soinesis.application.capabilities import DecayedBetaEstimator
from soinesis.domain.capabilities import MetacognitiveCapabilityState


def test_estimator_requires_an_explicit_lambda() -> None:
    parameter = inspect.signature(DecayedBetaEstimator).parameters["lambda_"]

    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty


@pytest.mark.parametrize("lambda_", (0.0, -0.1, 1.01, float("nan"), float("inf")))
def test_estimator_rejects_invalid_lambda(lambda_: float) -> None:
    with pytest.raises(ValidationError):
        DecayedBetaEstimator(lambda_=lambda_)


def test_prior_mean_is_point_six() -> None:
    state = DecayedBetaEstimator(lambda_=0.95).initial_state()

    assert state.alpha == 3.0
    assert state.beta == 2.0
    assert state.estimated_success == 0.60


def test_success_and_failure_follow_the_declared_recurrence() -> None:
    estimator = DecayedBetaEstimator(lambda_=0.90)

    after_success = estimator.update(estimator.initial_state(), intrinsic_success=True)
    after_failure = estimator.update(after_success, intrinsic_success=False)

    assert isclose(after_success.alpha, 4.0)
    assert isclose(after_success.beta, 2.0)
    assert isclose(after_failure.alpha, 3.9)
    assert isclose(after_failure.beta, 3.0)


def test_replay_of_empty_history_returns_a_fresh_prior() -> None:
    estimator = DecayedBetaEstimator(lambda_=0.94)

    assert estimator.replay(()) == estimator.initial_state()


def test_replay_is_exactly_equivalent_to_successive_updates() -> None:
    estimator = DecayedBetaEstimator(lambda_=0.94)
    history = (True, False, True, True, False)
    successive_state = estimator.initial_state()
    for intrinsic_success in history:
        successive_state = estimator.update(successive_state, intrinsic_success)

    assert estimator.replay(history) == successive_state


def test_replay_does_not_mutate_the_supplied_history() -> None:
    estimator = DecayedBetaEstimator(lambda_=0.92)
    history = [True, False, True]

    estimator.replay(history)

    assert history == [True, False, True]


def test_update_rejects_a_state_with_a_different_lambda() -> None:
    estimator = DecayedBetaEstimator(lambda_=0.90)
    incompatible_state = MetacognitiveCapabilityState(alpha=3.0, beta=2.0, lambda_=0.95)

    with pytest.raises(ValueError, match="facteur lambda différent"):
        estimator.update(incompatible_state, intrinsic_success=True)
