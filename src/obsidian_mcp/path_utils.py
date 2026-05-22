"""Path security utilities — all filesystem paths must go through this module.

SECURITY: This module is the sole boundary between user input and the filesystem.
Every path returned by safe_vault_path() is guaranteed to be inside vault_path.
"""

import logging
from pathlib import Path

from obsidian_mcp.exceptions import PathTraversalError

logger = logging.getLogger(__name__)

# Characters invalid in Obsidian filenames (Windows + Obsidian restrictions)
_INVALID_FILENAME_CHARS = frozenset(r'\/:*?"<>|')


def safe_vault_path(vault_path: Path, user_input: str) -> Path:
    """Resolve user_input relative to vault_path and verify it stays inside.

    Args:
        vault_path: Absolute, validated vault root path.
        user_input: User-supplied relative path string.

    Returns:
        Resolved absolute Path guaranteed to be inside vault_path.

    Raises:
        PathTraversalError: If the resolved path escapes vault_path.
    """
    # Strip leading slashes — treat all inputs as relative to vault
    cleaned = user_input.lstrip("/\\")
    resolved = (vault_path / cleaned).resolve()

    if not resolved.is_relative_to(vault_path):
        logger.warning("Path traversal attempt blocked: input=%r", user_input[:80])
        raise PathTraversalError("Path outside vault boundary")

    return resolved


def normalize_note_path(path: str) -> str:
    """Normalize a vault-relative note path.

    - Strips leading slashes
    - Resolves . and .. components (relative only, no filesystem access)
    - Appends .md if no extension present

    Args:
        path: Raw vault-relative path string.

    Returns:
        Normalized vault-relative path string with .md extension.
    """
    p = Path(path.lstrip("/\\"))
    # Collapse . and .. without hitting the filesystem
    try:
        p = Path(*p.parts)  # rebuild — Path handles normalization on construction
    except TypeError:
        pass

    if not p.suffix and p.name:
        p = p.with_suffix(".md")

    return str(p)


def sanitize_filename(name: str) -> str:
    """Replace characters invalid in Obsidian filenames with hyphens.

    Args:
        name: Proposed filename (without extension).

    Returns:
        Sanitized filename safe for use in vault.
    """
    return "".join("-" if c in _INVALID_FILENAME_CHARS else c for c in name).strip("-")


def is_markdown(path: Path) -> bool:
    """Return True if path has a .md extension."""
    return path.suffix.lower() == ".md"


def is_canvas(path: Path) -> bool:
    """Return True if path has a .canvas extension."""
    return path.suffix.lower() == ".canvas"


def to_vault_relative(vault_path: Path, absolute: Path) -> str:
    """Convert an absolute path to a vault-relative string.

    Args:
        vault_path: Vault root.
        absolute: Absolute path inside vault.

    Returns:
        POSIX-style vault-relative path string.
    """
    return absolute.relative_to(vault_path).as_posix()
