from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import warnings


@dataclass(frozen=True)
class Note:
    name: str
    content: str


def read_notes(folder_path: str | Path) -> list[Note]:
    source = Path(folder_path)

    if not source.exists():
        raise FileNotFoundError(f"Kaynak klasor bulunamadi: {source}")

    if not source.is_dir():
        raise NotADirectoryError(f"Kaynak yol bir klasor degil: {source}")

    candidates = sorted(
        [
            path
            for path in source.iterdir()
            if path.is_file() and path.suffix.lower() in {".md", ".txt"}
        ],
        key=lambda path: path.name.casefold(),
    )

    if not candidates:
        raise ValueError(f"Klasorde .md veya .txt dosyasi bulunamadi: {source}")

    notes: list[Note] = []
    for path in candidates:
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            warnings.warn(
                f"Dosya okunamadi, atlandi: {path.name} ({exc})",
                category=UserWarning,
                stacklevel=2,
            )
            continue

        notes.append(Note(name=path.name, content=content))

    return notes