import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- 1. የRender ፖርት ችግርን የሚከላከል ሰርቨር ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Adey Market Bot is running smoothly!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

Thread(target=run_web_server, daemon=True).start()

# --- 2. የቦት ማዋቀሪያ ---
BOT_TOKEN = "8780198432:AAH6rW5Miw2nP9HMZ67lqyUOKmDjGPrGYQk"
ADMIN_ID = "8703011579"

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
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = []
    row = []
    for name, url in CATEGORIES:
        row.append(InlineKeyboardButton(name, url=url))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("📩 Inbox ለማውራት", url="https://t.me/adeyused")])
    return InlineKeyboardMarkup(keyboard)

MENU_TEXT = (
    "🟡 **ADEY MARKET** 🏠\n\n"
    "ያገለገሉ የቤት እቃዎችን ከታች ይምረጡ።\n\n"
    "👇 **የሚፈልጉትን ምድብ ይንኩ።**\n\n"
    "📞 **ስልክ:** 0985427286\n"
    "📩 **Telegram Inbox:** @adeyused"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MENU_TEXT, reply_markup=make_menu(), parse_mode="Markdown")

# የአድሚኑን ምርጫ እና የሚላኩ ፎቶዎችን ማስተባበሪያ
admin_sessions = {}
media_groups = {}

async def handle_admin_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADMIN_ID or str(update.message.from_user.id) != str(ADMIN_ID):
        return

    admin_id = update.message.from_user.id
    message = update.message

    # አድሚኑ የየትኛውን ቻናል ቁልፍ አስቀድሞ እንደመረጠ እንፈትሻለን
    if admin_id in admin_sessions:
        target_channel, cat_name = admin_sessions.pop(admin_id)
        try:
            if message.media_group_id:
                gid = message.media_group_id
                if gid not in media_groups:
                    media_groups[gid] = []
                media_groups[gid].append(message)
                
                await asyncio.sleep(1.0) # ፎቶዎቹ በሙሉ እስኪሰባሰቡ ጠብቆ መላክ
                
                if message == media_groups[gid][0]:
                    group_msgs = media_groups.pop(gid)
                    media_list = []
                    for idx, m in enumerate(group_msgs):
                        if m.photo:
                            file_id = m.photo[-1].file_id
                            caption = m.caption if idx == 0 else ""
                            media_list.append(InputMediaPhoto(media=file_id, caption=caption, parse_mode="Markdown"))
                    
                    if media_list:
                        await context.bot.send_media_group(chat_id=target_channel, media=media_list)
                        await message.reply_text(f"✅ አልበሙ በትክክል ወደ {cat_name} ({target_channel}) ቻናል ተልኳል!")
            else:
                # ነጠላ ፎቶ ወይም ቪዲዮ ከሆነ
                await context.bot.copy_message(chat_id=target_channel, from_chat_id=message.chat.id, message_id=message.message_id)
                await message.reply_text(f"✅ እቃው በትክክል ወደ {cat_name} ({target_channel}) ቻናል ተልኳል!")
        except Exception as e:
            await message.reply_text(f"ስህተት ተፈጥሯል: {e}")
    else:
        # አድሚኑ ቁልፉን ሳይመርጥ ፎቶ ከላከ፣ የምድብ ምርጫ ቁልፎቹን እናሳየዋለን
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = []
        row = []
        for key, (name, _) in CATEGORY_CHANNELS.items():
            row.append(InlineKeyboardButton(name, callback_data=f"select_{key}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        markup = InlineKeyboardMarkup(keyboard)

        # ፎቶውን ለጊዜው እንይዘዋለን
        await message.reply_text("📦 **መጀመሪያ እቃው የሚለጠፍበትን ምድብ ቻናል ይምረጡ:**", parse_mode="Markdown", reply_markup=markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not ADMIN_ID or str(query.from_user.id) != str(ADMIN_ID):
        await query.answer("ይህን ማድረግ የሚችለው አድሚኑ ብቻ ነው!", show_alert=True)
        return

    await query.answer()
    data = query.data
    if not data.startswith("select_"):
        return

    cat_key = data.replace("select_", "")
    channel_info = CATEGORY_CHANNELS.get(cat_key)
    if not channel_info:
        await query.edit_message_text("ቻናል አልተገኘም!")
        return

    cat_name, target_channel = channel_info
    admin_sessions[query.from_user.id] = (target_channel, cat_name)

    await query.edit_message_text(f"✅ **{cat_name}** ተመርጧል!\nአሁን ፎቶውን ወይም አልበሙን (Media Group) ይላኩ, ቦቱ በቀጥታ ወደ ቻናሉ ይለጥፋል ሂደት ይጀምራል።", parse_mode="Markdown")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler(["start", "menu"], start))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO & ~filters.COMMAND, handle_admin_upload))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
