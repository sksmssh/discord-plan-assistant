#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || true)}"
LOG_FILE="$ROOT_DIR/logs/cron.log"

if [[ -z "$PYTHON_BIN" ]]; then
  echo "python3 not found. Install Python 3 first." >&2
  exit 1
fi

mkdir -p "$ROOT_DIR/logs"
touch "$LOG_FILE"

# Most machines run cron in local time. Adjust the cron expression if your
# server uses a different timezone from your planning timezone.
CRON_LINE="0 8 * * * cd '$ROOT_DIR' && '$PYTHON_BIN' scripts/send_morning_discord.py >> '$LOG_FILE' 2>&1"

TMP_CRON="$(mktemp)"
crontab -l 2>/dev/null | grep -v "send_morning_discord.py" > "$TMP_CRON" || true
{
  cat "$TMP_CRON"
  echo "$CRON_LINE"
} | crontab -
rm -f "$TMP_CRON"

echo "Installed daily 08:00 cron job:"
echo "$CRON_LINE"
echo "Check logs at: $LOG_FILE"
