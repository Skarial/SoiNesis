from datetime import UTC, datetime

from soinesis.application.memory import MemoryApplicationService
from soinesis.domain.models import AblationConfiguration
from soinesis.ports.repositories import UnitOfWork


class NeverCalledUnitOfWorkFactory:
    def __init__(self) -> None:
        self.call_count = 0

    def __call__(self) -> UnitOfWork:
        self.call_count += 1
        raise AssertionError("La persistance ne doit pas être consultée pendant l'ablation.")


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 8, 6, 15, 0, tzinfo=UTC)


class Identifiers:
    def new(self, prefix: str) -> str:
        return f"{prefix}_1"


def test_memory_ablation_prevents_repository_access() -> None:
    factory = NeverCalledUnitOfWorkFactory()
    service = MemoryApplicationService(
        unit_of_work_factory=factory,
        clock=FixedClock(),
        identifiers=Identifiers(),
    )

    decision = service.recall(
        agent_id="agent_soinesis",
        query="Quel est le nom du projet ?",
        ablation=AblationConfiguration(
            id="disabled",
            autobiographical_memory_enabled=False,
        ),
    )

    assert decision.answer is None
    assert decision.retrieved_memory_ids == ()
    assert factory.call_count == 0
