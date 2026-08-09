"""Persistance SQLite opt-in des configurations de condition P3 DEV."""

from __future__ import annotations

import sqlite3
from typing import Final

from pydantic import ValidationError

from soinesis.experiments.p3.condition_config import (
    CONDITION_CONFIGURATION_SCHEME,
    DEV_ESTIMATOR_LAMBDAS,
    ExperimentalCondition,
    ExperimentalConditionConfiguration,
    ExperimentalConditionConfigurationIntegrityError,
    ExperimentalExecutionConditionConfiguration,
)
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

_TABLE_NAME: Final = "p3_dev_execution_condition_configuration"
_CONFIGURATION_COLUMNS: Final = (
    "execution_id",
    "config_scheme",
    "condition",
    "estimator_lambda",
)
_CANONICAL_LAMBDAS: Final = {value: format(value, ".2f") for value in DEV_ESTIMATOR_LAMBDAS}
_LAMBDAS_BY_TEXT: Final = {text: value for value, text in _CANONICAL_LAMBDAS.items()}


class SQLiteExperimentalExecutionConditionConfigurationRepository:
    """Dépôt append-only distinct de toute persistance cognitive."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def initialize_schema(self) -> None:
        """Activer explicitement la table de configuration P3 DEV."""
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {_TABLE_NAME} (
                    execution_id TEXT PRIMARY KEY,
                    config_scheme TEXT NOT NULL CHECK (
                        config_scheme = '{CONDITION_CONFIGURATION_SCHEME}'
                    ),
                    condition TEXT NOT NULL CHECK (condition IN ('A', 'B', 'C')),
                    estimator_lambda TEXT,
                    CHECK (
                        (condition = 'A' AND estimator_lambda IS NULL)
                        OR
                        (condition IN ('B', 'C')
                            AND estimator_lambda IS NOT NULL
                            AND estimator_lambda IN (
                                '0.90', '0.92', '0.94', '0.95', '0.96', '0.97'
                            )
                        )
                    )
                )
                """
            )
            columns = tuple(
                str(row["name"])
                for row in connection.execute(f"PRAGMA table_info({_TABLE_NAME})").fetchall()
            )
            if columns != _CONFIGURATION_COLUMNS:
                raise ExperimentalConditionConfigurationIntegrityError(
                    "La table de configuration de condition P3 DEV possède un schéma incompatible."
                )
            connection.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS p3_dev_condition_configuration_no_update
                BEFORE UPDATE ON {_TABLE_NAME}
                BEGIN
                    SELECT RAISE(ABORT, 'modification de configuration interdite');
                END
                """
            )
            connection.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS p3_dev_condition_configuration_no_delete
                BEFORE DELETE ON {_TABLE_NAME}
                BEGIN
                    SELECT RAISE(ABORT, 'suppression de configuration interdite');
                END
                """
            )

    def get(self, *, execution_id: str) -> ExperimentalExecutionConditionConfiguration | None:
        self._validate_execution_id(execution_id)
        with self._database.connect() as connection:
            row = self._select(connection, execution_id=execution_id)
        return None if row is None else self._from_row(row)

    def register(
        self, configuration: ExperimentalExecutionConditionConfiguration
    ) -> ExperimentalExecutionConditionConfiguration:
        """Créer sous BEGIN IMMEDIATE ou reconnaître un retry strictement identique."""
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = self._select(connection, execution_id=configuration.execution_id)
            if row is not None:
                existing = self._from_row(row)
                if existing != configuration:
                    raise ExperimentalConditionConfigurationIntegrityError(
                        "Cette exécution possède déjà une autre configuration de condition."
                    )
                return existing
            candidate = configuration.configuration
            connection.execute(
                f"""
                INSERT INTO {_TABLE_NAME} (
                    execution_id, config_scheme, condition, estimator_lambda
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    configuration.execution_id,
                    candidate.scheme,
                    candidate.condition.value,
                    None
                    if candidate.estimator_lambda is None
                    else _CANONICAL_LAMBDAS[candidate.estimator_lambda],
                ),
            )
            return configuration

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
    def _from_row(row: sqlite3.Row) -> ExperimentalExecutionConditionConfiguration:
        condition_text = str(row["condition"])
        lambda_value = row["estimator_lambda"]
        if lambda_value is None:
            estimator_lambda = None
        else:
            lambda_text = str(lambda_value)
            estimator_lambda = _LAMBDAS_BY_TEXT.get(lambda_text)
            if estimator_lambda is None:
                raise ExperimentalConditionConfigurationIntegrityError(
                    "estimator_lambda persistant n'utilise pas une valeur canonique autorisée."
                )
        try:
            return ExperimentalExecutionConditionConfiguration(
                execution_id=str(row["execution_id"]),
                configuration=ExperimentalConditionConfiguration.model_validate(
                    {
                        "scheme": str(row["config_scheme"]),
                        "condition": ExperimentalCondition(condition_text),
                        "estimator_lambda": estimator_lambda,
                    }
                ),
            )
        except (ValueError, ValidationError) as error:
            raise ExperimentalConditionConfigurationIntegrityError(
                "La configuration de condition persistante est invalide."
            ) from error
