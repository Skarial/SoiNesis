"""Persistance SQLite opt-in de la provenance de génération P3 DEV."""

from __future__ import annotations

import sqlite3
from typing import Final

from soinesis.experiments.p3.plan import ExperimentalReplicationPlanIdentity
from soinesis.experiments.p3.provenance import (
    ExperimentalExecutionGenerationProvenance,
    ExperimentalExecutionGenerationProvenanceIntegrityError,
    ExperimentalPlanGenerationProvenance,
)
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

_TABLE_NAME: Final = "p3_dev_execution_generation_provenance"
_PROVENANCE_COLUMNS: Final = (
    "execution_id",
    "provenance_scheme",
    "fingerprint_scheme",
    "plan_fingerprint",
    "seed_text",
    "generator_version",
    "python_implementation",
    "python_version",
)


class SQLiteExperimentalExecutionGenerationProvenanceRepository:
    """Dépôt append-only séparé de toute persistance cognitive."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def initialize_schema(self) -> None:
        """Activer explicitement la table privée de provenance P3 DEV."""
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {_TABLE_NAME} (
                    execution_id TEXT PRIMARY KEY,
                    provenance_scheme TEXT NOT NULL CHECK (
                        provenance_scheme = 'p3-plan-generation-provenance-v1'
                    ),
                    fingerprint_scheme TEXT NOT NULL CHECK (
                        fingerprint_scheme = 'p3-plan-fingerprint-v1'
                    ),
                    plan_fingerprint TEXT NOT NULL CHECK (
                        length(plan_fingerprint) = 64
                        AND plan_fingerprint NOT GLOB '*[^0-9a-f]*'
                    ),
                    seed_text TEXT NOT NULL CHECK (length(seed_text) > 0),
                    generator_version TEXT NOT NULL,
                    python_implementation TEXT NOT NULL,
                    python_version TEXT NOT NULL
                )
                """
            )
            columns = tuple(
                str(row["name"])
                for row in connection.execute(f"PRAGMA table_info({_TABLE_NAME})").fetchall()
            )
            if columns != _PROVENANCE_COLUMNS:
                raise ExperimentalExecutionGenerationProvenanceIntegrityError(
                    "La table de provenance P3 DEV possède un schéma incompatible."
                )
            connection.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS p3_dev_execution_generation_provenance_no_update
                BEFORE UPDATE ON {_TABLE_NAME}
                BEGIN
                    SELECT RAISE(ABORT, 'modification de provenance interdite');
                END
                """
            )
            connection.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS p3_dev_execution_generation_provenance_no_delete
                BEFORE DELETE ON {_TABLE_NAME}
                BEGIN
                    SELECT RAISE(ABORT, 'suppression de provenance interdite');
                END
                """
            )

    def get(self, *, execution_id: str) -> ExperimentalExecutionGenerationProvenance | None:
        self._validate_execution_id(execution_id)
        with self._database.connect() as connection:
            row = self._select(connection, execution_id=execution_id)
        return None if row is None else self._from_row(row)

    def register(
        self, provenance: ExperimentalExecutionGenerationProvenance
    ) -> ExperimentalExecutionGenerationProvenance:
        """Créer atomiquement la provenance ou reconnaître son retry exact."""
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = self._select(connection, execution_id=provenance.execution_id)
            if row is not None:
                existing = self._from_row(row)
                if existing != provenance:
                    raise ExperimentalExecutionGenerationProvenanceIntegrityError(
                        "Cette exécution possède déjà une autre provenance de génération."
                    )
                return existing
            generation = provenance.generation_provenance
            connection.execute(
                f"""
                INSERT INTO {_TABLE_NAME} (
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
                    provenance.execution_id,
                    generation.scheme,
                    generation.plan_identity.scheme,
                    generation.plan_identity.fingerprint,
                    str(generation.seed),
                    generation.generator_version,
                    generation.python_implementation,
                    generation.python_version,
                ),
            )
            return provenance

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
    def _from_row(row: sqlite3.Row) -> ExperimentalExecutionGenerationProvenance:
        seed_text = str(row["seed_text"])
        try:
            seed = int(seed_text)
        except ValueError as error:
            raise ExperimentalExecutionGenerationProvenanceIntegrityError(
                "Le seed persistant n'est pas un entier décimal."
            ) from error
        if str(seed) != seed_text:
            raise ExperimentalExecutionGenerationProvenanceIntegrityError(
                "Le seed persistant n'utilise pas sa représentation décimale canonique."
            )
        return ExperimentalExecutionGenerationProvenance(
            execution_id=str(row["execution_id"]),
            generation_provenance=ExperimentalPlanGenerationProvenance.model_validate(
                {
                    "scheme": str(row["provenance_scheme"]),
                    "plan_identity": ExperimentalReplicationPlanIdentity.model_validate(
                        {
                            "scheme": str(row["fingerprint_scheme"]),
                            "fingerprint": str(row["plan_fingerprint"]),
                        }
                    ),
                    "seed": seed,
                    "generator_version": str(row["generator_version"]),
                    "python_implementation": str(row["python_implementation"]),
                    "python_version": str(row["python_version"]),
                }
            ),
        )
