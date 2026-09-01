import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Render ፖርት እንዲኖር ስለሚፈልግ የሚከፈት አነስተኛ ሰርቨር
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

# (ቀጣዩ የቦትዎ ኮዶች እዚህ ይቀጥላሉ... ማስታወሻ፦ ከዚህ በታች ያሉትን የቦትዎን ትክክለኛ የኮድ ክፍሎች ማስተካከል ከፈለጉ ማስገባት ይችላሉ)
