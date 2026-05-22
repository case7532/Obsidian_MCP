"""Shared data models for obsidian-mcp."""

from dataclasses import dataclass, field


@dataclass
class NoteContent:
    path: str          # vault-relative path, e.g. "folder/note.md"
    raw: str           # full file content
    frontmatter: dict  # parsed YAML frontmatter (empty dict if none)
    body: str          # markdown body without frontmatter block


@dataclass
class NoteInfo:
    path: str          # vault-relative
    title: str         # frontmatter["title"] or filename stem
    tags: list[str]    # normalized tags (no # prefix, lowercase)
    modified_at: str   # ISO 8601


@dataclass
class NoteMetadata:
    path: str
    frontmatter: dict
    tags: list[str]
    created_at: str | None  # ISO 8601 or None if unavailable
    modified_at: str        # ISO 8601
    size_bytes: int


@dataclass
class WikiLink:
    display: str            # text shown to reader
    target: str             # raw link target
    resolved_path: str | None  # vault-relative path if note exists


@dataclass
class SearchResult:
    path: str
    title: str
    excerpt: str   # ~100 chars around first match
    score: float   # 0.0–1.0


@dataclass
class GraphData:
    nodes: list[dict] = field(default_factory=list)  # {id, title, path, tags}
    edges: list[dict] = field(default_factory=list)  # {source, target}


@dataclass
class TagInfo:
    tag: str
    count: int
    notes: list[str]  # vault-relative paths


@dataclass
class AttachmentInfo:
    path: str        # vault-relative
    name: str        # filename with extension
    extension: str   # lowercase, no dot
    size_bytes: int
    modified_at: str  # ISO 8601
