"""Migrations SQLite additives réservées au socle de capacités."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

CAPABILITY_SCHEMA_VERSION: Final = 2
CAPABILITY_SCHEMA_MIGRATION_NAME: Final = "metacognitive_proof_cursor"


@dataclass(frozen=True)
class _CapabilitySchemaMigration:
    version: int
    name: str
    statements: tuple[str, ...]
    preflight: Callable[[sqlite3.Connection], None] | None = None


_CAPABILITY_SCHEMA_V1_STATEMENTS: Final[tuple[str, ...]] = (
    """
    CREATE TABLE capability_performances (
        id TEXT PRIMARY KEY NOT NULL,
        agent_id TEXT NOT NULL,
        trial_id TEXT NOT NULL,
        cycle_id TEXT NOT NULL,
        sequence_index INTEGER NOT NULL CHECK (
            typeof(sequence_index) = 'integer' AND sequence_index >= 0
        ),
        capability_key TEXT NOT NULL,
        intrinsic_success INTEGER NOT NULL CHECK (intrinsic_success IN (0, 1)),
        observed_at TEXT NOT NULL,
        source_type TEXT NOT NULL,
        UNIQUE (agent_id, trial_id),
        UNIQUE (agent_id, sequence_index)
    )
    """,
    """
    CREATE TRIGGER capability_performances_no_replace
    BEFORE INSERT ON capability_performances
    WHEN EXISTS (
        SELECT 1 FROM capability_performances
        WHERE id = NEW.id
           OR (agent_id = NEW.agent_id AND trial_id = NEW.trial_id)
           OR (agent_id = NEW.agent_id AND sequence_index = NEW.sequence_index)
    )
    BEGIN
        SELECT RAISE(ABORT, 'Une performance existante ne peut pas être remplacée');
    END
    """,
    """
    CREATE INDEX capability_performances_history_idx
    ON capability_performances (
        agent_id, capability_key, sequence_index, observed_at, id
    )
    """,
    """
    CREATE TRIGGER capability_performances_no_update
    BEFORE UPDATE ON capability_performances
    BEGIN
        SELECT RAISE(ABORT, 'Une performance de capacité est immuable');
    END
    """,
    """
    CREATE TRIGGER capability_performances_no_delete
    BEFORE DELETE ON capability_performances
    BEGIN
        SELECT RAISE(ABORT, 'Une performance de capacité est append-only');
    END
    """,
    """
    CREATE TABLE metacognitive_states (
        agent_id TEXT NOT NULL,
        capability_key TEXT NOT NULL,
        version INTEGER NOT NULL CHECK (version >= 1),
        alpha REAL NOT NULL CHECK (alpha > 0.0),
        beta REAL NOT NULL CHECK (beta > 0.0),
        decay_lambda REAL NOT NULL CHECK (
            decay_lambda > 0.0 AND decay_lambda <= 1.0
        ),
        PRIMARY KEY (agent_id, capability_key)
    )
    """,
    """
    CREATE TRIGGER metacognitive_states_validate_insert
    BEFORE INSERT ON metacognitive_states
    WHEN NEW.version <> 1
    BEGIN
        SELECT RAISE(ABORT, 'Un état métacognitif doit commencer à la version 1');
    END
    """,
    """
    CREATE TRIGGER metacognitive_states_no_replace
    BEFORE INSERT ON metacognitive_states
    WHEN EXISTS (
        SELECT 1 FROM metacognitive_states
        WHERE agent_id = NEW.agent_id
          AND capability_key = NEW.capability_key
    )
    BEGIN
        SELECT RAISE(ABORT, 'Un état métacognitif existant ne peut pas être remplacé');
    END
    """,
    """
    CREATE TRIGGER metacognitive_states_validate_update
    BEFORE UPDATE ON metacognitive_states
    WHEN NEW.agent_id <> OLD.agent_id
      OR NEW.capability_key <> OLD.capability_key
      OR NEW.version <> OLD.version + 1
    BEGIN
        SELECT RAISE(ABORT, 'Transition métacognitive invalide');
    END
    """,
    """
    CREATE TRIGGER metacognitive_states_no_delete
    BEFORE DELETE ON metacognitive_states
    BEGIN
        SELECT RAISE(ABORT, 'Un état métacognitif courant ne peut pas être supprimé');
    END
    """,
    """
    CREATE TABLE self_model_versions (
        id TEXT PRIMARY KEY NOT NULL,
        agent_id TEXT NOT NULL,
        version INTEGER NOT NULL CHECK (version >= 1),
        previous_version_id TEXT,
        created_at TEXT NOT NULL,
        UNIQUE (agent_id, version),
        CHECK (
            (version = 1 AND previous_version_id IS NULL)
            OR (version > 1 AND previous_version_id IS NOT NULL)
        ),
        FOREIGN KEY (previous_version_id) REFERENCES self_model_versions(id)
    )
    """,
    """
    CREATE TRIGGER self_model_versions_validate_insert
    BEFORE INSERT ON self_model_versions
    BEGIN
        SELECT CASE
            WHEN EXISTS (
                SELECT 1 FROM self_model_versions
                WHERE id = NEW.id
            ) THEN RAISE(ABORT, 'Une version du SelfModel avec cet id existe déjà')
            WHEN NEW.version = 1 AND EXISTS (
                SELECT 1 FROM self_model_versions
                WHERE agent_id = NEW.agent_id
            ) THEN RAISE(ABORT, 'La version initiale du SelfModel existe déjà')
            WHEN NEW.version > 1 AND NOT EXISTS (
                SELECT 1
                FROM self_model_versions AS previous
                WHERE previous.id = NEW.previous_version_id
                  AND previous.agent_id = NEW.agent_id
                  AND previous.version = NEW.version - 1
                  AND previous.version = (
                      SELECT MAX(current.version)
                      FROM self_model_versions AS current
                      WHERE current.agent_id = NEW.agent_id
                  )
            ) THEN RAISE(ABORT, 'Prédécesseur SelfModel non courant ou invalide')
        END;
    END
    """,
    """
    CREATE TRIGGER self_model_versions_no_update
    BEFORE UPDATE ON self_model_versions
    BEGIN
        SELECT RAISE(ABORT, 'Une version du SelfModel est immuable');
    END
    """,
    """
    CREATE TRIGGER self_model_versions_no_delete
    BEFORE DELETE ON self_model_versions
    BEGIN
        SELECT RAISE(ABORT, 'Une version du SelfModel est append-only');
    END
    """,
    """
    CREATE TABLE capability_self_attributes (
        id TEXT PRIMARY KEY NOT NULL,
        agent_id TEXT NOT NULL,
        attribute_type TEXT NOT NULL CHECK (attribute_type = 'CAPABILITY'),
        capability_key TEXT NOT NULL,
        estimated_success REAL NOT NULL CHECK (
            estimated_success >= 0.0 AND estimated_success <= 1.0
        ),
        self_model_version_id TEXT NOT NULL,
        attribute_version INTEGER NOT NULL CHECK (attribute_version >= 1),
        previous_attribute_id TEXT,
        created_at TEXT NOT NULL,
        UNIQUE (agent_id, capability_key, attribute_version),
        CHECK (
            (attribute_version = 1 AND previous_attribute_id IS NULL)
            OR (attribute_version > 1 AND previous_attribute_id IS NOT NULL)
        ),
        FOREIGN KEY (self_model_version_id) REFERENCES self_model_versions(id),
        FOREIGN KEY (previous_attribute_id) REFERENCES capability_self_attributes(id)
    )
    """,
    """
    CREATE TRIGGER capability_self_attributes_validate_insert
    BEFORE INSERT ON capability_self_attributes
    BEGIN
        SELECT CASE
            WHEN EXISTS (
                SELECT 1 FROM capability_self_attributes
                WHERE id = NEW.id
            ) THEN RAISE(ABORT, 'Un SelfAttribute avec cet id existe déjà')
            WHEN NOT EXISTS (
                SELECT 1 FROM self_model_versions
                WHERE id = NEW.self_model_version_id
                  AND agent_id = NEW.agent_id
            ) THEN RAISE(ABORT, 'SelfModelVersion absent ou rattaché à un autre agent')
            WHEN NEW.attribute_version = 1 AND EXISTS (
                SELECT 1 FROM capability_self_attributes
                WHERE agent_id = NEW.agent_id
                  AND capability_key = NEW.capability_key
            ) THEN RAISE(ABORT, 'La version initiale de cet attribut existe déjà')
            WHEN NEW.attribute_version > 1 AND NOT EXISTS (
                SELECT 1
                FROM capability_self_attributes AS previous
                WHERE previous.id = NEW.previous_attribute_id
                  AND previous.agent_id = NEW.agent_id
                  AND previous.capability_key = NEW.capability_key
                  AND previous.attribute_version = NEW.attribute_version - 1
                  AND previous.attribute_version = (
                      SELECT MAX(current.attribute_version)
                      FROM capability_self_attributes AS current
                      WHERE current.agent_id = NEW.agent_id
                        AND current.capability_key = NEW.capability_key
                  )
            ) THEN RAISE(ABORT, 'Prédécesseur SelfAttribute non courant ou invalide')
        END;
    END
    """,
    """
    CREATE TRIGGER capability_self_attributes_no_update
    BEFORE UPDATE ON capability_self_attributes
    BEGIN
        SELECT RAISE(ABORT, 'Un SelfAttribute historique est immuable');
    END
    """,
    """
    CREATE TRIGGER capability_self_attributes_no_delete
    BEFORE DELETE ON capability_self_attributes
    BEGIN
        SELECT RAISE(ABORT, 'Un SelfAttribute historique est append-only');
    END
    """,
)

_CAPABILITY_SCHEMA_V2_STATEMENTS: Final[tuple[str, ...]] = (
    """
    ALTER TABLE metacognitive_states
    ADD COLUMN last_processed_performance_id TEXT
    """,
    """
    ALTER TABLE metacognitive_states
    ADD COLUMN last_processed_sequence_index INTEGER CHECK (
        (
            version = 1
            AND last_processed_performance_id IS NULL
            AND last_processed_sequence_index IS NULL
        )
        OR (
            version > 1
            AND last_processed_performance_id IS NOT NULL
            AND last_processed_sequence_index IS NOT NULL
            AND typeof(last_processed_sequence_index) = 'integer'
            AND last_processed_sequence_index >= 0
        )
    )
    """,
)


def _refuse_ambiguous_metacognitive_cursor_backfill(
    connection: sqlite3.Connection,
) -> None:
    """Refuser d'inventer un curseur pour un état v1 déjà mis à jour."""
    legacy_updated_state = connection.execute(
        "SELECT 1 FROM metacognitive_states WHERE version > 1 LIMIT 1"
    ).fetchone()
    if legacy_updated_state is not None:
        raise sqlite3.IntegrityError(
            "La migration du curseur métacognitif ne peut pas déduire la preuve "
            "traitée d'un état historique de version supérieure à 1."
        )


_CAPABILITY_SCHEMA_MIGRATIONS: Final[tuple[_CapabilitySchemaMigration, ...]] = (
    _CapabilitySchemaMigration(
        version=1,
        name="capability_persistence",
        statements=_CAPABILITY_SCHEMA_V1_STATEMENTS,
    ),
    _CapabilitySchemaMigration(
        version=2,
        name=CAPABILITY_SCHEMA_MIGRATION_NAME,
        statements=_CAPABILITY_SCHEMA_V2_STATEMENTS,
        preflight=_refuse_ambiguous_metacognitive_cursor_backfill,
    ),
)


def apply_capability_schema_migrations(connection: sqlite3.Connection) -> None:
    """Appliquer dans la transaction courante les migrations de capacité manquantes."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS capability_schema_migrations (
            version INTEGER PRIMARY KEY NOT NULL,
            name TEXT NOT NULL UNIQUE
        )
        """
    )
    applied_versions = {
        int(row["version"])
        for row in connection.execute("SELECT version FROM capability_schema_migrations").fetchall()
    }
    known_versions = {migration.version for migration in _CAPABILITY_SCHEMA_MIGRATIONS}
    unsupported_versions = applied_versions - known_versions
    if unsupported_versions:
        raise RuntimeError("La base utilise une version de schéma P3 non prise en charge.")

    expected_prefix = set(range(1, max(applied_versions, default=0) + 1))
    if applied_versions != expected_prefix:
        raise RuntimeError("Les migrations P3 appliquées ne forment pas une suite continue.")

    for migration in _CAPABILITY_SCHEMA_MIGRATIONS:
        if migration.version in applied_versions:
            continue
        if migration.preflight is not None:
            migration.preflight(connection)
        for statement in migration.statements:
            connection.execute(statement)
        connection.execute(
            """
            INSERT INTO capability_schema_migrations (version, name)
            VALUES (?, ?)
            """,
            (migration.version, migration.name),
        )
        applied_versions.add(migration.version)
