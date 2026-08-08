"""Base SQLite et implémentation transactionnelle des dépôts."""

from __future__ import annotations

import json
import sqlite3
import unicodedata
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Any, Self, cast

from soinesis.domain.models import (
    AutobiographicalMemory,
    EventType,
    JournalEvent,
    MemoryType,
    Observation,
    RecordStatus,
    SourceType,
)
from soinesis.infrastructure.sqlite.migrations import apply_capability_schema_migrations


def _normalise_search_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(character for character in decomposed if not unicodedata.combining(character))


def _search_tokens(query: str) -> tuple[str, ...]:
    normalised = _normalise_search_text(query)
    tokens = tuple(token.strip(".,!?;:()[]{}'\"-") for token in normalised.split())
    return tuple(token for token in tokens if len(token) >= 3)


class SQLiteDatabase:
    """Gestion du fichier SQLite et de son schéma initial."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize_schema(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS observations (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    cycle_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    raw_content TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    confidence REAL NOT NULL CHECK (confidence BETWEEN 0.0 AND 1.0),
                    is_direct_experience INTEGER NOT NULL CHECK (
                        is_direct_experience IN (0, 1)
                    )
                );

                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    cycle_id TEXT NOT NULL,
                    source_observation_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    confidence REAL NOT NULL CHECK (confidence BETWEEN 0.0 AND 1.0),
                    importance REAL NOT NULL CHECK (importance BETWEEN 0.0 AND 1.0),
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    is_direct_experience INTEGER NOT NULL CHECK (
                        is_direct_experience IN (0, 1)
                    ),
                    belief_key TEXT,
                    parent_memory_ids_json TEXT NOT NULL DEFAULT '[]',
                    transition_reason TEXT,
                    FOREIGN KEY (source_observation_id) REFERENCES observations(id)
                );

                CREATE INDEX IF NOT EXISTS memories_agent_status_idx
                    ON memories(agent_id, status);

                CREATE TABLE IF NOT EXISTS journal_events (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    cycle_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    target_entity_type TEXT NOT NULL,
                    target_entity_id TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    new_value_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS journal_target_idx
                    ON journal_events(target_entity_type, target_entity_id);
                """
            )
            self._migrate_memories_for_p2(connection)
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS memories_agent_belief_idx
                ON memories(agent_id, belief_key, created_at)
                """
            )

    def initialize_capability_schema(self) -> None:
        """Initialiser le socle historique puis les migrations de capacité opt-in."""
        self.initialize_schema()
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            apply_capability_schema_migrations(connection)

    @staticmethod
    def _migrate_memories_for_p2(connection: sqlite3.Connection) -> None:
        """Ajouter sans perte les colonnes P2 aux bases créées par P0/P1."""
        columns = {
            str(row["name"]) for row in connection.execute("PRAGMA table_info(memories)").fetchall()
        }
        if "belief_key" not in columns:
            connection.execute("ALTER TABLE memories ADD COLUMN belief_key TEXT")
        if "parent_memory_ids_json" not in columns:
            connection.execute(
                "ALTER TABLE memories ADD COLUMN parent_memory_ids_json TEXT NOT NULL DEFAULT '[]'"
            )
        if "transition_reason" not in columns:
            connection.execute("ALTER TABLE memories ADD COLUMN transition_reason TEXT")


class SQLiteObservationRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, observation: Observation) -> None:
        self._connection.execute(
            """
            INSERT INTO observations (
                id, agent_id, cycle_id, source_type, raw_content,
                received_at, confidence, is_direct_experience
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                observation.id,
                observation.agent_id,
                observation.cycle_id,
                observation.source_type.value,
                observation.raw_content,
                observation.received_at.isoformat(),
                observation.confidence,
                int(observation.is_direct_experience),
            ),
        )


class SQLiteMemoryRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, memory: AutobiographicalMemory) -> None:
        self._connection.execute(
            """
            INSERT INTO memories (
                id, agent_id, cycle_id, source_observation_id, memory_type,
                title, content, source_type, confidence, importance, status,
                created_at, is_direct_experience, belief_key,
                parent_memory_ids_json, transition_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory.id,
                memory.agent_id,
                memory.cycle_id,
                memory.source_observation_id,
                memory.memory_type.value,
                memory.title,
                memory.content,
                memory.source_type.value,
                memory.confidence,
                memory.importance,
                memory.status.value,
                memory.created_at.isoformat(),
                int(memory.is_direct_experience),
                memory.belief_key,
                json.dumps(memory.parent_memory_ids, ensure_ascii=False),
                memory.transition_reason,
            ),
        )

    def get(self, memory_id: str) -> AutobiographicalMemory | None:
        row = self._connection.execute(
            "SELECT * FROM memories WHERE id = ?",
            (memory_id,),
        ).fetchone()
        return None if row is None else _memory_from_row(row)

    def update_status(self, *, memory_id: str, status: RecordStatus) -> None:
        cursor = self._connection.execute(
            "UPDATE memories SET status = ? WHERE id = ?",
            (status.value, memory_id),
        )
        if cursor.rowcount != 1:
            raise KeyError(f"Souvenir introuvable : {memory_id}")

    def list_for_belief(
        self,
        *,
        agent_id: str,
        belief_key: str,
    ) -> list[AutobiographicalMemory]:
        rows = self._connection.execute(
            """
            SELECT * FROM memories
            WHERE agent_id = ? AND belief_key = ?
            ORDER BY created_at ASC, id ASC
            """,
            (agent_id, belief_key),
        ).fetchall()
        return [_memory_from_row(row) for row in rows]

    def search(
        self,
        *,
        agent_id: str,
        query: str,
        limit: int = 5,
    ) -> list[AutobiographicalMemory]:
        if limit <= 0:
            return []

        rows = self._connection.execute(
            """
            SELECT * FROM memories
            WHERE agent_id = ? AND status = ?
            ORDER BY importance DESC, created_at DESC
            """,
            (agent_id, RecordStatus.ACTIVE.value),
        ).fetchall()

        tokens = _search_tokens(query)
        ranked: list[tuple[int, float, str, AutobiographicalMemory]] = []
        for row in rows:
            memory = _memory_from_row(row)
            searchable = _normalise_search_text(f"{memory.title} {memory.content}")
            score = sum(1 for token in tokens if token in searchable)
            if not tokens or score > 0:
                ranked.append((score, memory.importance, memory.created_at.isoformat(), memory))

        ranked.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
        return [item[3] for item in ranked[:limit]]


class SQLiteJournalRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def append(self, event: JournalEvent) -> None:
        self._connection.execute(
            """
            INSERT INTO journal_events (
                id, agent_id, cycle_id, event_type, target_entity_type,
                target_entity_id, occurred_at, reason, new_value_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.id,
                event.agent_id,
                event.cycle_id,
                event.event_type.value,
                event.target_entity_type,
                event.target_entity_id,
                event.occurred_at.isoformat(),
                event.reason,
                json.dumps(event.new_value, ensure_ascii=False, sort_keys=True),
            ),
        )

    def list_for_target(
        self,
        *,
        target_entity_type: str,
        target_entity_id: str,
    ) -> list[JournalEvent]:
        rows = self._connection.execute(
            """
            SELECT * FROM journal_events
            WHERE target_entity_type = ? AND target_entity_id = ?
            ORDER BY occurred_at ASC, id ASC
            """,
            (target_entity_type, target_entity_id),
        ).fetchall()
        return [_journal_event_from_row(row) for row in rows]


class SQLiteUnitOfWork:
    """Transaction SQLite exposant les dépôts du noyau."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database
        self._connection: sqlite3.Connection | None = None
        self._committed = False

    def __enter__(self) -> Self:
        self._connection = self._database.connect()
        self.observations = SQLiteObservationRepository(self._connection)
        self.memories = SQLiteMemoryRepository(self._connection)
        self.journal = SQLiteJournalRepository(self._connection)
        return self

    def commit(self) -> None:
        connection = self._require_connection()
        connection.commit()
        self._committed = True

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        connection = self._require_connection()
        try:
            if exc_type is not None or not self._committed:
                connection.rollback()
        finally:
            connection.close()
            self._connection = None

    def _require_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise RuntimeError("La transaction SQLite n'est pas ouverte.")
        return self._connection


class SQLiteUnitOfWorkFactory:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def __call__(self) -> SQLiteUnitOfWork:
        return SQLiteUnitOfWork(self._database)


def _memory_from_row(row: sqlite3.Row) -> AutobiographicalMemory:
    raw_parent_ids = cast(object, json.loads(row["parent_memory_ids_json"]))
    if not isinstance(raw_parent_ids, list):
        raise ValueError("Les parents d'un souvenir doivent être une liste JSON de chaînes.")
    parent_ids = cast(list[object], raw_parent_ids)
    if not all(isinstance(parent_id, str) for parent_id in parent_ids):
        raise ValueError("Les parents d'un souvenir doivent être une liste JSON de chaînes.")
    validated_parent_ids = cast(list[str], parent_ids)

    return AutobiographicalMemory(
        id=row["id"],
        agent_id=row["agent_id"],
        cycle_id=row["cycle_id"],
        source_observation_id=row["source_observation_id"],
        memory_type=MemoryType(row["memory_type"]),
        title=row["title"],
        content=row["content"],
        source_type=SourceType(row["source_type"]),
        confidence=float(row["confidence"]),
        importance=float(row["importance"]),
        status=RecordStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        is_direct_experience=bool(row["is_direct_experience"]),
        belief_key=row["belief_key"],
        parent_memory_ids=tuple(validated_parent_ids),
        transition_reason=row["transition_reason"],
    )


def _journal_event_from_row(row: sqlite3.Row) -> JournalEvent:
    raw_value = cast(object, json.loads(row["new_value_json"]))
    if not isinstance(raw_value, dict):
        raise ValueError("Le contenu JSON d'un événement doit être un objet.")

    return JournalEvent(
        id=row["id"],
        agent_id=row["agent_id"],
        cycle_id=row["cycle_id"],
        event_type=EventType(row["event_type"]),
        target_entity_type=row["target_entity_type"],
        target_entity_id=row["target_entity_id"],
        occurred_at=datetime.fromisoformat(row["occurred_at"]),
        reason=row["reason"],
        new_value=cast(dict[str, Any], raw_value),
    )
