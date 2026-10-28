import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ===== ADEY MARKET SETTINGS =====

BOT_TOKEN = os.getenv("8780198432:AAH6rW5Miw2nP9HMZ67lqyUOKmDjGPrGYQk")
CHANNEL_ID = os.getenv("@adeymark")
ADMIN_ID = os.getenv("870301157")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in Render Environment Variables")

bot = telebot.TeleBot(BOT_TOKEN)


# ማስታወሻ፡ BED_URL, WASHING_MACHINE_URL ወዘተ የሚሉትን በትክክለኛ የቴሌግራም ቻናልዎ ፖስት ሊንክ ወይም ዌብሳይት ይተኩ።
# ምሳሌ፡ "https://t.me/adeyused/123"
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

    # አዝራሮቹን በሁለት በሁለት ረድፍ ለማደራጀት
    buttons = [InlineKeyboardButton(name, url=url) for name, url in CATEGORIES]
    
    # 2 በ 2 ማደራጀት
    for i in range(0, len(buttons), 2):
        markup.add(*buttons[i:i+2])

    # የInbox አዝራር በብቸኝነት ከታች እንዲሆን
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


# Publish a menu post to your channel.
@bot.message_handler(commands=["publishmenu"])
def publish_menu(message):
    # ADMIN_ID በትክክል መሰጠቱን ማረጋገጥ
    if not ADMIN_ID or str(message.from_user.id) != str(ADMIN_ID):
        bot.reply_to(message, "ይህን ትእዛዝ አድሚኑ ብቻ መጠቀም ይችላል።")
        return

    if not CHANNEL_ID:
        bot.reply_to(message, "CHANNEL_ID በRender ላይ አልተዘጋጀም።")
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
    # Web server በጀርባ እንዲሰራ ማድረግ
    threading.Thread(target=run_web_server, daemon=True).start()

    print("ADEY MARKET Bot is running...")
    bot.infinity_polling(skip_pending=True)
