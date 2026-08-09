import inspect
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from soinesis.experiments.p3 import (
    ExperimentalCondition,
    ExperimentalConditionConfiguration,
    ExperimentalConditionConfigurationIntegrityError,
    ExperimentalCycleStartContext,
    ExperimentalExecutionConditionConfiguration,
    ExperimentalExecutionConditionConfigurationService,
    ExperimentalExecutionGenerationProvenance,
    ExperimentalExecutionGenerationProvenanceService,
    ExperimentalExecutionPlanBinding,
    ExperimentalExecutionPlanBindingService,
    ExperimentalReplicationCycleContext,
    ExperimentalReplicationExecutionManifest,
    ExperimentalReplicationManifestService,
    ExperimentalReplicationPlanGenerator,
    SQLiteExperimentalExecutionConditionConfigurationRepository,
    SQLiteExperimentalExecutionGenerationProvenanceRepository,
    SQLiteExperimentalExecutionPlanBindingRepository,
    SQLiteExperimentalReplicationManifestRepository,
)
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

SCHEME = "p3-condition-config-v1"
GRID = ("0.90", "0.92", "0.94", "0.95", "0.96", "0.97")
PRIVATE_FIELDS = {
    "agent_id",
    "alpha",
    "baseline",
    "beta",
    "dataset",
    "metrics",
    "phase",
    "plan",
    "seed",
    "self_model",
    "timestamp",
    "true_success_probability",
}


@dataclass(frozen=True)
class Harness:
    path: Path
    binding_repository: SQLiteExperimentalExecutionPlanBindingRepository
    provenance_repository: SQLiteExperimentalExecutionGenerationProvenanceRepository
    manifest_repository: SQLiteExperimentalReplicationManifestRepository
    configuration_repository: SQLiteExperimentalExecutionConditionConfigurationRepository
    binding_service: ExperimentalExecutionPlanBindingService
    provenance_service: ExperimentalExecutionGenerationProvenanceService
    manifest_service: ExperimentalReplicationManifestService
    configuration_service: ExperimentalExecutionConditionConfigurationService


def build_harness(path: Path) -> Harness:
    database = SQLiteDatabase(path)
    binding_repository = SQLiteExperimentalExecutionPlanBindingRepository(database)
    provenance_repository = SQLiteExperimentalExecutionGenerationProvenanceRepository(database)
    manifest_repository = SQLiteExperimentalReplicationManifestRepository(database)
    configuration_repository = SQLiteExperimentalExecutionConditionConfigurationRepository(database)
    binding_repository.initialize_schema()
    provenance_repository.initialize_schema()
    manifest_repository.initialize_schema()
    configuration_repository.initialize_schema()
    return Harness(
        path=path,
        binding_repository=binding_repository,
        provenance_repository=provenance_repository,
        manifest_repository=manifest_repository,
        configuration_repository=configuration_repository,
        binding_service=ExperimentalExecutionPlanBindingService(binding_repository),
        provenance_service=ExperimentalExecutionGenerationProvenanceService(
            repository=provenance_repository,
            binding_repository=binding_repository,
        ),
        manifest_service=ExperimentalReplicationManifestService(
            repository=manifest_repository,
            binding_repository=binding_repository,
            provenance_repository=provenance_repository,
        ),
        configuration_service=ExperimentalExecutionConditionConfigurationService(
            repository=configuration_repository,
            binding_repository=binding_repository,
            provenance_repository=provenance_repository,
            manifest_repository=manifest_repository,
        ),
    )


def build_manifest(execution_id: str = "execution-1") -> ExperimentalReplicationExecutionManifest:
    observed_at = datetime(2026, 8, 9, tzinfo=UTC)
    return ExperimentalReplicationExecutionManifest(
        execution_id=execution_id,
        cycle_contexts=tuple(
            ExperimentalReplicationCycleContext(
                sequence_index=index,
                start_context=ExperimentalCycleStartContext(
                    performance_id=f"performance-{index}",
                    agent_id="agent-1",
                    trial_id=f"trial-{index}",
                    cycle_id=f"cycle-{index}",
                    observed_at=observed_at + timedelta(seconds=index),
                ),
            )
            for index in range(180)
        ),
    )


def prepare_prerequisites(harness: Harness, *, execution_id: str = "execution-1") -> None:
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)
    harness.binding_service.bind(
        execution_id=execution_id,
        plan_identity=generated.plan.identity(),
    )
    harness.provenance_service.register(
        execution_id=execution_id,
        generation_provenance=generated.provenance,
    )
    harness.manifest_service.register(manifest=build_manifest(execution_id))


def configuration(
    condition: ExperimentalCondition = ExperimentalCondition.B,
    estimator_lambda: str | None = "0.94",
) -> ExperimentalConditionConfiguration:
    return ExperimentalConditionConfiguration(
        scheme=SCHEME,
        condition=condition,
        estimator_lambda=None if estimator_lambda is None else Decimal(estimator_lambda),
    )


def test_models_are_frozen_exact_and_conditions_are_only_a_b_c() -> None:
    candidate = configuration()
    binding = ExperimentalExecutionConditionConfiguration(
        execution_id="execution-1",
        configuration=candidate,
    )

    assert tuple(ExperimentalCondition) == (
        ExperimentalCondition.A,
        ExperimentalCondition.B,
        ExperimentalCondition.C,
    )
    assert set(ExperimentalConditionConfiguration.model_fields) == {
        "scheme",
        "condition",
        "estimator_lambda",
    }
    assert set(ExperimentalExecutionConditionConfiguration.model_fields) == {
        "execution_id",
        "configuration",
    }
    assert PRIVATE_FIELDS.isdisjoint(ExperimentalConditionConfiguration.model_fields)
    with pytest.raises(ValidationError):
        candidate.condition = ExperimentalCondition.C  # type: ignore[misc]
    with pytest.raises(ValidationError):
        ExperimentalConditionConfiguration.model_validate({**candidate.model_dump(), "seed": 1})
    with pytest.raises(ValidationError):
        binding.execution_id = "changed"  # type: ignore[misc]


def test_a_requires_no_lambda_and_b_c_require_one() -> None:
    assert configuration(ExperimentalCondition.A, None).estimator_lambda is None
    for condition in (ExperimentalCondition.B, ExperimentalCondition.C):
        with pytest.raises(ValidationError, match="exigent"):
            configuration(condition, None)
    with pytest.raises(ValidationError, match="aucun"):
        configuration(ExperimentalCondition.A, "0.94")


@pytest.mark.parametrize("condition", (ExperimentalCondition.B, ExperimentalCondition.C))
@pytest.mark.parametrize("value", GRID)
def test_b_and_c_accept_every_exact_dev_lambda(
    condition: ExperimentalCondition, value: str
) -> None:
    assert configuration(condition, value).estimator_lambda == Decimal(value)


@pytest.mark.parametrize(
    "value",
    ("0.0", "0.5", "0.91", "0.93", "0.99", "1.0", "NaN", "Infinity", "-Infinity"),
)
def test_lambda_outside_the_exact_dev_grid_is_rejected(value: str) -> None:
    with pytest.raises(ValidationError):
        configuration(ExperimentalCondition.B, value)


def test_schema_is_opt_in_minimal_and_stores_lambda_as_text(tmp_path: Path) -> None:
    path = tmp_path / "opt-in.db"
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    with database.connect() as connection:
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name='p3_dev_execution_condition_configuration'"
            ).fetchone()
            is None
        )

    repository = SQLiteExperimentalExecutionConditionConfigurationRepository(database)
    repository.initialize_schema()
    with database.connect() as connection:
        columns = {
            str(row["name"]): str(row["type"])
            for row in connection.execute(
                "PRAGMA table_info(p3_dev_execution_condition_configuration)"
            ).fetchall()
        }
    assert columns == {
        "execution_id": "TEXT",
        "config_scheme": "TEXT",
        "condition": "TEXT",
        "estimator_lambda": "TEXT",
    }
    assert PRIVATE_FIELDS.isdisjoint(columns)


def test_register_requires_binding_provenance_and_manifest_without_creating_them(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "prerequisites.db")
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)

    with pytest.raises(ExperimentalConditionConfigurationIntegrityError, match="3N"):
        harness.configuration_service.register(
            execution_id="execution-1", configuration=configuration()
        )
    harness.binding_service.bind(
        execution_id="execution-1", plan_identity=generated.plan.identity()
    )
    with pytest.raises(ExperimentalConditionConfigurationIntegrityError, match="3O"):
        harness.configuration_service.register(
            execution_id="execution-1", configuration=configuration()
        )
    harness.provenance_service.register(
        execution_id="execution-1", generation_provenance=generated.provenance
    )
    with pytest.raises(ExperimentalConditionConfigurationIntegrityError, match="3P"):
        harness.configuration_service.register(
            execution_id="execution-1", configuration=configuration()
        )

    assert harness.configuration_service.get(execution_id="execution-1") is None
    assert harness.manifest_repository.get(execution_id="execution-1") is None


def test_register_rejects_incoherent_binding_and_provenance(tmp_path: Path) -> None:
    harness = build_harness(tmp_path / "incoherent.db")
    first = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=1)
    second = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=2)
    # Les dépôts bas niveau permettent de synthétiser une corruption croisée pour auditer 3R.
    harness.binding_repository.bind(
        ExperimentalExecutionPlanBinding(
            execution_id="execution-1", plan_identity=first.plan.identity()
        )
    )
    harness.provenance_repository.register(
        ExperimentalExecutionGenerationProvenance(
            execution_id="execution-1",
            generation_provenance=second.provenance,
        )
    )
    harness.manifest_repository.register(build_manifest())

    with pytest.raises(ExperimentalConditionConfigurationIntegrityError, match="incohérents"):
        harness.configuration_service.register(
            execution_id="execution-1", configuration=configuration()
        )


def test_exact_retry_is_idempotent_after_reopen(tmp_path: Path) -> None:
    path = tmp_path / "idempotent.db"
    first = build_harness(path)
    prepare_prerequisites(first)
    created = first.configuration_service.register(
        execution_id="execution-1", configuration=configuration()
    )

    reopened = build_harness(path)
    retried = reopened.configuration_service.register(
        execution_id="execution-1", configuration=configuration()
    )

    assert retried == created
    assert reopened.configuration_service.get(execution_id="execution-1") == created
    with sqlite3.connect(path) as connection:
        assert connection.execute(
            "SELECT condition, estimator_lambda FROM "
            "p3_dev_execution_condition_configuration WHERE execution_id='execution-1'"
        ).fetchone() == ("B", "0.94")


def test_restart_with_another_lambda_is_refused_and_preserves_history(tmp_path: Path) -> None:
    path = tmp_path / "lambda-conflict.db"
    first = build_harness(path)
    prepare_prerequisites(first)
    original = first.configuration_service.register(
        execution_id="execution-1", configuration=configuration(estimator_lambda="0.94")
    )

    reopened = build_harness(path)
    with pytest.raises(ExperimentalConditionConfigurationIntegrityError, match="autre"):
        reopened.configuration_service.register(
            execution_id="execution-1", configuration=configuration(estimator_lambda="0.97")
        )

    assert reopened.configuration_service.get(execution_id="execution-1") == original


def test_existing_execution_cannot_change_condition(tmp_path: Path) -> None:
    path = tmp_path / "condition-conflict.db"
    harness = build_harness(path)
    prepare_prerequisites(harness)
    original = harness.configuration_service.register(
        execution_id="execution-1", configuration=configuration(ExperimentalCondition.B)
    )

    with pytest.raises(ExperimentalConditionConfigurationIntegrityError, match="autre"):
        harness.configuration_service.register(
            execution_id="execution-1",
            configuration=configuration(ExperimentalCondition.C),
        )

    assert harness.configuration_service.get(execution_id="execution-1") == original


def test_sqlite_rejects_update_delete_and_noncanonical_lambda(tmp_path: Path) -> None:
    path = tmp_path / "immutable.db"
    harness = build_harness(path)
    prepare_prerequisites(harness)
    harness.configuration_service.register(
        execution_id="execution-1", configuration=configuration()
    )

    with sqlite3.connect(path) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "UPDATE p3_dev_execution_condition_configuration "
                "SET estimator_lambda='0.97' WHERE execution_id='execution-1'"
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "DELETE FROM p3_dev_execution_condition_configuration "
                "WHERE execution_id='execution-1'"
            )
        for noncanonical in ("0.940", ".94", " 0.94"):
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO p3_dev_execution_condition_configuration VALUES (?, ?, 'B', ?)",
                    (f"execution-{noncanonical}", SCHEME, noncanonical),
                )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO p3_dev_execution_condition_configuration VALUES (?, ?, 'B', NULL)",
                ("execution-null", SCHEME),
            )


def test_3r_has_no_cognitive_or_execution_dependencies() -> None:
    import soinesis.experiments.p3.condition_config as module

    source = inspect.getsource(module)
    assert "DecayedBetaEstimator" not in source
    assert "DecisionService" not in source
    assert "SelfModel" not in source
    assert "MetaState" not in source
    assert "JournalEvent" not in source
    assert "runner" not in source.lower()
    assert "SELF-ABL" not in source
    assert "META-ABL" not in source
    assert "OFFICIAL" not in source
