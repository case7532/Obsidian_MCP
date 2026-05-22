"""Advanced Obsidian features — graph, tags, dataview, daily notes, attachments."""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from obsidian_mcp.exceptions import NoteNotFoundError, ObsidianMCPError
from obsidian_mcp.models import AttachmentInfo, GraphData, TagInfo
from obsidian_mcp.note_reader import NoteReader, _extract_tags, _parse_frontmatter, _WIKILINK_RE
from obsidian_mcp.path_utils import is_markdown, safe_vault_path, to_vault_relative
from obsidian_mcp.vault_config import VaultConfig

logger = logging.getLogger(__name__)

_DATAVIEW_FIELD_RE = re.compile(r"^([^:\n]+)::\s*(.+)$", re.MULTILINE)
_MARKDOWN_EXTS = {".md"}
_ATTACHMENT_EXTS_EXCLUDE = {".md", ".canvas"}


def _moment_to_filename(iso_date: str, moment_fmt: str) -> str:
    """Convert ISO date string to filename using a moment.js format string."""
    try:
        from datetime import date as date_type
        d = date_type.fromisoformat(iso_date)
        # Map common moment.js tokens to strftime
        py_fmt = (moment_fmt
                  .replace("YYYY", "%Y")
                  .replace("YY", "%y")
                  .replace("MM", "%m")
                  .replace("DD", "%d")
                  .replace("Do", "%d"))
        return d.strftime(py_fmt)
    except (ValueError, AttributeError):
        return iso_date  # fallback to ISO


def _mtime_iso(path: Path) -> str:
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


class AdvancedFeatures:
    def __init__(self, config: VaultConfig, reader: NoteReader) -> None:
        self._config = config
        self._reader = reader

    def get_graph_data(self) -> GraphData:
        """Build vault graph: nodes = notes, edges = wiki-links."""
        nodes = []
        edges = []

        for md in self._config.vault_path.rglob("*.md"):
            if ".obsidian" in md.parts:
                continue
            rel = to_vault_relative(self._config.vault_path, md)
            try:
                raw = md.read_text(encoding="utf-8")
            except OSError:
                continue
            fm, body = _parse_frontmatter(raw)
            tags = _extract_tags(fm, body)
            title = str(fm.get("title") or md.stem)
            nodes.append({"id": rel, "title": title, "path": rel, "tags": tags})

            for m in _WIKILINK_RE.finditer(raw):
                inner = m.group(1).split("|")[0].split("#")[0].strip()
                # Attempt to resolve target to vault-relative path
                from obsidian_mcp.note_reader import _resolve_wikilink
                resolved = _resolve_wikilink(inner, self._config.vault_path)
                target = resolved or (inner + ".md")
                edges.append({"source": rel, "target": target})

        return GraphData(nodes=nodes, edges=edges)

    def get_all_tags(self) -> list[TagInfo]:
        """Return all tags across vault with usage counts."""
        tag_map: dict[str, list[str]] = {}

        for md in self._config.vault_path.rglob("*.md"):
            if ".obsidian" in md.parts:
                continue
            try:
                raw = md.read_text(encoding="utf-8")
            except OSError:
                continue
            fm, body = _parse_frontmatter(raw)
            tags = _extract_tags(fm, body)
            rel = to_vault_relative(self._config.vault_path, md)
            for tag in tags:
                tag_map.setdefault(tag, []).append(rel)

        return [
            TagInfo(tag=tag, count=len(notes), notes=sorted(notes))
            for tag, notes in sorted(tag_map.items())
        ]

    def get_dataview_fields(self, path: str) -> dict[str, str]:
        """Parse Dataview inline fields (key:: value) from a note."""
        abs_path = safe_vault_path(self._config.vault_path, path)
        if not abs_path.exists():
            raise NoteNotFoundError(f"Note not found: {path}")
        try:
            raw = abs_path.read_text(encoding="utf-8")
        except OSError as e:
            raise ObsidianMCPError("Cannot read file") from e
        return {
            m.group(1).strip(): m.group(2).strip()
            for m in _DATAVIEW_FIELD_RE.finditer(raw)
        }

    def get_daily_note(self, date: str) -> dict | None:
        """Get daily note for a given date (YYYY-MM-DD).

        Checks common daily note locations:
        1. Vault root: {date}.md
        2. Daily Notes folder: Daily Notes/{date}.md
        3. Reads format from .obsidian/daily-notes.json if present
        """
        # Try to read daily notes plugin config
        config_path = self._config.vault_path / ".obsidian" / "daily-notes.json"
        folder = ""
        fmt = "YYYY-MM-DD"
        if config_path.exists():
            try:
                cfg = json.loads(config_path.read_text())
                folder = cfg.get("folder", "")
                fmt = cfg.get("format", "YYYY-MM-DD")
            except (json.JSONDecodeError, OSError):
                pass

        # Convert moment.js format to Python strftime then format date
        filename = _moment_to_filename(date, fmt)

        candidates = [
            self._config.vault_path / f"{filename}.md",
            self._config.vault_path / f"{date}.md",  # fallback: ISO format
            self._config.vault_path / "Daily Notes" / f"{filename}.md",
            self._config.vault_path / "Daily Notes" / f"{date}.md",
        ]
        if folder:
            candidates.insert(0, self._config.vault_path / folder / f"{date}.md")
            candidates.insert(0, self._config.vault_path / folder / f"{filename}.md")

        # Fallback: search vault for either filename pattern
        for md in self._config.vault_path.rglob("*.md"):
            if md.stem in (filename, date) and md not in candidates:
                candidates.append(md)

        for candidate in candidates:
            if candidate.exists():
                rel = to_vault_relative(self._config.vault_path, candidate)
                try:
                    note = self._reader.read_note(rel)
                    from dataclasses import asdict
                    return asdict(note)
                except Exception:
                    continue
        return None

    def list_attachments(self, folder: str | None = None) -> list[AttachmentInfo]:
        """List non-markdown, non-canvas files in the vault."""
        results = []
        search_root = self._config.vault_path
        if folder:
            search_root = safe_vault_path(self._config.vault_path, folder)

        for f in search_root.rglob("*"):
            if not f.is_file():
                continue
            if ".obsidian" in f.parts:
                continue
            if f.suffix.lower() in _ATTACHMENT_EXTS_EXCLUDE:
                continue
            try:
                stat = f.stat()
            except OSError:
                continue
            results.append(AttachmentInfo(
                path=to_vault_relative(self._config.vault_path, f),
                name=f.name,
                extension=f.suffix.lstrip(".").lower(),
                size_bytes=stat.st_size,
                modified_at=_mtime_iso(f),
            ))
        return results
