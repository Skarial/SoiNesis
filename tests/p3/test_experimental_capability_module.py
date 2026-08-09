import ast
from datetime import UTC, datetime
from pathlib import Path

import pytest

from soinesis.domain.capabilities import CapabilityPerformanceObservation
from soinesis.domain.models import SourceType
from soinesis.experiments.p3 import (
    ExperimentalCapabilityModule,
    UnknownExperimentalCapabilityError,
)

OBSERVED_AT = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
PRIVATE_EXPERIMENTAL_FIELDS = {
    "dataset",
    "final_success",
    "official_dataset_id",
    "oracle",
    "phase",
    "replication",
    "seed",
    "true_success_probability",
    "u_intrinsic",
}


def attempt(
    module: ExperimentalCapabilityModule,
    *,
    capability_key: str = "ALPHA",
    u_intrinsic: float,
) -> CapabilityPerformanceObservation:
    return module.attempt(
        performance_id="performance-1",
        agent_id="agent-1",
        trial_id="trial-1",
        cycle_id="cycle-1",
        sequence_index=0,
        capability_key=capability_key,
        observed_at=OBSERVED_AT,
        u_intrinsic=u_intrinsic,
    )


@pytest.mark.parametrize("u_intrinsic", (0.0, 0.5, 0.999999))
def test_zero_probability_always_fails_for_valid_latents(u_intrinsic: float) -> None:
    module = ExperimentalCapabilityModule(true_success_probabilities={"ALPHA": 0.0})

    observation = attempt(module, u_intrinsic=u_intrinsic)

    assert observation.intrinsic_success is False


@pytest.mark.parametrize("u_intrinsic", (0.0, 0.5, 0.999999))
def test_one_probability_always_succeeds_for_valid_latents(u_intrinsic: float) -> None:
    module = ExperimentalCapabilityModule(true_success_probabilities={"ALPHA": 1.0})

    observation = attempt(module, u_intrinsic=u_intrinsic)

    assert observation.intrinsic_success is True


@pytest.mark.parametrize(
    ("u_intrinsic", "expected_success"),
    (
        (0.649999, True),
        (0.65, False),
        (0.90, False),
    ),
)
def test_intrinsic_success_uses_the_exact_probability_boundary(
    u_intrinsic: float,
    expected_success: bool,
) -> None:
    module = ExperimentalCapabilityModule(true_success_probabilities={"ALPHA": 0.65})

    observation = attempt(module, u_intrinsic=u_intrinsic)

    assert observation.intrinsic_success is expected_success


@pytest.mark.parametrize(
    "probability",
    (-0.01, 1.01, float("nan"), float("inf"), float("-inf")),
)
def test_private_probability_must_be_finite_and_bounded(probability: float) -> None:
    with pytest.raises(ValueError):
        ExperimentalCapabilityModule(true_success_probabilities={"ALPHA": probability})


@pytest.mark.parametrize(
    "u_intrinsic",
    (-0.01, 1.0, 1.01, float("nan"), float("inf"), float("-inf")),
)
def test_intrinsic_latent_must_be_finite_and_in_half_open_unit_interval(
    u_intrinsic: float,
) -> None:
    module = ExperimentalCapabilityModule(true_success_probabilities={"ALPHA": 0.65})

    with pytest.raises(ValueError):
        attempt(module, u_intrinsic=u_intrinsic)


def test_unknown_capability_is_explicitly_rejected_without_fallback() -> None:
    module = ExperimentalCapabilityModule(true_success_probabilities={"ALPHA": 0.65})

    with pytest.raises(UnknownExperimentalCapabilityError, match="BETA"):
        attempt(module, capability_key="BETA", u_intrinsic=0.0)


def test_attempt_returns_only_the_public_direct_environment_observation() -> None:
    module = ExperimentalCapabilityModule(true_success_probabilities={"ALPHA": 0.65})

    observation = attempt(module, u_intrinsic=0.2)

    assert type(observation) is CapabilityPerformanceObservation
    assert observation.model_dump() == {
        "id": "performance-1",
        "agent_id": "agent-1",
        "trial_id": "trial-1",
        "cycle_id": "cycle-1",
        "sequence_index": 0,
        "capability_key": "ALPHA",
        "intrinsic_success": True,
        "observed_at": OBSERVED_AT,
        "source_type": SourceType.DIRECT_ENVIRONMENT,
    }
    assert PRIVATE_EXPERIMENTAL_FIELDS.isdisjoint(CapabilityPerformanceObservation.model_fields)


def test_same_latent_and_configuration_are_strictly_deterministic() -> None:
    module = ExperimentalCapabilityModule(true_success_probabilities={"ALPHA": 0.65})

    first = attempt(module, u_intrinsic=0.42)
    second = attempt(module, u_intrinsic=0.42)

    assert first.intrinsic_success is second.intrinsic_success


def test_independent_condition_modules_share_the_same_intrinsic_outcome() -> None:
    first_condition = ExperimentalCapabilityModule(true_success_probabilities={"ALPHA": 0.65})
    second_condition = ExperimentalCapabilityModule(true_success_probabilities={"ALPHA": 0.65})

    first = attempt(first_condition, u_intrinsic=0.42)
    second = attempt(second_condition, u_intrinsic=0.42)

    assert first.intrinsic_success is second.intrinsic_success


def test_private_configuration_is_copied_and_static_for_module_lifetime() -> None:
    configuration = {"ALPHA": 0.65}
    module = ExperimentalCapabilityModule(true_success_probabilities=configuration)
    configuration["ALPHA"] = 0.0

    observation = attempt(module, u_intrinsic=0.42)

    assert observation.intrinsic_success is True


def test_module_exposes_no_public_truth_probability_getter() -> None:
    public_members = {
        name for name in ExperimentalCapabilityModule.__dict__ if not name.startswith("_")
    }

    assert public_members == {"attempt"}


def test_cognitive_modules_do_not_import_the_private_experimental_module() -> None:
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
