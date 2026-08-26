from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 800
HEIGHT = 500
PADDING = 24
FONT_SIZE = 20
LINE_HEIGHT = 28
BG_COLOR = (18, 21, 27)
FG_COLOR = (230, 237, 243)
DIM_COLOR = (146, 158, 171)
ACCENT_COLOR = (88, 166, 255)
SUCCESS_COLOR = (63, 185, 80)


def load_monospace_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "DejaVuSansMono.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/Consolas.ttf",
        "C:/Windows/Fonts/cour.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except (OSError, FileNotFoundError):
            continue
    return ImageFont.load_default()


def draw_terminal_header(draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont) -> None:
    draw.rectangle([(0, 0), (WIDTH, 40)], fill=(28, 32, 40))
    draw.text((PADDING, 10), "DailyBrief Demo Terminal", font=font, fill=DIM_COLOR)


def render_frame(lines: list[tuple[str, tuple[int, int, int]]], font: ImageFont.ImageFont) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_terminal_header(draw, font)

    y = 56
    for text, color in lines:
        draw.text((PADDING, y), text, font=font, fill=color)
        y += LINE_HEIGHT

    return img


def build_output_lines() -> list[tuple[str, tuple[int, int, int]]]:
    return [
        ("", FG_COLOR),
        ("+--------------------------------------------------------------+", SUCCESS_COLOR),
        ("| DailyBrief                                    Tarih: 2026-08-26 |", SUCCESS_COLOR),
        ("+--------------------------------------------------------------+", SUCCESS_COLOR),
        ("", FG_COLOR),
        ("Bugun oncelikli 3 madde", ACCENT_COLOR),
        ("1) Login timeout sorununu bugun fixleyip yeniden test et.", FG_COLOR),
        ("2) Ogleye kadar release notlarini tamamla ve paylas.", FG_COLOR),
        ("3) Standup oncesi onboarding metni degisikliklerini netlestir.", FG_COLOR),
        ("", FG_COLOR),
        ("Unutulmamasi gerekenler", ACCENT_COLOR),
        ("- 16:00'da analytics raporunu kontrol et.", FG_COLOR),
        ("- Musteri geri bildirimlerini issue'lara ayir.", FG_COLOR),
        ("", FG_COLOR),
        ("3 dosyadan derlendi", DIM_COLOR),
    ]


def main() -> None:
    font = load_monospace_font(FONT_SIZE)
    frames: list[Image.Image] = []

    base_prompt = "$ "
    command = "python -m dailybrief --source ./notes"

    # a) Bos terminal
    frames.append(render_frame([(base_prompt, FG_COLOR)], font))

    # b) Komutun harf harf yazilmasi
    for idx in range(1, len(command) + 1):
        typed = base_prompt + command[:idx]
        frames.append(render_frame([(typed, FG_COLOR)], font))

    # c) Kisa loading efekti
    for dots in (".", "..", "..."):
        lines = [
            (base_prompt + command, FG_COLOR),
            (f"loading{dots}", DIM_COLOR),
        ]
        frames.append(render_frame(lines, font))

    # d) Ornek DailyBrief cikti
    result_lines = [(base_prompt + command, FG_COLOR)] + build_output_lines()
    final_frame = render_frame(result_lines, font)
    for _ in range(6):
        frames.append(final_frame.copy())

    output_path = Path(__file__).resolve().parents[1] / "demo.gif"
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=400,
        loop=0,
    )
    print(f"Demo GIF olusturuldu: {output_path}")


if __name__ == "__main__":
    main()