# Scripture Memory Bot

A Telegram bot that quizzes you on multipel Bible verses across 3 difficulty levels, highlighting every word you got right, wrong, missed, or added.

## Verses Included

| # | Reference | Translation |
|---|-----------|-------------|
| 1 | Proverbs 3:5-6 | NLT |
| 2 | Matthew 4:4 | NIV |
| 3 | Matthew 6:33 | NKJV |
| 4 | 1 Corinthians 13:13 | NLT |
| 5 | Philippians 2:5-8 | NLT |
| 6 | John 10:27 | NKJV |
| 7 | Psalms 119:72 | NIV |
| 8 | John 15:16 | NIV |
| 9 | 2 Timothy 2:24 | NKJV |
| 10 | Isaiah 26:3-4 | NKJV |

## Difficulty Levels

| Level | Description |
|-------|-------------|
| 🟢 Level 1 | ~1/3 of words are blanked out — most of the verse is shown |
| 🟡 Level 2 | ~2/3 of words are blanked out |
| 🔴 Level 3 | Entire verse is hidden — full recall from memory, no hints |

- For Levels 1 and 2, only the **word** is blanked (e.g. `_____;` not `_____`) — all punctuation stays visible.
- Blanked words are chosen **randomly** each attempt, so retrying gives a fresh set of blanks.
- You always type the **complete verse** regardless of level — not just the blanked words.

## Feedback Legend

| Format | Meaning |
|--------|---------|
| Normal text | ✅ Correct word |
| ~~strikethrough~~ | Your wrong or extra word |
| __underline__ | The correct word it should have been |
| **[word]** | Word you missed entirely |

**Notes on scoring:**
- Single and double quotation marks are both accepted (e.g. `'It is written'` and `"It is written"` both pass).
- Punctuation errors are ignored — missing commas, periods, and semicolons do not affect your score.
- Hyphens and dashes **are** checked (e.g. the em-dash in `forever—faith` must be present).

## Commands

| Command | Action |
|---------|--------|
| `/start` | Welcome message and instructions |
| `/quiz` | Pick one verse to practise, then choose difficulty |
| `/all` | Go through all 10 verses in order — choose difficulty once at the start, get a score summary at the end |

## Setup (Local)

### 1. Create a Telegram bot
1. Open Telegram and message **@BotFather**
2. Send `/newbot`
3. Give it a name (e.g. *Scripture Memory*) and a username (e.g. `scripture_memory_bot`)
4. BotFather replies with your **bot token** — copy it

### 2. Install dependencies
```bash
pip install python-telegram-bot==21.3
```

### 3. Set your token and run
```bash
# macOS / Linux
export TELEGRAM_BOT_TOKEN="your_token_here"
python scripture_bot.py

# Windows PowerShell
$env:TELEGRAM_BOT_TOKEN="your_token_here"
python scripture_bot.py
```

## Hosting on Railway (Recommended)

Railway keeps the bot running 24/7 without managing a server.

### Required files
Ensure your repo contains all four files:

```
your-repo/
├── scripture_bot.py
├── requirements.txt       # contains: python-telegram-bot==21.3
├── .python-version        # contains: 3.11
└── Procfile               # contains: worker: python scripture_bot.py
```

> **Important:** Use `worker:` in the Procfile, not `web:`. Railway must treat this as a background worker — not a web service — otherwise it will kill the container after ~3 seconds waiting for an HTTP port.

### Deployment steps
1. Push your repo to GitHub
2. Go to [railway.com](https://railway.com) → **New Project → Deploy from GitHub repo**
3. Select your repo — Railway auto-detects Python and builds
4. Go to **Variables** tab → add `TELEGRAM_BOT_TOKEN` with your token value
5. Go to **Settings → Deploy → Start Command** → set to `python scripture_bot.py`
6. Redeploy — check **Logs** tab for `Starting polling...`

### Healthy log output
```
=== Scripture Bot starting ===
Token found: 1234567890...
python-telegram-bot imported successfully.
Building application...
Starting polling...
HTTP Request: POST .../getUpdates "HTTP/1.1 200 OK"
```

The `getUpdates 200 OK` line repeats every ~30 seconds — this is normal. It is the bot polling Telegram for new messages.

### Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Container stops in ~3 seconds | Service type set to Web instead of Worker | Set `worker:` in Procfile; set Start Command manually in Settings |
| `Conflict: terminated by other getUpdates` | Two instances running simultaneously | Restart the service in Railway; stop any local instance running the same token |
| Bot starts but does not respond | Telegram IPs blocked by Railway | SSH into Railway and run `curl api.telegram.org` to check connectivity |
| `ModuleNotFoundError` | Dependencies not installed | Ensure `requirements.txt` contains `python-telegram-bot==21.3` |

## Multiple Users

A single Railway deployment handles **all users concurrently** — no additional setup needed. Each user gets a fully isolated quiz session via Python's async event loop. Share your bot link (`t.me/your_bot_username`) with anyone.
