#!/usr/bin/env python3
"""Generate README-ready previews from the Codex pet atlas."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ATLAS_PATH = ROOT / "spritesheet.webp"
OUTPUT = ROOT / "assets" / "previews"
CELL = (192, 208)
SCALE = 2

STATES = [
    ("idle", 0, [280, 110, 110, 140, 140, 320, 320]),
    ("running-right", 1, [120] * 7 + [220]),
    ("running-left", 2, [120] * 7 + [220]),
    ("waving", 3, [140, 140, 140, 280]),
    ("jumping", 4, [140, 140, 140, 140, 280]),
    ("failed", 5, [140] * 7 + [240]),
    ("waiting", 6, [150, 150, 150, 150, 150, 260]),
    ("running", 7, [120, 120, 120, 120, 120, 220]),
    ("review", 8, [150, 150, 150, 150, 150, 280]),
]


def frame(atlas: Image.Image, row: int, column: int) -> Image.Image:
    width, height = CELL
    return atlas.crop((column * width, row * height, (column + 1) * width, (row + 1) * height)).convert("RGBA")


def save_animation(frames: list[Image.Image], durations: list[int], name: str) -> None:
    enlarged = [item.resize((CELL[0] * SCALE, CELL[1] * SCALE), Image.Resampling.NEAREST) for item in frames]
    gif_dir = OUTPUT / "gifs"
    gif_dir.mkdir(parents=True, exist_ok=True)
    enlarged[0].save(
        gif_dir / f"{name}.gif",
        save_all=True,
        append_images=enlarged[1:],
        duration=durations,
        loop=0,
        optimize=False,
        disposal=2,
    )


def checkerboard(size: tuple[int, int], square: int = 12) -> Image.Image:
    image = Image.new("RGB", size, "#ffffff")
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], square):
        for x in range(0, size[0], square):
            if (x // square + y // square) % 2:
                draw.rectangle((x, y, x + square - 1, y + square - 1), fill="#e8e8e8")
    return image


def make_contact_sheet(atlas: Image.Image) -> None:
    label_height = 22
    cell_width, cell_height = CELL[0] // 2, CELL[1] // 2
    sheet = Image.new("RGB", (cell_width * 8, (cell_height + label_height) * 11), "#f7f7f7")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    labels = [name for name, _, _ in STATES] + ["look 000-157.5", "look 180-337.5"]
    counts = [len(durations) for _, _, durations in STATES] + [8, 8]
    for row, (label, count) in enumerate(zip(labels, counts, strict=True)):
        y = row * (cell_height + label_height)
        draw.rectangle((0, y, sheet.width, y + label_height - 1), fill="#111111")
        draw.text((6, y + 5), f"row {row}: {label}", fill="#ffffff", font=font)
        for column in range(8):
            source = frame(atlas, row, column)
            bg = checkerboard(CELL)
            bg.paste(source, (0, 0), source)
            tile = bg.resize((cell_width, cell_height), Image.Resampling.LANCZOS)
            x = column * cell_width
            sheet.paste(tile, (x, y + label_height))
            color = "#18a058" if column < count else "#cc3344"
            draw.rectangle((x, y + label_height, x + cell_width - 1, y + label_height + cell_height - 1), outline=color)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sheet.save(OUTPUT / "contact-sheet.png")


def main() -> None:
    with Image.open(ATLAS_PATH) as source:
        atlas = source.convert("RGBA")
    if atlas.size != (1536, 2288):
        raise SystemExit(f"expected a 1536x2288 v2 atlas, got {atlas.width}x{atlas.height}")

    thumbnail = frame(atlas, 0, 0).resize((384, 416), Image.Resampling.NEAREST)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    thumbnail.save(OUTPUT / "thumbnail.webp", format="WEBP", lossless=True, method=6, exact=True)

    for name, row, durations in STATES:
        save_animation([frame(atlas, row, column) for column in range(len(durations))], durations, name)

    look_frames = [frame(atlas, 9, column) for column in range(8)] + [frame(atlas, 10, column) for column in range(8)]
    save_animation(look_frames, [160] * 15 + [260], "looking-around")
    make_contact_sheet(atlas)
    print(f"Generated previews in {OUTPUT}")


if __name__ == "__main__":
    main()
