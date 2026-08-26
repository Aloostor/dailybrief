from __future__ import annotations

from datetime import date
from pathlib import Path

import click
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from dailybrief.reader import read_notes
from dailybrief.summarizer import generate_brief

console = Console()


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
