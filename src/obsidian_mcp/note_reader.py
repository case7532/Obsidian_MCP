"""Note reader — all read operations on an Obsidian vault."""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

from obsidian_mcp.exceptions import NoteNotFoundError, ObsidianMCPError
from obsidian_mcp.models import (
    NoteContent,
    NoteInfo,
    NoteMetadata,
    SearchResult,
    WikiLink,
)
from obsidian_mcp.path_utils import is_canvas, is_markdown, safe_vault_path, to_vault_relative
from obsidian_mcp.vault_config import VaultConfig

logger = logging.getLogger(__name__)

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
_WIKILINK_RE = re.compile(r"\[\[([^\[\]]+)\]\]")
_INLINE_TAG_RE = re.compile(r"(?<!\S)#([a-zA-Z0-9_\-/]+)")
_FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)


def _parse_frontmatter(raw: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) from raw note content."""
    m = _FRONTMATTER_RE.match(raw)
    if not m:
        return {}, raw
    try:
        fm = yaml.safe_load(m.group(1)) or {}
        if not isinstance(fm, dict):
            fm = {}
    except yaml.YAMLError:
        logger.warning("YAML parse error in frontmatter; treating as empty")
        fm = {}
    body = raw[m.end():]
    return fm, body


def _extract_tags(frontmatter: dict, body: str) -> list[str]:
    """Extract and normalize tags from frontmatter and inline #tags."""
    tags: set[str] = set()

    # Frontmatter tags
    fm_tags = frontmatter.get("tags", [])
    if isinstance(fm_tags, str):
        fm_tags = [fm_tags]
    for t in (fm_tags or []):
        tags.add(str(t).lstrip("#").lower())

    # Inline tags (exclude fenced code blocks)
    clean_body = _FENCED_CODE_RE.sub("", body)
    for m in _INLINE_TAG_RE.finditer(clean_body):
        tags.add(m.group(1).lower())

    return sorted(tags)


def _parse_wikilinks(text: str, vault_path: Path) -> list[WikiLink]:
    """Parse all [[wikilinks]] from text."""
    links = []
    for m in _WIKILINK_RE.finditer(text):
        inner = m.group(1)
        # Split alias: [[target|alias]] or [[target#heading|alias]]
        if "|" in inner:
            target_part, alias = inner.split("|", 1)
        else:
            target_part, alias = inner, None
        # Strip heading fragment
        target = target_part.split("#")[0].strip()
        display = alias.strip() if alias else target

        # Attempt to resolve
        resolved = _resolve_wikilink(target, vault_path)
        links.append(WikiLink(display=display, target=target, resolved_path=resolved))
    return links


def _resolve_wikilink(target: str, vault_path: Path) -> str | None:
    """Find the vault-relative path for a wiki-link target."""
    # Direct match: target already has .md or is a path
    candidates = [
        vault_path / f"{target}.md",
        vault_path / target,
    ]
    for c in candidates:
        if c.exists():
            return to_vault_relative(vault_path, c)

    # BFS search by filename stem
    target_stem = Path(target).stem
    for md in vault_path.rglob("*.md"):
        if md.stem == target_stem:
            return to_vault_relative(vault_path, md)
    return None


def _mtime_iso(path: Path) -> str:
    """Return file mtime as ISO 8601 UTC string."""
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


class NoteReader:
    def __init__(self, config: VaultConfig) -> None:
        self._config = config

    def _safe_resolve(self, user_path: str) -> Path:
        return safe_vault_path(self._config.vault_path, user_path)

    def read_note(self, path: str) -> NoteContent:
        """Read a note and parse its frontmatter and body."""
        abs_path = self._safe_resolve(path)
        if not abs_path.exists():
            raise NoteNotFoundError(f"Note not found: {path}")
        try:
            raw = abs_path.read_text(encoding="utf-8")
        except OSError as e:
            raise ObsidianMCPError("Cannot read file") from e
        fm, body = _parse_frontmatter(raw)
        return NoteContent(
            path=to_vault_relative(self._config.vault_path, abs_path),
            raw=raw,
            frontmatter=fm,
            body=body,
        )

    def list_notes(self, folder: str | None = None, tag: str | None = None) -> list[NoteInfo]:
        """List notes, optionally filtered by folder prefix or tag."""
        results = []
        norm_tag = tag.lstrip("#").lower() if tag else None

        for md in self._config.vault_path.rglob("*.md"):
            # Exclude .obsidian internals
            if ".obsidian" in md.parts:
                continue
            rel = to_vault_relative(self._config.vault_path, md)

            if folder and not rel.startswith(folder.strip("/") + "/"):
                if rel != folder.strip("/"):
                    continue

            try:
                raw = md.read_text(encoding="utf-8")
            except OSError:
                continue

            fm, body = _parse_frontmatter(raw)
            tags = _extract_tags(fm, body)

            if norm_tag and norm_tag not in tags:
                continue

            title = fm.get("title") or md.stem
            results.append(NoteInfo(
                path=rel,
                title=str(title),
                tags=tags,
                modified_at=_mtime_iso(md),
            ))
        return results

    def search_notes(self, query: str, limit: int = 20) -> list[SearchResult]:
        """Full-text search across all notes."""
        limit = min(limit, 100)
        q = query.lower()
        results = []

        for md in self._config.vault_path.rglob("*.md"):
            if ".obsidian" in md.parts:
                continue
            try:
                raw = md.read_text(encoding="utf-8")
            except OSError:
                continue

            raw_lower = raw.lower()
            if q not in raw_lower:
                continue

            rel = to_vault_relative(self._config.vault_path, md)
            fm, body = _parse_frontmatter(raw)
            title = str(fm.get("title") or md.stem)
            score = 1.0 if q in title.lower() else 0.5

            # Excerpt around first match
            idx = raw_lower.index(q)
            start = max(0, idx - 50)
            end = min(len(raw), idx + 50)
            excerpt = ("..." if start > 0 else "") + raw[start:end].strip() + ("..." if end < len(raw) else "")

            results.append(SearchResult(path=rel, title=title, excerpt=excerpt, score=score))
            if len(results) >= limit:
                break

        return sorted(results, key=lambda r: -r.score)

    def get_metadata(self, path: str) -> NoteMetadata:
        """Get metadata for a note."""
        abs_path = self._safe_resolve(path)
        if not abs_path.exists():
            raise NoteNotFoundError(f"Note not found: {path}")
        try:
            raw = abs_path.read_text(encoding="utf-8")
            stat = abs_path.stat()
        except OSError as e:
            raise ObsidianMCPError("Cannot read file") from e

        fm, body = _parse_frontmatter(raw)
        tags = _extract_tags(fm, body)
        return NoteMetadata(
            path=to_vault_relative(self._config.vault_path, abs_path),
            frontmatter=fm,
            tags=tags,
            created_at=None,  # not reliably available cross-platform
            modified_at=_mtime_iso(abs_path),
            size_bytes=stat.st_size,
        )

    def get_backlinks(self, path: str) -> list[str]:
        """Return vault-relative paths of notes that link to `path`."""
        abs_path = self._safe_resolve(path)
        target_stem = abs_path.stem
        target_rel = to_vault_relative(self._config.vault_path, abs_path)
        backlinks = []

        for md in self._config.vault_path.rglob("*.md"):
            if ".obsidian" in md.parts or md == abs_path:
                continue
            try:
                raw = md.read_text(encoding="utf-8")
            except OSError:
                continue
            # Match [[stem]], [[path/stem]], [[stem|alias]], [[path/stem|alias]]
            for m in _WIKILINK_RE.finditer(raw):
                inner = m.group(1).split("|")[0].split("#")[0].strip()
                if inner == target_stem or inner == target_rel or inner == target_rel.removesuffix(".md"):
                    backlinks.append(to_vault_relative(self._config.vault_path, md))
                    break
        return backlinks

    def get_outgoing_links(self, path: str) -> list[WikiLink]:
        """Return all wiki-links in a note."""
        note = self.read_note(path)
        return _parse_wikilinks(note.raw, self._config.vault_path)

    def read_canvas(self, path: str) -> dict:
        """Read and parse a .canvas file."""
        abs_path = self._safe_resolve(path)
        if not abs_path.exists():
            raise NoteNotFoundError(f"Canvas not found: {path}")
        try:
            raw = abs_path.read_text(encoding="utf-8")
        except OSError as e:
            raise ObsidianMCPError("Cannot read file") from e
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise NoteNotFoundError("Invalid canvas file") from e
