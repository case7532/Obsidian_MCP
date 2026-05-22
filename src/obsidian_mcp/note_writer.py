"""Note writer — all write/mutation operations on an Obsidian vault."""

import logging
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml

from obsidian_mcp.exceptions import (
    FolderNotEmptyError,
    NoteExistsError,
    NoteNotFoundError,
    ObsidianMCPError,
)
from obsidian_mcp.models import NoteInfo
from obsidian_mcp.note_reader import NoteReader, _parse_frontmatter
from obsidian_mcp.path_utils import safe_vault_path, sanitize_filename, to_vault_relative
from obsidian_mcp.vault_config import VaultConfig

logger = logging.getLogger(__name__)

_WIKILINK_RE = re.compile(r"\[\[([^\[\]]+)\]\]")


def _serialize_frontmatter(fm: dict) -> str:
    return "---\n" + yaml.dump(fm, allow_unicode=True, default_flow_style=False) + "---\n"


def _mtime_iso(path: Path) -> str:
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _build_document_template(title: str, description: str, content: str, links: list[str]) -> str:
    """Wrap content with standard document format: title, description, index, links."""
    lines = [f"# {title}", "", f"> {description}", ""]

    # Index — collect H2 headings from content
    headings = [ln.lstrip("# ").strip() for ln in content.splitlines() if ln.startswith("## ")]
    if headings:
        lines.append("## Contents")
        lines.extend(f"- [{h}](#{h.lower().replace(' ', '-')})" for h in headings)
        lines.append("")

    lines.append(content)

    if links:
        lines.append("")
        lines.append("## Related")
        lines.extend(f"- [[{link}]]" for link in links)

    return "\n".join(lines)


def _infer_folder(vault_path: Path, title: str, tags: list[str], content: str) -> str:
    """Infer best folder from existing vault structure using title/tags/content keywords."""
    # Collect existing top-level folders (exclude hidden)
    folders = [
        p.name for p in vault_path.iterdir()
        if p.is_dir() and not p.name.startswith(".") and p.name != "_index"
    ]
    if not folders:
        # Derive from first tag or title word
        if tags:
            return tags[0].replace("/", "-")
        return title.split()[0].lower() if title.split() else "notes"

    # Score each folder: count keyword matches in (title + tags + first 200 chars of content)
    text = " ".join([title.lower()] + tags + [content[:200].lower()])
    scores: dict[str, int] = {}
    for folder in folders:
        key = folder.lower().replace("-", " ").replace("_", " ")
        scores[folder] = sum(1 for word in key.split() if word in text)

    best = max(scores, key=lambda f: scores[f])
    # If no match at all, create new folder from first tag or title word
    if scores[best] == 0:
        candidate = tags[0].replace("/", "-") if tags else title.split()[0].lower()
        return candidate if candidate else "notes"
    return best


class NoteWriter:
    def __init__(self, config: VaultConfig, reader: NoteReader) -> None:
        self._config = config
        self._reader = reader

    def _safe_resolve(self, user_path: str) -> Path:
        return safe_vault_path(self._config.vault_path, user_path)

    def _note_info(self, abs_path: Path) -> NoteInfo:
        try:
            raw = abs_path.read_text(encoding="utf-8")
        except OSError:
            raw = ""
        fm, body = _parse_frontmatter(raw)
        from obsidian_mcp.note_reader import _extract_tags
        tags = _extract_tags(fm, body)
        title = str(fm.get("title") or abs_path.stem)
        return NoteInfo(
            path=to_vault_relative(self._config.vault_path, abs_path),
            title=title,
            tags=tags,
            modified_at=_mtime_iso(abs_path),
        )

    def _update_folder_index(self, folder_abs: Path) -> None:
        """Add missing notes to folder's _index.md — preserves existing descriptions."""
        index_path = folder_abs / "_index.md"
        if not index_path.exists():
            return
        raw = index_path.read_text(encoding="utf-8")

        # Find which stems are already linked in the index
        linked_stems = {m.group(1).split("|")[0].split("#")[0].strip() for m in _WIKILINK_RE.finditer(raw)}

        # Collect notes not yet in index
        missing = [
            p for p in sorted(folder_abs.glob("*.md"))
            if p.name != "_index.md" and p.stem not in linked_stems
        ]
        if not missing:
            return

        new_entries = "\n".join(f"- [[{p.stem}]] — {p.stem}" for p in missing)

        # Append inside ## Documents section if present, else append at end
        if "## Documents" in raw:
            # Insert before the next ## heading or end of file
            parts = raw.split("## Documents", 1)
            after = parts[1]
            next_section = re.search(r"\n##\s", after)
            if next_section:
                insert_at = next_section.start()
                parts[1] = after[:insert_at].rstrip("\n") + "\n" + new_entries + "\n" + after[insert_at:]
            else:
                parts[1] = after.rstrip("\n") + "\n" + new_entries + "\n"
            updated = "## Documents".join(parts)
        else:
            updated = raw.rstrip("\n") + "\n\n## Documents\n\n" + new_entries + "\n"

        index_path.write_text(updated, encoding="utf-8")

    def create_note(
        self,
        path: str | None,
        content: str,
        frontmatter: dict | None = None,
        title: str | None = None,
        description: str = "",
        links: list[str] | None = None,
    ) -> NoteInfo:
        """Create a new note with standard format (title, description, index, links).

        If path is None, infer folder from content/tags and save there.
        Raises NoteExistsError if already exists.
        """
        fm = frontmatter or {}
        tags_from_fm: list[str] = fm.get("tags", []) if isinstance(fm.get("tags"), list) else (
            [fm["tags"]] if isinstance(fm.get("tags"), str) else []
        )

        # Resolve title
        doc_title = title or str(fm.get("title", "")) or "Untitled"
        doc_desc = description or str(fm.get("description", "")) or doc_title

        # Infer path if not given
        if path is None:
            folder = _infer_folder(self._config.vault_path, doc_title, tags_from_fm, content)
            slug = sanitize_filename(doc_title) or "note"
            path = f"{folder}/{slug}.md"
            # Create folder + index if new
            folder_abs = self._config.vault_path / folder
            if not folder_abs.exists():
                self.create_folder(folder)

        abs_path = self._safe_resolve(path)
        if abs_path.exists():
            raise NoteExistsError(f"Note already exists: {path}")
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        # Build formatted body
        formatted = _build_document_template(doc_title, doc_desc, content, links or [])

        if fm:
            body = _serialize_frontmatter(fm) + formatted
        else:
            body = formatted

        try:
            abs_path.write_text(body, encoding="utf-8")
        except OSError as e:
            raise ObsidianMCPError("Cannot write file") from e

        # Update folder index
        self._update_folder_index(abs_path.parent)

        logger.info("Created note: %s", to_vault_relative(self._config.vault_path, abs_path))
        return self._note_info(abs_path)

    def update_note(
        self,
        path: str,
        content: str,
        mode: str = "replace",
    ) -> NoteInfo:
        """Update a note's content. mode: 'replace' or 'append'."""
        abs_path = self._safe_resolve(path)
        if not abs_path.exists():
            raise NoteNotFoundError(f"Note not found: {path}")
        try:
            if mode == "append":
                existing = abs_path.read_text(encoding="utf-8")
                body = existing.rstrip("\n") + "\n" + content
            else:
                body = content
            abs_path.write_text(body, encoding="utf-8")
        except OSError as e:
            raise ObsidianMCPError("Cannot write file") from e
        return self._note_info(abs_path)

    def delete_note(self, path: str) -> None:
        """Delete a note."""
        abs_path = self._safe_resolve(path)
        if not abs_path.exists():
            raise NoteNotFoundError(f"Note not found: {path}")
        try:
            abs_path.unlink()
        except OSError as e:
            raise ObsidianMCPError("Cannot delete file") from e
        logger.info("Deleted note: %s", path)

    def move_note(
        self,
        source: str,
        destination: str,
        update_links: bool = True,
    ) -> NoteInfo:
        """Move/rename a note. Optionally update backlinks in other notes."""
        src = self._safe_resolve(source)
        dst = self._safe_resolve(destination)
        if not src.exists():
            raise NoteNotFoundError(f"Note not found: {source}")
        if dst.exists():
            raise NoteExistsError(f"Destination already exists: {destination}")

        dst.parent.mkdir(parents=True, exist_ok=True)
        # Atomic: copy then delete
        try:
            dst.write_bytes(src.read_bytes())
            src.unlink()
        except OSError as e:
            # Rollback if partial
            if dst.exists():
                dst.unlink()
            raise ObsidianMCPError("Cannot move file") from e

        if update_links:
            self._update_backlinks(src.stem, dst.stem)

        logger.info("Moved note: %s -> %s", source, destination)
        return self._note_info(dst)

    def _update_backlinks(self, old_stem: str, new_stem: str) -> None:
        """Replace [[old_stem]] references with [[new_stem]] across vault."""
        pattern = re.compile(r"\[\[" + re.escape(old_stem) + r"(\|[^\]]+|#[^\]]+)?\]\]")
        for md in self._config.vault_path.rglob("*.md"):
            if ".obsidian" in md.parts:
                continue
            try:
                raw = md.read_text(encoding="utf-8")
            except OSError:
                continue
            if old_stem not in raw:
                continue

            def replace_link(m: re.Match) -> str:
                suffix = m.group(1) or ""
                return f"[[{new_stem}{suffix}]]"

            updated = pattern.sub(replace_link, raw)
            if updated != raw:
                md.write_text(updated, encoding="utf-8")

    def _create_folder_index(self, folder_abs: Path, folder_name: str) -> None:
        """Create _index.md summary document for a new folder."""
        index_path = folder_abs / "_index.md"
        if index_path.exists():
            return
        title = folder_name.replace("-", " ").replace("_", " ").title()
        content = "\n".join([
            f"# {title}",
            "",
            f"> Thư mục **{title}** — tóm tắt tài liệu để hỗ trợ graph view.",
            "",
            "## Documents",
            "",
            "<!-- Danh sách tài liệu được cập nhật tự động khi thêm note mới -->",
            "",
            "## Related",
            "",
        ])
        index_path.write_text(content, encoding="utf-8")

    def create_folder(self, path: str) -> None:
        """Create a folder in the vault and generate an _index.md summary."""
        abs_path = self._safe_resolve(path)
        is_new = not abs_path.exists()
        try:
            abs_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise ObsidianMCPError("Cannot create folder") from e
        if is_new:
            self._create_folder_index(abs_path, abs_path.name)

    def delete_folder(self, path: str, force: bool = False) -> None:
        """Delete a folder. Raises FolderNotEmptyError if non-empty and force=False."""
        abs_path = self._safe_resolve(path)
        if not abs_path.exists():
            raise NoteNotFoundError(f"Folder not found: {path}")
        if not abs_path.is_dir():
            raise ObsidianMCPError("Path is not a directory")
        if not force and any(abs_path.iterdir()):
            raise FolderNotEmptyError(f"Folder is not empty: {path}")
        try:
            shutil.rmtree(abs_path)
        except OSError as e:
            raise ObsidianMCPError("Cannot delete folder") from e
