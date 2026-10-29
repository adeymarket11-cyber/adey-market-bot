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

# አልበሞችን ለመሰብሰብ የሚረዳ መዝገብ
media_groups = {}

async def handle_admin_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADMIN_ID or str(update.message.from_user.id) != str(ADMIN_ID):
        return

    message = update.message
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = []
    row = []
    for key, (name, _) in CATEGORY_CHANNELS.items():
        row.append(InlineKeyboardButton(name, callback_data=f"post_{key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    markup = InlineKeyboardMarkup(keyboard)

    # ፎቶው በአልበም (Media Group) መልክ ከመጣ
    if message.media_group_id:
        gid = message.media_group_id
        if gid not in media_groups:
            media_groups[gid] = {
                "messages": [],
                "sent_prompt": False
            }
        
        media_groups[gid]["messages"].append(message)
        
        # ፎቶዎቹ በሙሉ እስኪሰባሰቡ ለጥቂት ሰኮንዶች እንጠብቃለን
        await asyncio.sleep(1.0)
        
        # አንዴ ብቻ (በመጀመሪያው ፎቶ ስር) የምድብ ምርጫ ቁልፉን እንልካለን
        if not media_groups[gid]["sent_prompt"]:
            media_groups[gid]["sent_prompt"] = True
            await message.reply_text(
                "📦 **ይህንን አልበም የየትኛው ምድብ ቻናል ላይ ፖስት እንድርገው?** ከታች ይምረጡ:",
                parse_mode="Markdown",
                reply_markup=markup
            )
    else:
        # ነጠላ ፎቶ ወይም ቪዲዮ ከሆነ
        await message.reply_text(
            "📦 **ይህን እቃ የየትኛው ምድብ ቻናል ላይ ፖስት እንድርገው?** ከታች ይምረጡ:",
            parse_mode="Markdown",
            reply_markup=markup
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not ADMIN_ID or str(query.from_user.id) != str(ADMIN_ID):
        await query.answer("ይህን ማድረግ የሚችለው አድሚኑ ብቻ ነው!", show_alert=True)
        return

    await query.answer()
    data = query.data
    if not data.startswith("post_"):
        return

    cat_key = data.replace("post_", "")
    channel_info = CATEGORY_CHANNELS.get(cat_key)
    if not channel_info:
        await query.edit_message_text("ቻናል አልተገኘም!")
        return

    cat_name, target_channel = channel_info
    reply_msg = query.message.reply_to_message

    if not reply_msg:
        await query.edit_message_text("እባክዎ መልእክቱን ሪፕሊ በማድረግ እንደገና ይሞክሩ።")
        return

    try:
        # ሪፕሊ የተደረገበት መልእክት አልበም (Media Group) አካል መሆኑን እንፈትሻለን
        target_gid = None
        for gid, group_data in media_groups.items():
            if any(m.message_id == reply_msg.message_id for m in group_data["messages"]):
                target_gid = gid
                break

        if target_gid:
            group_data = media_groups.pop(target_gid)
            media_list = []
            for idx, m in enumerate(group_data["messages"]):
                if m.photo:
                    file_id = m.photo[-1].file_id
                    caption = m.caption if idx == 0 else ""
                    media_list.append(InputMediaPhoto(media=file_id, caption=caption, parse_mode="Markdown"))
            
            if media_list:
                await context.bot.send_media_group(chat_id=target_channel, media=media_list)
                await query.edit_message_text(f"✅ አልበሙ በትክክል ወደ {cat_name} ({target_channel}) ቻናል ተልኳል!")
            else:
                await query.edit_message_text("ፎቶዎቹን ማንበብ አልተቻለም።")
        else:
            # ነጠላ ፎቶ ወይም ቪዲዮ ከሆነ
            await context.bot.copy_message(chat_id=target_channel, from_chat_id=reply_msg.chat.id, message_id=reply_msg.message_id)
            await query.edit_message_text(f"✅ እቃው በትክክል ወደ {cat_name} ({target_channel}) ቻናል ተልኳል!")
    except Exception as e:
        await query.edit_message_text(f"ስህተት ተፈጥሯል: {e}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler(["start", "menu"], start))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO & ~filters.COMMAND, handle_admin_upload))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
