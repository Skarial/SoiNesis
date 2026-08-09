import sqlite3
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from pydantic import ValidationError

from soinesis.experiments.p3 import (
    ExperimentalExecutionGenerationProvenance,
    ExperimentalExecutionGenerationProvenanceIntegrityError,
    ExperimentalExecutionGenerationProvenanceService,
    ExperimentalExecutionPlanBindingService,
    ExperimentalPlanGenerationProvenance,
    ExperimentalReplicationPlanGenerator,
    SQLiteExperimentalExecutionGenerationProvenanceRepository,
    SQLiteExperimentalExecutionPlanBindingRepository,
)
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

PRIVATE_FIELDS = {
    "agent_id",
    "condition",
    "dataset",
    "os",
    "phase",
    "replication",
    "timestamp",
    "user",
}


def build_services(
    path: Path,
) -> tuple[
    ExperimentalExecutionPlanBindingService,
    ExperimentalExecutionGenerationProvenanceService,
    SQLiteExperimentalExecutionGenerationProvenanceRepository,
]:
    database = SQLiteDatabase(path)
    binding_repository = SQLiteExperimentalExecutionPlanBindingRepository(database)
    binding_repository.initialize_schema()
    provenance_repository = SQLiteExperimentalExecutionGenerationProvenanceRepository(database)
    provenance_repository.initialize_schema()
    return (
        ExperimentalExecutionPlanBindingService(binding_repository),
        ExperimentalExecutionGenerationProvenanceService(
            repository=provenance_repository,
            binding_repository=binding_repository,
        ),
        provenance_repository,
    )


def test_generation_provenance_models_are_frozen_exact_and_forbid_extras() -> None:
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)
    ExperimentalExecutionGenerationProvenance(
        execution_id="execution-1",
        generation_provenance=generated.provenance,
    )

    assert set(ExperimentalPlanGenerationProvenance.model_fields) == {
        "scheme",
        "plan_identity",
        "seed",
        "generator_version",
        "python_implementation",
        "python_version",
    }
    assert set(ExperimentalExecutionGenerationProvenance.model_fields) == {
        "execution_id",
        "generation_provenance",
    }
    assert PRIVATE_FIELDS.isdisjoint(ExperimentalPlanGenerationProvenance.model_fields)
    assert PRIVATE_FIELDS.isdisjoint(ExperimentalExecutionGenerationProvenance.model_fields)
    with pytest.raises(ValidationError):
        generated.provenance.seed = 7  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        generated.plan = generated.plan  # type: ignore[misc]
    with pytest.raises(ValidationError):
        ExperimentalPlanGenerationProvenance.model_validate(
            {**generated.provenance.model_dump(), "commit_sha": "abc"}
        )


def test_provenance_schema_is_opt_in_and_minimal(tmp_path: Path) -> None:
    path = tmp_path / "opt-in.db"
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    binding_repository = SQLiteExperimentalExecutionPlanBindingRepository(database)
    binding_repository.initialize_schema()
    with database.connect() as connection:
        absent = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'p3_dev_execution_generation_provenance'
            """
        ).fetchone()
    assert absent is None

    provenance_repository = SQLiteExperimentalExecutionGenerationProvenanceRepository(database)
    provenance_repository.initialize_schema()
    with database.connect() as connection:
        columns = {
            str(row["name"])
            for row in connection.execute(
                "PRAGMA table_info(p3_dev_execution_generation_provenance)"
            ).fetchall()
        }
    assert columns == {
        "execution_id",
        "provenance_scheme",
        "fingerprint_scheme",
        "plan_fingerprint",
        "seed_text",
        "generator_version",
        "python_implementation",
        "python_version",
    }
    assert PRIVATE_FIELDS.isdisjoint(columns)


def test_registration_requires_an_existing_matching_3n_binding(tmp_path: Path) -> None:
    path = tmp_path / "binding-required.db"
    binding, provenance, _ = build_services(path)
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)

    with pytest.raises(ExperimentalExecutionGenerationProvenanceIntegrityError, match="3N"):
        provenance.register(
            execution_id="execution-1",
            generation_provenance=generated.provenance,
        )

    other = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=54321)
    binding.bind(execution_id="execution-1", plan_identity=other.plan.identity())
    with pytest.raises(ExperimentalExecutionGenerationProvenanceIntegrityError, match="correspond"):
        provenance.register(
            execution_id="execution-1",
            generation_provenance=generated.provenance,
        )
    assert provenance.get(execution_id="execution-1") is None


def test_registration_is_persistent_idempotent_and_immutable(tmp_path: Path) -> None:
    path = tmp_path / "persistent.db"
    binding, provenance, _ = build_services(path)
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)
    binding.bind(execution_id="execution-1", plan_identity=generated.plan.identity())

    created = provenance.register(
        execution_id="execution-1",
        generation_provenance=generated.provenance,
    )
    retried = provenance.register(
        execution_id="execution-1",
        generation_provenance=generated.provenance,
    )

    assert retried == created
    _, reopened, _ = build_services(path)
    stored = reopened.get(execution_id="execution-1")
    assert stored is not None
    assert stored.generation_provenance.seed == 12345
    with sqlite3.connect(path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM p3_dev_execution_generation_provenance"
        ).fetchone()
        assert count == (1,)
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                UPDATE p3_dev_execution_generation_provenance
                SET seed_text = '7' WHERE execution_id = 'execution-1'
                """
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                DELETE FROM p3_dev_execution_generation_provenance
                WHERE execution_id = 'execution-1'
                """
            )


@pytest.mark.parametrize("seed_text", ("00123", "+123", "-0"))
def test_read_rejects_a_noncanonical_persisted_seed_text(
    tmp_path: Path,
    seed_text: str,
) -> None:
    path = tmp_path / f"corrupt-seed-{seed_text.replace('+', 'plus')}.db"
    _, _, repository = build_services(path)
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=123)
    provenance = generated.provenance
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            INSERT INTO p3_dev_execution_generation_provenance (
                execution_id,
                provenance_scheme,
                fingerprint_scheme,
                plan_fingerprint,
                seed_text,
                generator_version,
                python_implementation,
                python_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "execution-corrupt",
                provenance.scheme,
                provenance.plan_identity.scheme,
                provenance.plan_identity.fingerprint,
                seed_text,
                provenance.generator_version,
                provenance.python_implementation,
                provenance.python_version,
            ),
        )

    with pytest.raises(
        ExperimentalExecutionGenerationProvenanceIntegrityError,
        match="canonique",
    ):
        repository.get(execution_id="execution-corrupt")


def test_same_execution_rejects_a_different_provenance(tmp_path: Path) -> None:
    path = tmp_path / "conflict.db"
    binding, provenance, _ = build_services(path)
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)
    binding.bind(execution_id="execution-1", plan_identity=generated.plan.identity())
    provenance.register(
        execution_id="execution-1",
        generation_provenance=generated.provenance,
    )
    conflicting = generated.provenance.model_copy(update={"seed": 12346})

    with pytest.raises(ExperimentalExecutionGenerationProvenanceIntegrityError):
        provenance.register(
            execution_id="execution-1",
            generation_provenance=conflicting,
        )

    stored = provenance.get(execution_id="execution-1")
    assert stored is not None
    assert stored.generation_provenance == generated.provenance


def test_arbitrarily_large_seed_round_trips_and_reproduces_after_reopen(tmp_path: Path) -> None:
    path = tmp_path / "large-seed.db"
    seed = 2**137 + 987654321
    generator = ExperimentalReplicationPlanGenerator()
    generated = generator.generate_with_provenance(seed=seed)
    binding, provenance, _ = build_services(path)
    binding.bind(execution_id="execution-large", plan_identity=generated.plan.identity())
    provenance.register(
        execution_id="execution-large",
        generation_provenance=generated.provenance,
    )

    _, reopened, _ = build_services(path)
    stored = reopened.get(execution_id="execution-large")

    assert stored is not None
    assert stored.generation_provenance.seed == seed
    reproduced = generator.reproduce(provenance=stored.generation_provenance)
    assert reproduced.identity() == generated.plan.identity()
