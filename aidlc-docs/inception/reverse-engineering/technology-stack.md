# Technology Stack

## Programming Languages

| Language | Version | Usage |
|---|---|---|
| Python | >= 3.10 | Toàn bộ codebase |

- Sử dụng: type hints (`str | None`, `list[dict]`), `dataclasses`, `match` statements (không dùng), `Path.is_relative_to()` (3.9+), `match/case` (không dùng)

## Frameworks & Libraries

| Library | Version | Purpose |
|---|---|---|
| `mcp` | >=1.0.0 | Model Context Protocol — FastMCP server, stdio transport, `@mcp.tool()` decorator |
| `PyYAML` | >=6.0.1 | YAML frontmatter parsing và serialization |

## Build Tools

| Tool | Version | Purpose |
|---|---|---|
| `uv` | latest | Package manager, virtual environment, run scripts |
| `hatchling` | latest | Build backend cho wheel/sdist |

## Testing Tools

| Tool | Version | Purpose |
|---|---|---|
| `pytest` | >=8.0.0 | Test framework |
| `pytest-cov` | >=5.0.0 | Coverage reporting |
| `hypothesis` | >=6.100.0 | Property-based testing — edge cases cho path utils và parsers |

## Standard Library Usage (notable)

| Module | Usage |
|---|---|
| `pathlib.Path` | Toàn bộ filesystem operations |
| `re` | Regex: frontmatter, wikilinks, inline tags, dataview fields, backlink update |
| `yaml` | Frontmatter parsing (via PyYAML) |
| `json` | Canvas file parsing, daily-notes.json config |
| `math` | BM25 IDF calculation (`math.log`) |
| `collections.defaultdict` | BM25 term frequency + document frequency counting |
| `dataclasses` | Models (NoteContent, NoteInfo, ...) |
| `logging` | Structured logging toàn server |
| `argparse` | CLI argument `--vault` |
| `shutil` | `rmtree` cho delete_folder |

## Infrastructure

- **Deployment**: Local process — chạy như subprocess của AI client
- **Transport**: MCP stdio (stdin/stdout)
- **Storage**: Filesystem (Obsidian vault directory)
- **Config**: Environment variable `OBSIDIAN_VAULT_PATH` hoặc `--vault` CLI arg

## Algorithms

| Algorithm | Location | Complexity |
|---|---|---|
| Full-text search | `NoteReader.search_notes` | O(N*M) N=docs, M=doc_size — linear scan |
| BM25 search | `NoteReader.bm25_search` | O(N*M) corpus build + O(N*T) scoring, T=terms |
| Backlink update | `NoteWriter._update_backlinks` | O(N*M) — scan all docs |
| Wikilink resolve | `_resolve_wikilink` | O(N) BFS vault rglob |
| Folder inference | `_infer_folder` | O(F*K) F=folders, K=keywords |
