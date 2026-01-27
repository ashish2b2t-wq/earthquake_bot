import requests
import asyncio
from flask import Flask
from threading import Thread

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ========== CONFIG ==========
BOT_TOKEN = "8460162101:AAEyHziGS-IN7rEidek8_Xl_SCY6RVuk21o"
MIN_MAGNITUDE = 0.5  # Change if you want
CHECK_INTERVAL = 300  # seconds (5 minutes)

subscribers = set()
last_event_id = None

# ========== FLASK SERVER (needed for Render) ==========
app = Flask(__name__)

@app.route("/")
def home():
    return "Earthquake Bot Running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ========== TELEGRAM COMMANDS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers.add(chat_id)
    await update.message.reply_text("✅ You are subscribed to GLOBAL earthquake alerts 🌍")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers.discard(chat_id)
    await update.message.reply_text("❌ You unsubscribed from alerts.")

# ========== EARTHQUAKE CHECKER ==========
async def check_earthquakes(bot_app):
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
                    time = event["properties"]["time"]
                    lat, lon, _ = event["geometry"]["coordinates"]

                    message = (
                        f"🚨 *Earthquake Alert!*\n\n"
                        f"🌍 Location: {place}\n"
                        f"📏 Magnitude: {magnitude}\n"
                        f"📍 Coordinates: {lon}, {lat}"
                    )

                    for user in subscribers:
                        await bot_app.bot.send_message(
                            chat_id=user,
                            text=message,
                            parse_mode="Markdown"
                        )

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(CHECK_INTERVAL)

# ========== MAIN ==========
async def main():
    telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("stop", stop))

    # Start earthquake monitoring task
    telegram_app.create_task(check_earthquakes(telegram_app))

    await telegram_app.run_polling()

# Run Flask in separate thread
Thread(target=run_flask).start()

# Start bot
asyncio.run(main())
