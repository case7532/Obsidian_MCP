"""MCP write tool handlers."""

import logging
from dataclasses import asdict

from mcp.server.fastmcp import FastMCP

from obsidian_mcp.note_writer import NoteWriter

logger = logging.getLogger(__name__)


def register_write_tools(mcp: FastMCP, writer: NoteWriter) -> None:

    @mcp.tool()
    def create_note(
        path: str | None = None,
        content: str = "",
        frontmatter: dict | None = None,
        title: str | None = None,
        description: str = "",
        links: list[str] | None = None,
    ) -> dict:
        """Create a new note in the vault with standard format (title, description, index, links).

        Args:
            path: Vault-relative path (e.g. 'folder/note.md'). If omitted, inferred from content/tags.
            content: Markdown content body.
            frontmatter: Optional YAML frontmatter as a dict.
            title: Document title (used in H1 heading). Falls back to frontmatter['title'] or filename.
            description: Short description shown below title.
            links: List of related note names for [[wikilinks]] in Related section.
        """
        return asdict(writer.create_note(path, content, frontmatter, title, description, links))

    @mcp.tool()
    def update_note(path: str, content: str, mode: str = "replace") -> dict:
        """Update a note's content.

        Args:
            path: Vault-relative path.
            content: New content.
            mode: 'replace' (default) or 'append'.
        """
        return asdict(writer.update_note(path, content, mode))

    @mcp.tool()
    def delete_note(path: str) -> dict:
        """Delete a note from the vault.

        Args:
            path: Vault-relative path.
        """
        writer.delete_note(path)
        return {"deleted": path}

    @mcp.tool()
    def move_note(source: str, destination: str, update_links: bool = True) -> dict:
        """Move or rename a note. Optionally updates backlinks.

        Args:
            source: Current vault-relative path.
            destination: New vault-relative path.
            update_links: Whether to update [[wikilinks]] in other notes (default True).
        """
        return asdict(writer.move_note(source, destination, update_links))

    @mcp.tool()
    def create_folder(path: str) -> dict:
        """Create a folder in the vault. Automatically creates a <folder_name>.md summary document.

        Args:
            path: Vault-relative folder path.
        """
        writer.create_folder(path)
        return {"created": path}

    @mcp.tool()
    def delete_folder(path: str, force: bool = False) -> dict:
        """Delete a folder from the vault.

        Args:
            path: Vault-relative folder path.
            force: If True, delete even if non-empty (default False).
        """
        writer.delete_folder(path, force)
        return {"deleted": path}
