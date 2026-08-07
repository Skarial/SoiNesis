"""Point d'entrée en ligne de commande de SoiNesis."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from soinesis import __version__
from soinesis.experiments.exp_001_p2_official import (
    P2OfficialRunError,
    run_official_experiment,
)


def build_parser() -> argparse.ArgumentParser:
    """Construire l'analyseur d'arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        prog="soinesis",
        description=(
            "Plateforme expérimentale pour l'étude de mécanismes fonctionnels "
            "associés à la conscience artificielle."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    commands = parser.add_subparsers(dest="command")
    p2_parser = commands.add_parser(
        "exp-001-p2",
        help="Commandes strictement gardées pour EXP-001-P2.",
    )
    p2_commands = p2_parser.add_subparsers(dest="p2_command")
    official_parser = p2_commands.add_parser(
        "run-official",
        help="Exécuter une unique campagne officielle P2 puis exporter son bundle brut.",
    )
    official_parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Racine du dépôt Git SoiNesis (défaut : répertoire courant).",
    )
    official_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Répertoire de sortie inexistant pour le bundle officiel.",
    )
    official_parser.add_argument(
        "--confirm",
        dest="confirmation",
        required=True,
        help="Confirmation humaine exacte exigée par le garde-fou officiel.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Exécuter la ligne de commande."""
    parser = build_parser()
    args = parser.parse_args(argv)
    command = cast(str | None, getattr(args, "command", None))
    p2_command = cast(str | None, getattr(args, "p2_command", None))

    if command == "exp-001-p2" and p2_command == "run-official":
        repo_root = cast(Path, args.repo_root).resolve()
        output_directory = cast(Path, args.output)
        if not output_directory.is_absolute():
            output_directory = repo_root / output_directory
        confirmation = cast(str, args.confirmation)
        try:
            run_official_experiment(
                repo_root=repo_root,
                output_directory=output_directory,
                confirmation=confirmation,
            )
        except P2OfficialRunError as error:
            parser.error(str(error))
        return 0

    parser.print_help()
    return 0
