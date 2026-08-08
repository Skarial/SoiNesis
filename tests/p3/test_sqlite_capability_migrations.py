import sqlite3
from pathlib import Path

import pytest

from soinesis.infrastructure.sqlite import SQLiteDatabase
from soinesis.infrastructure.sqlite.migrations import CAPABILITY_SCHEMA_VERSION

CAPABILITY_TABLES = {
    "capability_performances",
    "metacognitive_states",
    "self_model_versions",
    "capability_self_attributes",
}
PRIVATE_EXPERIMENTAL_COLUMNS = {
    "true_success_probability",
    "phase",
    "seed",
    "replication",
    "official_dataset_id",
    "u_correction",
    "final_success",
}


def table_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    return {str(row["name"]) for row in rows}


def column_names(connection: sqlite3.Connection, table: str) -> set[str]:
    return {
        str(row["name"]) for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
    }


def test_capability_migration_creates_a_fresh_schema_without_private_columns(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "fresh.db")
    database.initialize_capability_schema()

    with database.connect() as connection:
        tables = table_names(connection)
        performance_columns = column_names(connection, "capability_performances")
        cognitive_columns = {table: column_names(connection, table) for table in CAPABILITY_TABLES}

    assert tables >= CAPABILITY_TABLES
    assert "capability_schema_migrations" in tables
    assert performance_columns == {
        "id",
        "agent_id",
        "trial_id",
        "cycle_id",
        "sequence_index",
        "capability_key",
        "intrinsic_success",
        "observed_at",
        "source_type",
    }
    for columns in cognitive_columns.values():
        assert PRIVATE_EXPERIMENTAL_COLUMNS.isdisjoint(columns)


def test_capability_migration_preserves_a_synthetic_historical_schema(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "historical.db")
    database.initialize_schema()
    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO observations (
                id, agent_id, cycle_id, source_type, raw_content,
                received_at, confidence, is_direct_experience
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "legacy-observation",
                "agent-1",
                "legacy-cycle",
                "JORDAN_INPUT",
                "Ligne synthétique antérieure à P3.",
                "2026-08-08T00:00:00+00:00",
                1.0,
                0,
            ),
        )
        assert CAPABILITY_TABLES.isdisjoint(table_names(connection))

    database.initialize_capability_schema()

    with database.connect() as connection:
        legacy_content = connection.execute(
            "SELECT raw_content FROM observations WHERE id = ?",
            ("legacy-observation",),
        ).fetchone()["raw_content"]
        tables = table_names(connection)

    assert str(legacy_content) == "Ligne synthétique antérieure à P3."
    assert tables >= CAPABILITY_TABLES


def test_capability_migration_is_idempotent_on_reopen(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "idempotent.db")
    database.initialize_capability_schema()
    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO capability_performances (
                id, agent_id, trial_id, cycle_id, sequence_index,
                capability_key, intrinsic_success, observed_at, source_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "performance-1",
                "agent-1",
                "trial-1",
                "cycle-1",
                0,
                "ALPHA",
                1,
                "2026-08-08T00:00:00+00:00",
                "DIRECT_ENVIRONMENT",
            ),
        )

    database.initialize_capability_schema()
    database.initialize_capability_schema()

    with database.connect() as connection:
        migration_count = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM capability_schema_migrations
            WHERE version = ?
            """,
            (CAPABILITY_SCHEMA_VERSION,),
        ).fetchone()["count"]
        performance_count = connection.execute(
            "SELECT COUNT(*) AS count FROM capability_performances"
        ).fetchone()["count"]

    assert int(migration_count) == 1
    assert int(performance_count) == 1


def test_failed_capability_migration_is_not_marked_as_applied(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "conflicting.db")
    database.initialize_schema()
    with database.connect() as connection:
        connection.execute("CREATE TABLE metacognitive_states (id TEXT PRIMARY KEY)")

    with pytest.raises(sqlite3.OperationalError, match="already exists"):
        database.initialize_capability_schema()

    with database.connect() as connection:
        tables = table_names(connection)

    assert "metacognitive_states" in tables
    assert "capability_performances" not in tables
    assert "capability_schema_migrations" not in tables


def test_capability_schema_rejects_a_fractional_sequence_index(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "fractional-sequence.db")
    database.initialize_capability_schema()

    with pytest.raises(sqlite3.IntegrityError), database.connect() as connection:
        connection.execute(
            """
            INSERT INTO capability_performances (
                id, agent_id, trial_id, cycle_id, sequence_index,
                capability_key, intrinsic_success, observed_at, source_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "performance-fractional",
                "agent-1",
                "trial-fractional",
                "cycle-fractional",
                0.5,
                "ALPHA",
                1,
                "2026-08-08T00:00:00+00:00",
                "DIRECT_ENVIRONMENT",
            ),
        )


def test_snapshot_chain_constraints_hold_for_direct_sql(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "direct-snapshot-chain.db")
    database.initialize_capability_schema()

    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO self_model_versions (
                id, agent_id, version, previous_version_id, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            ("self-model-1", "agent-1", 1, None, "2026-08-08T00:00:00+00:00"),
        )
        with pytest.raises(sqlite3.IntegrityError, match="SelfModel"):
            connection.execute(
                """
                INSERT INTO self_model_versions (
                    id, agent_id, version, previous_version_id, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "self-model-3",
                    "agent-1",
                    3,
                    "self-model-1",
                    "2026-08-08T00:02:00+00:00",
                ),
            )
        connection.execute(
            """
            INSERT INTO self_model_versions (
                id, agent_id, version, previous_version_id, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                "self-model-2",
                "agent-1",
                2,
                "self-model-1",
                "2026-08-08T00:01:00+00:00",
            ),
        )

        for identifier, capability_key in (
            ("attribute-alpha-1", "ALPHA"),
            ("attribute-beta-1", "BETA"),
        ):
            connection.execute(
                """
                INSERT INTO capability_self_attributes (
                    id, agent_id, attribute_type, capability_key,
                    estimated_success, self_model_version_id,
                    attribute_version, previous_attribute_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier,
                    "agent-1",
                    "CAPABILITY",
                    capability_key,
                    0.6,
                    "self-model-1",
                    1,
                    None,
                    "2026-08-08T00:00:00+00:00",
                ),
            )

        with pytest.raises(sqlite3.IntegrityError, match="SelfAttribute"):
            connection.execute(
                """
                INSERT INTO capability_self_attributes (
                    id, agent_id, attribute_type, capability_key,
                    estimated_success, self_model_version_id,
                    attribute_version, previous_attribute_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "attribute-alpha-2-invalid",
                    "agent-1",
                    "CAPABILITY",
                    "ALPHA",
                    0.7,
                    "self-model-2",
                    2,
                    "attribute-beta-1",
                    "2026-08-08T00:01:00+00:00",
                ),
            )
        connection.execute(
            """
            INSERT INTO capability_self_attributes (
                id, agent_id, attribute_type, capability_key,
                estimated_success, self_model_version_id,
                attribute_version, previous_attribute_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "attribute-alpha-2",
                "agent-1",
                "CAPABILITY",
                "ALPHA",
                0.7,
                "self-model-2",
                2,
                "attribute-alpha-1",
                "2026-08-08T00:01:00+00:00",
            ),
        )

        model_versions = connection.execute(
            "SELECT version FROM self_model_versions ORDER BY version"
        ).fetchall()
        alpha_versions = connection.execute(
            """
            SELECT attribute_version
            FROM capability_self_attributes
            WHERE capability_key = 'ALPHA'
            ORDER BY attribute_version
            """
        ).fetchall()

    assert [int(row["version"]) for row in model_versions] == [1, 2]
    assert [int(row["attribute_version"]) for row in alpha_versions] == [1, 2]
