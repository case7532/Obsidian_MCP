"""MCP read tool handlers — thin wrappers around NoteReader."""

import logging
from dataclasses import asdict

from mcp.server.fastmcp import FastMCP

from obsidian_mcp.exceptions import ObsidianMCPError
from obsidian_mcp.note_reader import NoteReader

logger = logging.getLogger(__name__)


def register_read_tools(mcp: FastMCP, reader: NoteReader) -> None:
    """Register all read tools on the MCP server."""

    @mcp.tool()
    def read_note(path: str) -> dict:
        """Read a note's content and frontmatter.

        Args:
            path: Vault-relative path to the note (e.g. 'folder/note.md').
        """
        return asdict(reader.read_note(path))

    @mcp.tool()
    def list_notes(folder: str | None = None, tag: str | None = None) -> list[dict]:
        """List notes in the vault, optionally filtered by folder or tag.

        Args:
            folder: Optional vault-relative folder path to filter by.
            tag: Optional tag to filter by (with or without # prefix).
        """
        return [asdict(n) for n in reader.list_notes(folder=folder, tag=tag)]

    @mcp.tool()
    def search_notes(query: str, limit: int = 20) -> list[dict]:
        """Full-text search across all notes.

        Args:
            query: Search query string.
            limit: Maximum number of results (default 20, max 100).
        """
        return [asdict(r) for r in reader.search_notes(query, limit=limit)]

    @mcp.tool()
    def get_note_metadata(path: str) -> dict:
        """Get metadata for a note (frontmatter, tags, size, dates).

        Args:
            path: Vault-relative path to the note.
        """
        return asdict(reader.get_metadata(path))

    @mcp.tool()
    def get_backlinks(path: str) -> list[str]:
        """Get all notes that link to this note.

        Args:
            path: Vault-relative path to the target note.
        """
        return reader.get_backlinks(path)

    @mcp.tool()
    def get_outgoing_links(path: str) -> list[dict]:
        """Get all wiki-links in a note.

        Args:
            path: Vault-relative path to the note.
        """
        return [asdict(l) for l in reader.get_outgoing_links(path)]

    @mcp.tool()
    def read_canvas(path: str) -> dict:
        """Read an Obsidian Canvas file.

        Args:
            path: Vault-relative path to the .canvas file.
        """
        return reader.read_canvas(path)
