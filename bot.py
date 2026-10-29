import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

BOT_TOKEN = "8780198432:AAH6rW5Miw2nP9HMZ67lqyUOKmDjGPrGYQk"
ADMIN_IDS = ["8703011579", "8144813729", "8994655471"]

bot = telebot.TeleBot(BOT_TOKEN)
MAIN_CHANNEL = "@adeymarket3"

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

CATEGORIES_MENU = [
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
    buttons = [InlineKeyboardButton(name, url=url) for name, url in CATEGORIES_MENU]
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

admin_sessions = {}
media_group_buffer = {}

@bot.message_handler(content_types=['photo', 'video'])
def handle_admin_upload(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return

    admin_id = message.from_user.id
    
    if message.media_group_id:
        gid = message.media_group_id
        if gid not in media_group_buffer:
            media_group_buffer[gid] = {
                "messages": [],
                "sent_prompt": False
            }
        media_group_buffer[gid]["messages"].append(message)
        time.sleep(0.5)
        
        if not media_group_buffer[gid]["sent_prompt"]:
            media_group_buffer[gid]["sent_prompt"] = True
            ask_category(message, gid)
    else:
        media_group_buffer[message.message_id] = {
            "messages": [message],
            "sent_prompt": True
        }
        ask_category(message, message.message_id)

def ask_category(message, identifier):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for key, (name, _) in CATEGORY_CHANNELS.items():
        buttons.append(InlineKeyboardButton(name, callback_data=f"cat_{identifier}_{key}"))
    for i in range(0, len(buttons), 2):
        markup.add(*buttons[i:i+2])
    
    bot.reply_to(message, "📦 **ይህ እቃ የየትኛው ምድብ ነው?** ከታች ይምረጡ:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def callback_category(call):
    if str(call.from_user.id) not in ADMIN_IDS:
        return
    
    parts = call.data.split("_")
    identifier = parts[1]
    cat_key = "_".join(parts[2:])
    
    admin_sessions[call.from_user.id] = {
        "identifier": identifier,
        "cat_key": cat_key
    }

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✨ አዲስ (New)", callback_data="cond_New"),
        InlineKeyboardButton("🔄 ያገለገለ (Used)", callback_data="cond_Used"),
        InlineKeyboardButton("⭐ ንጹህ (Slightly Used)", callback_data="cond_SlightlyUsed"),
        InlineKeyboardButton("🏚️ ያረጀ (Old)", callback_data="cond_Old")
    )
    bot.edit_message_text("🛠️ **የእቃውን ሁኔታ (Condition) ይምረጡ:**", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cond_"))
def callback_condition(call):
    if str(call.from_user.id) not in ADMIN_IDS:
        return
    
    cond = call.data.replace("cond_", "")
    cond_map = {
        "New": "✨ አዲስ (New)",
        "Used": "🔄 ያገለገለ (Used)",
        "SlightlyUsed": "⭐ ንጹህ (Slightly Used)",
        "Old": "🏚️ ያረጀ (Old)"
    }
    
    if call.from_user.id in admin_sessions:
        admin_sessions[call.from_user.id]["condition"] = cond_map.get(cond, cond)
        
        bot.edit_message_text(
            "📝 **አሁን የእቃውን ዋጋ እና ቦታ ይጻፉልኝ**\n\n"
            "*(ማስታወሻ: ዋጋውን ብቻ ወይም ዋጋ እና ቦታ በአንድ ላይ መጻፍ ይችላሉ)*", 
            call.message.chat.id, 
            call.message.message_id, 
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda m: m.from_user.id in admin_sessions)
def handle_price_location(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return

    session = admin_sessions.pop(message.from_user.id, None)
    if not session:
        return

    user_text = message.text.strip()
    
    # ዋጋ እና ቦታን ለመለየት (በ | ወይም በባዶ ቦታ)
    if "|" in user_text:
        parts = user_text.split("|")
        price = parts[0].strip()
        location = parts[1].strip()
    else:
        # በባዶ ቦታ የተለየ ከሆነ ወይም ዋጋ ብቻ ከገባ
        parts = user_text.split(maxsplit=1)
        price = parts[0].strip() if len(parts) > 0 else user_text
        location = parts[1].strip() if len(parts) > 1 else "አዲስ አበባ"

    cat_key = session["cat_key"]
    identifier = session["identifier"]
    condition = session["condition"]
    
    cat_name, target_channel = CATEGORY_CHANNELS.get(cat_key, ("✨ ተጨማሪ", "@adey_market_other"))

    caption_text = (
        "🟡 **ADEY MARKET** 🏠\n\n"
        f"📦 **የእቃው አይነት፦** {cat_name}\n"
        f"💰 **ዋጋ፦** {price} ብር\n"
        f"📍 **ቦታ፦** {location}\n"
        f"☑ **ሁኔታ፦** {condition}\n"
        "📞 **ለመሸጥ፦** 0985427286\n"
        "📩 **ለInbox፦** @adeyused\n\n"
        "👇 **JOIN ያድርጉ፣ አዳዲስ እቃዎችን ያግኙ!**\n"
        f"📢 **Telegram Channel፦** {MAIN_CHANNEL}\n\n\n"
        "🤝 **ADEY MARKET**"
    )

    group_data = media_group_buffer.pop(identifier, None)
    if group_data and group_data["messages"]:
        messages = group_data["messages"]
        media_list = []
        
        for idx, m in enumerate(messages):
            if m.photo:
                file_id = m.photo[-1].file_id
                cap = caption_text if idx == 0 else ""
                media_list.append(InputMediaPhoto(file_id, caption=cap, parse_mode="Markdown"))
        
        try:
            if media_list:
                bot.send_media_group(target_channel, media_list)
                if target_channel != MAIN_CHANNEL:
                    bot.send_media_group(MAIN_CHANNEL, media_list)
                
                bot.reply_to(message, f"✅ እቃው በትክክል ወደ **{cat_name}** ({target_channel}) እና ዋናው ቻናል ተልኳል!", parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"ስህተት ተፈጥሯል: {e}")

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
