"""Démonstration exécutable de la première tranche verticale."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from soinesis.application.memory import MemoryApplicationService
from soinesis.domain.models import AblationConfiguration, SourceType
from soinesis.infrastructure.sqlite import SQLiteDatabase, SQLiteUnitOfWorkFactory
from soinesis.infrastructure.system import UtcClock, UuidIdentifierGenerator


def run_memory_demo(database_path: Path, *, reset: bool = True) -> str:
    """Exécuter le scénario mémoire active puis désactivée."""
    if reset:
        database_path.unlink(missing_ok=True)

    database = SQLiteDatabase(database_path)
    database.initialize_schema()
    service = MemoryApplicationService(
        unit_of_work_factory=SQLiteUnitOfWorkFactory(database),
        clock=UtcClock(),
        identifiers=UuidIdentifierGenerator(),
    )

    service.record_received_information(
        agent_id="agent_soinesis",
        cycle_id="cycle_record_project_name",
        title="Nom du projet",
        content="Jordan indique que le nom du projet est SoiNesis.",
        source_type=SourceType.JORDAN_INPUT,
        confidence=1.0,
        importance=0.9,
    )

    enabled = service.recall(
        agent_id="agent_soinesis",
        query="Quel nom Jordan a-t-il donné au projet ?",
        ablation=AblationConfiguration(
            id="ablation_memory_enabled",
            autobiographical_memory_enabled=True,
        ),
    )
    disabled = service.recall(
        agent_id="agent_soinesis",
        query="Quel nom Jordan a-t-il donné au projet ?",
        ablation=AblationConfiguration(
            id="ablation_memory_disabled",
            autobiographical_memory_enabled=False,
        ),
    )

    enabled_answer = enabled.answer or "Aucune réponse"
    disabled_answer = disabled.answer or "Aucune réponse issue de la mémoire"
    return "\n".join(
        (
            "=== Mémoire active ===",
            f"Réponse : {enabled_answer}",
            f"Source : {enabled.source_type.value if enabled.source_type else 'aucune'}",
            f"Souvenirs consultés : {len(enabled.retrieved_memory_ids)}",
            "",
            "=== Mémoire désactivée ===",
            f"Réponse : {disabled_answer}",
            f"Souvenirs consultés : {len(disabled.retrieved_memory_ids)}",
            f"Raison : {disabled.reason}",
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Exécuter la démonstration depuis la ligne de commande."""
    parser = argparse.ArgumentParser(description="Démonstration mémoire de SoiNesis.")
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("data/soinesis-demo.db"),
    )
    arguments = parser.parse_args(argv)
    print(run_memory_demo(arguments.database))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
