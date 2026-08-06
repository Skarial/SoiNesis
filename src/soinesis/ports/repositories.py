"""Ports de persistance utilisés par le noyau."""

from __future__ import annotations

from types import TracebackType
from typing import Protocol, Self

from soinesis.domain.models import AutobiographicalMemory, JournalEvent, Observation


class ObservationRepository(Protocol):
    def add(self, observation: Observation) -> None: ...


class MemoryRepository(Protocol):
    def add(self, memory: AutobiographicalMemory) -> None: ...

    def search(
        self,
        *,
        agent_id: str,
        query: str,
        limit: int = 5,
    ) -> list[AutobiographicalMemory]: ...


class JournalRepository(Protocol):
    def append(self, event: JournalEvent) -> None: ...

    def list_for_target(
        self,
        *,
        target_entity_type: str,
        target_entity_id: str,
    ) -> list[JournalEvent]: ...


class UnitOfWork(Protocol):
    observations: ObservationRepository
    memories: MemoryRepository
    journal: JournalRepository

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...


class UnitOfWorkFactory(Protocol):
    def __call__(self) -> UnitOfWork: ...
