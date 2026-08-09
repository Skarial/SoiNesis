import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from soinesis.experiments.p3 import (
    ExperimentalCycleStartContext,
    ExperimentalExecutionGenerationProvenance,
    ExperimentalExecutionGenerationProvenanceService,
    ExperimentalExecutionPlanBindingService,
    ExperimentalReplicationCycleContext,
    ExperimentalReplicationExecutionManifest,
    ExperimentalReplicationManifestIntegrityError,
    ExperimentalReplicationManifestService,
    ExperimentalReplicationPlanGenerator,
    SQLiteExperimentalExecutionGenerationProvenanceRepository,
    SQLiteExperimentalExecutionPlanBindingRepository,
    SQLiteExperimentalReplicationManifestRepository,
)
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

OBSERVED_AT = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
PRIVATE_FIELDS = {
    "capability_key",
    "condition",
    "decision",
    "final_success",
    "intrinsic_success",
    "phase",
    "seed",
    "self_model",
    "true_success_probability",
    "u_correction",
    "u_intrinsic",
}


def build_manifest(
    *,
    execution_id: str = "execution-1",
    changed_index: int | None = None,
    changed_performance_id: str | None = None,
    changed_observed_at: datetime | None = None,
) -> ExperimentalReplicationExecutionManifest:
    contexts: list[ExperimentalReplicationCycleContext] = []
    for sequence_index in range(180):
        performance_id = f"performance-{sequence_index}"
        observed_at = OBSERVED_AT + timedelta(minutes=sequence_index)
        if sequence_index == changed_index:
            performance_id = changed_performance_id or performance_id
            observed_at = changed_observed_at or observed_at
        contexts.append(
            ExperimentalReplicationCycleContext(
                sequence_index=sequence_index,
                start_context=ExperimentalCycleStartContext(
                    performance_id=performance_id,
                    agent_id="agent-1",
                    trial_id=f"trial-{sequence_index}",
                    cycle_id=f"cycle-{sequence_index}",
                    observed_at=observed_at,
                ),
            )
        )
    return ExperimentalReplicationExecutionManifest(
        execution_id=execution_id,
        cycle_contexts=tuple(contexts),
    )


@dataclass(frozen=True)
class ManifestHarness:
    path: Path
    database: SQLiteDatabase
    binding_repository: SQLiteExperimentalExecutionPlanBindingRepository
    provenance_repository: SQLiteExperimentalExecutionGenerationProvenanceRepository
    manifest_repository: SQLiteExperimentalReplicationManifestRepository
    binding_service: ExperimentalExecutionPlanBindingService
    provenance_service: ExperimentalExecutionGenerationProvenanceService
    manifest_service: ExperimentalReplicationManifestService


def build_harness(path: Path) -> ManifestHarness:
    database = SQLiteDatabase(path)
    binding_repository = SQLiteExperimentalExecutionPlanBindingRepository(database)
    binding_repository.initialize_schema()
    provenance_repository = SQLiteExperimentalExecutionGenerationProvenanceRepository(database)
    provenance_repository.initialize_schema()
    manifest_repository = SQLiteExperimentalReplicationManifestRepository(database)
    manifest_repository.initialize_schema()
    return ManifestHarness(
        path=path,
        database=database,
        binding_repository=binding_repository,
        provenance_repository=provenance_repository,
        manifest_repository=manifest_repository,
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
    )


def prepare_3n_and_3o(harness: ManifestHarness, *, execution_id: str = "execution-1") -> None:
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)
    harness.binding_service.bind(
        execution_id=execution_id,
        plan_identity=generated.plan.identity(),
    )
    harness.provenance_service.register(
        execution_id=execution_id,
        generation_provenance=generated.provenance,
    )


def manifest_row_count(path: Path, *, execution_id: str = "execution-1") -> int:
    with sqlite3.connect(path) as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) FROM p3_dev_replication_cycle_manifest
            WHERE execution_id = ?
            """,
            (execution_id,),
        ).fetchone()
    assert row is not None
    return int(row[0])


def test_manifest_models_are_frozen_exact_public_and_copy_contexts_to_a_tuple() -> None:
    manifest = build_manifest()
    first_context = manifest.cycle_contexts[0]

    assert set(ExperimentalReplicationCycleContext.model_fields) == {
        "sequence_index",
        "start_context",
    }
    assert set(ExperimentalReplicationExecutionManifest.model_fields) == {
        "execution_id",
        "cycle_contexts",
    }
    assert PRIVATE_FIELDS.isdisjoint(ExperimentalReplicationCycleContext.model_fields)
    assert PRIVATE_FIELDS.isdisjoint(ExperimentalReplicationExecutionManifest.model_fields)
    assert isinstance(manifest.cycle_contexts, tuple)
    assert tuple(context.sequence_index for context in manifest.cycle_contexts) == tuple(range(180))
    with pytest.raises(ValidationError):
        first_context.sequence_index = 1  # type: ignore[misc]
    with pytest.raises(ValidationError):
        manifest.execution_id = "another"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        ExperimentalReplicationCycleContext.model_validate(
            {**first_context.model_dump(), "capability_key": "ALPHA"}
        )
    with pytest.raises(ValidationError):
        ExperimentalReplicationCycleContext(
            sequence_index=True,  # type: ignore[arg-type]
            start_context=first_context.start_context,
        )
    with pytest.raises(ValidationError):
        ExperimentalReplicationExecutionManifest.model_validate(
            {**manifest.model_dump(), "seed": 7}
        )


@pytest.mark.parametrize("length", (179, 181))
def test_manifest_requires_exactly_180_contexts(length: int) -> None:
    contexts = list(build_manifest().cycle_contexts)
    if length == 179:
        contexts.pop()
    else:
        contexts.append(contexts[-1].model_copy(update={"sequence_index": 179}))

    with pytest.raises(ValidationError):
        ExperimentalReplicationExecutionManifest(
            execution_id="execution-1",
            cycle_contexts=tuple(contexts),
        )


def test_manifest_requires_ordered_indices_and_unique_performance_ids() -> None:
    contexts = list(build_manifest().cycle_contexts)
    contexts[72], contexts[73] = contexts[73], contexts[72]
    with pytest.raises(ValidationError, match="indices"):
        ExperimentalReplicationExecutionManifest(
            execution_id="execution-1",
            cycle_contexts=tuple(contexts),
        )

    contexts = list(build_manifest().cycle_contexts)
    duplicate = contexts[73].start_context.model_copy(
        update={"performance_id": contexts[72].start_context.performance_id}
    )
    contexts[73] = contexts[73].model_copy(update={"start_context": duplicate})
    with pytest.raises(ValidationError, match="performance_id"):
        ExperimentalReplicationExecutionManifest(
            execution_id="execution-1",
            cycle_contexts=tuple(contexts),
        )


def test_manifest_does_not_invent_cycle_id_uniqueness_or_timestamp_ordering() -> None:
    contexts = list(build_manifest().cycle_contexts)
    for index, context in enumerate(contexts):
        contexts[index] = context.model_copy(
            update={
                "start_context": context.start_context.model_copy(
                    update={
                        "cycle_id": "shared-public-cycle-reference",
                        "observed_at": OBSERVED_AT - timedelta(minutes=index),
                    }
                )
            }
        )

    manifest = ExperimentalReplicationExecutionManifest(
        execution_id="execution-1",
        cycle_contexts=tuple(contexts),
    )

    assert len(manifest.cycle_contexts) == 180


def test_manifest_schema_is_opt_in_explicit_and_enforces_performance_uniqueness(
    tmp_path: Path,
) -> None:
    path = tmp_path / "schema.db"
    database = SQLiteDatabase(path)
    database.initialize_capability_schema()
    with database.connect() as connection:
        absent = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'p3_dev_replication_cycle_manifest'
            """
        ).fetchone()
    assert absent is None

    repository = SQLiteExperimentalReplicationManifestRepository(database)
    repository.initialize_schema()
    with sqlite3.connect(path) as connection:
        columns = {
            str(row[1])
            for row in connection.execute(
                "PRAGMA table_info(p3_dev_replication_cycle_manifest)"
            ).fetchall()
        }
        assert columns == {
            "execution_id",
            "sequence_index",
            "performance_id",
            "agent_id",
            "trial_id",
            "cycle_id",
            "observed_at",
        }
        first = (
            "execution-1",
            0,
            "performance-shared",
            "agent-1",
            "trial-0",
            "cycle-shared",
            OBSERVED_AT.isoformat(),
        )
        connection.execute(
            """
            INSERT INTO p3_dev_replication_cycle_manifest VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            first,
        )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO p3_dev_replication_cycle_manifest VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("execution-1", 1, *first[2:]),
            )


def test_registration_requires_binding_then_provenance_and_matching_identities(
    tmp_path: Path,
) -> None:
    harness = build_harness(tmp_path / "prerequisites.db")
    manifest = build_manifest()
    generated = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=12345)

    with pytest.raises(ExperimentalReplicationManifestIntegrityError, match="3N"):
        harness.manifest_service.register(manifest=manifest)

    harness.binding_service.bind(
        execution_id=manifest.execution_id,
        plan_identity=generated.plan.identity(),
    )
    with pytest.raises(ExperimentalReplicationManifestIntegrityError, match="3O"):
        harness.manifest_service.register(manifest=manifest)

    incompatible = ExperimentalReplicationPlanGenerator().generate_with_provenance(seed=54321)
    harness.provenance_repository.register(
        ExperimentalExecutionGenerationProvenance(
            execution_id=manifest.execution_id,
            generation_provenance=incompatible.provenance,
        )
    )
    with pytest.raises(ExperimentalReplicationManifestIntegrityError, match="incohérentes"):
        harness.manifest_service.register(manifest=manifest)
    assert harness.manifest_repository.get(execution_id=manifest.execution_id) is None


def test_register_reopens_exactly_and_retry_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "reopen.db"
    first = build_harness(path)
    prepare_3n_and_3o(first)
    manifest = build_manifest()
    registered = first.manifest_service.register(manifest=manifest)

    reopened = build_harness(path)
    reloaded = reopened.manifest_service.get(execution_id="execution-1")
    retried = reopened.manifest_service.register(manifest=manifest)

    assert registered == reloaded == retried == manifest
    assert manifest_row_count(path) == 180
    assert reloaded is not None
    assert reloaded.cycle_contexts[73].start_context == manifest.cycle_contexts[73].start_context
    assert type(reloaded.cycle_contexts[73].start_context) is ExperimentalCycleStartContext


def test_conflict_after_reopen_is_refused_without_changing_history(tmp_path: Path) -> None:
    path = tmp_path / "conflict.db"
    first = build_harness(path)
    prepare_3n_and_3o(first)
    manifest = build_manifest()
    first.manifest_service.register(manifest=manifest)
    reopened = build_harness(path)
    changed = build_manifest(
        changed_index=127,
        changed_observed_at=OBSERVED_AT + timedelta(days=30),
    )

    with pytest.raises(ExperimentalReplicationManifestIntegrityError, match="autre manifeste"):
        reopened.manifest_service.register(manifest=changed)

    assert reopened.manifest_service.get(execution_id="execution-1") == manifest
    assert manifest_row_count(path) == 180


def test_register_rolls_back_all_rows_when_an_insert_fails_mid_manifest(tmp_path: Path) -> None:
    path = tmp_path / "rollback.db"
    harness = build_harness(path)
    prepare_3n_and_3o(harness)
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TRIGGER fail_manifest_at_73
            BEFORE INSERT ON p3_dev_replication_cycle_manifest
            WHEN NEW.sequence_index = 73
            BEGIN
                SELECT RAISE(ABORT, 'simulated manifest crash');
            END
            """
        )

    with pytest.raises(sqlite3.IntegrityError, match="simulated manifest crash"):
        harness.manifest_service.register(manifest=build_manifest())

    assert harness.manifest_service.get(execution_id="execution-1") is None
    assert manifest_row_count(path) == 0


def test_sqlite_manifest_rows_reject_update_and_delete(tmp_path: Path) -> None:
    path = tmp_path / "immutable.db"
    harness = build_harness(path)
    prepare_3n_and_3o(harness)
    manifest = build_manifest()
    harness.manifest_service.register(manifest=manifest)

    with sqlite3.connect(path) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                UPDATE p3_dev_replication_cycle_manifest
                SET trial_id = 'changed'
                WHERE execution_id = 'execution-1' AND sequence_index = 73
                """
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                DELETE FROM p3_dev_replication_cycle_manifest
                WHERE execution_id = 'execution-1' AND sequence_index = 73
                """
            )


def test_get_rejects_partial_or_invalid_persistent_manifests(tmp_path: Path) -> None:
    partial = build_harness(tmp_path / "partial.db")
    with sqlite3.connect(partial.path) as connection:
        connection.execute(
            """
            INSERT INTO p3_dev_replication_cycle_manifest VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "execution-1",
                0,
                "performance-0",
                "agent-1",
                "trial-0",
                "cycle-0",
                OBSERVED_AT.isoformat(),
            ),
        )
    with pytest.raises(ExperimentalReplicationManifestIntegrityError, match="180"):
        partial.manifest_repository.get(execution_id="execution-1")

    invalid = build_harness(tmp_path / "invalid.db")
    manifest = build_manifest()
    with sqlite3.connect(invalid.path) as connection:
        connection.executemany(
            """
            INSERT INTO p3_dev_replication_cycle_manifest VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                (
                    manifest.execution_id,
                    context.sequence_index,
                    context.start_context.performance_id,
                    context.start_context.agent_id,
                    context.start_context.trial_id,
                    context.start_context.cycle_id,
                    "invalid-datetime"
                    if context.sequence_index == 73
                    else context.start_context.observed_at.isoformat(),
                )
                for context in manifest.cycle_contexts
            ),
        )
    with pytest.raises(ExperimentalReplicationManifestIntegrityError, match="invalide"):
        invalid.manifest_repository.get(execution_id="execution-1")
