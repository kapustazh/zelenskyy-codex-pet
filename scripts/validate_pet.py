#!/usr/bin/env python3
"""Validate Zelenskyy's Codex v2 metadata and spritesheet geometry."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COUNTS = [7, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8]
PREVIEW_COUNTS = {
    "idle": 7,
    "running-right": 8,
    "running-left": 8,
    "waving": 4,
    "jumping": 5,
    "failed": 8,
    "waiting": 6,
    "running": 6,
    "review": 6,
    "looking-around": 16,
}
CELL_WIDTH = 192
CELL_HEIGHT = 208


def main() -> None:
    metadata = json.loads((ROOT / "pet.json").read_text(encoding="utf-8"))
    assert metadata["id"] == "zelenskyy", "pet id must be zelenskyy"
    assert metadata["spriteVersionNumber"] == 2, "spriteVersionNumber must be 2"
    assert metadata["spritesheetPath"] == "spritesheet.webp", "unexpected spritesheet path"

    with Image.open(ROOT / "spritesheet.webp") as source:
        atlas = source.convert("RGBA")
    assert atlas.size == (1536, 2288), f"unexpected atlas size: {atlas.size}"

    for row, used_count in enumerate(EXPECTED_COUNTS):
        for column in range(8):
            box = (
                column * CELL_WIDTH,
                row * CELL_HEIGHT,
                (column + 1) * CELL_WIDTH,
                (row + 1) * CELL_HEIGHT,
            )
            alpha = atlas.crop(box).getchannel("A")
            visible = alpha.getbbox() is not None
            assert visible == (column < used_count), f"row {row}, column {column} has unexpected occupancy"

    rgba = atlas.get_flattened_data() if hasattr(atlas, "get_flattened_data") else atlas.getdata()
    residue = sum(1 for red, green, blue, alpha in rgba if alpha == 0 and (red or green or blue))
    assert residue == 0, f"found {residue} transparent pixels with hidden RGB residue"

    preview_root = ROOT / "assets" / "previews"
    with Image.open(preview_root / "thumbnail.webp") as thumbnail:
        assert thumbnail.size == (384, 416), "unexpected thumbnail size"
    with Image.open(preview_root / "contact-sheet.png") as contact_sheet:
        assert contact_sheet.size == (768, 1386), "unexpected contact sheet size"
    for name, frame_count in PREVIEW_COUNTS.items():
        for extension in ("gif", "webp"):
            preview = preview_root / ("gifs" if extension == "gif" else "webp") / f"{name}.{extension}"
            with Image.open(preview) as animation:
                assert animation.size == (384, 416), f"unexpected size for {preview}"
                assert animation.n_frames == frame_count, f"unexpected frame count for {preview}"
    print("OK: valid 1536x2288 Codex pet v2 atlas (8 columns x 11 rows)")


if __name__ == "__main__":
    main()
