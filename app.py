import requests
import asyncio
from flask import Flask
from threading import Thread

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= CONFIG =================
BOT_TOKEN = ""
MIN_MAGNITUDE = 0.5
CHECK_INTERVAL = 300  # seconds

subscribers = set()
last_event_id = None

# ================= FLASK SERVER =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Earthquake Bot Running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ================= TELEGRAM COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers.add(chat_id)
    await update.message.reply_text("✅ You are subscribed to GLOBAL earthquake alerts 🌍")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers.discard(chat_id)
    await update.message.reply_text("❌ You unsubscribed from alerts.")

# ================= EARTHQUAKE CHECKER =================
async def check_earthquakes(app_bot):
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

                    magnitude = event["properties"]["mag"]
                    place = event["properties"]["place"]
                    lon, lat, _ = event["geometry"]["coordinates"]

                    message = (
                        f"🚨 *Earthquake Alert!*\n\n"
                        f"🌍 Location: {place}\n"
                        f"📏 Magnitude: {magnitude}\n"
                        f"📍 Coordinates: {lat}, {lon}"
                    )

                    for user in subscribers:
                        await app_bot.bot.send_message(chat_id=user, text=message, parse_mode="Markdown")

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(CHECK_INTERVAL)

# ================= BOT START FUNCTION =================
def start_bot():
    telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("stop", stop))

    telegram_app.create_task(check_earthquakes(telegram_app))
    telegram_app.run_polling()

# ================= RUN BOTH =================
Thread(target=run_flask).start()
Thread(target=start_bot).start()
