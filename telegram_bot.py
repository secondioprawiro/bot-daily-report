import os
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Load environment variables (user will fill them later)
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # not strictly needed for bot polling
CHAT_ID_FILE = "chat_id.txt"  # stores the real chat id from incoming messages
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # optional LLM key
LOGBOOK_HOUR = int(os.getenv("LOGBOOK_HOUR", "9"))  # default 9 AM
LOGBOOK_MINUTE = int(os.getenv("LOGBOOK_MINUTE", "0"))  # default 0 minute

# Import our reusable logbook logic
from logbook import run_logbook

# If LLM is desired, we import the helper (may fail if not installed)
try:
    from llm_responder import generate_reply
except Exception:
    generate_reply = None

# Configure logging with UTF-8 encoding for both file and console handlers
file_handler = logging.FileHandler('bot_audit.log', encoding='utf-8')
console_handler = logging.StreamHandler()
# Python 3.7+: set encoding on StreamHandler directly
if hasattr(console_handler, 'setEncoding'):
    console_handler.setEncoding('utf-8')

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
# Also reconfigure stdout/stderr for good measure (Python 3.7+)
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
logger = logging.getLogger(__name__)

def _get_stored_chat_id():
    """Return the real chat id saved from an incoming message, else the .env CHAT_ID."""
    try:
        with open(CHAT_ID_FILE, "r", encoding="utf-8") as f:
            value = f.read().strip()
            if value:
                return int(value)
    except Exception:
        pass
    return CHAT_ID

def _store_chat_id(chat_id):
    """Persist the correct chat id from a real user message."""
    try:
        with open(CHAT_ID_FILE, "w", encoding="utf-8") as f:
            f.write(str(chat_id))
    except Exception as e:
        logger.warning("Gagal menyimpan chat_id: %s", e)

async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    _store_chat_id(update.effective_chat.id)
    await update.message.reply_text(
        "👋 Halo! Aku bot Logbook MONEV pribadi Anda.\n"
        "Gunakan /logbook untuk kirim logbook sekarang, atau biarkan saya otomatis pada jam yang ditentukan.\n"
        "Kirim pesan apa saja untuk mendapatkan balasan (LLM optional).\n"
        "Gunakan perintah /ask <teks> untuk mendapatkan balasan LLM secara eksplisit.\n"
        "Gunakan /help untuk melihat daftar perintah yang tersedia."
    )

async def logbook_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _store_chat_id(update.effective_chat.id)
    await update.message.reply_text("🚀 Menjalankan logbook, mohon tunggu…")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    result = await run_logbook()
    await update.message.reply_text(result, parse_mode="Markdown")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Simple echo for non‑command text (fallback if LLM not used)
    _store_chat_id(update.effective_chat.id)
    user_text = update.message.text
    # Show typing action while LLM is processing
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    if generate_reply:
        try:
            reply = await generate_reply(user_text)
        except Exception as e:
            logger.exception("LLM error")
            reply = f"⚠️ LLM error: {e}"
    else:
        reply = f"Anda menulis: {user_text}\n(LLM belum dikonfigurasi)."
    # Log request & response for audit
    logger.info("User message: %s | Bot reply: %s", user_text, reply)
    await update.message.reply_text(reply)

# ---------------------------------------------------------------------
# /ask command – explicit LLM query
# ---------------------------------------------------------------------
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not generate_reply:
        await update.message.reply_text("⚠️ LLM belum dikonfigurasi di bot ini.")
        return
    # Combine command arguments into a single query string
    query = " ".join(context.args) if context.args else update.message.text
    # Show typing action while LLM processes the query
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    if not query:
        await update.message.reply_text("❓ Silakan beri teks setelah /ask.")
        return
    try:
        reply = await generate_reply(query)
    except Exception as e:
        logger.exception("LLM error in /ask")
        reply = f"⚠️ LLM error: {e}"
    # Log request & response for audit
    logger.info("/ask query: %s | Bot reply: %s", query, reply)
    await update.message.reply_text(reply)

# ---------------------------------------------------------------------
# /help command – show available commands
# ---------------------------------------------------------------------
async def help_cmd(update: Update, _: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛠️ *Daftar Perintah Bot*\n"
        "`/start` – Menyapa dan menampilkan petunjuk.\n"
        "`/logbook` – Menjalankan logbook secara manual.\n"
        "`/ask <teks>` – Dapatkan balasan LLM (Gemini).\n"
        "`/schedule [jam]` – Lihat atau ubah jam otomatis logbook (default 9).\n"
        "`/help` – Menampilkan bantuan ini."
    )
    await update.message.reply_markdown(help_text)

# ---------------------------------------------------------------------
# /schedule command – view or set LOGBOOK_HOUR
# ---------------------------------------------------------------------
async def schedule_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global LOGBOOK_HOUR, LOGBOOK_MINUTE
    if context.args:
        try:
            # Terima "10:30" atau ["10", "30"] atau "10"
            raw = context.args[0] if len(context.args) == 1 else f"{context.args[0]}:{context.args[1]}"
            if ":" in raw:
                h, m = raw.split(":")
                LOGBOOK_HOUR, LOGBOOK_MINUTE = int(h), int(m)
            else:
                LOGBOOK_HOUR = int(raw)
                LOGBOOK_MINUTE = 0
            if not (0 <= LOGBOOK_HOUR <= 23 and 0 <= LOGBOOK_MINUTE <= 59):
                raise ValueError
            await update.message.reply_text(f"✅ Logbook otomatis diubah menjadi {LOGBOOK_HOUR:02d}:{LOGBOOK_MINUTE:02d}.")
            logger.info("LOGBOOK_HOUR changed to %s:%s by user", LOGBOOK_HOUR, LOGBOOK_MINUTE)
        except (ValueError, IndexError):
            await update.message.reply_text("❗ Format salah. Gunakan /schedule 10:30")
    else:
        await update.message.reply_text(f"⏰ Logbook otomatis dijadwalkan pada {LOGBOOK_HOUR:02d}:{LOGBOOK_MINUTE:02d}.")

async def scheduled_logbook(context: ContextTypes.DEFAULT_TYPE):
    """JobQueue callback: run logbook at the configured hour and minute."""
    now = datetime.now()
    if now.hour == LOGBOOK_HOUR and now.minute == LOGBOOK_MINUTE:
        logger.info("Running scheduled logbook (hour=%s:%s)", LOGBOOK_HOUR, LOGBOOK_MINUTE)
        target_id = _get_stored_chat_id()
        try:
            await context.bot.send_message(chat_id=target_id, text="🚀 Menjalankan logbook otomatis, mohon tunggu…")
        except Exception as e:
            logger.error("Gagal kirim status awal scheduler: %s", e)
        result = await run_logbook()   # async Playwright
        if target_id:
            try:
                await context.bot.send_message(chat_id=target_id, text=result, parse_mode="Markdown")
            except Exception as e:
                logger.error("Failed to send scheduled notification: %s", e)

async def myid_cmd(update: Update, _: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    _store_chat_id(cid)
    await update.message.reply_text(f"🆔 Chat ID Anda: `{cid}`\n(Tersimpan untuk notifikasi otomatis.)", parse_mode="Markdown")

async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Mulai interaksi"),
        BotCommand("logbook", "Kirim logbook otomatis"),
        BotCommand("ask", "Tanya sesuatu ke AI (contoh: /ask apa itu MONEV?)"),
        BotCommand("schedule", "Lihat atau ubah jam otomatis logbook"),
        BotCommand("myid", "Tampilkan chat ID Anda"),
        BotCommand("help", "Tampilkan daftar perintah"),
    ])

def main():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing in .env")
        return
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("logbook", logbook_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    # Register the explicit LLM query command
    app.add_handler(CommandHandler("ask", ask))
    # Register help and schedule commands
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("schedule", schedule_cmd))
    app.add_handler(CommandHandler("myid", myid_cmd))

    # Schedule the job to run every minute
    app.job_queue.run_repeating(scheduled_logbook, interval=60, first=0)

    # Start polling (this handles the event loop internally)
    app.run_polling()

if __name__ == "__main__":
    main()
