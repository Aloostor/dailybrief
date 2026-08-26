from __future__ import annotations

from pathlib import Path

import pytest

from dailybrief.reader import read_notes


def test_read_notes_reads_and_sorts_md_and_txt(tmp_path: Path) -> None:
    (tmp_path / "b.txt").write_text("second", encoding="utf-8")
    (tmp_path / "a.md").write_text("first", encoding="utf-8")
    (tmp_path / "ignore.json").write_text("{}", encoding="utf-8")

    notes = read_notes(tmp_path)

    assert [note.name for note in notes] == ["a.md", "b.txt"]
    assert [note.content for note in notes] == ["first", "second"]


def test_read_notes_reads_windows_1254_text_file(tmp_path: Path) -> None:
    content = "Bugun oncelikli: müsteriyle görüsmeyi tamamla."
    (tmp_path / "windows.txt").write_bytes(content.encode("cp1254"))

    notes = read_notes(tmp_path)

    assert len(notes) == 1
    assert notes[0].name == "windows.txt"
    assert notes[0].content == content


def test_read_notes_raises_when_folder_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        read_notes(missing)


def test_read_notes_raises_when_no_supported_files(tmp_path: Path) -> None:
    (tmp_path / "only.json").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError):
        read_notes(tmp_path)


def test_read_notes_skips_unreadable_file_with_warning(tmp_path: Path) -> None:
    (tmp_path / "good.md").write_text("ok", encoding="utf-8")
    (tmp_path / "bad.txt").write_bytes(b"\xff\xfe\x00\x00")

    with pytest.warns(UserWarning, match="Dosya okunamadi, atlandi"):
        notes = read_notes(tmp_path)

    assert [note.name for note in notes] == ["good.md"]
    assert notes[0].content == "ok"
