"""Tests for NoteWriter."""

import pytest
from pathlib import Path

from obsidian_mcp.note_writer import NoteWriter
from obsidian_mcp.note_reader import NoteReader
from obsidian_mcp.vault_config import VaultConfig
from obsidian_mcp.exceptions import (
    FolderNotEmptyError,
    NoteExistsError,
    NoteNotFoundError,
)


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    (tmp_path / ".obsidian").mkdir()
    return tmp_path


@pytest.fixture
def writer(vault: Path) -> NoteWriter:
    config = VaultConfig(vault)
    reader = NoteReader(config)
    return NoteWriter(config, reader)


# ---------------------------------------------------------------------------
# create_note
# ---------------------------------------------------------------------------

def test_create_note(writer, vault):
    info = writer.create_note("new.md", "Hello world", title="New Note", description="A test note")
    assert (vault / "new.md").exists()
    assert info.path == "new.md"


def test_create_note_format_has_title(writer, vault):
    writer.create_note("fmt.md", "## Section\nBody text", title="My Doc", description="Short desc")
    raw = (vault / "fmt.md").read_text()
    assert "# My Doc" in raw
    assert "> Short desc" in raw
    assert "## Contents" in raw
    assert "## Related" not in raw  # no links given


def test_create_note_format_has_links(writer, vault):
    writer.create_note("linked.md", "content", title="T", description="D", links=["other-note"])
    raw = (vault / "linked.md").read_text()
    assert "## Related" in raw
    assert "[[other-note]]" in raw


def test_create_note_with_frontmatter(writer, vault):
    writer.create_note("fm.md", "Body", frontmatter={"title": "Test", "tags": ["a"]})
    raw = (vault / "fm.md").read_text()
    assert "title: Test" in raw
    assert "Body" in raw


def test_create_note_in_subfolder(writer, vault):
    writer.create_note("sub/note.md", "content", title="Note", description="desc")
    assert (vault / "sub" / "note.md").exists()


def test_create_note_already_exists(writer, vault):
    (vault / "exists.md").write_text("old")
    with pytest.raises(NoteExistsError):
        writer.create_note("exists.md", "new")


def test_create_note_infers_folder_from_existing(writer, vault):
    """When path=None and matching folder exists, note goes there."""
    (vault / "recipes").mkdir()
    (vault / "recipes" / "_index.md").write_text("# Recipes\n\n## Documents\n")
    info = writer.create_note(
        None, "Mix and bake.", title="Chocolate Cake",
        description="A recipe", frontmatter={"tags": ["recipes"]}
    )
    assert info.path.startswith("recipes/")


def test_create_note_infers_folder_creates_new(writer, vault):
    """When path=None and no matching folder, creates new folder with _index.md."""
    info = writer.create_note(
        None, "Some science content.", title="Quantum Notes",
        description="Physics notes", frontmatter={"tags": ["physics"]}
    )
    folder = Path(info.path).parent
    assert (vault / folder / "_index.md").exists()


# ---------------------------------------------------------------------------
# update_note
# ---------------------------------------------------------------------------

def test_update_note_replace(writer, vault):
    (vault / "note.md").write_text("old content")
    writer.update_note("note.md", "new content")
    assert (vault / "note.md").read_text() == "new content"


def test_update_note_append(writer, vault):
    (vault / "note.md").write_text("line one")
    writer.update_note("note.md", "line two", mode="append")
    assert "line one" in (vault / "note.md").read_text()
    assert "line two" in (vault / "note.md").read_text()


def test_update_note_not_found(writer):
    with pytest.raises(NoteNotFoundError):
        writer.update_note("ghost.md", "content")


# ---------------------------------------------------------------------------
# delete_note
# ---------------------------------------------------------------------------

def test_delete_note(writer, vault):
    (vault / "del.md").write_text("bye")
    writer.delete_note("del.md")
    assert not (vault / "del.md").exists()


def test_delete_note_not_found(writer):
    with pytest.raises(NoteNotFoundError):
        writer.delete_note("ghost.md")


# ---------------------------------------------------------------------------
# move_note
# ---------------------------------------------------------------------------

def test_move_note(writer, vault):
    (vault / "old.md").write_text("content")
    info = writer.move_note("old.md", "new.md")
    assert not (vault / "old.md").exists()
    assert (vault / "new.md").exists()
    assert info.path == "new.md"


def test_move_note_updates_backlinks(writer, vault):
    (vault / "target.md").write_text("# Target")
    (vault / "source.md").write_text("See [[target]] for info")
    writer.move_note("target.md", "renamed.md", update_links=True)
    content = (vault / "source.md").read_text()
    assert "[[renamed]]" in content
    assert "[[target]]" not in content


def test_move_note_destination_exists(writer, vault):
    (vault / "a.md").write_text("a")
    (vault / "b.md").write_text("b")
    with pytest.raises(NoteExistsError):
        writer.move_note("a.md", "b.md")


def test_move_note_not_found(writer):
    with pytest.raises(NoteNotFoundError):
        writer.move_note("ghost.md", "dest.md")


# ---------------------------------------------------------------------------
# create_folder / delete_folder
# ---------------------------------------------------------------------------

def test_create_folder(writer, vault):
    writer.create_folder("myfolder")
    assert (vault / "myfolder").is_dir()


def test_create_folder_generates_index(writer, vault):
    writer.create_folder("projects")
    index = vault / "projects" / "_index.md"
    assert index.exists()
    raw = index.read_text()
    assert "# Projects" in raw
    assert "## Documents" in raw


def test_create_folder_no_duplicate_index(writer, vault):
    """Creating an existing folder must not overwrite its _index.md."""
    writer.create_folder("existing")
    (vault / "existing" / "_index.md").write_text("# Custom\n")
    writer.create_folder("existing")  # should be no-op on _index
    assert (vault / "existing" / "_index.md").read_text() == "# Custom\n"


def test_delete_empty_folder(writer, vault):
    (vault / "empty").mkdir()
    writer.delete_folder("empty")
    assert not (vault / "empty").exists()


def test_delete_nonempty_folder_raises(writer, vault):
    (vault / "full").mkdir()
    (vault / "full" / "note.md").write_text("x")
    with pytest.raises(FolderNotEmptyError):
        writer.delete_folder("full")


def test_delete_nonempty_folder_force(writer, vault):
    (vault / "full").mkdir()
    (vault / "full" / "note.md").write_text("x")
    writer.delete_folder("full", force=True)
    assert not (vault / "full").exists()


def test_delete_folder_not_found(writer):
    with pytest.raises(NoteNotFoundError):
        writer.delete_folder("ghost")
