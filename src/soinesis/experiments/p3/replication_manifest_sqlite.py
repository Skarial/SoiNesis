"""Persistance SQLite opt-in du manifeste public P3 DEV."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Final

from soinesis.experiments.p3.replication_manifest import (
    ExperimentalReplicationCycleContext,
    ExperimentalReplicationExecutionManifest,
    ExperimentalReplicationManifestIntegrityError,
)
from soinesis.experiments.p3.runner import ExperimentalCycleStartContext
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

_TABLE_NAME: Final = "p3_dev_replication_cycle_manifest"
_MANIFEST_COLUMNS: Final = (
    "execution_id",
    "sequence_index",
    "performance_id",
    "agent_id",
    "trial_id",
    "cycle_id",
    "observed_at",
)
_TOTAL_CYCLES: Final = 180


class SQLiteExperimentalReplicationManifestRepository:
    """Dépôt append-only qui ne rend jamais visible un manifeste partiel."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def initialize_schema(self) -> None:
        """Activer explicitement la table du manifeste P3 DEV."""
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {_TABLE_NAME} (
                    execution_id TEXT NOT NULL,
                    sequence_index INTEGER NOT NULL CHECK (
                        typeof(sequence_index) = 'integer'
                        AND sequence_index >= 0
                        AND sequence_index < {_TOTAL_CYCLES}
                    ),
                    performance_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    trial_id TEXT NOT NULL,
                    cycle_id TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    PRIMARY KEY (execution_id, sequence_index),
                    UNIQUE (execution_id, performance_id)
                )
                """
            )
            columns = tuple(
                str(row["name"])
                for row in connection.execute(f"PRAGMA table_info({_TABLE_NAME})").fetchall()
            )
            if columns != _MANIFEST_COLUMNS:
                raise ExperimentalReplicationManifestIntegrityError(
                    "La table de manifeste P3 DEV possède un schéma incompatible."
                )
            connection.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS p3_dev_replication_cycle_manifest_no_update
                BEFORE UPDATE ON {_TABLE_NAME}
                BEGIN
                    SELECT RAISE(ABORT, 'modification de manifeste interdite');
                END
                """
            )
            connection.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS p3_dev_replication_cycle_manifest_no_delete
                BEFORE DELETE ON {_TABLE_NAME}
                BEGIN
                    SELECT RAISE(ABORT, 'suppression de manifeste interdite');
                END
                """
            )

    def get(self, *, execution_id: str) -> ExperimentalReplicationExecutionManifest | None:
        self._validate_execution_id(execution_id)
        with self._database.connect() as connection:
            rows = self._select_all(connection, execution_id=execution_id)
        if not rows:
            return None
        return self._from_rows(execution_id=execution_id, rows=rows)

    def register(
        self, manifest: ExperimentalReplicationExecutionManifest
    ) -> ExperimentalReplicationExecutionManifest:
        """Insérer les 180 contextes dans une transaction indivisible."""
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            rows = self._select_all(connection, execution_id=manifest.execution_id)
            if rows:
                existing = self._from_rows(execution_id=manifest.execution_id, rows=rows)
                if existing != manifest:
                    raise ExperimentalReplicationManifestIntegrityError(
                        "Cette exécution possède déjà un autre manifeste."
                    )
                return existing
            connection.executemany(
                f"""
                INSERT INTO {_TABLE_NAME} (
                    execution_id,
                    sequence_index,
                    performance_id,
                    agent_id,
                    trial_id,
                    cycle_id,
                    observed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    (
                        manifest.execution_id,
                        context.sequence_index,
                        context.start_context.performance_id,
                        context.start_context.agent_id,
                        context.start_context.trial_id,
                        context.start_context.cycle_id,
                        context.start_context.observed_at.isoformat(),
                    )
                    for context in manifest.cycle_contexts
                ),
            )
            return manifest

    @staticmethod
    def _validate_execution_id(execution_id: str) -> None:
        if type(execution_id) is not str or not execution_id:
            raise ValueError("execution_id doit être une chaîne opaque non vide.")

    @staticmethod
    def _select_all(connection: sqlite3.Connection, *, execution_id: str) -> list[sqlite3.Row]:
        return connection.execute(
            f"""
            SELECT * FROM {_TABLE_NAME}
            WHERE execution_id = ?
            ORDER BY sequence_index ASC
            """,
            (execution_id,),
        ).fetchall()

    @staticmethod
    def _from_rows(
        *,
        execution_id: str,
        rows: list[sqlite3.Row],
    ) -> ExperimentalReplicationExecutionManifest:
        if len(rows) != _TOTAL_CYCLES:
            raise ExperimentalReplicationManifestIntegrityError(
                "Un manifeste persistant doit posséder exactement 180 contextes."
            )
        try:
            cycle_contexts = tuple(
                ExperimentalReplicationCycleContext(
                    sequence_index=int(row["sequence_index"]),
                    start_context=ExperimentalCycleStartContext(
                        performance_id=str(row["performance_id"]),
                        agent_id=str(row["agent_id"]),
                        trial_id=str(row["trial_id"]),
                        cycle_id=str(row["cycle_id"]),
                        observed_at=datetime.fromisoformat(str(row["observed_at"])),
                    ),
                )
                for row in rows
            )
            return ExperimentalReplicationExecutionManifest(
                execution_id=execution_id,
                cycle_contexts=cycle_contexts,
            )
        except (TypeError, ValueError) as error:
            raise ExperimentalReplicationManifestIntegrityError(
                "Le manifeste persistant contient un contexte invalide."
            ) from error
