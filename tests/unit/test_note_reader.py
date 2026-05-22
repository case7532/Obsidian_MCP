"""Tests for NoteReader — example-based and property-based."""

import json
import pytest
from pathlib import Path
from hypothesis import given, settings
from hypothesis import strategies as st

from obsidian_mcp.note_reader import (
    NoteReader,
    _parse_frontmatter,
    _extract_tags,
    _parse_wikilinks,
)
from obsidian_mcp.exceptions import NoteNotFoundError
from obsidian_mcp.vault_config import VaultConfig


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def vault(tmp_path: Path) -> Path:
    (tmp_path / ".obsidian").mkdir()
    return tmp_path


@pytest.fixture
def reader(vault: Path) -> NoteReader:
    config = VaultConfig(vault)
    return NoteReader(config)


# ---------------------------------------------------------------------------
# _parse_frontmatter — example-based
# ---------------------------------------------------------------------------

def test_parse_frontmatter_basic():
    raw = "---\ntitle: Test\ntags: [a, b]\n---\nBody content"
    fm, body = _parse_frontmatter(raw)
    assert fm == {"title": "Test", "tags": ["a", "b"]}
    assert body == "Body content"


def test_parse_frontmatter_no_fm():
    raw = "Just body text"
    fm, body = _parse_frontmatter(raw)
    assert fm == {}
    assert body == raw


def test_parse_frontmatter_invalid_yaml():
    raw = "---\n: invalid: yaml:\n---\nBody"
    fm, body = _parse_frontmatter(raw)
    assert fm == {}  # graceful degradation


# ---------------------------------------------------------------------------
# _extract_tags — example-based
# ---------------------------------------------------------------------------

def test_extract_tags_from_frontmatter():
    fm = {"tags": ["python", "mcp"]}
    tags = _extract_tags(fm, "")
    assert "python" in tags
    assert "mcp" in tags


def test_extract_tags_inline():
    tags = _extract_tags({}, "Hello #world and #python stuff")
    assert "world" in tags
    assert "python" in tags


def test_extract_tags_excludes_code_block():
    body = "```\n#not-a-tag\n```\nBut #real-tag here"
    tags = _extract_tags({}, body)
    assert "not-a-tag" not in tags
    assert "real-tag" in tags


def test_extract_tags_normalized_lowercase():
    tags = _extract_tags({"tags": ["Python", "MCP"]}, "")
    assert all(t == t.lower() for t in tags)


# ---------------------------------------------------------------------------
# _parse_wikilinks — example-based
# ---------------------------------------------------------------------------

def test_wikilink_simple(vault):
    links = _parse_wikilinks("See [[MyNote]] for details", vault)
    assert len(links) == 1
    assert links[0].target == "MyNote"
    assert links[0].display == "MyNote"


def test_wikilink_with_alias(vault):
    links = _parse_wikilinks("See [[MyNote|click here]]", vault)
    assert links[0].target == "MyNote"
    assert links[0].display == "click here"


def test_wikilink_with_heading(vault):
    links = _parse_wikilinks("[[MyNote#Section]]", vault)
    assert links[0].target == "MyNote"


def test_wikilink_resolved(vault):
    (vault / "MyNote.md").write_text("content")
    links = _parse_wikilinks("[[MyNote]]", vault)
    assert links[0].resolved_path == "MyNote.md"


# ---------------------------------------------------------------------------
# NoteReader — example-based
# ---------------------------------------------------------------------------

def test_read_note(reader, vault):
    (vault / "test.md").write_text("---\ntitle: Hello\n---\nBody")
    note = reader.read_note("test.md")
    assert note.frontmatter == {"title": "Hello"}
    assert note.body == "Body"
    assert note.path == "test.md"


def test_read_note_not_found(reader):
    with pytest.raises(NoteNotFoundError):
        reader.read_note("nonexistent.md")


def test_list_notes(reader, vault):
    (vault / "a.md").write_text("# A")
    (vault / "b.md").write_text("# B")
    notes = reader.list_notes()
    paths = [n.path for n in notes]
    assert "a.md" in paths
    assert "b.md" in paths


def test_list_notes_filter_folder(reader, vault):
    (vault / "sub").mkdir()
    (vault / "sub" / "c.md").write_text("# C")
    (vault / "root.md").write_text("# Root")
    notes = reader.list_notes(folder="sub")
    assert all(n.path.startswith("sub/") for n in notes)


def test_list_notes_filter_tag(reader, vault):
    (vault / "tagged.md").write_text("---\ntags: [python]\n---\ncontent")
    (vault / "other.md").write_text("other content")
    notes = reader.list_notes(tag="python")
    assert all("python" in n.tags for n in notes)


def test_search_notes(reader, vault):
    (vault / "match.md").write_text("This has the keyword obsidian in it")
    (vault / "nomatch.md").write_text("nothing relevant here")
    results = reader.search_notes("obsidian")
    assert any(r.path == "match.md" for r in results)
    assert all(r.path != "nomatch.md" for r in results)


def test_get_backlinks(reader, vault):
    (vault / "target.md").write_text("# Target")
    (vault / "source.md").write_text("See [[target]] for more")
    backlinks = reader.get_backlinks("target.md")
    assert "source.md" in backlinks


def test_get_outgoing_links(reader, vault):
    (vault / "note.md").write_text("Links to [[other]] and [[second|alias]]")
    links = reader.get_outgoing_links("note.md")
    targets = [l.target for l in links]
    assert "other" in targets
    assert "second" in targets


def test_read_canvas(reader, vault):
    data = {"nodes": [], "edges": []}
    (vault / "board.canvas").write_text(json.dumps(data))
    result = reader.read_canvas("board.canvas")
    assert result == data


def test_read_canvas_invalid_json(reader, vault):
    (vault / "bad.canvas").write_text("not json")
    with pytest.raises(NoteNotFoundError):
        reader.read_canvas("bad.canvas")


# ---------------------------------------------------------------------------
# PBT: frontmatter round-trip (PBT-02)
# ---------------------------------------------------------------------------

import yaml as _yaml

simple_fm_values = st.one_of(
    st.text(
        alphabet=st.characters(
            whitelist_categories=("Lu", "Ll", "Nd", "Zs"),
            min_codepoint=32,
            max_codepoint=126,  # ASCII printable only — avoids YAML Unicode edge cases
        ),
        max_size=50,
    ).filter(lambda s: "\n" not in s and ":" not in s),
    st.integers(min_value=-1000, max_value=1000),
)
frontmatter_dicts = st.dictionaries(
    keys=st.from_regex(r'[a-zA-Z][a-zA-Z0-9_]*', fullmatch=True),
    values=simple_fm_values,
    max_size=5,
)


@given(fm=frontmatter_dicts)
@settings(max_examples=200)
def test_pbt_frontmatter_round_trip(fm):
    """PBT-02: parse(serialize(fm)) == fm for serializable frontmatter."""
    serialized = "---\n" + _yaml.dump(fm, allow_unicode=True) + "---\nBody text"
    parsed_fm, body = _parse_frontmatter(serialized)
    assert parsed_fm == fm
    assert body == "Body text"


# ---------------------------------------------------------------------------
# PBT: list_notes filter invariant — filtered ⊆ full (PBT-03)
# ---------------------------------------------------------------------------

@given(tag=st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True))
@settings(max_examples=50)
def test_pbt_list_notes_filter_subset(tag):
    """PBT-03: filtered list is always a subset of the full list."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        vault = Path(d).resolve()
        (vault / ".obsidian").mkdir()
        (vault / "a.md").write_text(f"#{tag}")
        (vault / "b.md").write_text("no tags here")
        config = VaultConfig(vault)
        r = NoteReader(config)
        full = {n.path for n in r.list_notes()}
        filtered = {n.path for n in r.list_notes(tag=tag)}
        assert filtered.issubset(full)
