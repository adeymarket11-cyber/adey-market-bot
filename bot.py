import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ===== ADEY MARKET SETTINGS =====

# አዲሱ እና ትክክለኛው የቦት ቶከን
BOT_TOKEN = "8780198432:AAH6rW5Miw2nP9HMZ67lqyUOKmDjGPrGYQk"

CHANNEL_ID = "@adeymarket3"
ADMIN_ID = "8703011579"

bot = telebot.TeleBot(BOT_TOKEN)


# የቴሌግራም ቻናልዎ ትክክለኛ የፖስት ሊንኮች እዚህ ይገባሉ
CATEGORIES = [
    ("🛏️ አልጋ", "https://t.me/adeyused"),
    ("🧺 Washing Machine", "https://t.me/adeyused"),
    ("🧊 ፍሪጅ", "https://t.me/adeyused"),
    ("🛋️ ሶፋ", "https://t.me/adeyused"),
    ("📺 TV", "https://t.me/adeyused"),
    ("🚪 ቁምሳጥን", "https://t.me/adeyused"),
]


def make_menu():
    markup = InlineKeyboardMarkup(row_width=2)

    buttons = [InlineKeyboardButton(name, url=url) for name, url in CATEGORIES]
    
    for i in range(0, len(buttons), 2):
        markup.add(*buttons[i:i+2])

    markup.add(
        InlineKeyboardButton(
            "📩 Inbox ለማውራት",
            url="https://t.me/adeyused"
        )
    )

    return markup


MENU_TEXT = (
    "🟡 ADEY MARKET 🏠\n\n"
    "ያገለገሉ የቤት እቃዎችን ከታች ይምረጡ።\n\n"
    "👇 የሚፈልጉትን ምድብ ይንኩ።\n\n"
    "📞 ስልክ: 0985427286\n"
    "📩 Telegram Inbox: @adeyused\n\n"
    "🤝 ሻጭን ከገዢ እናገናኛለን!"
)


# ===== BOT MENU =====

@bot.message_handler(commands=["start", "menu"])
def show_menu(message):
    bot.send_message(
        message.chat.id,
        MENU_TEXT,
        reply_markup=make_menu()
    )


@bot.message_handler(commands=["publishmenu"])
def publish_menu(message):
    if not ADMIN_ID or str(message.from_user.id) != str(ADMIN_ID):
        bot.reply_to(message, "ይህን ትእዛዝ አድሚኑ ብቻ መጠቀም ይችላል።")
        return

    if not CHANNEL_ID:
        bot.reply_to(message, "CHANNEL_ID አልተዘጋጀም።")
        return

    try:
        bot.send_message(
            CHANNEL_ID,
            MENU_TEXT,
            reply_markup=make_menu()
        )
        bot.reply_to(message, "የADEY MARKET ሜኑ ወደ Channel ተልኳል።")
    except Exception as e:
        bot.reply_to(message, f"ስህተት ተፈጥሯል: {e}")


# ===== RENDER HEALTH CHECK =====

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ADEY MARKET Bot is active!")

    def log_message(self, format, *args):
        pass


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()

    print("ADEY MARKET Bot is running...")
    bot.infinity_polling(skip_pending=True)
