"""Custom exception hierarchy for obsidian-mcp."""


class ObsidianMCPError(Exception):
    """Base exception for all obsidian-mcp errors."""


class VaultError(ObsidianMCPError):
    """Raised when vault path is invalid or inaccessible."""


class PathTraversalError(ObsidianMCPError):
    """Raised when a user-supplied path attempts to escape the vault boundary."""


class NoteNotFoundError(ObsidianMCPError):
    """Raised when a requested note does not exist."""


class NoteExistsError(ObsidianMCPError):
    """Raised when attempting to create a note that already exists."""


class FolderNotEmptyError(ObsidianMCPError):
    """Raised when attempting to delete a non-empty folder without force=True."""
