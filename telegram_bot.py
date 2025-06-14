import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
is_monitor_alive = True

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set. Check your environment variables.")

async def ping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_monitor_alive:
        await update.message.reply_text("I never left😈.")
    else:
        await update.message.reply_text("❌ Monitor seems down.")

async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("ping", ping_handler))
    await application.run_polling()
