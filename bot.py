import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Render ፖርት እንዲጠይቅ ስለሚፈልግ የሚከፈት አነስተኛ ሰርቨር (በጀርባ የሚሰራ)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# ሰርቨሩን ከቦቱ ጋር በአንድ ላይ በጀርባ (Background) ማስጀመር
threading.Thread(target=run_server, daemon=True).start()

# የቴሌግራም ቦት ማስተካከያዎችዎ
TOKEN = "8780198432:AAF5vqtPUan2dmKPSXmuCCZCiutle_VelZs"
bot = telebot.TeleBot(TOKEN)

ADMIN_CHAT_ID = "8703011579"
CHANNEL_USERNAME = "@adeymarket3"

BOT_LINK = "https://t.me/Adey_used_bot"
ADMIN_USERNAME = "https://t.me/adeyused"
ADMIN_PHONE_LINK = "https://t.me/adeyused"

# --- የቦቱ ዋና ተግባራት እና የኮድ ክፍሎች ---
user_albums = {}

@bot.message_handler(commands=['start'])
def send_welcome(bot_message):
    bot.reply_to(bot_message, "ሰላም! ወደ adey-market-bot እንኳን በደህና መጡ።")

# (የቀሩት የቦትዎ ኮዶች ካሉዎት ከዚህ በታች መለጠፍ ይችላሉ፣ ዋናው ቦቱ እንዳይዘጋ የሚያደርገው infinity_polling ከታች ተቀምጧል)

# ቦቱ ያለማቋረጥ እንዲሰራ የሚያደርገው ትዕዛዝ (ይህ መጥፋት የለበትም)
bot.infinity_polling()
