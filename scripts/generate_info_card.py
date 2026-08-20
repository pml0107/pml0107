from __future__ import annotations

from pathlib import Path

from svg_utils import ASSETS, esc, write_text


OUTPUT = ASSETS / "info-card.svg"


ROWS = [
    ("name", "Patrick"),
    ("github", "@pml0107"),
    ("role", "Developer & SaaS Builder"),
    ("location", "Germany"),
    ("stack", "Next.js / TypeScript / Supabase"),
    ("", "Power Platform / Power Apps / Power Automate"),
    ("focus", "SaaS / Automation / Business Software"),
]


def render_info_card(output_path: Path = OUTPUT) -> None:
    width = 520
    height = 314
    lines = []
    y = 100
    for index, (key, value) in enumerate(ROWS):
        delay = round(0.25 + index * 0.12, 2)
        key_part = f'<tspan class="key">{esc(key)}</tspan><tspan class="sep"> :: </tspan>' if key else '<tspan class="key muted">      </tspan>'
        lines.append(
            f'<text x="34" y="{y}" opacity="0">{key_part}<tspan>{esc(value)}</tspan>'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur="0.22s" fill="freeze" />'
            f'</text>'
        )
        y += 27

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Patrick terminal info card</title>
  <desc id="desc">A neofetch-inspired developer profile card for Patrick.</desc>
  <rect width="100%" height="100%" rx="8" fill="#0d1117"/>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="7.5" fill="none" stroke="#30363d"/>
  <circle cx="25" cy="25" r="5" fill="#ff7b72"/>
  <circle cx="43" cy="25" r="5" fill="#d29922"/>
  <circle cx="61" cy="25" r="5" fill="#3fb950"/>
  <style>
    text {{ font: 15px ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; fill: #c9d1d9; }}
    .prompt {{ fill: #39d353; font-weight: 700; }}
    .key {{ fill: #58a6ff; }}
    .sep {{ fill: #8b949e; }}
    .muted {{ fill: #484f58; }}
  </style>
  <text x="34" y="62"><tspan class="prompt">patrick@github</tspan><tspan class="sep">:~$</tspan><tspan> neofetch</tspan></text>
  <line x1="34" y1="78" x2="486" y2="78" stroke="#21262d"/>
  {''.join(lines)}
  <text x="34" y="285" opacity="0"><tspan class="prompt">status</tspan><tspan class="sep"> :: </tspan><tspan>building quiet software that does the work</tspan>
    <animate attributeName="opacity" from="0" to="1" begin="1.18s" dur="0.3s" fill="freeze" />
  </text>
</svg>
'''
    write_text(output_path, svg)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    render_info_card()

