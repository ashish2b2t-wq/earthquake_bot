import requests, time, threading
from flask import Flask, request
from telegram import Bot

BOT_TOKEN = "8460162101:AAEyHziGS-IN7rEidek8_Xl_SCY6RVuk21o"
USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
MIN_MAG = 0.5

users = set()
last_id = None
bot = Bot(token=BOT_TOKEN)

def check_quakes():
    global last_id
    while True:
        try:
            data = requests.get(USGS_URL).json()
            quake = data["features"][0]
            qid = quake["id"]
            mag = quake["properties"]["mag"]
            place = quake["properties"]["place"]
            lon, lat, _ = quake["geometry"]["coordinates"]

            if qid != last_id and mag >= MIN_MAG:
                last_id = qid
                msg = f"🚨 Earthquake Alert\n🌍 {place}\n📏 Mag: {mag}\n🗺 https://maps.google.com/?q={lat},{lon}"
                for u in users:
                    bot.send_message(u, msg)
                    time.sleep(1)

        except Exception as e:
            print(e)

        time.sleep(60)

threading.Thread(target=check_quakes).start()

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text")

    if text == "/start":
        users.add(chat_id)
        bot.send_message(chat_id, "✅ Subscribed to Earthquake Alerts")

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
