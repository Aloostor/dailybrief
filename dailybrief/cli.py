from __future__ import annotations

from datetime import date
import json
import os
from pathlib import Path
import re
import sys

import click
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from dailybrief.reader import read_notes
from dailybrief.summarizer import generate_brief

console = Console()
CONFIG_PATH = Path.home() / ".dailybrief" / "config.toml"


def _saved_api_key() -> str | None:
    try:
        config = CONFIG_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise RuntimeError(f"API ayari okunamadi: {CONFIG_PATH} ({exc})") from exc

    match = re.search(r'^\s*api_key\s*=\s*["\'](.*?)["\']\s*$', config, re.MULTILINE)
    return match.group(1) if match else None


def _ensure_api_key() -> None:
    if os.getenv("ANTHROPIC_API_KEY"):
        return

    saved_key = _saved_api_key()
    if saved_key:
        os.environ["ANTHROPIC_API_KEY"] = saved_key
        return

    if not sys.stdin.isatty():
        raise RuntimeError(
            "ANTHROPIC_API_KEY bulunamadi ve terminal etkileşimli degil. "
            "PowerShell'de ayarlayin: $env:ANTHROPIC_API_KEY='your_api_key'"
        )

    api_key = click.prompt("Anthropic API anahtariniz", hide_input=True).strip()
    if not api_key:
        raise RuntimeError("API anahtari bos olamaz.")

    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(
            f"api_key = {json.dumps(api_key)}\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise RuntimeError(f"API ayari kaydedilemedi: {CONFIG_PATH} ({exc})") from exc

    os.environ["ANTHROPIC_API_KEY"] = api_key


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--source",
    default="./notes",
    show_default=True,
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Kaynagin alinacagi klasor yolu.",
)
def main(source: Path) -> None:
    """Verilen klasordeki notlardan kisa bir gunluk brifing uretir."""
    today = date.today().strftime("%Y-%m-%d")
    header_text = Text()
    header_text.append("DailyBrief\n", style="bold cyan")
    header_text.append(f"Tarih: {today}", style="dim")
    console.print(Panel(Align.center(header_text), border_style="cyan"))

    try:
        notes = read_notes(source)
    except ValueError:
        console.print(
            Panel(
                "Bugun icin not bulunamadi.",
                title="Brifing",
                border_style="yellow",
            )
        )
        console.print(Text("0 dosyadan derlendi", style="dim"))
        return
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise click.ClickException(str(exc)) from exc

    try:
        _ensure_api_key()
        brief = generate_brief(notes)
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(
        Panel(
            brief,
            title="Gunluk Brifing",
            border_style="green",
            padding=(1, 2),
        )
    )
    console.print(Text(f"{len(notes)} dosyadan derlendi", style="dim"))


if __name__ == "__main__":
    main()
