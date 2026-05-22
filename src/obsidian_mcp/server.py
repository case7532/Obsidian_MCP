"""MCP server entry point for Obsidian vault."""

import argparse
import logging
import sys

from mcp.server.fastmcp import FastMCP

from obsidian_mcp.advanced_features import AdvancedFeatures
from obsidian_mcp.exceptions import ObsidianMCPError, VaultError
from obsidian_mcp.note_reader import NoteReader
from obsidian_mcp.note_writer import NoteWriter
from obsidian_mcp.tools.advanced_tools import register_advanced_tools
from obsidian_mcp.tools.read_tools import register_read_tools
from obsidian_mcp.tools.write_tools import register_write_tools
from obsidian_mcp.vault_config import VaultConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def _build_server(vault_path: str | None = None) -> FastMCP:
    config = VaultConfig.from_env_or_arg(vault_path)

    mcp = FastMCP("obsidian-mcp")
    reader = NoteReader(config)
    writer = NoteWriter(config, reader)
    advanced = AdvancedFeatures(config, reader)

    register_read_tools(mcp, reader)
    register_write_tools(mcp, writer)
    register_advanced_tools(mcp, advanced)

    logger.info("obsidian-mcp ready — vault: %s", config.vault_path)
    return mcp


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP server for Obsidian vault")
    parser.add_argument(
        "--vault",
        metavar="PATH",
        help="Path to Obsidian vault (overrides OBSIDIAN_VAULT_PATH env var)",
    )
    args = parser.parse_args()

    try:
        mcp = _build_server(args.vault)
    except VaultError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
