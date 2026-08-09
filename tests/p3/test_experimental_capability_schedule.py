import ast
import inspect
from datetime import UTC, datetime
from pathlib import Path

import pytest

from soinesis.domain.capabilities import CapabilityPerformanceObservation
from soinesis.domain.models import SourceType
from soinesis.experiments.p3 import (
    ExperimentalCapabilitySchedule,
    InvalidExperimentalCapabilityScheduleError,
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
    "segment",
    "true_success_probability",
    "u_intrinsic",
}


def valid_interleaved_order() -> list[str]:
    return [capability for _ in range(60) for capability in ("ALPHA", "BETA", "GAMMA")]


def attempt(
    schedule: ExperimentalCapabilitySchedule,
    *,
    sequence_index: int,
    u_intrinsic: float = 0.60,
) -> CapabilityPerformanceObservation:
    return schedule.attempt(
        performance_id=f"performance-{sequence_index}",
        agent_id="agent-1",
        trial_id=f"trial-{sequence_index}",
        cycle_id=f"cycle-{sequence_index}",
        sequence_index=sequence_index,
        observed_at=OBSERVED_AT,
        u_intrinsic=u_intrinsic,
    )


@pytest.mark.parametrize("length", (179, 181))
def test_schedule_requires_exactly_180_positions(length: int) -> None:
    order = valid_interleaved_order()
    invalid_order = order[:length] if length < 180 else [*order, "ALPHA"]

    with pytest.raises(InvalidExperimentalCapabilityScheduleError, match="180"):
        ExperimentalCapabilitySchedule(capability_order=invalid_order)


def test_schedule_rejects_an_unknown_capability() -> None:
    order = valid_interleaved_order()
    order[0] = "DELTA"

    with pytest.raises(InvalidExperimentalCapabilityScheduleError, match="inconnue"):
        ExperimentalCapabilitySchedule(capability_order=order)


def test_schedule_rejects_invalid_counts_in_any_segment() -> None:
    order = valid_interleaved_order()
    beta_index = order.index("BETA", 60, 120)
    order[beta_index] = "ALPHA"

    with pytest.raises(InvalidExperimentalCapabilityScheduleError, match="20 ALPHA"):
        ExperimentalCapabilitySchedule(capability_order=order)


def test_schedule_copies_the_supplied_order() -> None:
    order = valid_interleaved_order()
    schedule = ExperimentalCapabilitySchedule(capability_order=order)
    order[0] = "GAMMA"

    assert schedule.capability_key_for_sequence(0) == "ALPHA"


@pytest.mark.parametrize("sequence_index", (-1, 180))
def test_schedule_rejects_out_of_range_sequence_indices(sequence_index: int) -> None:
    schedule = ExperimentalCapabilitySchedule(capability_order=valid_interleaved_order())

    with pytest.raises(IndexError):
        schedule.capability_key_for_sequence(sequence_index)
    with pytest.raises(IndexError):
        attempt(schedule, sequence_index=sequence_index)


@pytest.mark.parametrize("sequence_index", (False, True, 1.0, "1"))
def test_schedule_rejects_non_strict_integer_sequence_indices(
    sequence_index: object,
) -> None:
    schedule = ExperimentalCapabilitySchedule(capability_order=valid_interleaved_order())

    with pytest.raises(TypeError):
        schedule.capability_key_for_sequence(sequence_index)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        attempt(schedule, sequence_index=sequence_index)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("sequence_index", "expected_success"),
    (
        (0, True),
        (60, True),
        (120, True),
        (1, True),
        (61, False),
        (121, False),
        (2, False),
        (62, True),
        (122, True),
    ),
)
def test_private_temporal_capabilities_apply_the_dev_schedule(
    sequence_index: int,
    expected_success: bool,
) -> None:
    schedule = ExperimentalCapabilitySchedule(capability_order=valid_interleaved_order())

    observation = attempt(schedule, sequence_index=sequence_index)

    assert observation.intrinsic_success is expected_success


@pytest.mark.parametrize("sequence_index", (0, 1, 2, 59, 60, 61, 119, 120, 179))
def test_predecision_capability_always_matches_the_attempt_observation(
    sequence_index: int,
) -> None:
    schedule = ExperimentalCapabilitySchedule(capability_order=valid_interleaved_order())

    expected_capability = schedule.capability_key_for_sequence(sequence_index)
    observation = attempt(schedule, sequence_index=sequence_index)

    assert observation.capability_key == expected_capability


def test_attempt_does_not_accept_a_caller_supplied_capability_key() -> None:
    parameters = inspect.signature(ExperimentalCapabilitySchedule.attempt).parameters

    assert "capability_key" not in parameters


@pytest.mark.parametrize("sequence_index", (0, 1, 2, 60, 61, 62, 120, 121, 122))
def test_independent_schedules_with_common_inputs_produce_the_same_outcome(
    sequence_index: int,
) -> None:
    order = valid_interleaved_order()
    first = ExperimentalCapabilitySchedule(capability_order=order)
    second = ExperimentalCapabilitySchedule(capability_order=order)

    first_observation = attempt(first, sequence_index=sequence_index, u_intrinsic=0.60)
    second_observation = attempt(second, sequence_index=sequence_index, u_intrinsic=0.60)

    assert first_observation.intrinsic_success is second_observation.intrinsic_success


def test_schedule_exposes_only_the_current_capability_and_attempt() -> None:
    public_members = {
        name for name in ExperimentalCapabilitySchedule.__dict__ if not name.startswith("_")
    }

    assert public_members == {"attempt", "capability_key_for_sequence"}


def test_attempt_returns_only_the_public_performance_observation() -> None:
    schedule = ExperimentalCapabilitySchedule(capability_order=valid_interleaved_order())

    observation = attempt(schedule, sequence_index=61)

    assert type(observation) is CapabilityPerformanceObservation
    assert observation.model_dump() == {
        "id": "performance-61",
        "agent_id": "agent-1",
        "trial_id": "trial-61",
        "cycle_id": "cycle-61",
        "sequence_index": 61,
        "capability_key": "BETA",
        "intrinsic_success": False,
        "observed_at": OBSERVED_AT,
        "source_type": SourceType.DIRECT_ENVIRONMENT,
    }
    assert PRIVATE_EXPERIMENTAL_FIELDS.isdisjoint(CapabilityPerformanceObservation.model_fields)


def test_cognitive_modules_do_not_import_the_private_schedule() -> None:
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
