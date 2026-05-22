"""Tests for AdvancedFeatures."""

import json
import pytest
from pathlib import Path
from hypothesis import given, settings
from hypothesis import strategies as st

from obsidian_mcp.advanced_features import AdvancedFeatures, _DATAVIEW_FIELD_RE
from obsidian_mcp.note_reader import NoteReader
from obsidian_mcp.vault_config import VaultConfig


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    (tmp_path / ".obsidian").mkdir()
    return tmp_path


@pytest.fixture
def advanced(vault: Path) -> AdvancedFeatures:
    config = VaultConfig(vault)
    reader = NoteReader(config)
    return AdvancedFeatures(config, reader)


# ---------------------------------------------------------------------------
# get_graph_data
# ---------------------------------------------------------------------------

def test_graph_nodes(advanced, vault):
    (vault / "a.md").write_text("# A")
    (vault / "b.md").write_text("# B")
    graph = advanced.get_graph_data()
    paths = [n["path"] for n in graph.nodes]
    assert "a.md" in paths
    assert "b.md" in paths


def test_graph_edges(advanced, vault):
    (vault / "a.md").write_text("links to [[b]]")
    (vault / "b.md").write_text("# B")
    graph = advanced.get_graph_data()
    sources = [e["source"] for e in graph.edges]
    assert "a.md" in sources


# ---------------------------------------------------------------------------
# get_all_tags
# ---------------------------------------------------------------------------

def test_get_all_tags(advanced, vault):
    (vault / "a.md").write_text("---\ntags: [python]\n---\ncontent")
    (vault / "b.md").write_text("#python and #mcp")
    tags = advanced.get_all_tags()
    tag_names = [t.tag for t in tags]
    assert "python" in tag_names
    assert "mcp" in tag_names


def test_get_all_tags_count(advanced, vault):
    (vault / "a.md").write_text("#shared")
    (vault / "b.md").write_text("#shared")
    tags = {t.tag: t.count for t in advanced.get_all_tags()}
    assert tags["shared"] == 2


# ---------------------------------------------------------------------------
# get_dataview_fields
# ---------------------------------------------------------------------------

def test_get_dataview_fields(advanced, vault):
    (vault / "note.md").write_text("status:: done\npriority:: high\n")
    fields = advanced.get_dataview_fields("note.md")
    assert fields == {"status": "done", "priority": "high"}


def test_get_dataview_fields_empty(advanced, vault):
    (vault / "empty.md").write_text("no dataview fields here")
    assert advanced.get_dataview_fields("empty.md") == {}


# ---------------------------------------------------------------------------
# get_daily_note
# ---------------------------------------------------------------------------

def test_get_daily_note_found(advanced, vault):
    (vault / "2026-05-19.md").write_text("# Daily")
    result = advanced.get_daily_note("2026-05-19")
    assert result is not None
    assert result["path"] == "2026-05-19.md"


def test_get_daily_note_not_found(advanced, vault):
    result = advanced.get_daily_note("2000-01-01")
    assert result is None


def test_get_daily_note_from_config_folder(advanced, vault):
    cfg = {"folder": "Journals", "format": "YYYY-MM-DD"}
    (vault / ".obsidian" / "daily-notes.json").write_text(json.dumps(cfg))
    (vault / "Journals").mkdir()
    (vault / "Journals" / "2026-05-19.md").write_text("# Journal")
    result = advanced.get_daily_note("2026-05-19")
    assert result is not None


# ---------------------------------------------------------------------------
# list_attachments
# ---------------------------------------------------------------------------

def test_list_attachments(advanced, vault):
    (vault / "image.png").write_bytes(b"fake png")
    (vault / "doc.pdf").write_bytes(b"fake pdf")
    (vault / "note.md").write_text("not an attachment")
    attachments = advanced.list_attachments()
    exts = {a.extension for a in attachments}
    assert "png" in exts
    assert "pdf" in exts
    assert "md" not in exts


def test_list_attachments_excludes_obsidian(advanced, vault):
    (vault / ".obsidian" / "workspace.json").write_text("{}")
    attachments = advanced.list_attachments()
    paths = [a.path for a in attachments]
    assert not any(".obsidian" in p for p in paths)


# ---------------------------------------------------------------------------
# PBT: dataview field parse round-trip (PBT-02)
# ---------------------------------------------------------------------------

simple_value = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=32),
    min_size=1, max_size=30,
).filter(lambda s: "\n" not in s)

field_key = st.from_regex(r'[a-zA-Z][a-zA-Z0-9_ ]*', fullmatch=True).filter(
    lambda s: "::" not in s and "\n" not in s
)


@given(fields=st.dictionaries(field_key, simple_value, min_size=1, max_size=5))
@settings(max_examples=100)
def test_pbt_dataview_fields_round_trip(fields):
    """PBT-02: Serialized key:: value fields are parsed back correctly."""
    text = "\n".join(f"{k}:: {v}" for k, v in fields.items())
    parsed = {
        m.group(1).strip(): m.group(2).strip()
        for m in _DATAVIEW_FIELD_RE.finditer(text)
    }
    for k, v in fields.items():
        assert parsed.get(k.strip()) == v.strip()
