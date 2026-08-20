from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

from svg_utils import ASSETS, DATA, esc, write_text


DEFAULT_INPUT = DATA / "contributions.json"
DEFAULT_OUTPUT = ASSETS / "contribution-graph.svg"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def fmt_number(value: int) -> str:
    return f"{value:,}"


def render_heatmap(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Contribution data not found: {input_path}. Run scripts/fetch_contributions.py first.")
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    days = payload.get("days", [])
    stats = payload.get("stats", {})
    by_date = {date.fromisoformat(day["date"]): day for day in days}
    if not by_date:
        raise RuntimeError("Contribution data contains no days.")

    end = max(by_date)
    start = end - timedelta(days=370)
    while start.weekday() != 6:
        start += timedelta(days=1)

    cell = 11
    gap = 4
    left = 32
    top = 78
    grid_w = 53 * cell + 52 * gap
    width = 900
    height = 226

    rects = []
    for week in range(53):
        for weekday in range(7):
            current = start + timedelta(days=week * 7 + weekday)
            day = by_date.get(current, {"count": 0, "level": 0})
            level = max(0, min(4, int(day.get("level", 0))))
            count = int(day.get("count", 0))
            x = left + week * (cell + gap)
            y = top + weekday * (cell + gap)
            delay = round(0.18 + week * 0.018 + weekday * 0.012, 3)
            rects.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{PALETTE[level]}" opacity="0">'
                f'<title>{current.isoformat()}: {count} contributions</title>'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur="0.18s" fill="freeze" />'
                f'</rect>'
            )

    total = int(stats.get("total_last_year", 0))
    current_streak = int(stats.get("current_streak", 0))
    longest_streak = int(stats.get("longest_streak", 0))
    best_day = stats.get("best_day")
    best_text = "n/a"
    if isinstance(best_day, dict):
        best_text = f"{best_day.get('date')} / {best_day.get('count')}"

    legend = []
    lx = width - 164
    ly = 188
    for index, color in enumerate(PALETTE):
        legend.append(f'<rect x="{lx + index * 17}" y="{ly}" width="11" height="11" rx="2.5" fill="{color}" />')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">GitHub contribution graph for pml0107</title>
  <desc id="desc">Animated 53 week contribution heatmap generated from public GitHub contribution data.</desc>
  <rect width="100%" height="100%" rx="8" fill="#0d1117"/>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="7.5" fill="none" stroke="#30363d"/>
  <style>
    text {{ font: 13px ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; fill: #c9d1d9; }}
    .prompt {{ fill: #39d353; font-weight: 700; }}
    .muted {{ fill: #8b949e; }}
    .metric {{ fill: #58a6ff; }}
  </style>
  <text x="28" y="38"><tspan class="prompt">patrick@github</tspan><tspan class="muted">:~$</tspan><tspan> ./contributions --user pml0107</tspan></text>
  <text x="28" y="60" class="muted">{esc(fmt_number(total))} contributions in the last 12 months</text>
  {''.join(rects)}
  <text x="28" y="197"><tspan class="metric">current</tspan><tspan class="muted"> {current_streak}d</tspan><tspan>   </tspan><tspan class="metric">longest</tspan><tspan class="muted"> {longest_streak}d</tspan><tspan>   </tspan><tspan class="metric">best</tspan><tspan class="muted"> {esc(best_text)}</tspan></text>
  <text x="{lx - 36}" y="{ly + 10}" class="muted">Less</text>
  {''.join(legend)}
  <text x="{lx + 91}" y="{ly + 10}" class="muted">More</text>
</svg>
'''
    write_text(output_path, svg)
    print(f"Wrote {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate animated GitHub contribution heatmap SVG.")
    parser.add_argument("-i", "--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    render_heatmap(args.input, args.output)


if __name__ == "__main__":
    main()

