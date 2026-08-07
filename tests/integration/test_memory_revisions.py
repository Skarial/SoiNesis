import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from soinesis.application.memory import MemoryApplicationService
from soinesis.domain.models import EventType, MemoryType, RecordStatus, SourceType
from soinesis.infrastructure.sqlite import SQLiteDatabase, SQLiteUnitOfWorkFactory


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 8, 7, 16, 0, tzinfo=UTC)


class SequentialIdentifiers:
    def __init__(self) -> None:
        self._index = 0

    def new(self, prefix: str) -> str:
        self._index += 1
        return f"{prefix}_{self._index:03d}"


def build_service(database_path: Path) -> tuple[MemoryApplicationService, SQLiteDatabase]:
    database = SQLiteDatabase(database_path)
    database.initialize_schema()
    return (
        MemoryApplicationService(
            unit_of_work_factory=SQLiteUnitOfWorkFactory(database),
            clock=FixedClock(),
            identifiers=SequentialIdentifiers(),
        ),
        database,
    )


def test_correction_preserves_old_version_and_journals_transition(tmp_path: Path) -> None:
    service, database = build_service(tmp_path / "soinesis.db")
    initial = service.record_memory(
        agent_id="agent_soinesis",
        cycle_id="cycle_1",
        title="Réglage module A",
        content="Le module A est réglé sur 12.",
        memory_type=MemoryType.RECEIVED_INFORMATION,
        source_type=SourceType.JORDAN_INPUT,
        belief_key="module-a-setting",
    )

    correction = service.record_belief_transition(
        agent_id="agent_soinesis",
        cycle_id="cycle_2",
        belief_key="module-a-setting",
        title="Réglage module A",
        content="Correction : le module A est réglé sur 17.",
        memory_type=MemoryType.RECEIVED_INFORMATION,
        source_type=SourceType.JORDAN_INPUT,
        parent_memory_ids=(initial.memory.id,),
        parent_new_status=RecordStatus.SUPERSEDED,
        new_status=RecordStatus.ACTIVE,
        transition_reason="Correction explicite de la valeur précédente.",
    )

    with SQLiteUnitOfWorkFactory(database)() as unit_of_work:
        versions = unit_of_work.memories.list_for_belief(
            agent_id="agent_soinesis",
            belief_key="module-a-setting",
        )
        old_events = unit_of_work.journal.list_for_target(
            target_entity_type="AutobiographicalMemory",
            target_entity_id=initial.memory.id,
        )
        new_events = unit_of_work.journal.list_for_target(
            target_entity_type="AutobiographicalMemory",
            target_entity_id=correction.memory.id,
        )

    assert [version.status for version in versions] == [
        RecordStatus.SUPERSEDED,
        RecordStatus.ACTIVE,
    ]
    assert correction.memory.parent_memory_ids == (initial.memory.id,)
    assert correction.memory.transition_reason == "Correction explicite de la valeur précédente."
    assert [event.event_type for event in old_events] == [
        EventType.MEMORY_CREATED,
        EventType.MEMORY_STATUS_CHANGED,
    ]
    assert [event.event_type for event in new_events] == [EventType.MEMORY_REVISION_CREATED]


def test_unresolved_contradiction_can_later_be_resolved_without_erasing_history(
    tmp_path: Path,
) -> None:
    service, database = build_service(tmp_path / "soinesis.db")
    initial = service.record_memory(
        agent_id="agent_soinesis",
        cycle_id="cycle_1",
        title="Repère B",
        content="Jordan indique que le repère B vaut 31.",
        memory_type=MemoryType.RECEIVED_INFORMATION,
        source_type=SourceType.JORDAN_INPUT,
        belief_key="marker-b",
    )
    contradiction = service.record_belief_transition(
        agent_id="agent_soinesis",
        cycle_id="cycle_2",
        belief_key="marker-b",
        title="Repère B",
        content="Un outil externe indique que le repère B vaut 44.",
        memory_type=MemoryType.RECEIVED_INFORMATION,
        source_type=SourceType.EXTERNAL_TOOL,
        parent_memory_ids=(initial.memory.id,),
        parent_new_status=RecordStatus.CONTESTED,
        new_status=RecordStatus.CONTESTED,
        transition_reason="Contradiction non résolue entre deux sources.",
    )

    with SQLiteUnitOfWorkFactory(database)() as unit_of_work:
        contested = unit_of_work.memories.list_for_belief(
            agent_id="agent_soinesis",
            belief_key="marker-b",
        )
    assert [version.status for version in contested] == [
        RecordStatus.CONTESTED,
        RecordStatus.CONTESTED,
    ]

    resolution = service.record_belief_transition(
        agent_id="agent_soinesis",
        cycle_id="cycle_3",
        belief_key="marker-b",
        title="Repère B",
        content="L'événement de résolution fixe le repère B à 44.",
        memory_type=MemoryType.RECEIVED_INFORMATION,
        source_type=SourceType.EXPERIMENTER_INPUT,
        parent_memory_ids=(initial.memory.id, contradiction.memory.id),
        parent_new_status=RecordStatus.SUPERSEDED,
        new_status=RecordStatus.ACTIVE,
        transition_reason="Résolution synthétique explicitement déclarée.",
    )

    with SQLiteUnitOfWorkFactory(database)() as unit_of_work:
        resolved = unit_of_work.memories.list_for_belief(
            agent_id="agent_soinesis",
            belief_key="marker-b",
        )

    assert [version.status for version in resolved] == [
        RecordStatus.SUPERSEDED,
        RecordStatus.SUPERSEDED,
        RecordStatus.ACTIVE,
    ]
    assert resolution.memory.parent_memory_ids == (
        initial.memory.id,
        contradiction.memory.id,
    )
    assert [version.content for version in resolved] == [
        initial.memory.content,
        contradiction.memory.content,
        resolution.memory.content,
    ]


def test_confirmation_is_persisted_without_creating_a_new_version(tmp_path: Path) -> None:
    service, database = build_service(tmp_path / "soinesis.db")
    initial = service.record_memory(
        agent_id="agent_soinesis",
        cycle_id="cycle_1",
        title="État module C",
        content="Le module C est actif.",
        memory_type=MemoryType.RECEIVED_INFORMATION,
        source_type=SourceType.JORDAN_INPUT,
        belief_key="module-c-state",
    )

    confirmation = service.record_belief_confirmation(
        agent_id="agent_soinesis",
        cycle_id="cycle_2",
        memory_id=initial.memory.id,
        content="Un outil externe confirme que le module C est actif.",
        source_type=SourceType.EXTERNAL_TOOL,
    )

    with SQLiteUnitOfWorkFactory(database)() as unit_of_work:
        versions = unit_of_work.memories.list_for_belief(
            agent_id="agent_soinesis",
            belief_key="module-c-state",
        )
        events = unit_of_work.journal.list_for_target(
            target_entity_type="AutobiographicalMemory",
            target_entity_id=initial.memory.id,
        )

    assert len(versions) == 1
    assert versions[0].status is RecordStatus.ACTIVE
    assert confirmation.memory_id == initial.memory.id
    assert [event.event_type for event in events] == [
        EventType.MEMORY_CREATED,
        EventType.MEMORY_CONFIRMED,
    ]


def test_schema_migrates_legacy_memories_table_for_p2(tmp_path: Path) -> None:
    path = tmp_path / "legacy.db"
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE memories (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                cycle_id TEXT NOT NULL,
                source_observation_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                importance REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_direct_experience INTEGER NOT NULL
            )
            """
        )

    database = SQLiteDatabase(path)
    database.initialize_schema()

    with database.connect() as connection:
        columns = {
            str(row["name"]) for row in connection.execute("PRAGMA table_info(memories)").fetchall()
        }

    assert {"belief_key", "parent_memory_ids_json", "transition_reason"} <= columns
