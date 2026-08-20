from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

from svg_utils import ASSETS


DEFAULT_INPUT = ASSETS / "input" / "portrait.jpg"
DEFAULT_OUTPUT = ASSETS / "input" / "portrait-prepared.png"


def prepare_photo(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(
            f"Portrait source not found: {input_path}. "
            "Place your photo at assets/input/portrait.jpg."
        )

    image = Image.open(input_path)
    image = ImageOps.exif_transpose(image).convert("L")

    # Center-crop to a portrait ratio that keeps the face readable in a narrow SVG.
    target_ratio = 0.72
    width, height = image.size
    current_ratio = width / height
    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / target_ratio)
        top = max(0, (height - new_height) // 2)
        image = image.crop((0, top, width, top + new_height))

    image = ImageOps.autocontrast(image, cutoff=1)
    image = image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=135, threshold=3))
    image = ImageOps.autocontrast(image, cutoff=2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a portrait photo for ASCII rendering.")
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    prepare_photo(args.input, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()

