from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from soinesis.application.memory import MemoryApplicationService
from soinesis.domain.models import AutobiographicalMemory, MemoryType, SourceType
from soinesis.infrastructure.sqlite import SQLiteDatabase, SQLiteUnitOfWorkFactory


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 8, 7, tzinfo=UTC)


class SequentialIdentifiers:
    def __init__(self) -> None:
        self.index = 0

    def new(self, prefix: str) -> str:
        self.index += 1
        return f"{prefix}_{self.index}"


def build_service(path: Path) -> MemoryApplicationService:
    database = SQLiteDatabase(path)
    database.initialize_schema()
    return MemoryApplicationService(
        unit_of_work_factory=SQLiteUnitOfWorkFactory(database),
        clock=FixedClock(),
        identifiers=SequentialIdentifiers(),
    )


def test_deduction_and_imagination_are_recorded_with_distinct_types(tmp_path: Path) -> None:
    service = build_service(tmp_path / "memory.db")
    deduction = service.record_deduction(
        agent_id="agent",
        cycle_id="deduction-cycle",
        title="Déduction",
        content="Le module nécessite deux relais.",
    )
    imagination = service.record_imagination(
        agent_id="agent",
        cycle_id="imagination-cycle",
        title="Imagination",
        content="Le module pourrait être placé sous une verrière.",
    )
    assert deduction.memory.memory_type is MemoryType.DEDUCTION
    assert deduction.memory.source_type is SourceType.DEDUCTION
    assert imagination.memory.memory_type is MemoryType.IMAGINED_SCENARIO
    assert imagination.memory.source_type is SourceType.IMAGINATION


def test_received_information_cannot_hide_deduction_or_imagination() -> None:
    with pytest.raises(ValidationError):
        AutobiographicalMemory(
            id="memory",
            agent_id="agent",
            cycle_id="cycle",
            source_observation_id="observation",
            memory_type=MemoryType.RECEIVED_INFORMATION,
            title="Mauvais typage",
            content="Contenu",
            source_type=SourceType.DEDUCTION,
            confidence=1.0,
            importance=0.5,
            created_at=datetime(2026, 8, 7, tzinfo=UTC),
        )
