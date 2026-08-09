import ast
import inspect
from datetime import UTC, datetime
from pathlib import Path

import pytest

from soinesis.domain.capabilities import CapabilityPerformanceObservation
from soinesis.domain.models import SourceType
from soinesis.experiments.p3 import (
    ExperimentalReplicationPlan,
    InvalidExperimentalReplicationPlanError,
)

OBSERVED_AT = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
PRIVATE_EXPERIMENTAL_FIELDS = {
    "dataset",
    "final_success",
    "oracle",
    "phase",
    "replication",
    "seed",
    "segment",
    "true_success_probability",
    "u_correction",
    "u_intrinsic",
}


def valid_interleaved_order() -> list[str]:
    return [capability for _ in range(60) for capability in ("ALPHA", "BETA", "GAMMA")]


def valid_latents(value: float = 0.60) -> list[float]:
    return [value] * 180


def build_plan(
    *,
    capability_order: list[str] | None = None,
    latents: list[float] | None = None,
    correction_latents: list[float] | None = None,
) -> ExperimentalReplicationPlan:
    return ExperimentalReplicationPlan(
        capability_order=capability_order or valid_interleaved_order(),
        u_intrinsic_by_sequence=latents or valid_latents(),
        u_correction_by_sequence=correction_latents or valid_latents(0.70),
    )


def attempt(
    plan: ExperimentalReplicationPlan,
    *,
    sequence_index: int,
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


@pytest.mark.parametrize("length", (179, 181))
def test_plan_requires_exactly_180_intrinsic_latents(length: int) -> None:
    latents = valid_latents()
    invalid_latents = latents[:length] if length < 180 else [*latents, 0.60]

    with pytest.raises(InvalidExperimentalReplicationPlanError, match="180"):
        build_plan(latents=invalid_latents)


@pytest.mark.parametrize("length", (179, 181))
def test_plan_requires_exactly_180_correction_latents(length: int) -> None:
    latents = valid_latents(0.70)
    invalid_latents = latents[:length] if length < 180 else [*latents, 0.70]

    with pytest.raises(InvalidExperimentalReplicationPlanError, match="180"):
        build_plan(correction_latents=invalid_latents)


@pytest.mark.parametrize(
    "invalid_latent",
    (-0.01, 1.0, 1.01, float("nan"), float("inf"), float("-inf")),
)
def test_plan_rejects_non_finite_or_out_of_range_latents(
    invalid_latent: float,
) -> None:
    latents = valid_latents()
    latents[91] = invalid_latent

    with pytest.raises(ValueError):
        build_plan(latents=latents)


@pytest.mark.parametrize("invalid_latent", (False, True))
def test_plan_rejects_boolean_latents(invalid_latent: bool) -> None:
    latents: list[float] = valid_latents()
    latents[91] = invalid_latent

    with pytest.raises(TypeError):
        build_plan(latents=latents)


@pytest.mark.parametrize(
    "invalid_latent",
    (-0.01, 1.0, 1.01, float("nan"), float("inf"), float("-inf")),
)
def test_plan_rejects_invalid_correction_latents(invalid_latent: float) -> None:
    latents = valid_latents(0.70)
    latents[91] = invalid_latent

    with pytest.raises(ValueError, match="u_correction"):
        build_plan(correction_latents=latents)


@pytest.mark.parametrize("invalid_latent", (False, True))
def test_plan_rejects_boolean_correction_latents(invalid_latent: bool) -> None:
    latents: list[float] = valid_latents(0.70)
    latents[91] = invalid_latent

    with pytest.raises(TypeError, match="u_correction"):
        build_plan(correction_latents=latents)


def test_plan_defensively_copies_capability_order_and_latents() -> None:
    order = valid_interleaved_order()
    latents = valid_latents()
    correction_latents = valid_latents(0.70)
    latents[0] = 0.20
    correction_latents[0] = 0.25
    plan = build_plan(
        capability_order=order,
        latents=latents,
        correction_latents=correction_latents,
    )
    order[0] = "GAMMA"
    latents[0] = 0.90
    correction_latents[0] = 0.95

    observation = attempt(plan, sequence_index=0)

    assert plan.capability_key_for_sequence(0) == "ALPHA"
    assert observation.capability_key == "ALPHA"
    assert observation.intrinsic_success is True
    assert vars(plan)["_u_correction_by_sequence"] == (0.25, *valid_latents(0.70)[1:])


@pytest.mark.parametrize("sequence_index", (0, 1, 2, 59, 60, 61, 119, 120, 179))
def test_predecision_capability_matches_the_public_observation(
    sequence_index: int,
) -> None:
    plan = build_plan()

    capability_key = plan.capability_key_for_sequence(sequence_index)
    observation = attempt(plan, sequence_index=sequence_index)

    assert observation.capability_key == capability_key


def test_each_sequence_uses_its_own_private_latent() -> None:
    latents = valid_latents()
    latents[0] = 0.20
    latents[3] = 0.90
    plan = build_plan(latents=latents)

    first_alpha = attempt(plan, sequence_index=0)
    second_alpha = attempt(plan, sequence_index=3)

    assert first_alpha.capability_key == second_alpha.capability_key == "ALPHA"
    assert first_alpha.intrinsic_success is True
    assert second_alpha.intrinsic_success is False


@pytest.mark.parametrize("sequence_index", (0, 1, 2, 60, 61, 62, 120, 121, 122))
def test_independent_plans_pair_capabilities_and_intrinsic_results(
    sequence_index: int,
) -> None:
    order = valid_interleaved_order()
    latents = [index / 180 for index in range(180)]
    first = build_plan(capability_order=order, latents=latents)
    second = build_plan(capability_order=order, latents=latents)

    first_observation = attempt(first, sequence_index=sequence_index, condition="A")
    second_observation = attempt(second, sequence_index=sequence_index, condition="B")

    assert first_observation.agent_id != second_observation.agent_id
    assert first_observation.trial_id != second_observation.trial_id
    assert first_observation.cycle_id != second_observation.cycle_id
    assert first_observation.capability_key == second_observation.capability_key
    assert first_observation.intrinsic_success is second_observation.intrinsic_success


def test_repeated_attempts_have_no_hidden_evolving_state() -> None:
    plan = build_plan()

    first = attempt(plan, sequence_index=61)
    second = attempt(plan, sequence_index=61)

    assert first == second


@pytest.mark.parametrize("sequence_index", (-1, 180))
def test_plan_reuses_the_schedule_index_bounds(sequence_index: int) -> None:
    plan = build_plan()

    with pytest.raises(IndexError):
        plan.capability_key_for_sequence(sequence_index)
    with pytest.raises(IndexError):
        attempt(plan, sequence_index=sequence_index)


@pytest.mark.parametrize("sequence_index", (False, True, 1.0, "1"))
def test_plan_reuses_strict_integer_index_validation(sequence_index: object) -> None:
    plan = build_plan()

    with pytest.raises(TypeError):
        plan.capability_key_for_sequence(sequence_index)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        attempt(plan, sequence_index=sequence_index)  # type: ignore[arg-type]


def test_attempt_accepts_no_capability_or_private_latent() -> None:
    parameters = inspect.signature(ExperimentalReplicationPlan.attempt).parameters

    assert "capability_key" not in parameters
    assert "u_intrinsic" not in parameters
    assert "true_success_probability" not in parameters


def test_plan_exposes_only_current_capability_attempt_and_outcome_resolution() -> None:
    public_members = {
        name for name in ExperimentalReplicationPlan.__dict__ if not name.startswith("_")
    }

    assert public_members == {
        "attempt",
        "capability_key_for_sequence",
        "resolve_outcome",
    }


def test_plan_requires_both_private_latent_sequences_without_defaults() -> None:
    parameters = inspect.signature(ExperimentalReplicationPlan).parameters

    assert tuple(parameters) == (
        "capability_order",
        "u_intrinsic_by_sequence",
        "u_correction_by_sequence",
    )
    assert all(parameter.default is inspect.Parameter.empty for parameter in parameters.values())


def test_attempt_returns_only_the_public_performance_observation() -> None:
    plan = build_plan()

    observation = attempt(plan, sequence_index=61)

    assert type(observation) is CapabilityPerformanceObservation
    assert observation.model_dump() == {
        "id": "performance-A-61",
        "agent_id": "agent-A",
        "trial_id": "trial-A-61",
        "cycle_id": "cycle-A-61",
        "sequence_index": 61,
        "capability_key": "BETA",
        "intrinsic_success": False,
        "observed_at": OBSERVED_AT,
        "source_type": SourceType.DIRECT_ENVIRONMENT,
    }
    assert PRIVATE_EXPERIMENTAL_FIELDS.isdisjoint(CapabilityPerformanceObservation.model_fields)


def test_cognitive_modules_do_not_import_the_private_replication_plan() -> None:
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


def _imported_module_names(node: ast.AST) -> tuple[str, ...]:
    if isinstance(node, ast.Import):
        return tuple(alias.name for alias in node.names)
    if isinstance(node, ast.ImportFrom) and node.module is not None:
        return (node.module,)
    return ()
