import ast
import inspect
from collections import Counter
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from random import Random
from typing import cast

import pytest

from soinesis.domain.capabilities import (
    CapabilityDecision,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    MetacognitiveCapabilityState,
)
from soinesis.domain.models import JournalEvent
from soinesis.experiments.p3 import (
    ExperimentalCapabilitySchedule,
    ExperimentalReplicationPlan,
    ExperimentalReplicationPlanGenerator,
)
from soinesis.experiments.p3 import generation as generation_module

OBSERVED_AT = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
PRIVATE_EXPERIMENTAL_FIELDS = {
    "dataset",
    "final_success",
    "official_dataset_id",
    "oracle",
    "phase",
    "replication",
    "seed",
    "segment",
    "true_success_probability",
    "u_correction",
    "u_intrinsic",
}


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


def behavioral_signature(
    plan: ExperimentalReplicationPlan,
) -> tuple[tuple[str, bool], ...]:
    return tuple(
        (
            plan.capability_key_for_sequence(sequence_index),
            attempt(plan, sequence_index=sequence_index).intrinsic_success,
        )
        for sequence_index in range(180)
    )


def private_capability_order(plan: ExperimentalReplicationPlan) -> tuple[str, ...]:
    schedule = cast(ExperimentalCapabilitySchedule, vars(plan)["_schedule"])
    return cast(tuple[str, ...], vars(schedule)["_capability_order"])


def private_intrinsic_latents(plan: ExperimentalReplicationPlan) -> tuple[float, ...]:
    return cast(tuple[float, ...], vars(plan)["_u_intrinsic_by_sequence"])


def private_correction_latents(plan: ExperimentalReplicationPlan) -> tuple[float, ...]:
    return cast(tuple[float, ...], vars(plan)["_u_correction_by_sequence"])


@pytest.mark.parametrize("invalid_seed", (False, True, 1.0, "1", None))
def test_generator_requires_a_strict_integer_seed(invalid_seed: object) -> None:
    generator = ExperimentalReplicationPlanGenerator()

    with pytest.raises(TypeError):
        generator.generate(seed=invalid_seed)  # type: ignore[arg-type]


def test_same_instance_and_seed_generate_identical_behavior_on_all_cycles() -> None:
    generator = ExperimentalReplicationPlanGenerator()

    first = generator.generate(seed=12345)
    second = generator.generate(seed=12345)

    assert behavioral_signature(first) == behavioral_signature(second)


def test_distinct_generator_instances_and_same_seed_generate_identical_plans() -> None:
    first = ExperimentalReplicationPlanGenerator().generate(seed=12345)
    second = ExperimentalReplicationPlanGenerator().generate(seed=12345)

    assert private_capability_order(first) == private_capability_order(second)
    assert private_intrinsic_latents(first) == private_intrinsic_latents(second)
    assert private_correction_latents(first) == private_correction_latents(second)


def test_call_order_does_not_change_a_repeated_seed() -> None:
    generator = ExperimentalReplicationPlanGenerator()

    first_seed_one = generator.generate(seed=1)
    generator.generate(seed=2)
    second_seed_one = generator.generate(seed=1)

    assert private_capability_order(first_seed_one) == private_capability_order(second_seed_one)
    assert private_intrinsic_latents(first_seed_one) == private_intrinsic_latents(second_seed_one)
    assert private_correction_latents(first_seed_one) == private_correction_latents(second_seed_one)


def test_fixed_distinct_seeds_generate_different_raw_plans() -> None:
    generator = ExperimentalReplicationPlanGenerator()

    first = generator.generate(seed=12345)
    second = generator.generate(seed=67890)

    assert (
        private_capability_order(first) != private_capability_order(second)
        or private_intrinsic_latents(first) != private_intrinsic_latents(second)
        or private_correction_latents(first) != private_correction_latents(second)
    )


def test_latent_substreams_are_derived_independently_from_other_consumption() -> None:
    private_module_members = vars(generation_module)
    derive_substream_seed = cast(
        Callable[[int, str], int],
        private_module_members["_derive_substream_seed"],
    )
    intrinsic_tag = cast(str, private_module_members["_INTRINSIC_SUBSTREAM"])
    correction_tag = cast(str, private_module_members["_CORRECTION_SUBSTREAM"])
    order_tag = cast(str, private_module_members["_CAPABILITY_ORDER_SUBSTREAM"])
    root_seed = 12345
    order_rng = Random(derive_substream_seed(root_seed, order_tag))
    for _ in range(10_000):
        order_rng.random()
    expected_intrinsic_rng = Random(derive_substream_seed(root_seed, intrinsic_tag))
    expected_latents = tuple(expected_intrinsic_rng.random() for _ in range(180))
    intrinsic_rng = Random(derive_substream_seed(root_seed, intrinsic_tag))
    for _ in range(10_000):
        intrinsic_rng.random()
    expected_correction_rng = Random(derive_substream_seed(root_seed, correction_tag))
    expected_correction_latents = tuple(expected_correction_rng.random() for _ in range(180))

    plan = ExperimentalReplicationPlanGenerator().generate(seed=root_seed)

    assert private_intrinsic_latents(plan) == expected_latents
    assert private_correction_latents(plan) == expected_correction_latents


def test_generator_version_and_three_private_substreams_are_explicit() -> None:
    private_module_members = vars(generation_module)

    assert private_module_members["_P3_DEV_GENERATOR_VERSION"] == "p3-dev-plan-v2"
    assert private_module_members["_CAPABILITY_ORDER_SUBSTREAM"] == "capability-order"
    assert private_module_members["_INTRINSIC_SUBSTREAM"] == "u-intrinsic"
    assert private_module_members["_CORRECTION_SUBSTREAM"] == "u-correction"


def test_generator_creates_exactly_180_values_for_each_latent_stream() -> None:
    plan = ExperimentalReplicationPlanGenerator().generate(seed=12345)

    assert len(private_capability_order(plan)) == 180
    assert len(private_intrinsic_latents(plan)) == 180
    assert len(private_correction_latents(plan)) == 180


@pytest.mark.parametrize("seed", (0, 1, 12345, -987654321))
def test_each_generated_segment_is_structurally_balanced(seed: int) -> None:
    plan = ExperimentalReplicationPlanGenerator().generate(seed=seed)

    for segment_start in (0, 60, 120):
        segment = tuple(
            plan.capability_key_for_sequence(index)
            for index in range(segment_start, segment_start + 60)
        )
        assert Counter(segment) == {"ALPHA": 20, "BETA": 20, "GAMMA": 20}


def test_generated_plan_attempt_uses_the_generated_capability_and_latent() -> None:
    plan = ExperimentalReplicationPlanGenerator().generate(seed=12345)

    for sequence_index in (0, 1, 2, 59, 60, 61, 119, 120, 179):
        observation = attempt(plan, sequence_index=sequence_index)
        assert observation.capability_key == plan.capability_key_for_sequence(sequence_index)
        assert type(observation) is CapabilityPerformanceObservation


def test_generator_has_no_evolving_instance_state_and_only_exposes_generate() -> None:
    generator = ExperimentalReplicationPlanGenerator()
    public_members = {
        name for name in ExperimentalReplicationPlanGenerator.__dict__ if not name.startswith("_")
    }

    assert vars(generator) == {}
    assert public_members == {"generate"}
    assert tuple(inspect.signature(generator.generate).parameters) == ("seed",)


def test_seed_and_private_plan_data_do_not_enter_cognitive_models() -> None:
    cognitive_models = (
        CapabilityPerformanceObservation,
        CapabilityDecision,
        CapabilitySelfAttribute,
        MetacognitiveCapabilityState,
        JournalEvent,
    )

    for cognitive_model in cognitive_models:
        assert PRIVATE_EXPERIMENTAL_FIELDS.isdisjoint(cognitive_model.model_fields)


def test_cognitive_modules_do_not_import_the_private_generator_or_plan() -> None:
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
