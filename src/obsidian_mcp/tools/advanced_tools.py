"""MCP advanced tool handlers."""

import logging
from dataclasses import asdict

from mcp.server.fastmcp import FastMCP

from obsidian_mcp.advanced_features import AdvancedFeatures

logger = logging.getLogger(__name__)


def register_advanced_tools(mcp: FastMCP, advanced: AdvancedFeatures) -> None:

    @mcp.tool()
    def get_graph_data() -> dict:
        """Get the vault's link graph (nodes = notes, edges = wiki-links)."""
        return asdict(advanced.get_graph_data())

    @mcp.tool()
    def get_all_tags() -> list[dict]:
        """Get all tags in the vault with usage counts."""
        return [asdict(t) for t in advanced.get_all_tags()]

    @mcp.tool()
    def get_dataview_fields(path: str) -> dict:
        """Get Dataview inline fields (key:: value) from a note.

        Args:
            path: Vault-relative path to the note.
        """
        return advanced.get_dataview_fields(path)

    @mcp.tool()
    def get_daily_note(date: str) -> dict | None:
        """Get the daily note for a given date.

        Args:
            date: Date in YYYY-MM-DD format.
        """
        return advanced.get_daily_note(date)

    @mcp.tool()
    def list_attachments(folder: str | None = None) -> list[dict]:
        """List attachments (images, PDFs, etc.) in the vault.

        Args:
            folder: Optional vault-relative folder to search within.
        """
        return [asdict(a) for a in advanced.list_attachments(folder)]
