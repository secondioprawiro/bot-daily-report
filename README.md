# Monev Bot - Logbook Submission Bot

A Telegram bot that automates the daily logbook submission process for MONEV (Monitoring and Evaluation) at KEMNAKER.

## Features

- Manual logbook submission via `/logbook` command
- Scheduled automatic logbook submission at configurable time
- LLM integration via `/ask` command (Gemini API optional)
- Screenshot capture for debugging (saved to `debug_picture/` folder)
- UTF-8 logging support for emoji characters on Windows

## Prerequisites

1. Install Python 3.8+
2. Install required packages:
   ```bash
   pip install python-telegram-bot playwright python-dotenv
   ```
3. Playwright browsers:
   ```bash
   playwright install
   ```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here  # optional fallback for scheduled notifications
KEMNAKER_USERNAME=your_kemnaker_username
KEMNAKER_PASSWORD=your_kemnaker_password
LOGBOOK_HOUR=9           # optional, default 9
LOGBOOK_MINUTE=0         # optional, default 0
GEMINI_API_KEY=your_gemini_api_key  # optional, for /ask command
```

## Configuration

- Default logbook submission time: 9:00 AM (configurable via `/schedule` command)
- Schedule format supports hour and minute, e.g. `/schedule 10:30`
- Defaults can also be set in `.env` via `LOGBOOK_HOUR` and `LOGBOOK_MINUTE`
- Logs are saved to `bot_audit.log` with UTF-8 encoding
- Debug screenshots are saved to `debug_picture/` directory
- **LOGBOOK_PAIRS Customization**: The logbook activity/lesson/obstacle pairs can be customized based on your academic major. Edit `logbook.py` and modify the `LOGBOOK_PAIRS` list to add activities relevant to your field of study. Each pair contains:
  - `activity`: Description of the day's activity
  - `lesson`: Learning outcome from the activity
  - `obstacle`: Challenges faced during the activity

Example structure for Computer Science major:
```python
LOGBOOK_PAIRS = [
    {
        "activity": "Debugging software issues and optimizing system performance",
        "lesson": "Learned systematic debugging techniques and performance tuning",
        "obstacle": "Encountered complex bug that required extensive root cause analysis"
    },
    # ... more pairs
]
```

## Troubleshooting

### UnicodeEncodeError on Windows

If you see `UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'`, the bot has been fixed to use UTF-8 encoding for logging. Make sure you're running the latest version.

### Bot not responding

- Check that `TELEGRAM_BOT_TOKEN` is set correctly in `.env`
- Ensure the bot has permission to send messages to your chat
- Check `bot_audit.log` for error details

### Screenshots not appearing

- Check that `debug_picture/` directory exists
- Screenshots are saved after each submission
- Old screenshots may have been from previous runs

### Scheduled notification fails with "Chat not found"

This means the bot could not find the chat ID for scheduled notifications.

- Send `/myid` to the bot once — this saves your real chat ID to `chat_id.txt`
- Or set `TELEGRAM_CHAT_ID` in `.env` to the numeric chat ID shown by `/myid`
- Restart the bot after making changes

### Customizing LOGBOOK_PAIRS for Your Major

To customize the logbook activities for your specific field of study:

1. Open `logbook.py`
2. Locate the `LOGBOOK_PAIRS` list (around line 20-55)
3. Replace the existing pairs with activities relevant to your major
4. Keep the same structure: each entry must have `activity`, `lesson`, and `obstacle` keys
5. Save the file and restart the bot

Example for **Engineering Majors**:
```python
LOGBOOK_PAIRS = [
    {
        "activity": "Performing routine maintenance on mechanical equipment",
        "lesson": "Gained insights into preventive maintenance schedules",
        "obstacle": "Identified wear and tear issues that required immediate attention"
    },
    # ... more engineering-focused pairs
]
```

Example for **Health Sciences Majors**:
```python
LOGBOOK_PAIRS = [
    {
        "activity": "Assisting with patient care rounds and vital sign monitoring",
        "lesson": "Understood the importance of systematic patient assessment",
        "obstacle": "Managed time constraints while ensuring comprehensive care"
    },
    # ... more health science-focused pairs
]
```

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `/start` | Greet the bot and show instructions |
| `/logbook` | Manually submit logbook now |
| `/schedule` | View current automatic schedule (e.g. `09:00`) |
| `/schedule 10:30` | Set automatic schedule to 10:30 (hour and minute) |
| `/schedule 10` | Set automatic schedule to 10:00 (minute reset to 0) |
| `/myid` | Show your Telegram chat ID and save it for notifications |
| `/help` | Show available commands |
| `/ask <teks>` | Get AI response (requires GEMINI_API_KEY) |

### Manual Workflow

1. Run `/logbook` to submit the daily logbook
2. The bot will:
   - Login to the MONEV system
   - Submit the logbook
   - Capture before/after screenshots to `debug_picture/`
   - Send a markdown summary to your Telegram chat

### Automatic (Scheduled) Workflow

The bot schedules the daily logbook itself — you do **not** need to run `scheduler.py` separately.

1. Set the time with `/schedule 10:30` (or `LOGBOOK_HOUR` / `LOGBOOK_MINUTE` in `.env`).
2. Keep the bot running (`python telegram_bot.py`).
3. Every day at the configured time, the bot will automatically:
   - Skip Sundays
   - Send `🚀 Menjalankan logbook otomatis, mohon tunggu…` to your chat
   - Run the logbook submission
   - Send the result (success ✅ or failure ❌) to your chat

> **Important:** To receive automatic notifications, send at least one message to the bot (e.g. `/myid` or `/start`) after starting it. This saves your chat ID to `chat_id.txt`. Without this, the bot falls back to `TELEGRAM_CHAT_ID` from `.env`.

### Notification Setup (Chat ID)

Scheduled notifications are sent to the chat ID stored in `chat_id.txt`:

1. Start the bot: `python telegram_bot.py`
2. Open Telegram and send `/myid` to the bot
3. The bot replies with your chat ID and saves it to `chat_id.txt`
4. The bot reads this file for all future scheduled notifications

Alternatively, set `TELEGRAM_CHAT_ID` in `.env` to the numeric chat ID (the same value shown by `/myid`).

## Project Structure

```
monev-bot/
├── telegram_bot.py     # Main bot logic (polling + scheduling)
├── logbook.py          # Playwright automation for logbook submission
├── .env                # Environment variables (create this)
├── .gitignore          # Git ignore rules
├── bot_audit.log       # Application logs (generated)
├── chat_id.txt         # Saved chat ID for notifications (generated, via /myid)
├── debug_picture/      # Debug screenshots (generated)
│   ├── debug_pre_submit_YYYY-MM-DD.png
│   └── debug_post_submit_YYYY-MM-DD.png
├── venv/               # Python virtual environment
├── __pycache__/        # Python cache
└── README.md           # This file
```