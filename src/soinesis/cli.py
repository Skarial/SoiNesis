"""Point d'entrée en ligne de commande de SoiNesis."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from soinesis import __version__


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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Exécuter la ligne de commande."""
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0
