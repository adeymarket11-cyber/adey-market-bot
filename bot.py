import logging
from asyncio import sleep
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ---------------- CONFIGURATION ----------------
TOKEN = "YOUR_BOT_TOKEN_HERE"  # የቦትዎን ቶክን እዚህ ያስገቡ
ADMIN_ID = 8703011579         # የእርስዎን Admin Telegram ID
CHANNEL_ID = "@adeymarket3"    # የመጨረሻው ፖስት የሚሄድበት ቻናል handle ወይም ID

# የፎቶዎች ጊዜያዊ ማከማቻ (Album Handling)
MEDIA_GROUPS = {}

# የምድብ ክፍሎች (Categories)
CATEGORIES = {
    "bed": "🛏️ አልጋ",
    "washing": "🧺 Washing Machine",
    "fridge": "🧊 ፍሪጅ",
    "sofa": "🛋️ ሶፋ",
    "tv": "📺 TV / ቲቪ ስታንድ",
    "wardrobe": "🚪 ቁምሳጥን",
    "dining": "🍽️ የምግብ ጠረቤዛ",
    "furniture": "🪑 ፉርኒቸር",
    "other": "✨ ተጨማሪ"
}

logging.basicConfig(level=logging.INFO)

# 1. ፎቶ (አንድም ይሁን ብዙ) ሲላክ የሚቀበል Handler
async def handle_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    media_group_id = update.message.media_group_id
    photo = update.message.photo[-1].file_id

    # ፎቶው የአልበም (የብዙ ፎቶ) አካል ከሆነ
    if media_group_id:
        if media_group_id not in MEDIA_GROUPS:
            MEDIA_GROUPS[media_group_id] = []
            MEDIA_GROUPS[media_group_id].append(photo)

            # ፎቶዎቹ በሙሉ እስኪደርሱ 1 ሰከንድ ይጠብቃል
            await sleep(1)

            photos = MEDIA_GROUPS.pop(media_group_id)
            context.user_data['pending_photos'] = photos
            await send_category_keyboard(update, context, len(photos))
        else:
            MEDIA_GROUPS[media_group_id].append(photo)
    else:
        # አንድ ፎቶ ብቻ ከሆነ
        context.user_data['pending_photos'] = [photo]
        await send_category_keyboard(update, context, 1)

# 2. የምድብ መምረጫ ቁልፎችን ለይቶ ማሳያ
async def send_category_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, count: int):
    keyboard = []
    keys = list(CATEGORIES.keys())
    for i in range(0, len(keys), 2):
        row = [InlineKeyboardButton(CATEGORIES[keys[i]], callback_data=f"cat_{keys[i]}")]
        if i + 1 < len(keys):
            row.append(InlineKeyboardButton(CATEGORIES[keys[i+1]], callback_data=f"cat_{keys[i+1]}"))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"📦 **{count} ፎቶ(ዎች) ተቀብለናል!**\n\nይህንን እቃ የየትኛው ምድብ ቻናል ላይ ፖስት እንዲሆን ይፈልጋሉ?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# 3. ምድብ ሲመረጥ መረጃ እንዲያስገባ መጠየቂያ
async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category_key = query.data.replace("cat_", "")
    context.user_data['selected_category'] = CATEGORIES[category_key]

    await query.edit_message_text(
        f"✅ የተመረጠው ምድብ: **{CATEGORIES[category_key]}**\n\n"
        "አሁን የእቃውን መረጃ በሚከተለው ፎርማት ይላኩልኝ፦\n\n"
        "የእቃው አይነት: DiningTable\n"
        "ዋጋ: 32,000\n"
        "ቦታ: ፉሪ\n"
        "ሁኔታ: ጥሩ ነው",
        parse_mode="Markdown"
    )

# 4. መረጃው ሲላክ ቻናል ላይ አልበም አድርጎ ፖስት ማድረጊያ
async def handle_text_and_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    photos = context.user_data.get('pending_photos')
    category = context.user_data.get('selected_category', 'ቤት እቃዎች')

    if not photos:
        await update.message.reply_text("እባክዎን በመጀመሪያ የቃውን ፎቶ(ዎች) ይላኩ።")
        return

    text = update.message.text

    caption = (
        f"🟡 **ADEY MARKET** 🏠\n\n"
        f"📦 **የእቃው ምድብ:** {category}\n"
        f"{text}\n\n"
        f"📞 **ለመግዛት:** 0985427286\n"
        f"📩 **Inbox:** @adeyused\n\n"
        f"👇 **JOIN ያድርጉ:**\n"
        f"👉 {CHANNEL_ID}"
    )

    # ፎቶዎቹን በአንድ ላይ (Media Group/Album) ወደ ቻናል መላክ
    if len(photos) == 1:
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=photos[0],
            caption=caption,
            parse_mode="Markdown"
        )
    else:
        media = [InputMediaPhoto(media=p) for p in photos]
        # የመጀመሪያው ፎቶ ላይ Caption ያያይዛል
        media[0] = InputMediaPhoto(media=photos[0], caption=caption, parse_mode="Markdown")
        await context.bot.send_media_group(chat_id=CHANNEL_ID, media=media)

    await update.message.reply_text("✅ እቃው በስኬት ቻናል ላይ ፖስት ተደርጓል!")

    # Memory Clear ማድረግ
    context.user_data.clear()

# main function
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.PHOTO, handle_photos))
    app.add_handler(CallbackQueryHandler(category_callback, pattern="^cat_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_and_post))

    print("Bot is running...")
    app.run_polling()
