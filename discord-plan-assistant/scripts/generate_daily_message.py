#!/usr/bin/env python3
"""Generate the daily Discord planning message.

This script is intentionally dependency-free so cron or GitHub Actions can run
it anywhere with Python 3.9+.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "routine.json"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_start_date(config: dict) -> date:
    raw = os.environ.get("PLAN_ASSISTANT_START_DATE") or config.get("start_date")
    if not raw:
        raise RuntimeError("Missing start_date. Set PLAN_ASSISTANT_START_DATE or config/routine.json:start_date.")
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError as exc:
        raise RuntimeError(f"Invalid start_date '{raw}'. Expected YYYY-MM-DD.") from exc


def today_in_tz(tz_name: str) -> date:
    try:
        return datetime.now(ZoneInfo(tz_name)).date()
    except Exception as exc:
        raise RuntimeError(f"Invalid timezone '{tz_name}'.") from exc


def rotate(items: list[str], day_index: int, k: int) -> list[str]:
    if not items:
        return []
    return [items[(day_index + i) % len(items)] for i in range(k)]


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def numbered_list(items: list[str]) -> str:
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, start=1))


def generate_message() -> str:
    config = load_config()
    tz = config.get("timezone", "Asia/Seoul")
    today = today_in_tz(tz)
    start = parse_start_date(config)
    day_index = max(0, (today - start).days)
    day_number = day_index + 1
    weekday = str(today.weekday())
    weekday_info = config["weekday_focus"][weekday]

    checklist = bullet_list(config["daily_checklist"])
    planning_questions = numbered_list(rotate(config["planning_questions"], day_index, 5))
    shutdown_questions = numbered_list(rotate(config["shutdown_questions"], day_index, 3))
    reply_template = "\n".join(config["reply_template"])

    msg = f"""🌅 **Morning Plan Check-in — {today.isoformat()}**
**Day {day_number} | {weekday_info['name']} | Focus: {weekday_info['focus']}**

**Main prompt**
{weekday_info['main_prompt']}

**08:00 setup checklist**
{checklist}

**Planning questions**
{planning_questions}

**Reply template**
```text
{reply_template}
```

**Evening shutdown prompts**
{shutdown_questions}
"""
    return msg.strip()


if __name__ == "__main__":
    print(generate_message())
