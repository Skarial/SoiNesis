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


def migration_versions(connection: sqlite3.Connection) -> list[int]:
    rows = connection.execute(
        "SELECT version FROM capability_schema_migrations ORDER BY version"
    ).fetchall()
    return [int(row["version"]) for row in rows]


def initialize_synthetic_capability_v1(
    database: SQLiteDatabase,
    *,
    state_version: int = 1,
    conflicting_sequence_column: bool = False,
) -> None:
    database.initialize_capability_schema()
    with database.connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "DELETE FROM capability_schema_migrations WHERE version > 1",
        )
        connection.execute(
            "DROP TRIGGER IF EXISTS capability_performances_require_increasing_sequence"
        )
        connection.execute(
            "ALTER TABLE metacognitive_states DROP COLUMN last_processed_sequence_index"
        )
        connection.execute(
            "ALTER TABLE metacognitive_states DROP COLUMN last_processed_performance_id"
        )
        connection.execute(
            """
            INSERT INTO metacognitive_states (
                agent_id, capability_key, version, alpha, beta, decay_lambda
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("agent-1", "ALPHA", 1, 3.0, 2.0, 0.9),
        )
        if state_version > 1:
            connection.execute(
                """
                UPDATE metacognitive_states
                SET version = ?, alpha = ?, beta = ?
                WHERE agent_id = ? AND capability_key = ?
                """,
                (state_version, 4.0, 2.5, "agent-1", "ALPHA"),
            )
        if conflicting_sequence_column:
            connection.execute(
                """
                ALTER TABLE metacognitive_states
                ADD COLUMN last_processed_sequence_index INTEGER
                """
            )


def initialize_synthetic_capability_v2(database: SQLiteDatabase) -> None:
    database.initialize_capability_schema()
    with database.connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "DELETE FROM capability_schema_migrations WHERE version = ?",
            (CAPABILITY_SCHEMA_VERSION,),
        )
        connection.execute("DROP TRIGGER capability_performances_require_increasing_sequence")


def test_capability_migration_creates_a_fresh_schema_without_private_columns(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "fresh.db")
    database.initialize_capability_schema()

    with database.connect() as connection:
        tables = table_names(connection)
        performance_columns = column_names(connection, "capability_performances")
        metacognitive_columns = column_names(connection, "metacognitive_states")
        cognitive_columns = {table: column_names(connection, table) for table in CAPABILITY_TABLES}
        applied_versions = migration_versions(connection)

    assert CAPABILITY_SCHEMA_VERSION == 3
    assert applied_versions == [1, 2, 3]
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
    assert {
        "last_processed_performance_id",
        "last_processed_sequence_index",
    }.issubset(metacognitive_columns)
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


def test_capability_migration_upgrades_a_synthetic_v1_prior_without_loss(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "capability-v1.db")
    initialize_synthetic_capability_v1(database)

    database.initialize_capability_schema()

    with database.connect() as connection:
        stored_state = connection.execute(
            """
            SELECT agent_id, capability_key, version, alpha, beta, decay_lambda,
                   last_processed_performance_id, last_processed_sequence_index
            FROM metacognitive_states
            """
        ).fetchone()
        applied_versions = migration_versions(connection)

    assert stored_state is not None
    assert str(stored_state["agent_id"]) == "agent-1"
    assert str(stored_state["capability_key"]) == "ALPHA"
    assert int(stored_state["version"]) == 1
    assert float(stored_state["alpha"]) == 3.0
    assert float(stored_state["beta"]) == 2.0
    assert float(stored_state["decay_lambda"]) == 0.9
    assert stored_state["last_processed_performance_id"] is None
    assert stored_state["last_processed_sequence_index"] is None
    assert applied_versions == [1, 2, 3]


def test_capability_v3_migration_preserves_v2_data_and_enforces_sequence(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "capability-v2-to-v3.db")
    initialize_synthetic_capability_v2(database)
    with database.connect() as connection:
        connection.executemany(
            """
            INSERT INTO capability_performances (
                id, agent_id, trial_id, cycle_id, sequence_index,
                capability_key, intrinsic_success, observed_at, source_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                (
                    "performance-0",
                    "agent-1",
                    "trial-0",
                    "cycle-0",
                    0,
                    "ALPHA",
                    1,
                    "2026-08-08T00:00:00+00:00",
                    "DIRECT_ENVIRONMENT",
                ),
                (
                    "performance-2",
                    "agent-1",
                    "trial-2",
                    "cycle-2",
                    2,
                    "BETA",
                    0,
                    "2026-08-08T00:02:00+00:00",
                    "DIRECT_ENVIRONMENT",
                ),
            ),
        )

    database.initialize_capability_schema()

    with database.connect() as connection:
        applied_versions = migration_versions(connection)
        trigger = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'trigger'
              AND name = 'capability_performances_require_increasing_sequence'
            """
        ).fetchone()
        with pytest.raises(sqlite3.IntegrityError, match="strictement supérieur"):
            connection.execute(
                """
                INSERT INTO capability_performances (
                    id, agent_id, trial_id, cycle_id, sequence_index,
                    capability_key, intrinsic_success, observed_at, source_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "performance-1-late",
                    "agent-1",
                    "trial-1-late",
                    "cycle-1-late",
                    1,
                    "ALPHA",
                    1,
                    "2026-08-08T00:01:00+00:00",
                    "DIRECT_ENVIRONMENT",
                ),
            )
        stored_ids = [
            str(row["id"])
            for row in connection.execute(
                "SELECT id FROM capability_performances ORDER BY sequence_index"
            ).fetchall()
        ]

    assert applied_versions == [1, 2, 3]
    assert trigger is not None
    assert str(trigger["name"]) == "capability_performances_require_increasing_sequence"
    assert stored_ids == ["performance-0", "performance-2"]


def test_capability_v2_migration_rolls_back_a_late_alter_failure(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "capability-v2-conflict.db")
    initialize_synthetic_capability_v1(database, conflicting_sequence_column=True)

    with pytest.raises(sqlite3.OperationalError, match="duplicate column"):
        database.initialize_capability_schema()

    with database.connect() as connection:
        columns = column_names(connection, "metacognitive_states")
        applied_versions = migration_versions(connection)

    assert "last_processed_performance_id" not in columns
    assert "last_processed_sequence_index" in columns
    assert applied_versions == [1]


def test_capability_v2_migration_refuses_to_invent_a_legacy_cursor(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "ambiguous-capability-v1.db")
    initialize_synthetic_capability_v1(database, state_version=2)

    with pytest.raises(sqlite3.IntegrityError, match="ne peut pas déduire"):
        database.initialize_capability_schema()

    with database.connect() as connection:
        stored_state = connection.execute(
            """
            SELECT version, alpha, beta
            FROM metacognitive_states
            WHERE agent_id = ? AND capability_key = ?
            """,
            ("agent-1", "ALPHA"),
        ).fetchone()
        columns = column_names(connection, "metacognitive_states")
        applied_versions = migration_versions(connection)

    assert stored_state is not None
    assert int(stored_state["version"]) == 2
    assert float(stored_state["alpha"]) == 4.0
    assert float(stored_state["beta"]) == 2.5
    assert "last_processed_performance_id" not in columns
    assert "last_processed_sequence_index" not in columns
    assert applied_versions == [1]


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
        applied_versions = migration_versions(connection)

    assert int(migration_count) == 1
    assert applied_versions == [1, 2, 3]
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


def test_capability_v2_schema_enforces_the_cursor_pair_and_sequence_type(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "metacognitive-cursor-check.db")
    database.initialize_capability_schema()

    invalid_cursors: tuple[tuple[str | None, int | float | None], ...] = (
        (None, None),
        ("performance-1", None),
        (None, 0),
        ("performance-1", -1),
        ("performance-1", 0.5),
    )
    with database.connect() as connection:
        connection.execute(
            """
            INSERT INTO metacognitive_states (
                agent_id, capability_key, version, alpha, beta, decay_lambda,
                last_processed_performance_id, last_processed_sequence_index
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("agent-1", "ALPHA", 1, 3.0, 2.0, 0.9, None, None),
        )
        for performance_id, sequence_index in invalid_cursors:
            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    UPDATE metacognitive_states
                    SET version = 2,
                        last_processed_performance_id = ?,
                        last_processed_sequence_index = ?
                    WHERE agent_id = ? AND capability_key = ?
                    """,
                    (performance_id, sequence_index, "agent-1", "ALPHA"),
                )

        connection.execute(
            """
            UPDATE metacognitive_states
            SET version = 2,
                last_processed_performance_id = ?,
                last_processed_sequence_index = ?
            WHERE agent_id = ? AND capability_key = ?
            """,
            ("performance-1", 0, "agent-1", "ALPHA"),
        )
        stored_cursor = connection.execute(
            """
            SELECT version, last_processed_performance_id,
                   last_processed_sequence_index
            FROM metacognitive_states
            """
        ).fetchone()

    assert stored_cursor is not None
    assert int(stored_cursor["version"]) == 2
    assert str(stored_cursor["last_processed_performance_id"]) == "performance-1"
    assert int(stored_cursor["last_processed_sequence_index"]) == 0


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
