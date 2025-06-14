# telegram_bot.py
from telegram.ext import ApplicationBuilder, CommandHandler
import asyncio
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("Bot is alive!")

async def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # ✅ Instead of app.run_polling(), use this async-friendly way:
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
