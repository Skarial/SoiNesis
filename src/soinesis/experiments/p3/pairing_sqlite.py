"""Persistance SQLite opt-in des groupes appariés P3 DEV."""

from __future__ import annotations

import sqlite3
from decimal import Decimal
from typing import Final

from pydantic import ValidationError

from soinesis.experiments.p3.condition_config import DEV_ESTIMATOR_LAMBDAS
from soinesis.experiments.p3.pairing import (
    ExperimentalPairedConditionGroup,
    ExperimentalPairingIntegrityError,
)
from soinesis.experiments.p3.plan import ExperimentalReplicationPlanIdentity
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

_GROUP_TABLE: Final = "p3_dev_paired_condition_groups"
_MEMBER_TABLE: Final = "p3_dev_paired_condition_group_members"
_GROUP_COLUMNS: Final = (
    "pairing_id",
    "plan_identity_scheme",
    "plan_fingerprint",
    "estimator_lambda",
)
_MEMBER_COLUMNS: Final = ("pairing_id", "condition", "execution_id")
_CANONICAL_LAMBDAS: Final = {value: format(value, ".2f") for value in DEV_ESTIMATOR_LAMBDAS}
_LAMBDAS_BY_TEXT: Final = {text: value for value, text in _CANONICAL_LAMBDAS.items()}


class SQLiteExperimentalPairedConditionGroupRepository:
    """Dépôt atomique normalisé garantissant une seule paire par exécution."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def initialize_schema(self) -> None:
        """Activer explicitement les deux tables append-only du pairing DEV."""
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {_GROUP_TABLE} (
                    pairing_id TEXT PRIMARY KEY,
                    plan_identity_scheme TEXT NOT NULL CHECK (
                        plan_identity_scheme = 'p3-plan-fingerprint-v1'
                    ),
                    plan_fingerprint TEXT NOT NULL CHECK (
                        length(plan_fingerprint) = 64
                        AND plan_fingerprint NOT GLOB '*[^0-9a-f]*'
                    ),
                    estimator_lambda TEXT NOT NULL CHECK (
                        estimator_lambda IN ('0.90', '0.92', '0.94', '0.95', '0.96', '0.97')
                    )
                )
                """
            )
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {_MEMBER_TABLE} (
                    pairing_id TEXT NOT NULL,
                    condition TEXT NOT NULL CHECK (condition IN ('A', 'B', 'C')),
                    execution_id TEXT NOT NULL UNIQUE,
                    PRIMARY KEY (pairing_id, condition),
                    FOREIGN KEY (pairing_id) REFERENCES {_GROUP_TABLE}(pairing_id)
                )
                """
            )
            self._validate_schema(connection)
            for table_name in (_GROUP_TABLE, _MEMBER_TABLE):
                connection.execute(
                    f"""
                    CREATE TRIGGER IF NOT EXISTS {table_name}_no_update
                    BEFORE UPDATE ON {table_name}
                    BEGIN
                        SELECT RAISE(ABORT, 'modification de pairing interdite');
                    END
                    """
                )
                connection.execute(
                    f"""
                    CREATE TRIGGER IF NOT EXISTS {table_name}_no_delete
                    BEFORE DELETE ON {table_name}
                    BEGIN
                        SELECT RAISE(ABORT, 'suppression de pairing interdite');
                    END
                    """
                )
            self._validate_triggers(connection)
            self._validate_persisted_groups(connection)

    def get(self, *, pairing_id: str) -> ExperimentalPairedConditionGroup | None:
        self._validate_pairing_id(pairing_id)
        with self._database.connect() as connection:
            return self._get_with_connection(connection, pairing_id=pairing_id)

    def register(self, group: ExperimentalPairedConditionGroup) -> ExperimentalPairedConditionGroup:
        """Insérer le groupe et ses trois membres sous une transaction immédiate."""
        try:
            with self._database.connect() as connection:
                connection.execute("BEGIN IMMEDIATE")
                existing = self._get_with_connection(
                    connection,
                    pairing_id=group.pairing_id,
                )
                if existing is not None:
                    if existing != group:
                        raise ExperimentalPairingIntegrityError(
                            "Ce pairing_id existe déjà avec un autre triplet ou paramétrage."
                        )
                    return existing
                executions = (group.execution_a, group.execution_b, group.execution_c)
                occupied = connection.execute(
                    f"""
                    SELECT pairing_id, execution_id FROM {_MEMBER_TABLE}
                    WHERE execution_id IN (?, ?, ?)
                    """,
                    executions,
                ).fetchall()
                if occupied:
                    raise ExperimentalPairingIntegrityError(
                        "Une exécution appartient déjà à un autre groupe apparié."
                    )
                connection.execute(
                    f"""
                    INSERT INTO {_GROUP_TABLE} (
                        pairing_id, plan_identity_scheme, plan_fingerprint, estimator_lambda
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        group.pairing_id,
                        group.plan_identity.scheme,
                        group.plan_identity.fingerprint,
                        _CANONICAL_LAMBDAS[group.estimator_lambda],
                    ),
                )
                for condition, execution_id in zip("ABC", executions, strict=True):
                    connection.execute(
                        f"""
                        INSERT INTO {_MEMBER_TABLE} (pairing_id, condition, execution_id)
                        VALUES (?, ?, ?)
                        """,
                        (group.pairing_id, condition, execution_id),
                    )
                return group
        except sqlite3.IntegrityError as error:
            raise ExperimentalPairingIntegrityError(
                "L'écriture atomique du groupe apparié a été refusée."
            ) from error

    @staticmethod
    def _validate_pairing_id(pairing_id: str) -> None:
        if type(pairing_id) is not str or not pairing_id:
            raise ValueError("pairing_id doit être une chaîne opaque non vide.")

    @staticmethod
    def _validate_schema(connection: sqlite3.Connection) -> None:
        group_info = connection.execute(f"PRAGMA table_info({_GROUP_TABLE})").fetchall()
        member_info = connection.execute(f"PRAGMA table_info({_MEMBER_TABLE})").fetchall()
        group_columns = tuple(str(row["name"]) for row in group_info)
        member_columns = tuple(str(row["name"]) for row in member_info)
        group_primary_key = tuple(
            str(row["name"])
            for row in sorted(group_info, key=lambda row: int(row["pk"]))
            if int(row["pk"]) > 0
        )
        member_primary_key = tuple(
            str(row["name"])
            for row in sorted(member_info, key=lambda row: int(row["pk"]))
            if int(row["pk"]) > 0
        )
        if (
            group_columns != _GROUP_COLUMNS
            or member_columns != _MEMBER_COLUMNS
            or group_primary_key != ("pairing_id",)
            or member_primary_key != ("pairing_id", "condition")
        ):
            raise ExperimentalPairingIntegrityError(
                "Le schéma SQLite du pairing P3 DEV est incompatible."
            )

        unique_indexes = connection.execute(f"PRAGMA index_list({_MEMBER_TABLE})").fetchall()
        has_execution_unique = any(
            int(index["unique"]) == 1
            and tuple(
                str(column["name"])
                for column in connection.execute(f"PRAGMA index_info({index['name']!s})").fetchall()
            )
            == ("execution_id",)
            for index in unique_indexes
        )
        foreign_keys = connection.execute(f"PRAGMA foreign_key_list({_MEMBER_TABLE})").fetchall()
        has_group_foreign_key = any(
            str(foreign_key["table"]) == _GROUP_TABLE
            and str(foreign_key["from"]) == "pairing_id"
            and str(foreign_key["to"]) == "pairing_id"
            for foreign_key in foreign_keys
        )
        schema_rows = connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE type = 'table' AND name IN (?, ?)",
            (_GROUP_TABLE, _MEMBER_TABLE),
        ).fetchall()
        schema_sql = {
            str(row["name"]): " ".join(str(row["sql"]).split()).lower() for row in schema_rows
        }
        group_sql = schema_sql.get(_GROUP_TABLE, "")
        member_sql = schema_sql.get(_MEMBER_TABLE, "")
        has_required_checks = (
            all(
                fragment in group_sql
                for fragment in (
                    "plan_identity_scheme = 'p3-plan-fingerprint-v1'",
                    "length(plan_fingerprint) = 64",
                    "estimator_lambda in ('0.90', '0.92', '0.94', '0.95', '0.96', '0.97')",
                )
            )
            and "condition in ('a', 'b', 'c')" in member_sql
        )
        if not has_execution_unique or not has_group_foreign_key or not has_required_checks:
            raise ExperimentalPairingIntegrityError(
                "Les contraintes SQLite du pairing P3 DEV sont incompatibles."
            )

    @staticmethod
    def _validate_triggers(connection: sqlite3.Connection) -> None:
        for table_name in (_GROUP_TABLE, _MEMBER_TABLE):
            for operation in ("update", "delete"):
                trigger_name = f"{table_name}_no_{operation}"
                row = connection.execute(
                    "SELECT tbl_name, sql FROM sqlite_master WHERE type = 'trigger' AND name = ?",
                    (trigger_name,),
                ).fetchone()
                if row is None:
                    raise ExperimentalPairingIntegrityError(
                        "Les triggers append-only du pairing P3 DEV sont incomplets."
                    )
                trigger_sql = " ".join(str(row["sql"]).split()).lower()
                if (
                    str(row["tbl_name"]) != table_name
                    or f"before {operation} on {table_name}" not in trigger_sql
                    or "raise(abort" not in trigger_sql
                ):
                    raise ExperimentalPairingIntegrityError(
                        "Un trigger append-only du pairing P3 DEV est incompatible."
                    )

    @staticmethod
    def _validate_persisted_groups(connection: sqlite3.Connection) -> None:
        orphan = connection.execute(
            f"""
            SELECT 1
            FROM {_MEMBER_TABLE} AS member
            LEFT JOIN {_GROUP_TABLE} AS pairing
                ON pairing.pairing_id = member.pairing_id
            WHERE pairing.pairing_id IS NULL
            LIMIT 1
            """
        ).fetchone()
        incomplete = connection.execute(
            f"""
            SELECT 1
            FROM {_GROUP_TABLE} AS pairing
            LEFT JOIN {_MEMBER_TABLE} AS member
                ON member.pairing_id = pairing.pairing_id
            GROUP BY pairing.pairing_id
            HAVING COUNT(member.execution_id) != 3
                OR COUNT(DISTINCT member.condition) != 3
                OR SUM(member.condition = 'A') != 1
                OR SUM(member.condition = 'B') != 1
                OR SUM(member.condition = 'C') != 1
            LIMIT 1
            """
        ).fetchone()
        if orphan is not None or incomplete is not None:
            raise ExperimentalPairingIntegrityError(
                "Les données historiques du pairing P3 DEV sont incomplètes ou orphelines."
            )

    @staticmethod
    def _get_with_connection(
        connection: sqlite3.Connection,
        *,
        pairing_id: str,
    ) -> ExperimentalPairedConditionGroup | None:
        group_row = connection.execute(
            f"SELECT * FROM {_GROUP_TABLE} WHERE pairing_id = ?",
            (pairing_id,),
        ).fetchone()
        member_rows = connection.execute(
            f"""
            SELECT * FROM {_MEMBER_TABLE}
            WHERE pairing_id = ?
            ORDER BY condition ASC
            """,
            (pairing_id,),
        ).fetchall()
        if group_row is None:
            if member_rows:
                raise ExperimentalPairingIntegrityError(
                    "Des membres orphelins existent sans groupe apparié."
                )
            return None
        if len(member_rows) != 3:
            raise ExperimentalPairingIntegrityError(
                "Un groupe persistant doit posséder exactement trois membres A/B/C."
            )
        conditions = tuple(str(row["condition"]) for row in member_rows)
        executions = tuple(str(row["execution_id"]) for row in member_rows)
        if conditions != ("A", "B", "C") or len(set(executions)) != 3:
            raise ExperimentalPairingIntegrityError(
                "Les membres persistants ne forment pas exactement A/B/C."
            )
        lambda_text = str(group_row["estimator_lambda"])
        estimator_lambda = _LAMBDAS_BY_TEXT.get(lambda_text)
        if estimator_lambda is None:
            raise ExperimentalPairingIntegrityError(
                "Le lambda persistant n'utilise pas une représentation canonique."
            )
        try:
            return ExperimentalPairedConditionGroup(
                pairing_id=str(group_row["pairing_id"]),
                execution_a=executions[0],
                execution_b=executions[1],
                execution_c=executions[2],
                plan_identity=ExperimentalReplicationPlanIdentity.model_validate(
                    {
                        "scheme": str(group_row["plan_identity_scheme"]),
                        "fingerprint": str(group_row["plan_fingerprint"]),
                    }
                ),
                estimator_lambda=Decimal(estimator_lambda),
            )
        except (TypeError, ValueError, ValidationError) as error:
            raise ExperimentalPairingIntegrityError(
                "Le groupe apparié persistant est invalide."
            ) from error
