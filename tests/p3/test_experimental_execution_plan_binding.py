import sqlite3
from pathlib import Path

import pytest
from pydantic import ValidationError

from soinesis.experiments.p3 import (
    ExperimentalExecutionPlanBinding,
    ExperimentalExecutionPlanBindingIntegrityError,
    ExperimentalExecutionPlanBindingService,
    ExperimentalReplicationPlanIdentity,
    SQLiteExperimentalExecutionPlanBindingRepository,
)
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

PRIVATE_FIELDS = {
    "agent_id",
    "condition",
    "dataset",
    "phase",
    "replication",
    "seed",
    "timestamp",
}


def identity(character: str = "a") -> ExperimentalReplicationPlanIdentity:
    return ExperimentalReplicationPlanIdentity(
        scheme="p3-plan-fingerprint-v1",
        fingerprint=character * 64,
    )


def build_service(
    path: Path,
) -> tuple[
    ExperimentalExecutionPlanBindingService,
    SQLiteExperimentalExecutionPlanBindingRepository,
]:
    repository = SQLiteExperimentalExecutionPlanBindingRepository(SQLiteDatabase(path))
    repository.initialize_schema()
    return ExperimentalExecutionPlanBindingService(repository), repository


def row_count(path: Path) -> int:
    with sqlite3.connect(path) as connection:
        row = connection.execute("SELECT COUNT(*) FROM p3_dev_execution_plan_bindings").fetchone()
    assert row is not None
    return int(row[0])


def test_binding_model_is_frozen_exact_and_has_no_campaign_metadata() -> None:
    binding = ExperimentalExecutionPlanBinding(
        execution_id="execution-1",
        plan_identity=identity(),
    )

    assert set(ExperimentalExecutionPlanBinding.model_fields) == {
        "execution_id",
        "plan_identity",
    }
    assert PRIVATE_FIELDS.isdisjoint(ExperimentalExecutionPlanBinding.model_fields)
    with pytest.raises(ValidationError):
        binding.execution_id = "another"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        ExperimentalExecutionPlanBinding.model_validate({**binding.model_dump(), "seed": 1})


def test_binding_schema_is_opt_in_and_contains_only_explicit_identity_columns(
    tmp_path: Path,
) -> None:
    path = tmp_path / "opt-in.db"
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    with database.connect() as connection:
        absent = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'p3_dev_execution_plan_bindings'
            """
        ).fetchone()
    assert absent is None

    repository = SQLiteExperimentalExecutionPlanBindingRepository(database)
    repository.initialize_schema()
    with database.connect() as connection:
        columns = {
            str(row["name"])
            for row in connection.execute(
                "PRAGMA table_info(p3_dev_execution_plan_bindings)"
            ).fetchall()
        }
    assert columns == {"execution_id", "fingerprint_scheme", "plan_fingerprint"}
    assert PRIVATE_FIELDS.isdisjoint(columns)


def test_bind_is_persistent_and_exact_retry_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "binding.db"
    first_service, _ = build_service(path)
    created = first_service.bind(execution_id="execution-1", plan_identity=identity())

    reopened_service, _ = build_service(path)
    retried = reopened_service.bind(execution_id="execution-1", plan_identity=identity())

    assert retried == created
    assert reopened_service.get(execution_id="execution-1") == created
    assert row_count(path) == 1


def test_same_execution_cannot_be_rebound_to_another_plan(tmp_path: Path) -> None:
    path = tmp_path / "conflict.db"
    service, _ = build_service(path)
    original = service.bind(execution_id="execution-1", plan_identity=identity("a"))

    with pytest.raises(ExperimentalExecutionPlanBindingIntegrityError):
        service.bind(execution_id="execution-1", plan_identity=identity("b"))

    assert service.get(execution_id="execution-1") == original
    assert row_count(path) == 1


def test_binding_rejects_update_and_delete_at_sqlite_level(tmp_path: Path) -> None:
    path = tmp_path / "immutable.db"
    service, _ = build_service(path)
    original = service.bind(execution_id="execution-1", plan_identity=identity())

    with sqlite3.connect(path) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                UPDATE p3_dev_execution_plan_bindings
                SET plan_fingerprint = ? WHERE execution_id = 'execution-1'
                """,
                ("b" * 64,),
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "DELETE FROM p3_dev_execution_plan_bindings WHERE execution_id = 'execution-1'"
            )

    assert service.get(execution_id="execution-1") == original


@pytest.mark.parametrize(
    ("scheme", "fingerprint"),
    (
        ("another-scheme", "a" * 64),
        ("p3-plan-fingerprint-v1", "a" * 63),
        ("p3-plan-fingerprint-v1", "A" * 64),
        ("p3-plan-fingerprint-v1", "g" * 64),
    ),
)
def test_sqlite_rejects_invalid_identity_encoding(
    tmp_path: Path,
    scheme: str,
    fingerprint: str,
) -> None:
    path = tmp_path / f"invalid-{len(fingerprint)}-{fingerprint[0]}.db"
    _, _ = build_service(path)

    with sqlite3.connect(path) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO p3_dev_execution_plan_bindings (
                execution_id, fingerprint_scheme, plan_fingerprint
            ) VALUES ('execution-1', ?, ?)
            """,
            (scheme, fingerprint),
        )
