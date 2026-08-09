"""Inspection SQLite expérimentale et read-only de l'état cognitif P3."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, cast

from pydantic import ValidationError

from soinesis.domain.capabilities import (
    CapabilityPerformanceObservation,
    CapabilitySelfAttribute,
    MetacognitiveCapabilityState,
    SelfAttributeType,
    SelfModelVersion,
    VersionedMetacognitiveCapabilityState,
)
from soinesis.domain.models import EventType, JournalEvent, SourceType
from soinesis.experiments.p3.condition_runtime import (
    ExperimentalAgentCognitiveState,
    ExperimentalConditionRuntimeIntegrityError,
)
from soinesis.infrastructure.sqlite.database import SQLiteDatabase


class SQLiteExperimentalAgentCognitiveStateInspector:
    """Lire uniquement les tables cognitives pour un agent expérimental ciblé."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def inspect(self, *, agent_id: str) -> ExperimentalAgentCognitiveState:
        if type(agent_id) is not str or not agent_id:
            raise ValueError("agent_id doit être une chaîne opaque non vide.")
        try:
            with self._database.connect() as connection:
                performances = tuple(
                    CapabilityPerformanceObservation(
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
                    for row in connection.execute(
                        """
                        SELECT * FROM capability_performances
                        WHERE agent_id = ?
                        ORDER BY sequence_index ASC, observed_at ASC, id ASC
                        """,
                        (agent_id,),
                    ).fetchall()
                )
                metacognitive_states = tuple(
                    VersionedMetacognitiveCapabilityState(
                        agent_id=str(row["agent_id"]),
                        capability_key=str(row["capability_key"]),
                        version=int(row["version"]),
                        state=MetacognitiveCapabilityState(
                            alpha=float(row["alpha"]),
                            beta=float(row["beta"]),
                            lambda_=float(row["decay_lambda"]),
                        ),
                        last_processed_performance_id=(
                            None
                            if row["last_processed_performance_id"] is None
                            else str(row["last_processed_performance_id"])
                        ),
                        last_processed_sequence_index=(
                            None
                            if row["last_processed_sequence_index"] is None
                            else int(row["last_processed_sequence_index"])
                        ),
                    )
                    for row in connection.execute(
                        """
                        SELECT * FROM metacognitive_states
                        WHERE agent_id = ?
                        ORDER BY capability_key ASC
                        """,
                        (agent_id,),
                    ).fetchall()
                )
                self_model_versions = tuple(
                    SelfModelVersion(
                        id=str(row["id"]),
                        agent_id=str(row["agent_id"]),
                        version=int(row["version"]),
                        previous_version_id=(
                            None
                            if row["previous_version_id"] is None
                            else str(row["previous_version_id"])
                        ),
                        created_at=datetime.fromisoformat(str(row["created_at"])),
                    )
                    for row in connection.execute(
                        """
                        SELECT * FROM self_model_versions
                        WHERE agent_id = ?
                        ORDER BY version ASC, id ASC
                        """,
                        (agent_id,),
                    ).fetchall()
                )
                capability_self_attributes = tuple(
                    CapabilitySelfAttribute(
                        id=str(row["id"]),
                        agent_id=str(row["agent_id"]),
                        attribute_type=SelfAttributeType(str(row["attribute_type"])),
                        capability_key=str(row["capability_key"]),
                        estimated_success=float(row["estimated_success"]),
                        self_model_version_id=str(row["self_model_version_id"]),
                        attribute_version=int(row["attribute_version"]),
                        previous_attribute_id=(
                            None
                            if row["previous_attribute_id"] is None
                            else str(row["previous_attribute_id"])
                        ),
                        created_at=datetime.fromisoformat(str(row["created_at"])),
                    )
                    for row in connection.execute(
                        """
                        SELECT * FROM capability_self_attributes
                        WHERE agent_id = ?
                        ORDER BY attribute_version ASC, created_at ASC, id ASC
                        """,
                        (agent_id,),
                    ).fetchall()
                )
                capability_journal_events = tuple(
                    self._journal_event_from_row(row)
                    for row in connection.execute(
                        """
                        SELECT * FROM journal_events
                        WHERE agent_id = ?
                          AND event_type IN (?, ?)
                        ORDER BY occurred_at ASC, id ASC
                        """,
                        (
                            agent_id,
                            EventType.CAPABILITY_SELF_ATTRIBUTE_INITIALIZED.value,
                            EventType.CAPABILITY_SELF_ATTRIBUTE_REVISED.value,
                        ),
                    ).fetchall()
                )
        except (TypeError, ValueError, ValidationError, json.JSONDecodeError) as error:
            raise ExperimentalConditionRuntimeIntegrityError(
                "L'état cognitif SQLite de l'agent est invalide."
            ) from error
        return ExperimentalAgentCognitiveState(
            agent_id=agent_id,
            performances=performances,
            metacognitive_states=metacognitive_states,
            self_model_versions=self_model_versions,
            capability_self_attributes=capability_self_attributes,
            capability_journal_events=capability_journal_events,
        )

    @staticmethod
    def _journal_event_from_row(row: Any) -> JournalEvent:
        raw_value = cast(object, json.loads(str(row["new_value_json"])))
        if not isinstance(raw_value, dict):
            raise ValueError("Le contenu d'un JournalEvent CAPABILITY doit être un objet JSON.")
        return JournalEvent(
            id=str(row["id"]),
            agent_id=str(row["agent_id"]),
            cycle_id=str(row["cycle_id"]),
            event_type=EventType(str(row["event_type"])),
            target_entity_type=str(row["target_entity_type"]),
            target_entity_id=str(row["target_entity_id"]),
            occurred_at=datetime.fromisoformat(str(row["occurred_at"])),
            reason=str(row["reason"]),
            new_value=cast(dict[str, Any], raw_value),
        )
