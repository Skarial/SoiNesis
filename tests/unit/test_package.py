import pytest

from soinesis import __version__
from soinesis.cli import main


def test_package_version() -> None:
    assert __version__ == "0.1.0"


def test_cli_displays_help(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main([])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Plateforme expérimentale" in captured.out
