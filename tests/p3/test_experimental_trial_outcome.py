import ast
import inspect
from datetime import UTC, datetime
from math import isclose
from pathlib import Path

import pytest
from pydantic import ValidationError

from soinesis.application.capabilities import CapabilityDecisionPolicy
from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityDecision,
    CapabilityEstimate,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    EstimateSource,
    MetacognitiveCapabilityState,
)
from soinesis.domain.models import JournalEvent, SourceType
from soinesis.experiments.p3 import (
    ExperimentalTrialContextMismatchError,
    ExperimentalTrialOutcome,
    ExperimentalTrialOutcomeResolver,
)

OBSERVED_AT = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
PRIVATE_OUTCOME_FIELDS = {
    "correction_applied",
    "final_success",
    "realized_reward",
    "u_correction",
}
ACTION_ESTIMATES = {
    CapabilityAction.DIRECT: 0.80,
    CapabilityAction.VERIFY: 0.60,
    CapabilityAction.HELP: 0.40,
}


def build_decision(
    action: CapabilityAction,
    *,
    agent_id: str = "agent-1",
    capability_key: str = "ALPHA",
) -> CapabilityDecision:
    decision = CapabilityDecisionPolicy().decide(
        CapabilityEstimate(
            agent_id=agent_id,
            capability_key=capability_key,
            estimated_success=ACTION_ESTIMATES[action],
            source=EstimateSource.FIXED_BASELINE,
        )
    )
    assert decision.action is action
    return decision


def build_performance(
    *,
    intrinsic_success: bool,
    agent_id: str = "agent-1",
    capability_key: str = "ALPHA",
) -> CapabilityPerformanceObservation:
    return CapabilityPerformanceObservation(
        id="performance-1",
        agent_id=agent_id,
        trial_id="trial-1",
        cycle_id="cycle-1",
        sequence_index=7,
        capability_key=capability_key,
        intrinsic_success=intrinsic_success,
        observed_at=OBSERVED_AT,
        source_type=SourceType.DIRECT_ENVIRONMENT,
    )


def resolve(
    action: CapabilityAction,
    *,
    intrinsic_success: bool,
    u_correction: float,
) -> ExperimentalTrialOutcome:
    return ExperimentalTrialOutcomeResolver().resolve(
        decision=build_decision(action),
        performance=build_performance(intrinsic_success=intrinsic_success),
        u_correction=u_correction,
    )


@pytest.mark.parametrize("u_correction", (0.0, 0.49, 0.99))
def test_direct_never_corrects_an_intrinsic_failure(u_correction: float) -> None:
    outcome = resolve(
        CapabilityAction.DIRECT,
        intrinsic_success=False,
        u_correction=u_correction,
    )

    assert outcome.correction_applied is False
    assert outcome.final_success is False
    assert outcome.action_cost == 0
    assert outcome.outcome_reward == -10
    assert outcome.realized_reward == -10


@pytest.mark.parametrize(
    ("u_correction", "expected_correction", "expected_reward"),
    (
        (0.0, True, 8),
        (0.499999, True, 8),
        (0.50, False, -12),
        (0.99, False, -12),
    ),
)
def test_verify_uses_the_exact_strict_correction_boundary(
    u_correction: float,
    expected_correction: bool,
    expected_reward: int,
) -> None:
    outcome = resolve(
        CapabilityAction.VERIFY,
        intrinsic_success=False,
        u_correction=u_correction,
    )

    assert outcome.correction_applied is expected_correction
    assert outcome.final_success is expected_correction
    assert outcome.action_cost == 2
    assert outcome.outcome_reward == (10 if expected_correction else -10)
    assert outcome.realized_reward == expected_reward


@pytest.mark.parametrize(
    ("u_correction", "expected_correction", "expected_reward"),
    (
        (0.0, True, 4),
        (0.899999, True, 4),
        (0.90, False, -16),
        (0.99, False, -16),
    ),
)
def test_help_uses_the_exact_strict_correction_boundary(
    u_correction: float,
    expected_correction: bool,
    expected_reward: int,
) -> None:
    outcome = resolve(
        CapabilityAction.HELP,
        intrinsic_success=False,
        u_correction=u_correction,
    )

    assert outcome.correction_applied is expected_correction
    assert outcome.final_success is expected_correction
    assert outcome.action_cost == 6
    assert outcome.outcome_reward == (10 if expected_correction else -10)
    assert outcome.realized_reward == expected_reward


@pytest.mark.parametrize(
    ("action", "expected_cost", "expected_reward"),
    (
        (CapabilityAction.DIRECT, 0, 10),
        (CapabilityAction.VERIFY, 2, 8),
        (CapabilityAction.HELP, 6, 4),
    ),
)
def test_intrinsic_success_is_never_attributed_to_correction(
    action: CapabilityAction,
    expected_cost: int,
    expected_reward: int,
) -> None:
    performance = build_performance(intrinsic_success=True)

    outcome = ExperimentalTrialOutcomeResolver().resolve(
        decision=build_decision(action),
        performance=performance,
        u_correction=0.0,
    )

    assert performance.intrinsic_success is True
    assert outcome.intrinsic_success is True
    assert outcome.correction_applied is False
    assert outcome.final_success is True
    assert outcome.action_cost == expected_cost
    assert outcome.outcome_reward == 10
    assert outcome.realized_reward == expected_reward


@pytest.mark.parametrize(
    "u_correction",
    (-0.01, 1.0, 1.01, float("nan"), float("inf"), float("-inf")),
)
def test_correction_latent_must_be_finite_and_in_half_open_unit_interval(
    u_correction: float,
) -> None:
    with pytest.raises(ValueError, match="u_correction"):
        resolve(
            CapabilityAction.DIRECT,
            intrinsic_success=True,
            u_correction=u_correction,
        )


@pytest.mark.parametrize("u_correction", (False, True))
def test_correction_latent_rejects_booleans_even_after_intrinsic_success(
    u_correction: bool,
) -> None:
    with pytest.raises(TypeError, match="u_correction"):
        resolve(
            CapabilityAction.DIRECT,
            intrinsic_success=True,
            u_correction=u_correction,
        )


@pytest.mark.parametrize(
    ("decision", "performance", "message"),
    (
        (
            build_decision(CapabilityAction.DIRECT, agent_id="agent-2"),
            build_performance(intrinsic_success=False),
            "agent",
        ),
        (
            build_decision(CapabilityAction.DIRECT, capability_key="BETA"),
            build_performance(intrinsic_success=False),
            "capability_key",
        ),
    ),
)
def test_decision_and_performance_context_mismatch_is_rejected(
    decision: CapabilityDecision,
    performance: CapabilityPerformanceObservation,
    message: str,
) -> None:
    with pytest.raises(ExperimentalTrialContextMismatchError, match=message):
        ExperimentalTrialOutcomeResolver().resolve(
            decision=decision,
            performance=performance,
            u_correction=0.0,
        )


def test_resolver_is_deterministic_and_has_no_evolving_state() -> None:
    resolver = ExperimentalTrialOutcomeResolver()
    decision = build_decision(CapabilityAction.VERIFY)
    performance = build_performance(intrinsic_success=False)

    first = resolver.resolve(
        decision=decision,
        performance=performance,
        u_correction=0.25,
    )
    second = resolver.resolve(
        decision=decision,
        performance=performance,
        u_correction=0.25,
    )

    assert first == second
    assert vars(resolver) == {}


@pytest.mark.parametrize(
    ("action", "estimated_success", "correction_probability"),
    (
        (CapabilityAction.DIRECT, 0.80, 0.0),
        (CapabilityAction.VERIFY, 0.60, 0.50),
        (CapabilityAction.HELP, 0.40, 0.90),
    ),
)
def test_realized_mechanics_match_the_existing_expected_utilities(
    action: CapabilityAction,
    estimated_success: float,
    correction_probability: float,
) -> None:
    decision = build_decision(action)
    intrinsic_success_reward = resolve(
        action,
        intrinsic_success=True,
        u_correction=0.0,
    ).realized_reward
    corrected_failure_reward = resolve(
        action,
        intrinsic_success=False,
        u_correction=0.0,
    ).realized_reward
    uncorrected_failure_reward = resolve(
        action,
        intrinsic_success=False,
        u_correction=correction_probability,
    ).realized_reward
    expected_utility = estimated_success * intrinsic_success_reward + (1.0 - estimated_success) * (
        correction_probability * corrected_failure_reward
        + (1.0 - correction_probability) * uncorrected_failure_reward
    )

    if action is CapabilityAction.DIRECT:
        assert isclose(expected_utility, decision.direct_utility)
    elif action is CapabilityAction.VERIFY:
        assert isclose(expected_utility, decision.verify_utility)
    else:
        assert isclose(expected_utility, decision.help_utility)


def test_outcome_is_strict_frozen_and_extra_forbidden() -> None:
    outcome = resolve(
        CapabilityAction.DIRECT,
        intrinsic_success=True,
        u_correction=0.25,
    )

    with pytest.raises(ValidationError):
        ExperimentalTrialOutcome.model_validate({**outcome.model_dump(), "unknown": "value"})
    with pytest.raises(ValidationError):
        ExperimentalTrialOutcome.model_validate({**outcome.model_dump(), "action_cost": 0.0})
    with pytest.raises(ValidationError):
        outcome.final_success = False  # type: ignore[misc]


def test_outcome_keeps_intrinsic_and_final_success_separate() -> None:
    performance = build_performance(intrinsic_success=False)

    outcome = ExperimentalTrialOutcomeResolver().resolve(
        decision=build_decision(CapabilityAction.HELP),
        performance=performance,
        u_correction=0.0,
    )

    assert performance.intrinsic_success is False
    assert outcome.intrinsic_success is False
    assert outcome.final_success is True
    assert type(outcome) is ExperimentalTrialOutcome


def test_private_outcome_fields_do_not_enter_cognitive_models() -> None:
    cognitive_models = (
        CapabilityPerformanceObservation,
        CapabilityEstimate,
        CapabilityDecision,
        MetacognitiveCapabilityState,
        CapabilitySelfAttribute,
        JournalEvent,
    )

    for cognitive_model in cognitive_models:
        assert PRIVATE_OUTCOME_FIELDS.isdisjoint(cognitive_model.model_fields)


def test_cognitive_modules_do_not_import_the_private_outcome_mechanics() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    cognitive_paths = (
        repository_root / "src" / "soinesis" / "domain" / "capabilities.py",
        repository_root / "src" / "soinesis" / "application" / "capabilities.py",
        repository_root / "src" / "soinesis" / "ports" / "capabilities.py",
    )

    for cognitive_path in cognitive_paths:
        syntax_tree = ast.parse(cognitive_path.read_text(encoding="utf-8"))
        imported_modules = {
            imported_name
            for node in ast.walk(syntax_tree)
            for imported_name in _imported_module_names(node)
        }
        assert not any(
            imported_module.startswith("soinesis.experiments.p3")
            for imported_module in imported_modules
        )


def test_resolver_signature_accepts_only_decision_performance_and_one_latent() -> None:
    parameters = inspect.signature(ExperimentalTrialOutcomeResolver.resolve).parameters

    assert tuple(parameters) == ("self", "decision", "performance", "u_correction")


def _imported_module_names(node: ast.AST) -> tuple[str, ...]:
    if isinstance(node, ast.Import):
        return tuple(alias.name for alias in node.names)
    if isinstance(node, ast.ImportFrom) and node.module is not None:
        return (node.module,)
    return ()
