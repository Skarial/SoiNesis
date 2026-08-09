import inspect
import sqlite3
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from soinesis.experiments.p3 import (
    ExperimentalCondition,
    ExperimentalConditionConfiguration,
    ExperimentalCycleStartContext,
    ExperimentalExecutionConditionConfigurationService,
    ExperimentalExecutionGenerationProvenanceService,
    ExperimentalExecutionPlanBindingService,
    ExperimentalGeneratedReplicationPlan,
    ExperimentalPairedConditionGroup,
    ExperimentalPairedConditionGroupService,
    ExperimentalPairingIntegrityError,
    ExperimentalReplicationCycleContext,
    ExperimentalReplicationExecutionManifest,
    ExperimentalReplicationManifestService,
    ExperimentalReplicationPlanGenerator,
    SQLiteExperimentalExecutionConditionConfigurationRepository,
    SQLiteExperimentalExecutionGenerationProvenanceRepository,
    SQLiteExperimentalExecutionPlanBindingRepository,
    SQLiteExperimentalPairedConditionGroupRepository,
    SQLiteExperimentalReplicationManifestRepository,
)
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

START_TIME = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)


class ManifestReaderOverride:
    def __init__(
        self,
        delegate: ExperimentalReplicationManifestService,
        overrides: dict[str, ExperimentalReplicationExecutionManifest],
    ) -> None:
        self._delegate = delegate
        self._overrides = overrides

    def get(self, *, execution_id: str) -> ExperimentalReplicationExecutionManifest | None:
        return self._overrides.get(execution_id) or self._delegate.get(execution_id=execution_id)


class PairingHarness:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.database = SQLiteDatabase(path)
        self.binding_repository = SQLiteExperimentalExecutionPlanBindingRepository(self.database)
        self.provenance_repository = SQLiteExperimentalExecutionGenerationProvenanceRepository(
            self.database
        )
        self.manifest_repository = SQLiteExperimentalReplicationManifestRepository(self.database)
        self.configuration_repository = SQLiteExperimentalExecutionConditionConfigurationRepository(
            self.database
        )
        self.pairing_repository = SQLiteExperimentalPairedConditionGroupRepository(self.database)
        self.binding_repository.initialize_schema()
        self.provenance_repository.initialize_schema()
        self.manifest_repository.initialize_schema()
        self.configuration_repository.initialize_schema()
        self.pairing_repository.initialize_schema()
        self.binding_service = ExperimentalExecutionPlanBindingService(self.binding_repository)
        self.provenance_service = ExperimentalExecutionGenerationProvenanceService(
            repository=self.provenance_repository,
            binding_repository=self.binding_repository,
        )
        self.manifest_service = ExperimentalReplicationManifestService(
            repository=self.manifest_repository,
            binding_repository=self.binding_repository,
            provenance_repository=self.provenance_repository,
        )
        self.configuration_service = ExperimentalExecutionConditionConfigurationService(
            repository=self.configuration_repository,
            binding_repository=self.binding_repository,
            provenance_repository=self.provenance_repository,
            manifest_repository=self.manifest_repository,
        )
        self.generator = ExperimentalReplicationPlanGenerator()
        self.service = ExperimentalPairedConditionGroupService(
            repository=self.pairing_repository,
            configuration_service=self.configuration_service,
            binding_service=self.binding_service,
            provenance_service=self.provenance_service,
            manifest_service=self.manifest_service,
            plan_generator=self.generator,
        )

    def service_with_manifest_reader(
        self,
        manifest_reader: ManifestReaderOverride,
    ) -> ExperimentalPairedConditionGroupService:
        return ExperimentalPairedConditionGroupService(
            repository=self.pairing_repository,
            configuration_service=self.configuration_service,
            binding_service=self.binding_service,
            provenance_service=self.provenance_service,
            manifest_service=manifest_reader,
            plan_generator=self.generator,
        )


def build_manifest(
    *,
    execution_id: str,
    agent_id: str,
    performance_prefix: str | None = None,
    changed_time_at: int | None = None,
) -> ExperimentalReplicationExecutionManifest:
    selected_prefix = performance_prefix or execution_id
    return ExperimentalReplicationExecutionManifest(
        execution_id=execution_id,
        cycle_contexts=tuple(
            ExperimentalReplicationCycleContext(
                sequence_index=index,
                start_context=ExperimentalCycleStartContext(
                    performance_id=f"{selected_prefix}-performance-{index}",
                    agent_id=agent_id,
                    trial_id=f"{execution_id}-trial-{index}",
                    cycle_id=f"{execution_id}-cycle-{index}",
                    observed_at=(
                        START_TIME
                        + timedelta(minutes=index)
                        + (timedelta(seconds=1) if index == changed_time_at else timedelta())
                    ),
                ),
            )
            for index in range(180)
        ),
    )


def prepare_execution(
    harness: PairingHarness,
    *,
    execution_id: str,
    agent_id: str,
    condition: ExperimentalCondition,
    generated: ExperimentalGeneratedReplicationPlan,
    estimator_lambda: str | None,
    performance_prefix: str | None = None,
    changed_time_at: int | None = None,
) -> None:
    harness.binding_service.bind(
        execution_id=execution_id,
        plan_identity=generated.plan.identity(),
    )
    harness.provenance_service.register(
        execution_id=execution_id,
        generation_provenance=generated.provenance,
    )
    harness.manifest_service.register(
        manifest=build_manifest(
            execution_id=execution_id,
            agent_id=agent_id,
            performance_prefix=performance_prefix,
            changed_time_at=changed_time_at,
        )
    )
    harness.configuration_service.register(
        execution_id=execution_id,
        configuration=ExperimentalConditionConfiguration(
            scheme="p3-condition-config-v1",
            condition=condition,
            estimator_lambda=(None if estimator_lambda is None else Decimal(estimator_lambda)),
        ),
    )


def prepare_triplet(
    harness: PairingHarness,
    *,
    suffix: str = "1",
    generated: ExperimentalGeneratedReplicationPlan | None = None,
    lambda_b: str = "0.94",
    lambda_c: str = "0.94",
    conditions: tuple[ExperimentalCondition, ExperimentalCondition, ExperimentalCondition] = (
        ExperimentalCondition.A,
        ExperimentalCondition.B,
        ExperimentalCondition.C,
    ),
    agents: tuple[str, str, str] | None = None,
    shared_performance_prefix: str | None = None,
    changed_c_time_at: int | None = None,
) -> tuple[str, str, str]:
    plan = generated or harness.generator.generate_with_provenance(seed=12345)
    executions = (
        f"execution-A-{suffix}",
        f"execution-B-{suffix}",
        f"execution-C-{suffix}",
    )
    selected_agents = agents or (
        f"agent-A-{suffix}",
        f"agent-B-{suffix}",
        f"agent-C-{suffix}",
    )
    for index, (execution_id, agent_id, condition, estimator_lambda) in enumerate(
        zip(
            executions,
            selected_agents,
            conditions,
            (None, lambda_b, lambda_c),
            strict=True,
        )
    ):
        prepare_execution(
            harness,
            execution_id=execution_id,
            agent_id=agent_id,
            condition=condition,
            generated=plan,
            estimator_lambda=estimator_lambda,
            performance_prefix=shared_performance_prefix,
            changed_time_at=changed_c_time_at if index == 2 else None,
        )
    return executions


def register_triplet(
    harness: PairingHarness,
    *,
    pairing_id: str,
    executions: tuple[str, str, str],
    service: ExperimentalPairedConditionGroupService | None = None,
) -> ExperimentalPairedConditionGroup:
    selected_service = service or harness.service
    return selected_service.register(
        pairing_id=pairing_id,
        execution_a=executions[0],
        execution_b=executions[1],
        execution_c=executions[2],
    )


def row_counts(path: Path) -> tuple[int, int]:
    with sqlite3.connect(path) as connection:
        group_count = int(
            connection.execute("SELECT COUNT(*) FROM p3_dev_paired_condition_groups").fetchone()[0]
        )
        member_count = int(
            connection.execute(
                "SELECT COUNT(*) FROM p3_dev_paired_condition_group_members"
            ).fetchone()[0]
        )
    return group_count, member_count


def test_valid_pairing_round_trips_idempotently_and_is_immutable(tmp_path: Path) -> None:
    harness = PairingHarness(tmp_path / "valid-pairing.db")
    generated = harness.generator.generate_with_provenance(seed=12345)
    executions = prepare_triplet(harness, generated=generated)

    first = register_triplet(harness, pairing_id="pairing-1", executions=executions)
    reopened = PairingHarness(harness.path)
    second = register_triplet(reopened, pairing_id="pairing-1", executions=executions)

    assert second == first
    assert harness.service.get(pairing_id="pairing-1") == first
    assert first.plan_identity == generated.plan.identity()
    assert first.estimator_lambda == Decimal("0.94")
    assert row_counts(harness.path) == (1, 3)
    assert set(ExperimentalPairedConditionGroup.model_fields) == {
        "pairing_id",
        "execution_a",
        "execution_b",
        "execution_c",
        "plan_identity",
        "estimator_lambda",
    }
    with pytest.raises(ValidationError):
        first.execution_a = "other"  # type: ignore[misc]
    with pytest.raises(ExperimentalPairingIntegrityError):
        harness.pairing_repository.register(
            first.model_copy(update={"execution_c": "other-execution"})
        )
    with pytest.raises(ExperimentalPairingIntegrityError):
        harness.pairing_repository.register(
            first.model_copy(update={"estimator_lambda": Decimal("0.97")})
        )
    foreign_plan = harness.generator.generate_with_provenance(seed=54321).plan.identity()
    with pytest.raises(ExperimentalPairingIntegrityError):
        harness.pairing_repository.register(
            first.model_copy(update={"plan_identity": foreign_plan})
        )
    for statement in (
        "UPDATE p3_dev_paired_condition_groups SET estimator_lambda = '0.97'",
        "DELETE FROM p3_dev_paired_condition_groups",
        "UPDATE p3_dev_paired_condition_group_members SET execution_id = 'other'",
        "DELETE FROM p3_dev_paired_condition_group_members",
    ):
        with pytest.raises(sqlite3.IntegrityError), harness.database.connect() as connection:
            connection.execute(statement)
    assert harness.service.get(pairing_id="pairing-1") == first
    assert row_counts(harness.path) == (1, 3)


def test_different_plan_or_provenance_is_rejected_before_persistence(tmp_path: Path) -> None:
    harness = PairingHarness(tmp_path / "different-plan.db")
    canonical = harness.generator.generate_with_provenance(seed=12345)
    foreign = harness.generator.generate_with_provenance(seed=54321)
    executions = ("execution-A", "execution-B", "execution-C")
    prepare_execution(
        harness,
        execution_id=executions[0],
        agent_id="agent-A",
        condition=ExperimentalCondition.A,
        generated=canonical,
        estimator_lambda=None,
    )
    prepare_execution(
        harness,
        execution_id=executions[1],
        agent_id="agent-B",
        condition=ExperimentalCondition.B,
        generated=canonical,
        estimator_lambda="0.94",
    )
    prepare_execution(
        harness,
        execution_id=executions[2],
        agent_id="agent-C",
        condition=ExperimentalCondition.C,
        generated=foreign,
        estimator_lambda="0.94",
    )

    with pytest.raises(ExperimentalPairingIntegrityError, match="plan latent"):
        register_triplet(harness, pairing_id="pairing-1", executions=executions)

    assert row_counts(harness.path) == (0, 0)


def test_lambda_mismatch_and_inverted_conditions_are_rejected(tmp_path: Path) -> None:
    lambda_harness = PairingHarness(tmp_path / "lambda-mismatch.db")
    lambda_executions = prepare_triplet(lambda_harness, lambda_c="0.97")
    with pytest.raises(ExperimentalPairingIntegrityError, match="lambda"):
        register_triplet(
            lambda_harness,
            pairing_id="pairing-1",
            executions=lambda_executions,
        )
    assert row_counts(lambda_harness.path) == (0, 0)

    condition_harness = PairingHarness(tmp_path / "inverted-condition.db")
    generated = condition_harness.generator.generate_with_provenance(seed=12345)
    condition_executions = ("execution-A", "execution-B", "execution-C")
    prepare_execution(
        condition_harness,
        execution_id=condition_executions[0],
        agent_id="agent-A",
        condition=ExperimentalCondition.B,
        generated=generated,
        estimator_lambda="0.94",
    )
    prepare_execution(
        condition_harness,
        execution_id=condition_executions[1],
        agent_id="agent-B",
        condition=ExperimentalCondition.A,
        generated=generated,
        estimator_lambda=None,
    )
    prepare_execution(
        condition_harness,
        execution_id=condition_executions[2],
        agent_id="agent-C",
        condition=ExperimentalCondition.C,
        generated=generated,
        estimator_lambda="0.94",
    )
    with pytest.raises(ExperimentalPairingIntegrityError, match="configurés A, B, C"):
        register_triplet(
            condition_harness,
            pairing_id="pairing-1",
            executions=condition_executions,
        )
    assert row_counts(condition_harness.path) == (0, 0)


@pytest.mark.parametrize("corruption", ("chronology", "agent", "performance_id"))
def test_manifest_pairing_corruptions_are_rejected(
    tmp_path: Path,
    corruption: str,
) -> None:
    harness = PairingHarness(tmp_path / f"manifest-{corruption}.db")
    executions = prepare_triplet(
        harness,
        changed_c_time_at=73 if corruption == "chronology" else None,
    )
    selected_service = harness.service
    if corruption in ("agent", "performance_id"):
        manifest_a = harness.manifest_service.get(execution_id=executions[0])
        assert manifest_a is not None
        overridden_b = build_manifest(
            execution_id=executions[1],
            agent_id=(
                manifest_a.cycle_contexts[0].start_context.agent_id
                if corruption == "agent"
                else "agent-B-1"
            ),
            performance_prefix=(executions[0] if corruption == "performance_id" else None),
        )
        selected_service = harness.service_with_manifest_reader(
            ManifestReaderOverride(
                harness.manifest_service,
                {executions[1]: overridden_b},
            )
        )

    expected_message = {
        "chronology": "chronologie",
        "agent": "agents",
        "performance_id": "performance_id",
    }[corruption]
    with pytest.raises(ExperimentalPairingIntegrityError, match=expected_message):
        register_triplet(
            harness,
            pairing_id="pairing-1",
            executions=executions,
            service=selected_service,
        )

    assert row_counts(harness.path) == (0, 0)


def test_execution_can_belong_to_only_one_group_across_all_roles(tmp_path: Path) -> None:
    harness = PairingHarness(tmp_path / "execution-unique.db")
    generated = harness.generator.generate_with_provenance(seed=12345)
    first_executions = prepare_triplet(harness, suffix="1", generated=generated)
    register_triplet(harness, pairing_id="pairing-1", executions=first_executions)
    prepare_execution(
        harness,
        execution_id="execution-A-2",
        agent_id="agent-A-2",
        condition=ExperimentalCondition.A,
        generated=generated,
        estimator_lambda=None,
    )
    prepare_execution(
        harness,
        execution_id="execution-C-2",
        agent_id="agent-C-2",
        condition=ExperimentalCondition.C,
        generated=generated,
        estimator_lambda="0.94",
    )

    with pytest.raises(ExperimentalPairingIntegrityError, match="appartient déjà"):
        harness.service.register(
            pairing_id="pairing-2",
            execution_a="execution-A-2",
            execution_b=first_executions[1],
            execution_c="execution-C-2",
        )
    with pytest.raises(ExperimentalPairingIntegrityError, match="appartient déjà"):
        harness.pairing_repository.register(
            ExperimentalPairedConditionGroup(
                pairing_id="pairing-3",
                execution_a="execution-A-3",
                execution_b="execution-B-3",
                execution_c=first_executions[1],
                plan_identity=generated.plan.identity(),
                estimator_lambda=Decimal("0.94"),
            )
        )

    assert harness.service.get(pairing_id="pairing-1") is not None
    assert harness.service.get(pairing_id="pairing-2") is None
    assert row_counts(harness.path) == (1, 3)


def test_third_member_failure_rolls_back_group_and_all_members(tmp_path: Path) -> None:
    harness = PairingHarness(tmp_path / "atomicity.db")
    executions = prepare_triplet(harness)
    with harness.database.connect() as connection:
        connection.execute(
            """
            CREATE TRIGGER fail_third_pairing_member
            BEFORE INSERT ON p3_dev_paired_condition_group_members
            WHEN NEW.condition = 'C'
            BEGIN
                SELECT RAISE(ABORT, 'simulated third member failure');
            END
            """
        )

    with pytest.raises(ExperimentalPairingIntegrityError, match="atomique"):
        register_triplet(harness, pairing_id="pairing-1", executions=executions)

    assert row_counts(harness.path) == (0, 0)
    assert harness.service.get(pairing_id="pairing-1") is None


def test_get_rejects_a_partial_persistent_group_instead_of_returning_none(tmp_path: Path) -> None:
    harness = PairingHarness(tmp_path / "partial-group.db")
    generated = harness.generator.generate_with_provenance(seed=12345)
    with harness.database.connect() as connection:
        connection.execute(
            """
            INSERT INTO p3_dev_paired_condition_groups (
                pairing_id, plan_identity_scheme, plan_fingerprint, estimator_lambda
            ) VALUES (?, ?, ?, ?)
            """,
            (
                "pairing-1",
                generated.plan.identity().scheme,
                generated.plan.identity().fingerprint,
                "0.94",
            ),
        )
        connection.execute(
            """
            INSERT INTO p3_dev_paired_condition_group_members (
                pairing_id, condition, execution_id
            ) VALUES ('pairing-1', 'A', 'execution-A')
            """
        )

    with pytest.raises(ExperimentalPairingIntegrityError, match="exactement trois"):
        harness.service.get(pairing_id="pairing-1")


def test_schema_guarantees_primary_keys_unique_foreign_key_checks_and_triggers(
    tmp_path: Path,
) -> None:
    harness = PairingHarness(tmp_path / "schema.db")
    with harness.database.connect() as connection:
        group_info = connection.execute(
            "PRAGMA table_info(p3_dev_paired_condition_groups)"
        ).fetchall()
        member_info = connection.execute(
            "PRAGMA table_info(p3_dev_paired_condition_group_members)"
        ).fetchall()
        assert tuple(row["name"] for row in group_info if row["pk"]) == ("pairing_id",)
        assert tuple(
            row["name"] for row in sorted(member_info, key=lambda row: row["pk"]) if row["pk"]
        ) == ("pairing_id", "condition")
        unique_indexes = connection.execute(
            "PRAGMA index_list(p3_dev_paired_condition_group_members)"
        ).fetchall()
        assert any(
            row["unique"]
            and tuple(
                column["name"]
                for column in connection.execute(f"PRAGMA index_info({row['name']})").fetchall()
            )
            == ("execution_id",)
            for row in unique_indexes
        )
        assert any(
            row["table"] == "p3_dev_paired_condition_groups"
            and row["from"] == "pairing_id"
            and row["to"] == "pairing_id"
            for row in connection.execute(
                "PRAGMA foreign_key_list(p3_dev_paired_condition_group_members)"
            ).fetchall()
        )
        schema_objects = connection.execute(
            """
            SELECT type, name, sql FROM sqlite_master
            WHERE name LIKE 'p3_dev_paired_condition_group%'
            """
        ).fetchall()
    table_sql = " ".join(str(row["sql"]) for row in schema_objects if row["type"] == "table")
    assert "condition IN ('A', 'B', 'C')" in table_sql
    assert "estimator_lambda IN ('0.90', '0.92', '0.94', '0.95', '0.96', '0.97')" in table_sql
    triggers = [row for row in schema_objects if row["type"] == "trigger"]
    assert len(triggers) == 4
    assert all("RAISE(ABORT" in str(row["sql"]) for row in triggers)


def test_initialize_schema_rejects_homonymous_tables_without_required_constraints(
    tmp_path: Path,
) -> None:
    path = tmp_path / "invalid-schema.db"
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE p3_dev_paired_condition_groups (
                pairing_id TEXT,
                plan_identity_scheme TEXT,
                plan_fingerprint TEXT,
                estimator_lambda TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE p3_dev_paired_condition_group_members (
                pairing_id TEXT,
                condition TEXT,
                execution_id TEXT
            )
            """
        )

    repository = SQLiteExperimentalPairedConditionGroupRepository(SQLiteDatabase(path))
    with pytest.raises(ExperimentalPairingIntegrityError, match="schéma SQLite"):
        repository.initialize_schema()


@pytest.mark.parametrize("corruption", ("orphan", "partial"))
def test_initialize_schema_rejects_historical_orphan_or_partial_groups(
    tmp_path: Path,
    corruption: str,
) -> None:
    harness = PairingHarness(tmp_path / f"historical-{corruption}.db")
    generated = harness.generator.generate_with_provenance(seed=12345)
    with sqlite3.connect(harness.path) as connection:
        if corruption == "orphan":
            connection.execute(
                """
                INSERT INTO p3_dev_paired_condition_group_members (
                    pairing_id, condition, execution_id
                ) VALUES ('missing-pairing', 'A', 'execution-A')
                """
            )
        else:
            connection.execute(
                """
                INSERT INTO p3_dev_paired_condition_groups (
                    pairing_id, plan_identity_scheme, plan_fingerprint, estimator_lambda
                ) VALUES (?, ?, ?, '0.94')
                """,
                (
                    "partial-pairing",
                    generated.plan.identity().scheme,
                    generated.plan.identity().fingerprint,
                ),
            )

    with pytest.raises(ExperimentalPairingIntegrityError, match="incomplètes ou orphelines"):
        harness.pairing_repository.initialize_schema()


def test_3u_source_has_no_runner_cognitive_access_metrics_or_private_latents() -> None:
    assert list(inspect.signature(ExperimentalPairedConditionGroupService.register).parameters) == [
        "self",
        "pairing_id",
        "execution_a",
        "execution_b",
        "execution_c",
    ]
    sources = "".join(
        Path(path).read_text(encoding="utf-8")
        for path in (
            "src/soinesis/experiments/p3/pairing.py",
            "src/soinesis/experiments/p3/pairing_sqlite.py",
        )
    )
    assert ".generate(" not in sources
    assert ".generate_with_provenance(" not in sources
    assert ".reproduce(" in sources
    for forbidden in (
        "ExperimentalConditionReplicationRunner",
        "ExperimentalReplicationRunner",
        "ExperimentalCycleRunner",
        "capability_performances",
        "metacognitive_states",
        "SelfModel",
        "SelfAttribute",
        "checkpoint",
        "u_intrinsic",
        "u_correction",
        "SELF-ABL",
        "META-ABL",
        "MAE",
        "regret",
        "Brier",
        "VALIDATION",
        "OFFICIAL",
    ):
        assert forbidden not in sources
