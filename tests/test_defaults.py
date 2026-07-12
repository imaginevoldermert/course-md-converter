from pathlib import Path

from cmd_converter.defaults import get_default_output_dir


def test_configured_default_output(monkeypatch):
    configured = Path.home() / "Documents" / "example-vault"
    monkeypatch.setenv("CMD_OUTPUT_DIR", str(configured))
    assert get_default_output_dir() == configured
