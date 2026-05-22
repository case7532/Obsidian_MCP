# Component Methods — Obsidian MCP Server

> Data models và method signatures chi tiết cho mỗi component.

## Contents
- [C-02: VaultConfig](#c-02-vaultconfig)
- [C-03: PathUtils](#c-03-pathutils)
- [C-04: NoteReader](#c-04-notereader)
- [C-05: NoteWriter](#c-05-notewriter)
- [C-06: AdvancedFeatures](#c-06-advancedfeatures)
- [Data Models](#data-models)
- [Custom Exceptions](#custom-exceptions)

## C-02: VaultConfig

```python
class VaultConfig:
    vault_path: Path

    @classmethod
    def from_env_or_arg(cls, vault_path: str | None = None) -> "VaultConfig": ...
    def validate(self) -> None: ...  # raises VaultError if invalid
    def resolve_path(self, relative: str) -> Path: ...  # vault_path / relative
    def to_relative(self, absolute: Path) -> str: ...   # relative to vault_path
```

---

## C-03: PathUtils

```python
def safe_vault_path(vault_path: Path, user_input: str) -> Path:
    """Resolve user_input relative to vault_path; raise PathTraversalError if outside."""

def normalize_note_path(path: str) -> str:
    """Strip .., normalize separators, ensure .md extension."""

def sanitize_filename(name: str) -> str:
    """Remove/replace chars invalid in filenames."""

def is_markdown(path: Path) -> bool: ...
def is_canvas(path: Path) -> bool: ...
```

---

## C-04: NoteReader

```python
class NoteReader:
    def __init__(self, config: VaultConfig) -> None: ...

    def read_note(self, path: str) -> NoteContent: ...
    # Returns: raw markdown + parsed frontmatter

    def list_notes(self, folder: str | None = None, tag: str | None = None) -> list[NoteInfo]: ...
    # Returns: list of {path, title, tags, modified_at}

    def search_notes(self, query: str, limit: int = 20) -> list[SearchResult]: ...
    # Returns: list of {path, title, excerpt, score}

    def get_metadata(self, path: str) -> NoteMetadata: ...
    # Returns: frontmatter, tags, created_at, modified_at, size

    def get_backlinks(self, path: str) -> list[str]: ...
    # Returns: list of note paths that link to `path`

    def get_outgoing_links(self, path: str) -> list[WikiLink]: ...
    # Returns: list of {display, target, resolved_path}

    def read_canvas(self, path: str) -> dict: ...
    # Returns: raw canvas JSON parsed as dict
```

---

## C-05: NoteWriter

```python
class NoteWriter:
    def __init__(self, config: VaultConfig) -> None: ...

    def create_note(self, path: str, content: str, frontmatter: dict | None = None) -> NoteInfo: ...
    # Raises NoteExistsError if already exists

    def update_note(self, path: str, content: str, mode: Literal["replace", "append"] = "replace") -> NoteInfo: ...

    def delete_note(self, path: str) -> None: ...

    def move_note(self, source: str, destination: str, update_links: bool = True) -> NoteInfo: ...
    # Atomic: write new → verify → delete old

    def create_folder(self, path: str) -> None: ...

    def delete_folder(self, path: str, force: bool = False) -> None: ...
    # force=False raises FolderNotEmptyError if has content
```

---

## C-06: AdvancedFeatures

```python
class AdvancedFeatures:
    def __init__(self, config: VaultConfig) -> None: ...

    def get_graph_data(self) -> GraphData: ...
    # Returns: {nodes: [{id, title, tags}], edges: [{source, target}]}

    def get_all_tags(self) -> list[TagInfo]: ...
    # Returns: [{tag, count, notes: [paths]}]

    def get_dataview_fields(self, path: str) -> dict[str, str]: ...
    # Parse `key:: value` inline fields from note

    def get_daily_note(self, date: str) -> NoteContent | None: ...
    # date: ISO format YYYY-MM-DD

    def list_attachments(self, folder: str | None = None) -> list[AttachmentInfo]: ...
    # Returns non-markdown, non-canvas files
```

---

## Data Models

```python
# src/obsidian_mcp/models.py

@dataclass
class NoteContent:
    path: str           # vault-relative
    raw: str            # full markdown content
    frontmatter: dict   # parsed YAML frontmatter
    body: str           # markdown without frontmatter block

@dataclass
class NoteInfo:
    path: str
    title: str          # filename without .md, or frontmatter title
    tags: list[str]
    modified_at: str    # ISO 8601

@dataclass
class NoteMetadata:
    path: str
    frontmatter: dict
    tags: list[str]
    created_at: str | None
    modified_at: str
    size_bytes: int

@dataclass
class SearchResult:
    path: str
    title: str
    excerpt: str        # snippet around match
    score: float        # relevance 0.0-1.0

@dataclass
class WikiLink:
    display: str        # text shown [[display|target]] or [[target]]
    target: str         # link target
    resolved_path: str | None  # absolute path if resolved

@dataclass
class GraphData:
    nodes: list[dict]   # {id, title, tags, path}
    edges: list[dict]   # {source, target}

@dataclass
class TagInfo:
    tag: str
    count: int
    notes: list[str]

@dataclass
class AttachmentInfo:
    path: str
    name: str
    extension: str
    size_bytes: int
    modified_at: str
```

---

## Custom Exceptions

```python
# src/obsidian_mcp/exceptions.py

class ObsidianMCPError(Exception): ...
class VaultError(ObsidianMCPError): ...         # vault not found / invalid
class PathTraversalError(ObsidianMCPError): ... # path goes outside vault
class NoteNotFoundError(ObsidianMCPError): ...
class NoteExistsError(ObsidianMCPError): ...
class FolderNotEmptyError(ObsidianMCPError): ...
```

## Related
- [[components]]
- [[services]]
- [[application-design]]
