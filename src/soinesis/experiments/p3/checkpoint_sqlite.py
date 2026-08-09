"""Persistance SQLite opt-in des checkpoints d'exécution P3 DEV."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Final

from soinesis.domain.capabilities import (
    CapabilityAction,
    CapabilityDecision,
    CapabilityEstimate,
    EstimateSource,
)
from soinesis.experiments.p3.checkpoint import (
    ExperimentalCycleCheckpoint,
    ExperimentalCycleCheckpointIntegrityError,
    ExperimentalCycleCheckpointNotFoundError,
    ExperimentalCycleCheckpointOrderError,
    ExperimentalCycleCheckpointStatus,
)
from soinesis.infrastructure.sqlite.database import SQLiteDatabase

_TABLE_NAME: Final = "p3_dev_cycle_checkpoints"
_CHECKPOINT_COLUMNS: Final = (
    "execution_id",
    "sequence_index",
    "performance_id",
    "agent_id",
    "trial_id",
    "cycle_id",
    "capability_key",
    "observed_at",
    "decision_agent_id",
    "decision_capability_key",
    "decision_estimated_success",
    "decision_estimate_source",
    "decision_action",
    "decision_direct_utility",
    "decision_verify_utility",
    "decision_help_utility",
    "checkpoint_status",
)


class SQLiteExperimentalCycleCheckpointRepository:
    """Dépôt SQLite atomique, séparé des dépôts cognitifs."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def initialize_schema(self) -> None:
        """Activer explicitement la table expérimentale et ses garde-fous."""
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {_TABLE_NAME} (
                    execution_id TEXT NOT NULL,
                    sequence_index INTEGER NOT NULL CHECK (sequence_index >= 0),
                    performance_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    trial_id TEXT NOT NULL,
                    cycle_id TEXT NOT NULL,
                    capability_key TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    decision_agent_id TEXT NOT NULL,
                    decision_capability_key TEXT NOT NULL,
                    decision_estimated_success REAL NOT NULL CHECK (
                        decision_estimated_success BETWEEN 0.0 AND 1.0
                    ),
                    decision_estimate_source TEXT NOT NULL,
                    decision_action TEXT NOT NULL,
                    decision_direct_utility REAL NOT NULL CHECK (
                        decision_direct_utility BETWEEN -1.0e308 AND 1.0e308
                    ),
                    decision_verify_utility REAL NOT NULL CHECK (
                        decision_verify_utility BETWEEN -1.0e308 AND 1.0e308
                    ),
                    decision_help_utility REAL NOT NULL CHECK (
                        decision_help_utility BETWEEN -1.0e308 AND 1.0e308
                    ),
                    checkpoint_status TEXT NOT NULL CHECK (
                        checkpoint_status IN ('STARTED', 'COMPLETED')
                    ),
                    PRIMARY KEY (execution_id, sequence_index),
                    UNIQUE (execution_id, performance_id)
                )
                """
            )
            columns = tuple(
                str(row["name"])
                for row in connection.execute(f"PRAGMA table_info({_TABLE_NAME})").fetchall()
            )
            if columns != _CHECKPOINT_COLUMNS:
                raise ExperimentalCycleCheckpointIntegrityError(
                    "La table de checkpoints P3 DEV possède un schéma incompatible."
                )
            connection.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS p3_dev_cycle_checkpoints_start_only
                BEFORE INSERT ON {_TABLE_NAME}
                WHEN NEW.checkpoint_status != 'STARTED'
                BEGIN
                    SELECT RAISE(ABORT, 'un checkpoint doit être créé STARTED');
                END
                """
            )
            connection.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS p3_dev_cycle_checkpoints_complete_only
                BEFORE UPDATE ON {_TABLE_NAME}
                WHEN NOT (
                    OLD.checkpoint_status = 'STARTED'
                    AND NEW.checkpoint_status = 'COMPLETED'
                    AND NEW.execution_id IS OLD.execution_id
                    AND NEW.sequence_index IS OLD.sequence_index
                    AND NEW.performance_id IS OLD.performance_id
                    AND NEW.agent_id IS OLD.agent_id
                    AND NEW.trial_id IS OLD.trial_id
                    AND NEW.cycle_id IS OLD.cycle_id
                    AND NEW.capability_key IS OLD.capability_key
                    AND NEW.observed_at IS OLD.observed_at
                    AND NEW.decision_agent_id IS OLD.decision_agent_id
                    AND NEW.decision_capability_key IS OLD.decision_capability_key
                    AND NEW.decision_estimated_success IS OLD.decision_estimated_success
                    AND NEW.decision_estimate_source IS OLD.decision_estimate_source
                    AND NEW.decision_action IS OLD.decision_action
                    AND NEW.decision_direct_utility IS OLD.decision_direct_utility
                    AND NEW.decision_verify_utility IS OLD.decision_verify_utility
                    AND NEW.decision_help_utility IS OLD.decision_help_utility
                )
                BEGIN
                    SELECT RAISE(ABORT, 'transition de checkpoint interdite');
                END
                """
            )
            connection.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS p3_dev_cycle_checkpoints_no_delete
                BEFORE DELETE ON {_TABLE_NAME}
                BEGIN
                    SELECT RAISE(ABORT, 'suppression de checkpoint interdite');
                END
                """
            )

    def get(self, *, execution_id: str, sequence_index: int) -> ExperimentalCycleCheckpoint | None:
        """Relire un checkpoint sans modifier son état."""
        self._validate_key(execution_id=execution_id, sequence_index=sequence_index)
        with self._database.connect() as connection:
            row = self._select_exact(
                connection,
                execution_id=execution_id,
                sequence_index=sequence_index,
            )
        return None if row is None else self._from_row(row)

    def begin(self, checkpoint: ExperimentalCycleCheckpoint) -> ExperimentalCycleCheckpoint:
        """Créer STARTED dans l'ordre ou relire une tentative identique."""
        if checkpoint.status is not ExperimentalCycleCheckpointStatus.STARTED:
            raise ExperimentalCycleCheckpointIntegrityError(
                "Un nouveau checkpoint doit être dans l'état STARTED."
            )
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            exact_row = self._select_exact(
                connection,
                execution_id=checkpoint.execution_id,
                sequence_index=checkpoint.sequence_index,
            )
            if exact_row is not None:
                existing = self._from_row(exact_row)
                self._require_identical_payload(existing=existing, requested=checkpoint)
                return existing

            latest_row = connection.execute(
                f"""
                SELECT * FROM {_TABLE_NAME}
                WHERE execution_id = ?
                ORDER BY sequence_index DESC
                LIMIT 1
                """,
                (checkpoint.execution_id,),
            ).fetchone()
            if latest_row is None:
                if checkpoint.sequence_index != 0:
                    raise ExperimentalCycleCheckpointOrderError(
                        "Le premier checkpoint d'une exécution doit avoir sequence_index=0."
                    )
            else:
                latest = self._from_row(latest_row)
                if latest.status is not ExperimentalCycleCheckpointStatus.COMPLETED:
                    raise ExperimentalCycleCheckpointOrderError(
                        "Le checkpoint précédent doit être COMPLETED avant le suivant."
                    )
                if checkpoint.sequence_index != latest.sequence_index + 1:
                    raise ExperimentalCycleCheckpointOrderError(
                        "Les checkpoints d'une exécution doivent être contigus."
                    )

            self._insert(connection, checkpoint)
            return checkpoint

    def complete(self, *, execution_id: str, sequence_index: int) -> ExperimentalCycleCheckpoint:
        """Appliquer uniquement la transition idempotente STARTED vers COMPLETED."""
        self._validate_key(execution_id=execution_id, sequence_index=sequence_index)
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = self._select_exact(
                connection,
                execution_id=execution_id,
                sequence_index=sequence_index,
            )
            if row is None:
                raise ExperimentalCycleCheckpointNotFoundError(
                    "Aucun checkpoint ne correspond à cette exécution et cette position."
                )
            checkpoint = self._from_row(row)
            if checkpoint.status is ExperimentalCycleCheckpointStatus.COMPLETED:
                return checkpoint
            cursor = connection.execute(
                f"""
                UPDATE {_TABLE_NAME}
                SET checkpoint_status = 'COMPLETED'
                WHERE execution_id = ?
                  AND sequence_index = ?
                  AND checkpoint_status = 'STARTED'
                """,
                (execution_id, sequence_index),
            )
            if cursor.rowcount != 1:
                raise ExperimentalCycleCheckpointIntegrityError(
                    "La transition atomique du checkpoint a échoué."
                )
            return checkpoint.model_copy(
                update={"status": ExperimentalCycleCheckpointStatus.COMPLETED}
            )

    @staticmethod
    def _validate_key(*, execution_id: str, sequence_index: int) -> None:
        if type(execution_id) is not str or not execution_id:
            raise ValueError("execution_id doit être une chaîne opaque non vide.")
        if type(sequence_index) is not int or sequence_index < 0:
            raise ValueError("sequence_index doit être un entier positif ou nul.")

    @staticmethod
    def _select_exact(
        connection: sqlite3.Connection,
        *,
        execution_id: str,
        sequence_index: int,
    ) -> sqlite3.Row | None:
        return connection.execute(
            f"""
            SELECT * FROM {_TABLE_NAME}
            WHERE execution_id = ? AND sequence_index = ?
            """,
            (execution_id, sequence_index),
        ).fetchone()

    @staticmethod
    def _insert(
        connection: sqlite3.Connection,
        checkpoint: ExperimentalCycleCheckpoint,
    ) -> None:
        decision = checkpoint.decision
        connection.execute(
            f"""
            INSERT INTO {_TABLE_NAME} (
                execution_id, sequence_index, performance_id, agent_id,
                trial_id, cycle_id, capability_key, observed_at, decision_agent_id,
                decision_capability_key, decision_estimated_success,
                decision_estimate_source, decision_action,
                decision_direct_utility, decision_verify_utility,
                decision_help_utility, checkpoint_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                checkpoint.execution_id,
                checkpoint.sequence_index,
                checkpoint.performance_id,
                checkpoint.agent_id,
                checkpoint.trial_id,
                checkpoint.cycle_id,
                checkpoint.capability_key,
                checkpoint.observed_at.isoformat(),
                decision.estimate.agent_id,
                decision.estimate.capability_key,
                decision.estimate.estimated_success,
                decision.estimate.source.value,
                decision.action.value,
                decision.direct_utility,
                decision.verify_utility,
                decision.help_utility,
                checkpoint.status.value,
            ),
        )

    @staticmethod
    def _require_identical_payload(
        *,
        existing: ExperimentalCycleCheckpoint,
        requested: ExperimentalCycleCheckpoint,
    ) -> None:
        comparable_existing = existing.model_copy(
            update={"status": ExperimentalCycleCheckpointStatus.STARTED}
        )
        if comparable_existing != requested:
            raise ExperimentalCycleCheckpointIntegrityError(
                "Ce cycle existe déjà avec un contexte ou une décision différents."
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> ExperimentalCycleCheckpoint:
        decision = CapabilityDecision(
            estimate=CapabilityEstimate(
                agent_id=str(row["decision_agent_id"]),
                capability_key=str(row["decision_capability_key"]),
                estimated_success=float(row["decision_estimated_success"]),
                source=EstimateSource(str(row["decision_estimate_source"])),
            ),
            action=CapabilityAction(str(row["decision_action"])),
            direct_utility=float(row["decision_direct_utility"]),
            verify_utility=float(row["decision_verify_utility"]),
            help_utility=float(row["decision_help_utility"]),
        )
        return ExperimentalCycleCheckpoint(
            execution_id=str(row["execution_id"]),
            sequence_index=int(row["sequence_index"]),
            performance_id=str(row["performance_id"]),
            agent_id=str(row["agent_id"]),
            trial_id=str(row["trial_id"]),
            cycle_id=str(row["cycle_id"]),
            capability_key=str(row["capability_key"]),
            observed_at=datetime.fromisoformat(str(row["observed_at"])),
            decision=decision,
            status=ExperimentalCycleCheckpointStatus(str(row["checkpoint_status"])),
        )
