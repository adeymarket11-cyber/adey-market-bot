import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

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

# ብዙ ፎቶዎችን (Media Groups) ለመሰብሰብ የሚረዳ ማህደር
pending_albums = {}

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

    # ፎቶው በአልበም (Media Group) መልክ የመጣ ከሆነ
    if message.media_group_id:
        gid = message.media_group_id
        if gid not in pending_albums:
            pending_albums[gid] = {
                "messages": [],
                "target_message": message # አድሚኑ ቁልፉን እንዲነካበት
            }
        pending_albums[gid]["messages"].append(message)
        
        # የመጀመሪያው ፎቶ ላይ ብቻ የምድብ ምርጫ ቁልፎቹን እንለጥፋለን
        if len(pending_albums[gid]["messages"]) == 1:
            bot.reply_to(message, f"📦 **ይህ አልበም (Media Group) የየትኛው ምድብ ቻናል ላይ ፖስት እንድርገው?**\n(አልበሙ በመሰብሰብ ላይ ነው...) ይጫኑ:", parse_mode="Markdown", reply_markup=markup)
    else:
        # ነጠላ ፎቶ ወይም ቪዲዮ ከሆነ
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
        replied_msg = call.message.reply_to_message
        if replied_msg:
            # ፎቶው በአልበም (Media Group) መልክ የመጣ መሆኑን ማረጋገጥ
            if replied_msg.media_group_id and replied_msg.media_group_id in pending_albums:
                gid = replied_msg.media_group_id
                album_data = pending_albums.pop(gid, None)
                
                if album_data and album_data["messages"]:
                    media_group = []
                    for m in album_data["messages"]:
                        if m.photo:
                            file_id = m.photo[-1].file_id
                            # የመጀመሪያው ፎቶ ላይ ካፕሽን (Caption) ካለው እንይዛለን
                            caption = m.caption if m == album_data["messages"][0] else ""
                            media_group.append(InputMediaPhoto(file_id, caption=caption, parse_mode="Markdown"))
                    
                    if media_group:
                        bot.send_media_group(target_channel, media_group)
                        bot.edit_message_text(
                            f"✅ አልበሙ (Media Group) በትክክል ወደ {cat_name} ({target_channel}) ቻናል ተልኳል!",
                            call.message.chat.id, 
                            call.message.message_id
                        )
                    else:
                        bot.answer_callback_query(call.id, "ፎቶዎቹን ማንበብ አልተቻለም።", show_alert=True)
                else:
                    bot.answer_callback_query(call.id, "የአልበሙ መረጃ አልተገኘም፣ እባክዎ እንደገና ይሞክሩ።", show_alert=True)
            else:
                # ነጠላ ፎቶ ወይም መልእክት ከሆነ
                bot.copy_message(target_channel, call.message.chat.id, replied_msg.message_id)
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
