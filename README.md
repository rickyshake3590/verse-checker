# Scripture Memory Bot

A Telegram bot that quizzes you on 5 Bible verses and highlights every
word you got right, wrong, missed, or added.

## 5 Verses included

| # | Reference | Translation |
|---|-----------|-------------|
| 1 | Proverbs 3:5-6 | NLT |
| 2 | Matthew 4:4 | NIV |
| 3 | Matthew 6:33 | NKJV |
| 4 | 1 Corinthians 13:13 | NLT |
| 5 | Philippians 2:5-8 | NLT |

## Feedback legend

| Format | Meaning |
|--------|---------|
| Normal text | ✅ Correct word |
| ~~strikethrough~~ | The word that should have been there (paired with wrong word below) |
| __underline__ | The wrong word you typed |
| **[word]** | Word you missed entirely |
| _italic_ | Extra word you added |

## Setup

### 1. Create a Telegram bot
1. Open Telegram and message **@BotFather**
2. Send `/newbot`
3. Give it a name (e.g. *Scripture Memory*) and a username (e.g. `scripture_memory_bot`)
4. BotFather replies with your **bot token** — copy it

### 2. Install dependencies
```bash
pip install python-telegram-bot
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

## Commands

| Command | Action |
|---------|--------|
| `/start` | Welcome message |
| `/quiz` | Pick one verse to practise |
| `/all` | Go through all 5 verses in order, with a score summary at the end |

## Hosting (optional)

For 24/7 availability, deploy on any Python host:
- **Railway / Render / Fly.io** — free tier works fine
- **AWS EC2 / Lightsail** — your existing AWS setup
- Set `TELEGRAM_BOT_TOKEN` as an environment variable on the platform