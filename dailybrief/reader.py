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
            raw_content = path.read_bytes()
            content = _decode_content(raw_content)
        except (UnicodeDecodeError, OSError, ValueError) as exc:
            warnings.warn(
                f"Dosya okunamadi, atlandi: {path.name} ({exc})",
                category=UserWarning,
                stacklevel=2,
            )
            continue

        notes.append(Note(name=path.name, content=content))

    return notes


def _decode_content(raw_content: bytes) -> str:
    for encoding in ("utf-8", "cp1254"):
        try:
            content = raw_content.decode(encoding)
        except UnicodeDecodeError:
            continue

        if "\x00" in content:
            raise ValueError("dosya ikili veya bozuk gorunuyor")
        return content

    raise UnicodeDecodeError(
        "supported encodings",
        raw_content,
        0,
        min(len(raw_content), 1),
        "UTF-8 veya Windows-1254 olarak cozumlenemedi",
    )