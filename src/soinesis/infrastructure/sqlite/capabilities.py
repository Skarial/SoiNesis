"""Adapters SQLite transactionnels pour les contrats de capacités."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Self

from soinesis.domain.capabilities import (
    CapabilityHistoryBoundary,
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    MetacognitiveCapabilityState,
    SelfAttributeType,
    SelfModelVersion,
    VersionedMetacognitiveCapabilityState,
)
from soinesis.domain.models import SourceType
from soinesis.infrastructure.sqlite.database import SQLiteDatabase, SQLiteUnitOfWork


class MetacognitiveStateConflictError(RuntimeError):
    """Signaler un conflit de création ou de version optimiste."""


class SQLiteCapabilityPerformanceRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, observation: CapabilityPerformanceObservation) -> None:
        self._connection.execute(
            """
            INSERT INTO capability_performances (
                id, agent_id, trial_id, cycle_id, sequence_index,
                capability_key, intrinsic_success, observed_at, source_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                observation.id,
                observation.agent_id,
                observation.trial_id,
                observation.cycle_id,
                observation.sequence_index,
                observation.capability_key,
                int(observation.intrinsic_success),
                observation.observed_at.isoformat(),
                observation.source_type.value,
            ),
        )

    def get(self, observation_id: str) -> CapabilityPerformanceObservation | None:
        row = self._connection.execute(
            """
            SELECT id, agent_id, trial_id, cycle_id, sequence_index,
                   capability_key, intrinsic_success, observed_at, source_type
            FROM capability_performances
            WHERE id = ?
            """,
            (observation_id,),
        ).fetchone()
        return None if row is None else _capability_performance_from_row(row)

    def list_before(
        self,
        *,
        boundary: CapabilityHistoryBoundary,
    ) -> list[CapabilityPerformanceObservation]:
        rows = self._connection.execute(
            """
            SELECT id, agent_id, trial_id, cycle_id, sequence_index,
                   capability_key, intrinsic_success, observed_at, source_type
            FROM capability_performances
            WHERE agent_id = ?
              AND capability_key = ?
              AND sequence_index < ?
            ORDER BY sequence_index ASC, observed_at ASC, id ASC
            """,
            (
                boundary.agent_id,
                boundary.capability_key,
                boundary.sequence_index,
            ),
        ).fetchall()
        return [_capability_performance_from_row(row) for row in rows]


class SQLiteMetacognitiveStateRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_current(
        self,
        *,
        agent_id: str,
        capability_key: str,
    ) -> VersionedMetacognitiveCapabilityState | None:
        row = self._connection.execute(
            """
            SELECT agent_id, capability_key, version, alpha, beta, decay_lambda,
                   last_processed_performance_id, last_processed_sequence_index
            FROM metacognitive_states
            WHERE agent_id = ? AND capability_key = ?
            """,
            (agent_id, capability_key),
        ).fetchone()
        return None if row is None else _metacognitive_state_from_row(row)

    def replace_current(
        self,
        *,
        state: VersionedMetacognitiveCapabilityState,
        expected_version: int | None,
    ) -> None:
        if expected_version is None:
            self._create_initial(state)
            return
        if expected_version < 1:
            raise ValueError("La version métacognitive attendue doit être positive.")
        if state.version != expected_version + 1:
            raise ValueError("La nouvelle version métacognitive doit suivre la version attendue.")

        cursor = self._connection.execute(
            """
            UPDATE metacognitive_states
            SET version = ?, alpha = ?, beta = ?, decay_lambda = ?,
                last_processed_performance_id = ?,
                last_processed_sequence_index = ?
            WHERE agent_id = ?
              AND capability_key = ?
              AND version = ?
            """,
            (
                state.version,
                state.state.alpha,
                state.state.beta,
                state.state.lambda_,
                state.last_processed_performance_id,
                state.last_processed_sequence_index,
                state.agent_id,
                state.capability_key,
                expected_version,
            ),
        )
        if cursor.rowcount != 1:
            raise MetacognitiveStateConflictError(
                "L'état métacognitif courant ne correspond pas à la version attendue."
            )

    def _create_initial(self, state: VersionedMetacognitiveCapabilityState) -> None:
        if state.version != 1:
            raise ValueError("Un état métacognitif initial doit utiliser la version 1.")
        try:
            self._connection.execute(
                """
                INSERT INTO metacognitive_states (
                    agent_id, capability_key, version, alpha, beta, decay_lambda,
                    last_processed_performance_id, last_processed_sequence_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.agent_id,
                    state.capability_key,
                    state.version,
                    state.state.alpha,
                    state.state.beta,
                    state.state.lambda_,
                    state.last_processed_performance_id,
                    state.last_processed_sequence_index,
                ),
            )
        except sqlite3.IntegrityError as error:
            raise MetacognitiveStateConflictError(
                "Un état métacognitif courant existe déjà pour cet agent et cette capacité."
            ) from error


class SQLiteSelfModelVersionRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, version: SelfModelVersion) -> None:
        current = self.get_current(agent_id=version.agent_id)
        if current is None:
            if version.version != 1 or version.previous_version_id is not None:
                raise ValueError("La première version du SelfModel doit être la version 1.")
        elif version.version != current.version + 1 or version.previous_version_id != current.id:
            raise ValueError(
                "La version du SelfModel doit prolonger exactement la version courante."
            )

        self._connection.execute(
            """
            INSERT INTO self_model_versions (
                id, agent_id, version, previous_version_id, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                version.id,
                version.agent_id,
                version.version,
                version.previous_version_id,
                version.created_at.isoformat(),
            ),
        )

    def get_current(self, *, agent_id: str) -> SelfModelVersion | None:
        row = self._connection.execute(
            """
            SELECT id, agent_id, version, previous_version_id, created_at
            FROM self_model_versions
            WHERE agent_id = ?
            ORDER BY version DESC, id ASC
            LIMIT 1
            """,
            (agent_id,),
        ).fetchone()
        return None if row is None else _self_model_version_from_row(row)

    def list_versions(self, *, agent_id: str) -> list[SelfModelVersion]:
        rows = self._connection.execute(
            """
            SELECT id, agent_id, version, previous_version_id, created_at
            FROM self_model_versions
            WHERE agent_id = ?
            ORDER BY version ASC, id ASC
            """,
            (agent_id,),
        ).fetchall()
        return [_self_model_version_from_row(row) for row in rows]


class SQLiteCapabilitySelfAttributeRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, attribute: CapabilitySelfAttribute) -> None:
        model_owner = self._connection.execute(
            """
            SELECT agent_id FROM self_model_versions WHERE id = ?
            """,
            (attribute.self_model_version_id,),
        ).fetchone()
        if model_owner is None or str(model_owner["agent_id"]) != attribute.agent_id:
            raise ValueError("Le SelfAttribute doit référencer un SelfModel du même agent.")

        current = self.get_current(
            agent_id=attribute.agent_id,
            capability_key=attribute.capability_key,
        )
        if current is None:
            if attribute.attribute_version != 1 or attribute.previous_attribute_id is not None:
                raise ValueError("Le premier SelfAttribute doit utiliser la version 1.")
        elif (
            attribute.attribute_version != current.attribute_version + 1
            or attribute.previous_attribute_id != current.id
        ):
            raise ValueError("Le SelfAttribute doit prolonger exactement sa version courante.")

        self._connection.execute(
            """
            INSERT INTO capability_self_attributes (
                id, agent_id, attribute_type, capability_key, estimated_success,
                self_model_version_id, attribute_version, previous_attribute_id,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attribute.id,
                attribute.agent_id,
                attribute.attribute_type.value,
                attribute.capability_key,
                attribute.estimated_success,
                attribute.self_model_version_id,
                attribute.attribute_version,
                attribute.previous_attribute_id,
                attribute.created_at.isoformat(),
            ),
        )

    def get_current(
        self,
        *,
        agent_id: str,
        capability_key: str,
    ) -> CapabilitySelfAttribute | None:
        row = self._connection.execute(
            """
            SELECT id, agent_id, attribute_type, capability_key, estimated_success,
                   self_model_version_id, attribute_version, previous_attribute_id,
                   created_at
            FROM capability_self_attributes
            WHERE agent_id = ? AND capability_key = ?
            ORDER BY attribute_version DESC, id ASC
            LIMIT 1
            """,
            (agent_id, capability_key),
        ).fetchone()
        return None if row is None else _capability_self_attribute_from_row(row)

    def list_versions(
        self,
        *,
        agent_id: str,
        capability_key: str,
    ) -> list[CapabilitySelfAttribute]:
        rows = self._connection.execute(
            """
            SELECT id, agent_id, attribute_type, capability_key, estimated_success,
                   self_model_version_id, attribute_version, previous_attribute_id,
                   created_at
            FROM capability_self_attributes
            WHERE agent_id = ? AND capability_key = ?
            ORDER BY attribute_version ASC, id ASC
            """,
            (agent_id, capability_key),
        ).fetchall()
        return [_capability_self_attribute_from_row(row) for row in rows]


class SQLiteCapabilityUnitOfWork(SQLiteUnitOfWork):
    """UoW SQLite additif partageant une connexion entre cœur et capacités."""

    capability_performances: SQLiteCapabilityPerformanceRepository
    metacognitive_states: SQLiteMetacognitiveStateRepository
    self_model_versions: SQLiteSelfModelVersionRepository
    capability_self_attributes: SQLiteCapabilitySelfAttributeRepository

    def __enter__(self) -> Self:
        super().__enter__()
        connection = self._require_connection()
        self.capability_performances = SQLiteCapabilityPerformanceRepository(connection)
        self.metacognitive_states = SQLiteMetacognitiveStateRepository(connection)
        self.self_model_versions = SQLiteSelfModelVersionRepository(connection)
        self.capability_self_attributes = SQLiteCapabilitySelfAttributeRepository(connection)
        return self


class SQLiteCapabilityUnitOfWorkFactory:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def __call__(self) -> SQLiteCapabilityUnitOfWork:
        return SQLiteCapabilityUnitOfWork(self._database)


def _capability_performance_from_row(row: sqlite3.Row) -> CapabilityPerformanceObservation:
    return CapabilityPerformanceObservation(
        id=str(row["id"]),
        agent_id=str(row["agent_id"]),
        trial_id=str(row["trial_id"]),
        cycle_id=str(row["cycle_id"]),
        sequence_index=int(row["sequence_index"]),
        capability_key=str(row["capability_key"]),
        intrinsic_success=bool(row["intrinsic_success"]),
        observed_at=datetime.fromisoformat(str(row["observed_at"])),
        source_type=SourceType(str(row["source_type"])),
    )


def _metacognitive_state_from_row(row: sqlite3.Row) -> VersionedMetacognitiveCapabilityState:
    last_processed_performance_id = row["last_processed_performance_id"]
    last_processed_sequence_index = row["last_processed_sequence_index"]
    return VersionedMetacognitiveCapabilityState(
        agent_id=str(row["agent_id"]),
        capability_key=str(row["capability_key"]),
        version=int(row["version"]),
        state=MetacognitiveCapabilityState(
            alpha=float(row["alpha"]),
            beta=float(row["beta"]),
            lambda_=float(row["decay_lambda"]),
        ),
        last_processed_performance_id=(
            None if last_processed_performance_id is None else str(last_processed_performance_id)
        ),
        last_processed_sequence_index=(
            None if last_processed_sequence_index is None else int(last_processed_sequence_index)
        ),
    )


def _self_model_version_from_row(row: sqlite3.Row) -> SelfModelVersion:
    previous_version_id = row["previous_version_id"]
    return SelfModelVersion(
        id=str(row["id"]),
        agent_id=str(row["agent_id"]),
        version=int(row["version"]),
        previous_version_id=(None if previous_version_id is None else str(previous_version_id)),
        created_at=datetime.fromisoformat(str(row["created_at"])),
    )


def _capability_self_attribute_from_row(row: sqlite3.Row) -> CapabilitySelfAttribute:
    previous_attribute_id = row["previous_attribute_id"]
    return CapabilitySelfAttribute(
        id=str(row["id"]),
        agent_id=str(row["agent_id"]),
        attribute_type=SelfAttributeType(str(row["attribute_type"])),
        capability_key=str(row["capability_key"]),
        estimated_success=float(row["estimated_success"]),
        self_model_version_id=str(row["self_model_version_id"]),
        attribute_version=int(row["attribute_version"]),
        previous_attribute_id=(
            None if previous_attribute_id is None else str(previous_attribute_id)
        ),
        created_at=datetime.fromisoformat(str(row["created_at"])),
    )
