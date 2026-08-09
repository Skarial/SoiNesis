import inspect
from datetime import UTC, datetime

import pytest

from soinesis.application.capabilities import CapabilityDecisionPolicy
from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityDecision,
    CapabilityEstimate,
    CapabilityPerformanceObservation,
    EstimateSource,
)
from soinesis.experiments.p3 import (
    ExperimentalPlanPerformanceMismatchError,
    ExperimentalReplicationPlan,
    ExperimentalTrialOutcome,
)

OBSERVED_AT = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)


def valid_interleaved_order() -> list[str]:
    return [capability for _ in range(60) for capability in ("ALPHA", "BETA", "GAMMA")]


def build_plan(
    *,
    correction_latents: list[float] | None = None,
) -> ExperimentalReplicationPlan:
    return ExperimentalReplicationPlan(
        capability_order=valid_interleaved_order(),
        u_intrinsic_by_sequence=[0.90] * 180,
        u_correction_by_sequence=correction_latents or [0.70] * 180,
    )


def attempt(
    plan: ExperimentalReplicationPlan,
    *,
    sequence_index: int = 0,
    condition: str = "A",
) -> CapabilityPerformanceObservation:
    return plan.attempt(
        performance_id=f"performance-{condition}-{sequence_index}",
        agent_id=f"agent-{condition}",
        trial_id=f"trial-{condition}-{sequence_index}",
        cycle_id=f"cycle-{condition}-{sequence_index}",
        sequence_index=sequence_index,
        observed_at=OBSERVED_AT,
    )


def build_decision(
    action: CapabilityAction,
    *,
    agent_id: str = "agent-A",
    capability_key: str = "ALPHA",
) -> CapabilityDecision:
    estimated_success = 0.60 if action is CapabilityAction.VERIFY else 0.40
    decision = CapabilityDecisionPolicy().decide(
        CapabilityEstimate(
            agent_id=agent_id,
            capability_key=capability_key,
            estimated_success=estimated_success,
            source=EstimateSource.FIXED_BASELINE,
        )
    )
    assert decision.action is action
    return decision


def test_plan_resolves_an_outcome_from_its_private_cycle_latent() -> None:
    plan = build_plan()
    performance = attempt(plan)

    outcome = plan.resolve_outcome(
        decision=build_decision(CapabilityAction.VERIFY),
        performance=performance,
    )

    assert type(outcome) is ExperimentalTrialOutcome
    assert outcome.performance_id == performance.id
    assert outcome.intrinsic_success is False
    assert outcome.u_correction == 0.70
    assert outcome.correction_applied is False
    assert outcome.final_success is False


@pytest.mark.parametrize(
    "changed_fields",
    (
        {"intrinsic_success": True},
        {"capability_key": "BETA"},
        {"sequence_index": 1},
    ),
)
def test_plan_rejects_a_performance_incompatible_with_the_selected_cycle(
    changed_fields: dict[str, object],
) -> None:
    plan = build_plan()
    performance = attempt(plan).model_copy(update=changed_fields)

    with pytest.raises(ExperimentalPlanPerformanceMismatchError, match="incompatible"):
        plan.resolve_outcome(
            decision=build_decision(CapabilityAction.VERIFY),
            performance=performance,
        )


def test_plan_selects_correction_latent_at_the_exact_performance_index() -> None:
    correction_latents = [0.70] * 180
    correction_latents[3] = 0.20
    plan = build_plan(correction_latents=correction_latents)
    decision = build_decision(CapabilityAction.VERIFY)

    first = plan.resolve_outcome(decision=decision, performance=attempt(plan))
    second = plan.resolve_outcome(
        decision=decision,
        performance=attempt(plan, sequence_index=3),
    )

    assert first.u_correction == 0.70
    assert first.final_success is False
    assert second.u_correction == 0.20
    assert second.final_success is True


def test_same_plan_decision_and_performance_resolve_deterministically() -> None:
    plan = build_plan()
    decision = build_decision(CapabilityAction.HELP)
    performance = attempt(plan)

    first = plan.resolve_outcome(decision=decision, performance=performance)
    second = plan.resolve_outcome(decision=decision, performance=performance)

    assert first == second


def test_paired_conditions_share_one_correction_latent_with_different_actions() -> None:
    first_plan = build_plan()
    second_plan = build_plan()
    first_performance = attempt(first_plan, condition="A")
    second_performance = attempt(second_plan, condition="B")

    verify_outcome = first_plan.resolve_outcome(
        decision=build_decision(CapabilityAction.VERIFY, agent_id="agent-A"),
        performance=first_performance,
    )
    help_outcome = second_plan.resolve_outcome(
        decision=build_decision(CapabilityAction.HELP, agent_id="agent-B"),
        performance=second_performance,
    )

    assert first_performance.intrinsic_success is second_performance.intrinsic_success is False
    assert verify_outcome.u_correction == help_outcome.u_correction == 0.70
    assert verify_outcome.final_success is False
    assert help_outcome.final_success is True


def test_outcome_resolution_accepts_no_public_latent_or_capability() -> None:
    parameters = inspect.signature(ExperimentalReplicationPlan.resolve_outcome).parameters

    assert tuple(parameters) == ("self", "decision", "performance")
    assert "u_correction" not in parameters
    assert "u_intrinsic" not in parameters
    assert "capability_key" not in parameters
