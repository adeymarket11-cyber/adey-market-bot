import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ===== ADEY MARKET SETTINGS =====

BOT_TOKEN = "8780198432:AAH6rW5Miw2nP9HMZ67lqyUOKmDjGPrGYQk"
ADMIN_ID = "8703011579"

bot = telebot.TeleBot(BOT_TOKEN)


# ለእያንዳንዱ እቃ የተለዩ የቴሌግራም ቻናሎች (ለፖስቲንግ አገልግሎት)
CATEGORY_CHANNELS = {
    "bed": "@adey_market_bed",
    "washing": "@adey_market_washingmachine",
    "fridge": "@adey_market_Refrigerator",
    "sofa": "@adey_market_sofa",
    "tv": "@adey_market_Tv",
    "wardrobe": "@adey_market_Wardrobe",
}

# ለሜኑ ቁልፎች የሚያገለግሉ ሊንኮች
CATEGORIES = [
    ("🛏️ አልጋ", "https://t.me/adey_market_bed"),
    ("🧺 Washing Machine", "https://t.me/adey_market_washingmachine"),
    ("🧊 ፍሪጅ", "https://t.me/adey_market_Refrigerator"),
    ("🛋️ ሶፋ", "https://t.me/adey_market_sofa"),
    ("📺 TV", "https://t.me/adey_market_Tv"),
    ("🚪 ቁምሳጥን", "https://t.me/adey_market_Wardrobe"),
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


# ===== ADMIN POSTING COMMANDS =====
# አድሚኑ እቃዎችን በቀጥታ ወደየራሳቸው ቻናል ለመልቀቅ እነዚህን ትዕዛዞች ይጠቀማል

@bot.message_handler(commands=["postbed", "postwashing", "postfridge", "postsofa", "posttv", "postwardrobe"])
def handle_posting(message):
    if not ADMIN_ID or str(message.from_user.id) != str(ADMIN_ID):
        bot.reply_to(message, "ይህን ትእዛዝ አድሚኑ ብቻ መጠቀም ይችላል።")
        return

    # የትእዛዙን አይነት በመለየት ተስማሚውን ቻናል እንመርጣለን
    command = message.text.split()[0].replace("/", "")
    cat_key = command.replace("post", "")
    
    target_channel = CATEGORY_CHANNELS.get(cat_key)
    
    if not target_channel:
        bot.reply_to(message, "ትክክለኛ ቻናል አልተገኘም።")
        return

    # አድሚኑ የላከውን ፎቶ ወይም ጽሁፍ ወደ ቻናሉ እናስተላልፋለን
    try:
        if message.reply_to_message:
            bot.copy_message(target_channel, message.chat.id, message.reply_to_message.message_id)
            bot.reply_to(message, f"እቃው በትክክል ወደ {target_channel} ተልኳል!")
        else:
            bot.reply_to(message, "እባክዎ መለጠፍ የሚፈልጉትን ፎቶ/መረጃ (Caption ጋር) Reply በማድረግ ትዕዛዙን ይጻፉ።")
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
