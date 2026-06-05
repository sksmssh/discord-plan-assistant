# Discord Plan Assistant

Discord Plan Assistant is a lightweight, webhook-based planning assistant for daily check-ins and Codex-friendly planning workflows.

Every morning, it sends a structured planning message to Discord so you can decide today's priorities, first action, blockers, and shutdown criteria inside the workspace you already use.

The project is intentionally small and easy to inspect:

- no database
- no long-running Discord bot process
- no external Python dependencies
- one Discord incoming webhook
- one cron job or GitHub Actions schedule
- one `AGENTS.md` file for Codex-friendly repository instructions

This repository is useful when you want Discord to act as a lightweight planning surface around coding-agent workflows, personal automation, or shared execution routines without depending on Hermes, OpenClaw, or another orchestration framework.

## What It Does

Every morning, Plan Assistant sends a message like:

```text
Morning Plan Check-in — 2026-06-05

Today's focus: Deep work

1. What must be done today?
2. What are the top 3 priorities?
3. What is the first 25-minute action?
4. What might block you?
5. What does "done for today" mean?
```

You can reply directly in Discord, use the message as a prompt for your notes, or pair it with Codex while working through code tasks.

## Folder Structure

```text
plan_assistant/
├── AGENTS.md
├── README.md
├── .env.example
├── .gitignore
├── LICENSE
├── requirements.txt
├── config/
│   └── routine.json
├── data/
│   ├── daily_plan_template.md
│   ├── planning_rules.md
│   └── weekly_review_template.md
├── logs/
│   └── .gitkeep
├── prompts/
│   ├── daily_planning.md
│   ├── plan_review.md
│   └── weekly_review.md
├── schedules/
│   ├── crontab_kst.example
│   └── github_actions_morning_discord.yml
├── scripts/
│   ├── generate_daily_message.py
│   ├── install_cron.sh
│   ├── send_morning_discord.py
│   └── test_discord.py
└── state/
    ├── .gitkeep
    └── progress.example.json
```

## Quick Start

### 1. Download or clone

```bash
git clone https://github.com/YOUR_USERNAME/discord-plan-assistant.git
cd discord-plan-assistant
```

Zip downloads work as well. Unzip the file and enter the folder.

### 2. Check Python

Python 3.9 or later is recommended because the scripts use `zoneinfo` from the Python standard library.

```bash
python3 --version
```

The scripts use only the Python standard library.

```bash
pip install -r requirements.txt
```

The command above is optional because `requirements.txt` currently has no external packages.

### 3. Create a Discord webhook

1. Open Discord.
2. Choose the server and channel where you want planning reminders.
3. Open channel settings.
4. Go to `Integrations`.
5. Create a webhook.
6. Copy the webhook URL.

Keep the webhook URL private. Anyone with the URL can post to that channel.

### 4. Create `.env`

```bash
cp .env.example .env
```

Edit `.env`:

```bash
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
DISCORD_USERNAME="Plan Assistant"
```

Optional:

```bash
PLAN_ASSISTANT_START_DATE="2026-06-01"
```

If `PLAN_ASSISTANT_START_DATE` is omitted, `config/routine.json` is used.

### 5. Preview today's message

```bash
python3 scripts/generate_daily_message.py
```

### 6. Send a test message

```bash
python3 scripts/test_discord.py
```

### 7. Send today's planning message manually

```bash
python3 scripts/send_morning_discord.py
```

## Run Every Morning With Cron

On Linux or macOS:

```bash
bash scripts/install_cron.sh
```

Check the installed job:

```bash
crontab -l
```

The helper installs a job like:

```cron
0 8 * * * cd '/path/to/discord-plan-assistant' && '/usr/bin/python3' scripts/send_morning_discord.py >> '/path/to/discord-plan-assistant/logs/cron.log' 2>&1
```

This sends a Discord message every day at 08:00 local time.

View logs:

```bash
tail -n 100 logs/cron.log
```

Remove the job:

```bash
crontab -l | grep -v "send_morning_discord.py" | crontab -
```

## Run With GitHub Actions

You can also run the reminder from GitHub Actions.

1. Push this repository to GitHub.
2. Open repository `Settings`.
3. Go to `Secrets and variables` -> `Actions`.
4. Add a repository secret named:

```text
DISCORD_WEBHOOK_URL
```

5. Copy the workflow file:

```bash
mkdir -p .github/workflows
cp schedules/github_actions_morning_discord.yml .github/workflows/morning-discord.yml
```

6. Commit and push.

The included workflow uses UTC. For 08:00 in Asia/Seoul, use:

```yaml
schedule:
  - cron: "0 23 * * *"
```

GitHub Actions schedules can be delayed by several minutes.

## Customize the Plan Assistant

Edit:

```text
config/routine.json
```

Useful fields:

- `timezone`: timezone used for date calculation
- `start_date`: day 1 of your plan assistant
- `daily_checklist`: fixed morning checklist
- `weekday_focus`: different focus for each weekday
- `planning_questions`: rotating questions for daily planning
- `shutdown_questions`: evening review prompts

Preview after editing:

```bash
python3 scripts/generate_daily_message.py
```

## Suggested Daily Use

Morning:

1. Read the Discord message.
2. Reply with today's top 3 priorities.
3. Pick the first 25-minute action.
4. Name the likely blocker.
5. Define what counts as done.

Evening:

1. Mark what actually got done.
2. Move unfinished work to tomorrow or delete it.
3. Write one reason the plan succeeded or failed.
4. Choose tomorrow's first action.

## Publishing Your Own Open Source Copy

Before uploading to GitHub:

1. Keep `.env` out of commits.
2. Keep Discord webhook URLs private.
3. Keep `logs/cron.log` private.
4. Remove private names, server paths, IP addresses, and personal schedules.
5. Review `config/routine.json`, `AGENTS.md`, `data/`, and `prompts/`.

Useful scan:

```bash
rg -n "discord.com/api/webhooks|WEBHOOK|TOKEN|SECRET|PASSWORD|/home/|/Users/|/data1/|165\\.132|PRIVATE|YOUR_REAL_NAME"
```

Initialize a fresh repository:

```bash
git init
git add .
git commit -m "Initial public release"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/discord-plan-assistant.git
git push -u origin main
```

## Security Notes

- `.env` is ignored by `.gitignore`.
- Webhook URLs belong only in `.env`, environment variables, or GitHub Secrets.
- Logs can contain local paths or personal routines, so they are ignored.
- The current version posts messages to Discord via webhook; replies stay inside Discord.
- `state/progress.example.json` is only a public template. Keep real progress files in `state/progress.json` or another ignored private file.

## Project Status

This is a compact public template for lightweight Discord-centered planning workflows. The code is designed to be small enough to read, modify, and extend in a few minutes.

## Disclaimer

This is an independent, unofficial project, maintained separately from OpenAI, Discord, Hermes, and OpenClaw.

## License

MIT License. See `LICENSE`.
