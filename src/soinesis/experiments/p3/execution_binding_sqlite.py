"""Persistance SQLite opt-in des liaisons plan/exécution P3 DEV."""

from __future__ import annotations

import sqlite3
from typing import Final

from soinesis.experiments.p3.execution_binding import (
    ExperimentalExecutionPlanBinding,
    ExperimentalExecutionPlanBindingIntegrityError,
)
from soinesis.experiments.p3.plan import ExperimentalReplicationPlanIdentity
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

_TABLE_NAME: Final = "p3_dev_execution_plan_bindings"
_BINDING_COLUMNS: Final = (
    "execution_id",
    "fingerprint_scheme",
    "plan_fingerprint",
)


class SQLiteExperimentalExecutionPlanBindingRepository:
    """Dépôt SQLite append-only, distinct de toute persistance cognitive."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def initialize_schema(self) -> None:
        """Activer explicitement la table privée de liaison P3 DEV."""
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {_TABLE_NAME} (
                    execution_id TEXT PRIMARY KEY,
                    fingerprint_scheme TEXT NOT NULL CHECK (
                        fingerprint_scheme = 'p3-plan-fingerprint-v1'
                    ),
                    plan_fingerprint TEXT NOT NULL CHECK (
                        length(plan_fingerprint) = 64
                        AND plan_fingerprint NOT GLOB '*[^0-9a-f]*'
                    )
                )
                """
            )
            columns = tuple(
                str(row["name"])
                for row in connection.execute(f"PRAGMA table_info({_TABLE_NAME})").fetchall()
            )
            if columns != _BINDING_COLUMNS:
                raise ExperimentalExecutionPlanBindingIntegrityError(
                    "La table de liaisons P3 DEV possède un schéma incompatible."
                )
            connection.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS p3_dev_execution_plan_bindings_no_update
                BEFORE UPDATE ON {_TABLE_NAME}
                BEGIN
                    SELECT RAISE(ABORT, 'modification de liaison interdite');
                END
                """
            )
            connection.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS p3_dev_execution_plan_bindings_no_delete
                BEFORE DELETE ON {_TABLE_NAME}
                BEGIN
                    SELECT RAISE(ABORT, 'suppression de liaison interdite');
                END
                """
            )

    def get(self, *, execution_id: str) -> ExperimentalExecutionPlanBinding | None:
        """Relire une liaison sans création ni mutation."""
        self._validate_execution_id(execution_id)
        with self._database.connect() as connection:
            row = self._select(connection, execution_id=execution_id)
        return None if row is None else self._from_row(row)

    def bind(self, binding: ExperimentalExecutionPlanBinding) -> ExperimentalExecutionPlanBinding:
        """Créer atomiquement la liaison ou reconnaître son retry exact."""
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = self._select(connection, execution_id=binding.execution_id)
            if row is not None:
                existing = self._from_row(row)
                if existing != binding:
                    raise ExperimentalExecutionPlanBindingIntegrityError(
                        "Cette exécution est déjà liée à un autre plan."
                    )
                return existing
            connection.execute(
                f"""
                INSERT INTO {_TABLE_NAME} (
                    execution_id, fingerprint_scheme, plan_fingerprint
                ) VALUES (?, ?, ?)
                """,
                (
                    binding.execution_id,
                    binding.plan_identity.scheme,
                    binding.plan_identity.fingerprint,
                ),
            )
            return binding

    @staticmethod
    def _validate_execution_id(execution_id: str) -> None:
        if type(execution_id) is not str or not execution_id:
            raise ValueError("execution_id doit être une chaîne opaque non vide.")

    @staticmethod
    def _select(connection: sqlite3.Connection, *, execution_id: str) -> sqlite3.Row | None:
        return connection.execute(
            f"SELECT * FROM {_TABLE_NAME} WHERE execution_id = ?",
            (execution_id,),
        ).fetchone()

    @staticmethod
    def _from_row(row: sqlite3.Row) -> ExperimentalExecutionPlanBinding:
        return ExperimentalExecutionPlanBinding(
            execution_id=str(row["execution_id"]),
            plan_identity=ExperimentalReplicationPlanIdentity.model_validate(
                {
                    "scheme": str(row["fingerprint_scheme"]),
                    "fingerprint": str(row["plan_fingerprint"]),
                }
            ),
        )
