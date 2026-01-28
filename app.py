import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8242017172:AAHyFWsoHrKCpeAiGQIIBb6AxpROjGFyfTg"

logging.basicConfig(level=logging.INFO)

subscribers = set()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers.add(chat_id)
    await update.message.reply_text("✅ You are subscribed to GLOBAL earthquake alerts 🌍")

# Earthquake checker
async def check_earthquakes(context: ContextTypes.DEFAULT_TYPE):
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_hour.geojson"
    data = requests.get(url).json()

    for quake in data["features"][:1]:
        mag = quake["properties"]["mag"]
        place = quake["properties"]["place"]
        link = quake["properties"]["url"]

        message = f"🚨 Earthquake Alert!\nMagnitude: {mag}\nLocation: {place}\nMore info: {link}"

        for chat_id in subscribers:
            await context.bot.send_message(chat_id, message)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # Run earthquake check every 5 min
    app.job_queue.run_repeating(check_earthquakes, interval=300, first=10)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
