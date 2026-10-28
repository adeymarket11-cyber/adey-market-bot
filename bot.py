import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8780198432:AAH6rW5Miw2nP9HMZ67lqyUOKmDjGPrGYQk"
ADMIN_ID = "8703011579"

bot = telebot.TeleBot(BOT_TOKEN)

CATEGORY_CHANNELS = {
    "bed": ("🛏️ አልጋ", "@adey_market_bed"),
    "washing": ("🧺 Washing Machine", "@adey_market_washingmachine"),
    "fridge": ("🧊 ፍሪጅ", "@adey_market_Refrigerator"),
    "sofa": ("🛋️ ሶፋ", "@adey_market_sofa"),
    "tv": ("📺 TV / ቲቪ ስታንድ", "@adey_market_Tv"),
    "wardrobe": ("🚪 ቁምሳጥን", "@adey_market_Wardrobe"),
    "dining": ("🍽️ የምግብ ጠረቤዛ", "@adey_market_dining_table"),
    "furniture": ("🪑 ፈርኒቸር", "@adey_market_furniture"),
    "extra": ("✨ ተጨማሪ", "@adey_market_other"),
}

CATEGORIES = [
    ("🛏️ አልጋ", "https://t.me/adey_market_bed"),
    ("🧺 Washing Machine", "https://t.me/adey_market_washingmachine"),
    ("🧊 ፍሪጅ", "https://t.me/adey_market_Refrigerator"),
    ("🛋️ ሶፋ", "https://t.me/adey_market_sofa"),
    ("📺 TV / ቲቪ ስታንድ", "https://t.me/adey_market_Tv"),
    ("🚪 ቁምሳጥን", "https://t.me/adey_market_Wardrobe"),
    ("🍽️ የምግብ ጠረቤዛ", "https://t.me/adey_market_dining_table"),
    ("🪑 ፈርኒቸር", "https://t.me/adey_market_furniture"),
    ("✨ ተጨማሪ", "https://t.me/adey_market_other"),
]

def make_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(name, url=url) for name, url in CATEGORIES]
    for i in range(0, len(buttons), 2):
        markup.add(*buttons[i:i+2])
    markup.add(InlineKeyboardButton("📩 Inbox ለማውራት", url="https://t.me/adeyused"))
    return markup

MENU_TEXT = (
    "🟡 **ADEY MARKET** 🏠\n\n"
    "ያገለገሉ የቤት እቃዎችን ከታች ይምረጡ።\n\n"
    "👇 **የሚፈልጉትን ምድብ ይንኩ።**\n\n"
    "📞 **ስልክ:** 0985427286\n"
    "📩 **Telegram Inbox:** @adeyused"
)

@bot.message_handler(commands=["start", "menu"])
def show_menu(message):
    bot.send_message(message.chat.id, MENU_TEXT, reply_markup=make_menu(), parse_mode="Markdown")

@bot.message_handler(content_types=['photo', 'video'])
def handle_admin_upload(message):
    if not ADMIN_ID or str(message.from_user.id) != str(ADMIN_ID):
        return

    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for key, (name, _) in CATEGORY_CHANNELS.items():
        buttons.append(InlineKeyboardButton(name, callback_data=f"post_{key}"))
        
    for i in range(0, len(buttons), 2):
        markup.add(*buttons[i:i+2])

    bot.reply_to(message, "📦 **ይህን እቃ የየትኛው ምድብ ቻናል ላይ ፖስት እንድርገው?**", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("post_"))
def callback_post_handler(call):
    if not ADMIN_ID or str(call.from_user.id) != str(ADMIN_ID):
        bot.answer_callback_query(call.id, "ይህን ማድረግ የሚችለው አድሚኑ ብቻ ነው!")
        return

    cat_key = call.data.replace("post_", "")
    channel_info = CATEGORY_CHANNELS.get(cat_key)
    if not channel_info:
        bot.answer_callback_query(call.id, "ቻናል አልተገኘም!")
        return

    cat_name, target_channel = channel_info
    try:
        if call.message.reply_to_message:
            bot.copy_message(target_channel, call.message.chat.id, call.message.reply_to_message.message_id)
            # Markdown ሳንጠቀም በቀጥታ ጽሁፉን እንልካለን (ግጭት እንዳይፈጥር)
            bot.edit_message_text(
                f"✅ እቃው በትክክል ወደ {cat_name} ({target_channel}) ቻናል ተልኳል!",
                call.message.chat.id, 
                call.message.message_id
            )
        else:
            bot.answer_callback_query(call.id, "እባክዎ ፎቶውን ሪፕሊ በማድረግ እንደገና ይሞክሩ።", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, f"ስህተት ተፈጥሯል: {e}", show_alert=True)

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
    while True:
        try:
            bot.remove_webhook()
            bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Polling error: {e}")
