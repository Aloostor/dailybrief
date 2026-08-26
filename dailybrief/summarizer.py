from __future__ import annotations

import os
from importlib import import_module
from types import ModuleType

from dailybrief.reader import Note

SYSTEM_PROMPT = (
    "Sen bir asistan olarak notlari kisa bir gunluk brifinge donustur. "
    "Girdi notlari Turkce ve Ingilizce karisik olabilir; her iki dili de anlayip tek bir tutarli ozette birlestir. "
    "Ciktiyi sadece Turkce ver. Cikti iki bolumden olussun:\n"
    "1) Bugun Oncelikli 3-5 Madde\n"
    "2) Unutulmamasi Gerekenler\n"
    "Kisa, uygulanabilir ve tekrar etmeyen maddeler yaz."
)


def _load_anthropic() -> ModuleType:
    try:
        return import_module("anthropic")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Anthropic SDK kurulu degil. Kurmak icin su komutu calistirin: pip install anthropic"
        ) from exc


def generate_brief(notes: list[Note]) -> str:
    if not notes:
        raise RuntimeError("Ozet uretmek icin not bulunamadi.")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY bulunamadi. Once API anahtarini ayarlayin:\n"
            "PowerShell: $env:ANTHROPIC_API_KEY='your_api_key'\n"
            "cmd.exe: set ANTHROPIC_API_KEY=your_api_key"
        )

    notes_payload = "\n\n".join(
        [f"Dosya: {note.name}\nIcerik:\n{note.content}" for note in notes]
    )

    anthropic = _load_anthropic()
    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=700,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Asagidaki notlari analiz et ve istenen iki bolumlu kisa brifingi uret:\n\n"
                        f"{notes_payload}"
                    ),
                }
            ],
        )
    except anthropic.RateLimitError as exc:
        raise RuntimeError(
            "Anthropic API rate limit hatasi. Biraz bekleyip tekrar deneyin."
        ) from exc
    except anthropic.APIConnectionError as exc:
        raise RuntimeError(
            "Anthropic API baglanti hatasi. Internet baglantinizi ve ag erisiminizi kontrol edin."
        ) from exc
    except anthropic.APIError as exc:
        raise RuntimeError(f"Anthropic API hatasi: {exc}") from exc

    text_parts = [block.text for block in response.content if hasattr(block, "text")]
    brief = "\n".join(text_parts).strip()

    if not brief:
        raise RuntimeError("Anthropic API bos bir ozet dondu.")

    return brief