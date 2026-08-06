import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from soinesis.application.memory import MemoryApplicationService
from soinesis.domain.models import AblationConfiguration, EventType, SourceType
from soinesis.infrastructure.sqlite import SQLiteDatabase, SQLiteUnitOfWorkFactory


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 8, 6, 15, 0, tzinfo=UTC)


class SequentialIdentifiers:
    def __init__(self) -> None:
        self._index = 0

    def new(self, prefix: str) -> str:
        self._index += 1
        return f"{prefix}_{self._index}"


def build_service(database_path: Path) -> tuple[MemoryApplicationService, SQLiteDatabase]:
    database = SQLiteDatabase(database_path)
    database.initialize_schema()
    service = MemoryApplicationService(
        unit_of_work_factory=SQLiteUnitOfWorkFactory(database),
        clock=FixedClock(),
        identifiers=SequentialIdentifiers(),
    )
    return service, database


def test_memory_is_persisted_retrieved_and_journaled(tmp_path: Path) -> None:
    service, database = build_service(tmp_path / "soinesis.db")

    recorded = service.record_received_information(
        agent_id="agent_soinesis",
        cycle_id="cycle_1",
        title="Nom du projet",
        content="Jordan indique que le nom du projet est SoiNesis.",
        source_type=SourceType.JORDAN_INPUT,
        confidence=1.0,
        importance=0.9,
    )

    decision = service.recall(
        agent_id="agent_soinesis",
        query="Quel nom Jordan a-t-il donné au projet ?",
        ablation=AblationConfiguration(
            id="enabled",
            autobiographical_memory_enabled=True,
        ),
    )

    assert decision.answer is not None
    assert "SoiNesis" in decision.answer
    assert decision.source_type is SourceType.JORDAN_INPUT
    assert decision.retrieved_memory_ids == (recorded.memory.id,)

    with SQLiteUnitOfWorkFactory(database)() as unit_of_work:
        events = unit_of_work.journal.list_for_target(
            target_entity_type="AutobiographicalMemory",
            target_entity_id=recorded.memory.id,
        )

    assert len(events) == 1
    assert events[0].event_type is EventType.MEMORY_CREATED


def test_failed_transaction_does_not_leave_partial_memory(tmp_path: Path) -> None:
    service, database = build_service(tmp_path / "soinesis.db")

    first = service.record_received_information(
        agent_id="agent_soinesis",
        cycle_id="cycle_1",
        title="Nom du projet",
        content="Jordan indique que le nom du projet est SoiNesis.",
        source_type=SourceType.JORDAN_INPUT,
    )

    duplicate_service = MemoryApplicationService(
        unit_of_work_factory=SQLiteUnitOfWorkFactory(database),
        clock=FixedClock(),
        identifiers=SequentialIdentifiers(),
    )

    with pytest.raises(sqlite3.IntegrityError):
        duplicate_service.record_received_information(
            agent_id="agent_soinesis",
            cycle_id="cycle_2",
            title="Information dupliquée",
            content="Cette transaction doit échouer.",
            source_type=SourceType.JORDAN_INPUT,
        )

    with SQLiteUnitOfWorkFactory(database)() as unit_of_work:
        memories = unit_of_work.memories.search(
            agent_id="agent_soinesis",
            query="projet",
            limit=10,
        )
        events = unit_of_work.journal.list_for_target(
            target_entity_type="AutobiographicalMemory",
            target_entity_id=first.memory.id,
        )

    assert [memory.id for memory in memories] == [first.memory.id]
    assert len(events) == 1
