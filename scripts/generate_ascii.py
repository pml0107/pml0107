from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps

from svg_utils import ASSETS, esc, write_text


DEFAULT_INPUT = ASSETS / "input" / "portrait-prepared.png"
DEFAULT_OUTPUT = ASSETS / "profile-ascii-v2.svg"
RAMP = " .`:-=+*#%@"


def image_to_ascii(input_path: Path, columns: int = 58) -> list[str]:
    if not input_path.exists():
        raise FileNotFoundError(
            f"Prepared portrait not found: {input_path}. "
            "Run scripts/prepare_photo.py first or place assets/input/portrait-prepared.png."
        )

    image = Image.open(input_path).convert("L")
    width, height = image.size
    rows = max(1, int((height / width) * columns * 0.48))
    image = ImageOps.autocontrast(image.resize((columns, rows)))

    chars: list[str] = []
    for y in range(rows):
        line = []
        for x in range(columns):
            value = image.getpixel((x, y))
            index = int((255 - value) / 255 * (len(RAMP) - 1))
            line.append(RAMP[index])
        chars.append("".join(line).rstrip())
    return chars


def render_ascii_svg(lines: list[str], output_path: Path) -> None:
    char_w = 7.2
    line_h = 11.5
    pad_x = 22
    pad_y = 26
    width = 460
    height = int(pad_y * 2 + len(lines) * line_h)

    text_lines = []
    for index, line in enumerate(lines):
        y = pad_y + (index + 1) * line_h
        delay = round(index * 0.035, 3)
        text_lines.append(
            f'<g opacity="0" transform="translate(-6 0)">'
            f'<text x="{pad_x}" y="{y:.1f}">{esc(line)}</text>'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur="0.12s" fill="freeze" />'
            f'<animateTransform attributeName="transform" type="translate" from="-6 0" to="0 0" begin="{delay}s" dur="0.18s" fill="freeze" />'
            f'</g>'
        )

    last_delay = round(len(lines) * 0.035 + 0.2, 3)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">ASCII portrait of Patrick</title>
  <desc id="desc">A monochrome terminal-style ASCII portrait rendered from a local photo.</desc>
  <rect width="100%" height="100%" rx="8" fill="#0d1117"/>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="7.5" fill="none" stroke="#30363d"/>
  <style>
    text {{ font: 10px ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; fill: #c9d1d9; white-space: pre; }}
    .cursor {{ fill: #39d353; opacity: 0; }}
  </style>
  <g>
    {''.join(text_lines)}
  </g>
  <rect class="cursor" x="{pad_x}" y="{pad_y - 4}" width="7" height="11" rx="1">
    <animate attributeName="opacity" values="0;1;0;1;0" begin="0s" dur="0.7s" fill="freeze" />
    <animate attributeName="y" from="{pad_y - 4}" to="{pad_y + max(0, len(lines) - 1) * line_h - 4:.1f}" begin="0.2s" dur="{max(1.2, len(lines) * 0.035):.2f}s" fill="freeze" />
    <animate attributeName="opacity" values="0;1;0" begin="{last_delay}s" dur="0.5s" fill="freeze" />
  </rect>
</svg>
'''
    write_text(output_path, svg)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate animated ASCII portrait SVG.")
    parser.add_argument("-i", "--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--columns", type=int, default=58)
    args = parser.parse_args()
    lines = image_to_ascii(args.input, args.columns)
    render_ascii_svg(lines, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
