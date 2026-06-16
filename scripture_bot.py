#!/usr/bin/env python3
import os
import re
import sys
import difflib
import logging

# ── Logging setup (shows in Railway logs) ──────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

logger.info("=== Scripture Bot starting ===")
logger.info(f"Python version: {sys.version}")

# ── Validate token BEFORE importing telegram ──────────────────────────────
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN is not set or is empty. Exiting.")
    sys.exit(1)
logger.info(f"Token found: {TOKEN[:10]}...")

# ── Import telegram library ───────────────────────────────────────────────
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, MessageHandler,
        CallbackQueryHandler, ContextTypes, filters,
    )
    from telegram.constants import ParseMode
    logger.info("python-telegram-bot imported successfully.")
except ImportError as e:
    logger.error(f"Import failed: {e}")
    logger.error("Make sure requirements.txt contains: python-telegram-bot==21.3")
    sys.exit(1)

# ─────────────────────────────────────────────
#  Scripture data
# ─────────────────────────────────────────────
VERSES = [
    {
        "id": 1,
        "ref":  "Proverbs 3:5-6 (NLT)",
        "text": (
            "Trust in the Lord with all your heart; do not depend on your own understanding. "
            "Seek his will in all you do, and he will show you which path to take."
        ),
    },
    {
        "id": 2,
        "ref":  "Matthew 4:4 (NIV)",
        "text": (
            "Jesus answered, 'It is written: Man shall not live on bread alone, "
            "but on every word that comes from the mouth of God.'"
        ),
    },
    {
        "id": 3,
        "ref":  "Matthew 6:33 (NKJV)",
        "text": (
            "But seek first the kingdom of God and His righteousness, "
            "and all these things shall be added to you."
        ),
    },
    {
        "id": 4,
        "ref":  "1 Corinthians 13:13 (NLT)",
        "text": (
            "Three things will last forever—faith, hope, and love—"
            "and the greatest of these is love."
        ),
    },
    {
        "id": 5,
        "ref":  "Philippians 2:5-8 (NLT)",
        "text": (
            "You must have the same attitude that Christ Jesus had. "
            "Though he was God, he did not think of equality with God as something to cling to. "
            "Instead, he gave up his divine privileges; he took the humble position of a slave "
            "and was born as a human being. When he appeared in human form, he humbled himself "
            "in obedience to God and died a criminal's death on a cross."
        ),
    },
]

# ─────────────────────────────────────────────
#  Diff / compare helpers
# ─────────────────────────────────────────────
def tokenise(text: str):
    return text.split()

def normalise(word: str) -> str:
    return re.sub(r"[^a-z0-9'\-]", "", word.lower())

def escape_md(text: str) -> str:
    special = r"\_*[]()~`>#+-=|{}.!"
    return re.sub(r"([" + re.escape(special) + r"])", r"\\\1", text)

def compare_verses(reference: str, attempt: str):
    ref_tokens = tokenise(reference)
    att_tokens = tokenise(attempt)
    matcher = difflib.SequenceMatcher(
        None,
        [normalise(w) for w in ref_tokens],
        [normalise(w) for w in att_tokens],
        autojunk=False,
    )
    stats = {"correct": 0, "total": len(ref_tokens),
             "missing": 0, "wrong": 0, "extra": 0}
    parts = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for w in ref_tokens[i1:i2]:
                parts.append(escape_md(w))
            stats["correct"] += i2 - i1
        elif tag == "replace":
            for w in ref_tokens[i1:i2]:
                parts.append(f"~{escape_md(w)}~")
            for w in att_tokens[j1:j2]:
                parts.append(f"__{escape_md(w)}__")
            stats["wrong"] += i2 - i1
        elif tag == "delete":
            for w in ref_tokens[i1:i2]:
                parts.append(f"*\[{escape_md(w)}\]*")
            stats["missing"] += i2 - i1
        elif tag == "insert":
            for w in att_tokens[j1:j2]:
                parts.append(f"_{escape_md(w)}_")
            stats["extra"] += j2 - j1
    return " ".join(parts), stats

def legend() -> str:
    return (
        "\n*Legend:*\n"
        "Normal text \= correct\n"
        "~strikethrough~ \= correct word\n"
        "__underline__ \= your wrong word\n"
        "*\[word\]* \= missing word\n"
        "_italic_ \= extra word"
    )

def build_feedback(ref: str, attempt: str, verse_ref: str) -> str:
    annotated, stats = compare_verses(ref, attempt)
    pct = round(stats["correct"] / max(stats["total"], 1) * 100)
    emoji = "🎉" if pct == 100 else "💪" if pct >= 70 else "📖"
    header = f"{emoji} *{escape_md(verse_ref)}*\n\n"
    score_line = (
        f"\n\n*Score:* {pct}% "
        f"\({stats['correct']}/{stats['total']} words\)"
    )
    if stats["wrong"]:
        score_line += f" \| {stats['wrong']} wrong"
    if stats["missing"]:
        score_line += f" \| {stats['missing']} missing"
    if stats["extra"]:
        score_line += f" \| {stats['extra']} extra"
    return header + annotated + score_line + legend()

# ─────────────────────────────────────────────
#  Handlers
# ─────────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text(
        "📖 *Scripture Memory Bot*\n\n"
        "Use /quiz to pick a verse, or /all to go through all 5 in order\.",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

async def cmd_quiz(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(v["ref"], callback_data=f"verse_{v['id']}")]
        for v in VERSES
    ]
    await update.message.reply_text(
        "Choose a verse to practise:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def cmd_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["queue"] = [v["id"] for v in VERSES]
    ctx.user_data["scores"] = []
    await send_next_verse(update, ctx)

async def callback_verse(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    verse_id = int(query.data.split("_")[1])
    verse = next(v for v in VERSES if v["id"] == verse_id)
    ctx.user_data["active_verse"] = verse_id
    await query.message.reply_text(
        f"📝 *{escape_md(verse['ref'])}*\n\nType the verse from memory:",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    ud = ctx.user_data
    if "queue" in ud and ud["queue"]:
        verse_id = ud["queue"][0]
        verse = next(v for v in VERSES if v["id"] == verse_id)
        _, stats = compare_verses(verse["text"], user_text)
        pct = round(stats["correct"] / max(stats["total"], 1) * 100)
        ud["scores"].append(pct)
        ud["queue"].pop(0)
        feedback = build_feedback(verse["text"], user_text, verse["ref"])
        await update.message.reply_text(feedback, parse_mode=ParseMode.MARKDOWN_V2)
        if ud["queue"]:
            await send_next_verse(update, ctx)
        else:
            avg = round(sum(ud["scores"]) / len(ud["scores"]))
            summary = "\n".join(
                f"{escape_md(VERSES[i]['ref'])}: {ud['scores'][i]}%"
                for i in range(len(VERSES))
            )
            await update.message.reply_text(
                f"🏁 *Quiz complete\!*\n\n{summary}\n\n*Average: {avg}%*",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            ud.clear()
        return
    if "active_verse" in ud:
        verse_id = ud.pop("active_verse")
        verse = next(v for v in VERSES if v["id"] == verse_id)
        feedback = build_feedback(verse["text"], user_text, verse["ref"])
        await update.message.reply_text(feedback, parse_mode=ParseMode.MARKDOWN_V2)
        keyboard = [
            [InlineKeyboardButton("Try again", callback_data=f"verse_{verse_id}")],
            [InlineKeyboardButton("Pick another verse", callback_data="menu_quiz")],
        ]
        await update.message.reply_text(
            "What would you like to do next?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return
    await update.message.reply_text(
        "Use /quiz to pick a verse or /all to go through all 5\.",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

async def callback_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "menu_quiz":
        keyboard = [
            [InlineKeyboardButton(v["ref"], callback_data=f"verse_{v['id']}")]
            for v in VERSES
        ]
        await query.message.reply_text(
            "Choose a verse:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

async def send_next_verse(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ud = ctx.user_data
    verse_id = ud["queue"][0]
    verse = next(v for v in VERSES if v["id"] == verse_id)
    remaining = len(ud["queue"])
    current = len(VERSES) - remaining + 1
    msg = (
        f"📝 *Verse {current}/{len(VERSES)}: {escape_md(verse['ref'])}*\n\n"
        "Type the verse from memory:"
    )
    if hasattr(update, "callback_query") and update.callback_query:
        await update.callback_query.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)

# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────
def main():
    logger.info("Building application...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("quiz", cmd_quiz))
    app.add_handler(CommandHandler("all", cmd_all))
    app.add_handler(CallbackQueryHandler(callback_verse, pattern=r"^verse_"))
    app.add_handler(CallbackQueryHandler(callback_menu, pattern=r"^menu_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
