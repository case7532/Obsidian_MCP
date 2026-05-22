"""Tests for VaultConfig."""

import os
import pytest
from pathlib import Path

from obsidian_mcp.vault_config import VaultConfig
from obsidian_mcp.exceptions import VaultError


@pytest.fixture
def valid_vault(tmp_path: Path) -> Path:
    (tmp_path / ".obsidian").mkdir()
    return tmp_path


def test_valid_vault(valid_vault):
    config = VaultConfig(valid_vault)
    config.validate()  # should not raise
    assert config.vault_path == valid_vault


def test_missing_vault(tmp_path):
    config = VaultConfig(tmp_path / "nonexistent")
    with pytest.raises(VaultError, match="does not exist"):
        config.validate()


def test_not_a_directory(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("x")
    config = VaultConfig(f)
    with pytest.raises(VaultError, match="not a directory"):
        config.validate()


def test_missing_obsidian_dir(tmp_path):
    config = VaultConfig(tmp_path)
    with pytest.raises(VaultError, match=".obsidian"):
        config.validate()


def test_from_env(valid_vault, monkeypatch):
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(valid_vault))
    config = VaultConfig.from_env_or_arg()
    assert config.vault_path == valid_vault


def test_from_arg(valid_vault):
    config = VaultConfig.from_env_or_arg(str(valid_vault))
    assert config.vault_path == valid_vault


def test_no_path_raises(monkeypatch):
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)
    with pytest.raises(VaultError, match="Vault path required"):
        VaultConfig.from_env_or_arg()


def test_resolve_path(valid_vault):
    config = VaultConfig(valid_vault)
    config.validate()
    assert config.resolve_path("notes/test.md") == valid_vault / "notes" / "test.md"


def test_to_relative(valid_vault):
    config = VaultConfig(valid_vault)
    config.validate()
    absolute = valid_vault / "folder" / "note.md"
    assert config.to_relative(absolute) == "folder/note.md"
