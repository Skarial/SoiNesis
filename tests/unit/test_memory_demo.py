from pathlib import Path

from soinesis.application.demo import run_memory_demo


def test_memory_demo_compares_active_and_disabled_memory(tmp_path: Path) -> None:
    output = run_memory_demo(tmp_path / "demo.db")

    assert "Mémoire active" in output
    assert "SoiNesis" in output
    assert "Source : JORDAN_INPUT" in output
    assert "Mémoire désactivée" in output
    assert "Souvenirs consultés : 0" in output
