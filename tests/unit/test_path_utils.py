"""Tests for path_utils — example-based and property-based."""

import pytest
from pathlib import Path
from hypothesis import given, settings
from hypothesis import strategies as st

from obsidian_mcp.exceptions import PathTraversalError
from obsidian_mcp.path_utils import (
    safe_vault_path,
    normalize_note_path,
    sanitize_filename,
    is_markdown,
    is_canvas,
    to_vault_relative,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    (tmp_path / ".obsidian").mkdir()
    return tmp_path


# ---------------------------------------------------------------------------
# Example-based: safe_vault_path
# ---------------------------------------------------------------------------

def test_safe_vault_path_simple(vault_path):
    result = safe_vault_path(vault_path, "notes/test.md")
    assert result == vault_path / "notes" / "test.md"
    assert result.is_relative_to(vault_path)


def test_safe_vault_path_blocks_traversal(vault_path):
    with pytest.raises(PathTraversalError):
        safe_vault_path(vault_path, "../../../etc/passwd")


def test_safe_vault_path_blocks_traversal_encoded(vault_path):
    with pytest.raises(PathTraversalError):
        safe_vault_path(vault_path, "notes/../../..")


def test_safe_vault_path_strips_leading_slash(vault_path):
    result = safe_vault_path(vault_path, "/notes/test.md")
    assert result.is_relative_to(vault_path)


# ---------------------------------------------------------------------------
# Example-based: normalize_note_path
# ---------------------------------------------------------------------------

def test_normalize_adds_md_extension():
    assert normalize_note_path("notes/test") == "notes/test.md"


def test_normalize_keeps_existing_extension():
    assert normalize_note_path("notes/test.md") == "notes/test.md"


def test_normalize_strips_leading_slash():
    result = normalize_note_path("/notes/test.md")
    assert not result.startswith("/")


# ---------------------------------------------------------------------------
# Example-based: sanitize_filename
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,expected", [
    ("valid name", "valid name"),
    ("file/with/slashes", "file-with-slashes"),
    ("file:colon", "file-colon"),
    ('file"quote', "file-quote"),
])
def test_sanitize_filename(name, expected):
    assert sanitize_filename(name) == expected


# ---------------------------------------------------------------------------
# Example-based: is_markdown, is_canvas
# ---------------------------------------------------------------------------

def test_is_markdown():
    assert is_markdown(Path("note.md"))
    assert is_markdown(Path("note.MD"))
    assert not is_markdown(Path("note.canvas"))
    assert not is_markdown(Path("image.png"))


def test_is_canvas():
    assert is_canvas(Path("board.canvas"))
    assert not is_canvas(Path("note.md"))


# ---------------------------------------------------------------------------
# Example-based: to_vault_relative
# ---------------------------------------------------------------------------

def test_to_vault_relative(vault_path):
    absolute = vault_path / "folder" / "note.md"
    assert to_vault_relative(vault_path, absolute) == "folder/note.md"


# ---------------------------------------------------------------------------
# PBT: safe_vault_path invariant — output always inside vault (PBT-03)
# ---------------------------------------------------------------------------

valid_path_components = st.from_regex(r'[a-zA-Z0-9_\- ]+', fullmatch=True)
valid_relative_paths = st.lists(valid_path_components, min_size=1, max_size=4).map(
    lambda parts: "/".join(parts) + ".md"
)


@given(relative=valid_relative_paths)
@settings(max_examples=200)
def test_pbt_safe_vault_path_always_inside_vault(relative):
    """PBT-03: safe_vault_path output is always relative to vault_path."""
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir).resolve()  # resolve symlinks (macOS /var -> /private/var)
        (vault / ".obsidian").mkdir()
        result = safe_vault_path(vault, relative)
        assert result.is_relative_to(vault)


# ---------------------------------------------------------------------------
# PBT: normalize_note_path idempotence (PBT-04)
# ---------------------------------------------------------------------------

path_strings = st.from_regex(r'[a-zA-Z0-9_\- /]+', fullmatch=True).filter(
    lambda s: s.strip() and s.strip("/\\")
)


@given(path=path_strings)
@settings(max_examples=200)
def test_pbt_normalize_idempotent(path):
    """PBT-04: normalize_note_path(normalize_note_path(p)) == normalize_note_path(p)."""
    once = normalize_note_path(path)
    twice = normalize_note_path(once)
    assert once == twice


# ---------------------------------------------------------------------------
# PBT: to_vault_relative / safe_vault_path round-trip (PBT-02)
# ---------------------------------------------------------------------------

@given(relative=valid_relative_paths)
@settings(max_examples=200)
def test_pbt_vault_relative_round_trip(relative):
    """PBT-02: to_vault_relative(safe_vault_path(vault, p)) == normalize(p)."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir).resolve()
        (vault / ".obsidian").mkdir()
        absolute = safe_vault_path(vault, relative)
        back = to_vault_relative(vault, absolute)
        assert back == str(Path(relative.lstrip("/\\")))
