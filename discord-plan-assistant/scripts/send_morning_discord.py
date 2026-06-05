#!/usr/bin/env python3
"""Send the daily morning planning message to Discord.

Environment variables:
- DISCORD_WEBHOOK_URL: required
- DISCORD_USERNAME: optional
- PLAN_ASSISTANT_START_DATE: optional
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
GENERATOR = ROOT / "scripts" / "generate_daily_message.py"
DISCORD_CONTENT_LIMIT = 1900


def load_dotenv(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def generate_message() -> str:
    result = subprocess.run(
        [sys.executable, str(GENERATOR)],
        cwd=str(ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def split_content(content: str, limit: int = DISCORD_CONTENT_LIMIT) -> Iterable[str]:
    """Split long webhook messages on line boundaries when possible."""
    if len(content) <= limit:
        yield content
        return

    current: list[str] = []
    current_len = 0
    for line in content.splitlines(keepends=True):
        if len(line) > limit:
            if current:
                yield "".join(current).rstrip()
                current = []
                current_len = 0
            for i in range(0, len(line), limit):
                yield line[i : i + limit].rstrip()
            continue

        if current_len + len(line) > limit and current:
            yield "".join(current).rstrip()
            current = []
            current_len = 0

        current.append(line)
        current_len += len(line)

    if current:
        yield "".join(current).rstrip()


def post_webhook_message(webhook_url: str, content: str, username: str) -> None:
    payload = {"content": content, "username": username}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status not in (200, 204):
                raise RuntimeError(f"Discord returned HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Discord webhook failed: HTTP {e.code}: {body}") from e


def send_to_discord(content: str) -> None:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL is missing. Create .env or export the variable.")

    username = os.environ.get("DISCORD_USERNAME", "Plan Assistant")
    for chunk in split_content(content):
        post_webhook_message(webhook_url, chunk, username)


def main() -> None:
    load_dotenv()
    content = generate_message()
    send_to_discord(content)
    print("Sent morning planning message to Discord.")


if __name__ == "__main__":
    main()
