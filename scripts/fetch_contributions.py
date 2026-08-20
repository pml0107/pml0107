from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from svg_utils import DATA, write_text


DEFAULT_OUTPUT = DATA / "contributions.json"


def parse_count(raw: str | None) -> int:
    if not raw:
        return 0
    text = raw.lower().replace(",", "").replace(".", "")
    if "no contributions" in text:
        return 0
    match = re.search(r"(\d+)\s+contributions?", text)
    return int(match.group(1)) if match else 0


def fetch_html(username: str, attempts: int = 3) -> str:
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "Accept": "text/html",
        "User-Agent": "pml0107-profile-readme-generator",
    }
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            if attempt < attempts - 1:
                time.sleep(2**attempt)
    raise RuntimeError(f"Could not fetch GitHub contributions for {username}: {last_error}")


def parse_days(html: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.select("[data-date]")
    tooltips = {
        tooltip.get("for"): tooltip.get_text(" ", strip=True)
        for tooltip in soup.select("tool-tip[for]")
    }
    days: dict[str, dict[str, object]] = {}
    for cell in cells:
        day = cell.get("data-date")
        if not day:
            continue
        tooltip = tooltips.get(cell.get("id"))
        count = parse_count(cell.get("data-count") or cell.get("aria-label") or tooltip or cell.text)
        level_raw = cell.get("data-level")
        if level_raw is None:
            level_raw = cell.get("class", [""])[0]
        try:
            level = max(0, min(4, int(str(level_raw))))
        except ValueError:
            level = 0 if count == 0 else min(4, 1 + count.bit_length() // 2)
        days[day] = {"date": day, "count": count, "level": level}

    if not days:
        raise RuntimeError("No contribution day cells found in GitHub response.")
    return [days[key] for key in sorted(days)]


def compute_stats(days: list[dict[str, object]]) -> dict[str, object]:
    counts = {date.fromisoformat(str(day["date"])): int(day["count"]) for day in days}
    if not counts:
        return {
            "total_last_year": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": None,
        }

    sorted_dates = sorted(counts)
    end = min(max(sorted_dates), date.today())
    start = end - timedelta(days=364)
    total = sum(count for day, count in counts.items() if start <= day <= end)

    current = 0
    cursor = end
    while cursor in counts and counts[cursor] > 0:
        current += 1
        cursor -= timedelta(days=1)

    longest = 0
    running = 0
    cursor = min(sorted_dates)
    while cursor <= max(sorted_dates):
        if counts.get(cursor, 0) > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
        cursor += timedelta(days=1)

    best_date, best_count = max(counts.items(), key=lambda item: item[1])
    best_day = {"date": best_date.isoformat(), "count": best_count} if best_count > 0 else None
    return {
        "total_last_year": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
    }


def fetch_contributions(username: str, output_path: Path) -> dict[str, object]:
    html = fetch_html(username)
    days = parse_days(html)
    payload = {
        "username": username,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": f"https://github.com/users/{username}/contributions",
        "days": days,
        "stats": compute_stats(days),
    }
    write_text(output_path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch public GitHub contribution calendar data.")
    parser.add_argument("--username", default="pml0107")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        payload = fetch_contributions(args.username, args.output)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Wrote {args.output} with {len(payload['days'])} days")


if __name__ == "__main__":
    main()
