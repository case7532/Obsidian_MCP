"""Vault configuration and validation."""

import logging
import os
from pathlib import Path

from obsidian_mcp.exceptions import VaultError

logger = logging.getLogger(__name__)


class VaultConfig:
    """Holds and validates the Obsidian vault path."""

    def __init__(self, vault_path: Path) -> None:
        self.vault_path = vault_path.resolve()

    @classmethod
    def from_env_or_arg(cls, vault_path: str | None = None) -> "VaultConfig":
        """Create VaultConfig from CLI argument or OBSIDIAN_VAULT_PATH env var.

        Args:
            vault_path: Optional path string from CLI argument.

        Returns:
            Validated VaultConfig instance.

        Raises:
            VaultError: If no vault path provided or vault is invalid.
        """
        raw = vault_path or os.environ.get("OBSIDIAN_VAULT_PATH")
        if not raw:
            raise VaultError(
                "Vault path required. Provide via --vault argument or "
                "OBSIDIAN_VAULT_PATH environment variable."
            )
        config = cls(Path(raw))
        config.validate()
        return config

    def validate(self) -> None:
        """Validate that vault_path is an existing Obsidian vault.

        Raises:
            VaultError: If vault_path does not exist or lacks .obsidian/ directory.
        """
        if not self.vault_path.exists():
            raise VaultError("Vault path does not exist")
        if not self.vault_path.is_dir():
            raise VaultError("Vault path is not a directory")
        if not (self.vault_path / ".obsidian").is_dir():
            raise VaultError("Not a valid Obsidian vault: .obsidian directory not found")

    def resolve_path(self, relative: str) -> Path:
        """Resolve a vault-relative path to absolute. Does NOT validate security.

        Use path_utils.safe_vault_path() for user-supplied paths.
        This is for internal use with known-safe relative paths.
        """
        return self.vault_path / relative

    def to_relative(self, absolute: Path) -> str:
        """Convert absolute path to vault-relative POSIX string."""
        return absolute.relative_to(self.vault_path).as_posix()
