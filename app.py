import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8242017172:AAHyFWsoHrKCpeAiGQIIBb6AxpROjGFyfTg"
MIN_MAGNITUDE = 0.5

app = Flask(__name__)
bot = Bot(BOT_TOKEN)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

subscribers = set()
last_event_id = None

# ===== TELEGRAM COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribers.add(update.effective_chat.id)
    await update.message.reply_text("✅ Subscribed to earthquake alerts 🌍")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribers.discard(update.effective_chat.id)
    await update.message.reply_text("❌ Unsubscribed")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("stop", stop))

# ===== WEBHOOK ROUTE =====
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok"

# ===== ROOT ROUTE =====
@app.route("/")
def home():
    return "Bot running"

# ===== EARTHQUAKE CHECK =====
async def check_earthquakes():
    global last_event_id
    while True:
        try:
            url = f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{MIN_MAGNITUDE}_hour.geojson"
            data = requests.get(url).json()
            if data["features"]:
                event = data["features"][0]
                event_id = event["id"]

                if event_id != last_event_id:
                    last_event_id = event_id
                    mag = event["properties"]["mag"]
                    place = event["properties"]["place"]

                    msg = f"🚨 Earthquake Alert!\n🌍 {place}\n📏 Magnitude: {mag}"
                    for user in subscribers:
                        await bot.send_message(user, msg)
        except:
            pass

# ===== START TELEGRAM BACKEND =====
telegram_app.create_task(check_earthquakes())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

