import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ===== ADEY MARKET SETTINGS =====

BOT_TOKEN = "8780198432:AAH6rW5Miw2nP9HMZ67lqyUOKmDjGPrGYQk"
ADMIN_ID = "8703011579"

bot = telebot.TeleBot(BOT_TOKEN)


# ለእያንዳንዱ እቃ የተለዩ የቴሌግራም ቻናሎች
CATEGORY_CHANNELS = {
    "bed": ("🛏️ አልጋ", "@adey_market_bed"),
    "washing": ("🧺 Washing Machine", "@adey_market_washingmachine"),
    "fridge": ("🧊 ፍሪጅ", "@adey_market_Refrigerator"),
    "sofa": ("🛋️ ሶፋ", "@adey_market_sofa"),
    "tv": ("📺 TV", "@adey_market_Tv"),
    "wardrobe": ("🚪 ቁምሳጥን", "@adey_market_Wardrobe"),
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


# ===== SMART ADMIN POSTING (አድሚኑ ፎቶ ሲልክ ምርጫ የሚያሳይ) =====

@bot.message_handler(content_types=['photo', 'video', 'text'])
def handle_admin_upload(message):
    # አድሚኑ ብቻ መሆኑን እናረጋግጣለን (በግል ቻት ውስጥ ሲልክ)
    if not ADMIN_ID or str(message.from_user.id) != str(ADMIN_ID):
        return

    # አድሚኑ ፎቶ ወይም ቪዲዮ ሲልክ ቦቱ የትኛውን ቻናል እንደሚመርጥ ቁልፎችን ያሳያል
    if message.content_type in ['photo', 'video']:
        markup = InlineKeyboardMarkup(row_width=2)
        
        # ለእያንዳንዱ ምድብ አዝራር እንፈጥራለን (callback_data ውስጥ የቻናሉ ቁልፍ ይያዛል)
        buttons = []
        for key, (name, _) in CATEGORY_CHANNELS.items():
            buttons.append(InlineKeyboardButton(name, callback_data=f"post_{key}"))
            
        for i in range(0, len(buttons), 2):
            markup.add(*buttons[i:i+2])

        bot.reply_to(
            message,
            "📦 ይህንን እቃ የየትኛው ምድብ ቻናል ላይ ፖስት እንድርገው?",
            reply_markup=markup
        )


# አድሚኑ ከቀረቡት ቁልፎች ውስጥ አንዱን ሲጫን የሚሰራ
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
        # የተላከውን ፎቶ/መረጃ ወደ ተመረጠው ቻናል ኮፒ ያደርጋል
        if call.message.reply_to_message:
            bot.copy_message(target_channel, call.message.chat.id, call.message.reply_to_message.message_id)
            bot.edit_message_text(
                f"✅ እቃው በትክክል ወደ **{cat_name}** ({target_channel}) ቻናል ተልኳል!",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )
        else:
            bot.answer_callback_query(call.id, "የመጀመሪያው ፎቶ ጠፍቷል እባክዎ እንደገና ይሞክሩ።", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, f"ስህተት ተፈጥሯል: {e}", show_alert=True)


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
