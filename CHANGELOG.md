# Changelog

All notable changes to this project will be documented in this file.

## [0.1.2] - 2026-05-22

### Added
- `bm25_search(query, limit)` tool — BM25-ranked search (k1=1.5, b=0.75), multi-word queries, returns JSON with `path`, `title`, `score`, `matched_terms`, and per-term `excerpts`. Faster and more relevant than `search_notes` for multi-keyword queries.

### Changed
- Folder introduction file renamed from `_index.md` to `<folder_name>.md` (e.g. `recipes/recipes.md`). Applies to both `create_folder` and `_update_folder_index`.
- `create_note`: folder index update now checks for existing links before appending — preserves manually-written descriptions, only adds missing entries.
- `update_note`: after writing, automatically syncs the note's entry in `<folder_name>.md`:
  - If entry exists → updates the description with a fresh summary extracted from the new content.
  - If entry missing → adds a new entry.
  - If no folder index exists → no-op.
  - Summary extraction priority: blockquote `>` line → first non-heading text line (max 120 chars).

### Tests
- Added 3 new tests for `update_note` folder index sync behavior (88 total, all passing).

## [0.1.1] - 2026-05-22

### Added

**Write tools**
- `create_note` — create a note with standard format: optional frontmatter, H1 title, description, body, and Related wikilinks section; auto-infers path from content/tags if omitted
- `update_note` — replace or append content to an existing note
- `delete_note` — delete a note from the vault
- `move_note` — move/rename a note with optional backlink update across all vault notes
- `create_folder` — create a folder and auto-generate an `_index.md` summary document
- `delete_folder` — delete a folder; requires `force=True` for non-empty folders

**Advanced tools**
- `get_graph_data` — build full vault link graph (nodes = notes with tags, edges = wiki-links)
- `get_all_tags` — list all tags across vault with per-tag note counts and note paths
- `get_dataview_fields` — parse Dataview inline fields (`key:: value`) from any note
- `get_daily_note` — retrieve daily note by date; reads `.obsidian/daily-notes.json` for custom folder/format config, falls back to common locations
- `list_attachments` — list all non-markdown files (images, PDFs, etc.) with size and modified date; filterable by folder

**Models**
- `NoteContent` — path, raw content, parsed frontmatter dict, body without frontmatter
- `NoteInfo` — path, title, normalized tags, modified_at
- `NoteMetadata` — full metadata including size, created_at, modified_at
- `WikiLink` — display text, raw target, resolved vault-relative path
- `SearchResult` — path, title, excerpt (~100 chars), relevance score
- `GraphData` — nodes and edges for vault link graph
- `TagInfo` — tag name, count, list of note paths
- `AttachmentInfo` — path, name, extension, size_bytes, modified_at

**Exceptions**
- `ObsidianMCPError` — base exception
- `VaultError` — invalid or inaccessible vault path
- `PathTraversalError` — path escapes vault boundary
- `NoteNotFoundError` — requested note does not exist
- `NoteExistsError` — attempted to create an already-existing note
- `FolderNotEmptyError` — attempted to delete non-empty folder without `force=True`

**Infrastructure**
- `VaultConfig` — validates vault path (must have `.obsidian/` directory); reads from `--vault` CLI arg or `OBSIDIAN_VAULT_PATH` env var
- `path_utils` — safe path resolution with traversal prevention (`safe_vault_path`), markdown detection, vault-relative conversion
- MCP server entry point with `stdio` transport via FastMCP
- `--vault PATH` CLI argument

**Read tools**
- `read_note` — read note content and parsed frontmatter
- `list_notes` — list notes filtered by folder and/or tag
- `search_notes` — full-text search with scored excerpts (max 100 results)
- `get_note_metadata` — frontmatter, tags, size, created/modified dates
- `get_backlinks` — find all notes linking to a given note
- `get_outgoing_links` — list all wiki-links in a note with resolution
- `read_canvas` — read and parse `.canvas` JSON files

**Tests**
- Unit tests: `NoteWriter`, `NoteReader`, `AdvancedFeatures`, `VaultConfig`, `path_utils`
- Property-based tests via Hypothesis for path and tag edge cases

## [0.1.0] - 2026-05-19

- Initial project scaffolding
