import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8242017172:AAHyFWsoHrKCpeAiGQIIBb6AxpROjGFyfTg"
RENDER_URL = "RENDER_URL = "https://example.onrender.com"
MIN_MAGNITUDE = 0.5

app = Flask(__name__)
bot = Bot(BOT_TOKEN)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

subscribers = set()
last_event_id = None

# ---------- TELEGRAM COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribers.add(update.effective_chat.id)
    await update.message.reply_text("✅ Subscribed to earthquake alerts 🌍")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribers.discard(update.effective_chat.id)
    await update.message.reply_text("❌ Unsubscribed")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("stop", stop))

# ---------- WEBHOOK ROUTE ----------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def home():
    return "Bot is live"

# ---------- START ----------
if __name__ == "__main__":
    bot.set_webhook(url=f"{RENDER_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=10000)
