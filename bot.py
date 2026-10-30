import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

BOT_TOKEN = "8780198432:AAGg6BsFGIevBGeCsVU84EzBDPfAyPqXZaQ"
ADMIN_IDS = ["8703011579", "8144813729", "8994655471"]

bot = telebot.TeleBot(BOT_TOKEN)
MAIN_CHANNEL = "@adeymarket3"
MAIN_CHANNEL_LINK = "https://t.me/adeymarket3"
ARCHIVE_CHANNEL = "@adey_market_archive"
REVIEW_CHANNEL = "@adey_market_review"

CATEGORY_CHANNELS = {
    "bed": ("🛏️ አልጋ", "@adey_market_bed"),
    "washing": ("🧺 Washing Machine", "@adey_market_washingmachine"),
    "fridge": ("🧊 ፍሪጅ", "@adey_market_Refrigerator"),
    "sofa": ("🛋️ ሶፋ", "@adey_market_sofa"),
    "tv": ("📺 ቲቪ (TV)", "@adey_market_Tv"),
    "tvstand": ("🪞 TV Stand", "@adeymarket_tvstand"),
    "centertable": ("🛋️ የመሀል ጠረቤዛ", "@adeymarket_center_table"),
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
    ("📺 ቲቪ (TV)", "https://t.me/adey_market_Tv"),
    ("🪞 TV Stand", "https://t.me/adeymarket_tvstand"),
    ("🛋️ የመሀል ጠረቤዛ", "https://t.me/adeymarket_center_table"),
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
    
    markup.add(
        InlineKeyboardButton("🔎 ዕቃ ለመፈለግ", callback_data="user_search"),
        InlineKeyboardButton("⭐ አስተያየት ለመስጠት", callback_data="user_review")
    )
    markup.add(
        InlineKeyboardButton("📦 የተሸጡ ዕቃዎች (Archive)", url="https://t.me/adey_market_archive"),
        InlineKeyboardButton("📩 Inbox ለማውራት", url="https://t.me/adeyused")
    )
    return markup

MENU_TEXT = (
    "🟡 **ADEY MARKET** 🏠\n\n"
    "ያገለገሉ የቤት እቃዎችን ከታች ይምረጡ።\n\n"
    "👇 **የሚፈልጉትን ምድብ ይንኩ።**\n\n"
    "📞 **ስልክ:** 0985427286\n"
    "📩 **Telegram Inbox:** @adeyused"
)

user_states = {}

@bot.message_handler(commands=["start", "menu"])
def show_menu(message):
    if str(message.from_user.id) in ADMIN_IDS:
        admin_sessions.pop(message.from_user.id, None)
    user_states.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, MENU_TEXT, reply_markup=make_menu(), parse_mode="Markdown")

admin_sessions = {}
media_group_buffer = {}

def clean_caption_for_sold(old_caption):
    lines = old_caption.split("\n")
    new_lines = []
    for line in lines:
        lower_line = line.lower()
        if "ዋጋ፦" in line or "ዋጋ:" in line or "price" in lower_line:
            new_lines.append("💰 **ዋጋ፦**")
        elif "ቦታ፦" in line or "ቦታ:" in line or "location" in lower_line:
            new_lines.append("📍 **ቦታ፦**")
        else:
            new_lines.append(line)
    
    cleaned_body = "\n".join(new_lines).strip()
    if "🔴 [ተሽጧል]" not in cleaned_body and "🔴 **[ተሽጧል" not in cleaned_body:
        return f"🔴 **[ተሽጧል / SOLD OUT]**\n\n{cleaned_body}"
    return cleaned_body

# User Review & Search Handlers
@bot.callback_query_handler(func=lambda call: call.data in ["user_search", "user_review"] or call.data.startswith("rate_"))
def handle_user_callbacks(call):
    if call.data == "user_search":
        user_states[call.from_user.id] = {"step": "waiting_search_query"}
        bot.send_message(call.message.chat.id, "🔎 **የሚፈልጉትን ዕቃ ስም ይጻፉልኝ፦**\n*(ምሳሌ: ሶፋ፣ ፍሪጅ፣ ቲቪ)*", parse_mode="Markdown")
        bot.answer_callback_query(call.id)
    
    elif call.data == "user_review":
        markup = InlineKeyboardMarkup(row_width=5)
        markup.add(
            InlineKeyboardButton("⭐ 1", callback_data="rate_1"),
            InlineKeyboardButton("⭐ 2", callback_data="rate_2"),
            InlineKeyboardButton("⭐ 3", callback_data="rate_3"),
            InlineKeyboardButton("⭐ 4", callback_data="rate_4"),
            InlineKeyboardButton("⭐ 5", callback_data="rate_5")
        )
        bot.send_message(call.message.chat.id, "🌟 **ለአገልግሎታችን ስንት ኮከብ መስጠት ይፈልጋሉ?**", reply_markup=markup, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        
    elif call.data.startswith("rate_"):
        rating = call.data.split("_")[1]
        user_states[call.from_user.id] = {"step": "waiting_review_text", "rating": rating}
        bot.send_message(call.message.chat.id, f"🙏 **ስለሰጡን {rating} ኮከብ እናመሰግናለን!**\nእባክዎ ተጨማሪ አስተያየት ካልዎት ይጻፉልን፦", parse_mode="Markdown")
        bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: str(m.from_user.id) not in ADMIN_IDS and m.from_user.id in user_states)
def handle_user_inputs(message):
    state = user_states.get(message.from_user.id, {})
    step = state.get("step")

    if step == "waiting_search_query":
        query = message.text.strip().lower()
        found = []
        for key, (name, link) in CATEGORY_CHANNELS.items():
            if query in name.lower() or query in key:
                found.append((name, link))
        
        if found:
            text = f"🔎 **የሚከተሉትን ምድቦች አግኝተናል፦**\n\n"
            markup = InlineKeyboardMarkup()
            for name, link in found:
                markup.add(InlineKeyboardButton(name, url=f"https://t.me/{link.replace('@', '')}"))
            bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")
        else:
            bot.reply_to(
                message, 
                "ℹ️ **ለጥያቄዎ አግባብ ያለው ምድብ አልተገኘም።**\nእባክዎ በዋናው ቻናል ላይ ይመልከቱ፦", 
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("📢 ADEY MARKET ቻናል", url=MAIN_CHANNEL_LINK)),
                parse_mode="Markdown"
            )
        user_states.pop(message.from_user.id, None)

    elif step == "waiting_review_text":
        rating = state.get("rating", "5")
        text = message.text.strip()
        user_name = message.from_user.first_name or "ደንበኛ"
        
        review_msg = (
            "💬 **አዲስ ደንበኛ አስተያየት!**\n\n"
            f"👤 **ስም፦** {user_name}\n"
            f"⭐ **ሬቲንግ፦** {'⭐' * int(rating)}\n"
            f"📝 **አስተያየት፦** {text}"
        )
        try:
            bot.send_message(REVIEW_CHANNEL, review_msg, parse_mode="Markdown")
            bot.reply_to(message, "✅ **አስተያየትዎ በጥሩ ሁኔታ ደርሶናል፣ እጅግ እናመሰግናለን!**")
        except Exception as e:
            bot.reply_to(message, "✅ **አስተያየትዎ ተቀብለናል!**")
        user_states.pop(message.from_user.id, None)

@bot.message_handler(func=lambda m: str(m.from_user.id) in ADMIN_IDS and m.text and "t.me/" in m.text)
def handle_post_link_sold(message):
    try:
        text = message.text.strip()
        parts = text.split("t.me/")[-1].split("/")
        if len(parts) >= 2:
            chan_part = parts[0]
            if not chan_part.startswith("@"):
                target_chan = "@" + chan_part
            else:
                target_chan = chan_part
            msg_id = int(parts[1])

            forwarded = bot.forward_message(message.chat.id, target_chan, msg_id)
            old_caption = forwarded.caption or forwarded.text or ""
            forwarded_id = forwarded.message_id
            bot.delete_message(message.chat.id, forwarded_id)

            if "🔴 [ተሽጧል]" not in old_caption and "🔴 **[ተሽጧል" not in old_caption:
                updated_caption = clean_caption_for_sold(old_caption)
                
                if forwarded.photo:
                    photo_file_id = forwarded.photo[-1].file_id
                    bot.edit_message_media(
                        chat_id=target_chan,
                        message_id=msg_id,
                        media=InputMediaPhoto(photo_file_id, caption=updated_caption, parse_mode="Markdown")
                    )
                else:
                    bot.edit_message_caption(
                        chat_id=target_chan,
                        message_id=msg_id,
                        caption=updated_caption,
                        parse_mode="Markdown"
                    )
                
                try:
                    bot.forward_message(ARCHIVE_CHANNEL, target_chan, msg_id)
                except Exception as ex:
                    print(f"Archive error: {ex}")

                bot.reply_to(message, "✅ እቃው ተሽጧል ተብሎ ተስተካክሏል፣ ወደ Archive ቻናልም ተልኳል!")
            else:
                bot.reply_to(message, "ℹ️ ይህ እቃ ቀደም ብሎ ተሽጧል ተብሎ ተስተካክሏል።")
        else:
            bot.reply_to(message, "⚠️ ትክክለኛ የፖስት ሊንክ ይላኩ (ምሳሌ: https://t.me/adey_market_bed/12)")
    except Exception as e:
        bot.reply_to(message, f"ስህተት ተፈጥሯል: {e}")

@bot.message_handler(content_types=['photo', 'video'], chat_types=['private'])
def handle_admin_upload(message):
    if message.forward_from_chat or message.forward_origin or message.forward_date:
        return

    if str(message.from_user.id) not in ADMIN_IDS:
        return

    admin_id = message.from_user.id
    admin_sessions[admin_id] = {}
    
    if message.media_group_id:
        gid = message.media_group_id
        if gid not in media_group_buffer:
            media_group_buffer[gid] = {
                "messages": [],
                "sent_prompt": False,
                "chat_id": message.chat.id
            }
        media_group_buffer[gid]["messages"].append(message)
        time.sleep(1.0)
        
        if not media_group_buffer[gid]["sent_prompt"]:
            media_group_buffer[gid]["sent_prompt"] = True
            ask_category(message, gid)
    else:
        single_id = f"single_{message.message_id}"
        media_group_buffer[single_id] = {
            "messages": [message],
            "chat_id": message.chat.id
        }
        ask_category(message, single_id)

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
    identifier = "_".join(parts[1:-1])
    cat_key = parts[-1]
    
    admin_sessions[call.from_user.id] = {
        "identifier": identifier,
        "cat_key": cat_key,
        "step": "waiting_condition"
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
        cat_key = admin_sessions[call.from_user.id]["cat_key"]
        
        if cat_key == "tv":
            admin_sessions[call.from_user.id]["step"] = "waiting_tv_details"
            bot.edit_message_text(
                "📺 **የቲቪውን ኢንች (እና ስማርት ከሆነ ስማርት የሚለውን ቃል) ይጻፉልኝ**\n\n"
                "*(ምሳሌ: 40 ወይም 40 smart)*", 
                call.message.chat.id, 
                call.message.message_id, 
                parse_mode="Markdown"
            )
        elif cat_key == "tvstand":
            admin_sessions[call.from_user.id]["step"] = "waiting_tvstand_details"
            bot.edit_message_text(
                "🪞 **የ TV Stand መጠን ወይም ዓይነት ይጻፉልኝ**\n\n"
                "*(ምሳሌ: 1.2 ሜትር ወይም ዘመናዊ TV Stand)*", 
                call.message.chat.id, 
                call.message.message_id, 
                parse_mode="Markdown"
            )
        elif cat_key == "centertable":
            admin_sessions[call.from_user.id]["step"] = "waiting_centertable_details"
            bot.edit_message_text(
                "🛋️ **የመሀል ጠረቤዛውን ዓይነት ወይም መጠን ይጻፉልኝ**\n\n"
                "*(ምሳሌ: ማርብል ጠረቤዛ ወይም የእንጨት)*", 
                call.message.chat.id, 
                call.message.message_id, 
                parse_mode="Markdown"
            )
        elif cat_key == "wardrobe":
            admin_sessions[call.from_user.id]["step"] = "waiting_wardrobe_details"
            bot.edit_message_text(
                "🚪 **የቁምሳጥኑን መጠን ወይም ዓይነት ይጻፉልኝ**\n\n"
                "*(ምሳሌ: 1-20 ወይም 1-50 ወይም 80 cm)*", 
                call.message.chat.id, 
                call.message.message_id, 
                parse_mode="Markdown"
            )
        else:
            admin_sessions[call.from_user.id]["step"] = "waiting_price"
            bot.edit_message_text(
                "📝 **አሁን የእቃውን ዋጋ እና ቦታ (Price & Location) ይጻፉልኝ**\n\n"
                "*(ምሳሌ: 18,000 ብር | ጀሞ)*", 
                call.message.chat.id, 
                call.message.message_id, 
                parse_mode="Markdown"
            )

@bot.message_handler(func=lambda m: m.from_user.id in admin_sessions and admin_sessions[m.from_user.id].get("step") == "waiting_tv_details")
def handle_tv_details(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return

    user_text = message.text.strip().lower()
    is_smart = "smart" in user_text
    import re
    numbers = re.findall(r'\d+', user_text)
    inch_val = numbers[0] if numbers else user_text

    if is_smart:
        tv_formatted = f"{inch_val} inch Smart TV"
    else:
        tv_formatted = f"{inch_val} inch TV"

    admin_sessions[message.from_user.id]["tv_details"] = tv_formatted
    admin_sessions[message.from_user.id]["step"] = "waiting_price"
    
    bot.reply_to(message, "📝 **አሁን የቲቪውን ዋጋ እና ቦታ (Price & Location) ይጻፉልኝ**\n\n*(ምሳሌ: 29,000 ብር | መገናኛ)*", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id in admin_sessions and admin_sessions[m.from_user.id].get("step") == "waiting_tvstand_details")
def handle_tvstand_details(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return

    user_text = message.text.strip()
    if "tv stand" not in user_text.lower():
        tvstand_formatted = f"{user_text} TV Stand"
    else:
        tvstand_formatted = user_text

    admin_sessions[message.from_user.id]["tvstand_details"] = tvstand_formatted
    admin_sessions[message.from_user.id]["step"] = "waiting_price"
    
    bot.reply_to(message, "📝 **አሁን የ TV Stand ዋጋ እና ቦታ (Price & Location) ይጻፉልኝ**\n\n*(ምሳሌ: 8,500 ብር | ቦሌ)*", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id in admin_sessions and admin_sessions[m.from_user.id].get("step") == "waiting_centertable_details")
def handle_centertable_details(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return

    user_text = message.text.strip()
    if "ጠረቤዛ" not in user_text:
        ct_formatted = f"{user_text} የመሀል ጠረቤዛ"
    else:
        ct_formatted = user_text

    admin_sessions[message.from_user.id]["centertable_details"] = ct_formatted
    admin_sessions[message.from_user.id]["step"] = "waiting_price"
    
    bot.reply_to(message, "📝 **አሁን የመሀል ጠረቤዛውን ዋጋ እና ቦታ (Price & Location) ይጻፉልኝ**\n\n*(ምሳሌ: 6,000 ብር | ፒያሳ)*", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id in admin_sessions and admin_sessions[m.from_user.id].get("step") == "waiting_wardrobe_details")
def handle_wardrobe_details(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return

    user_text = message.text.strip()
    if "ቁምሳጥን" not in user_text:
        wardrobe_formatted = f"{user_text} ቁምሳጥን"
    else:
        wardrobe_formatted = user_text

    admin_sessions[message.from_user.id]["wardrobe_details"] = wardrobe_formatted
    admin_sessions[message.from_user.id]["step"] = "waiting_price"
    
    bot.reply_to(message, "📝 **አሁን የቁምሳጥኑን ዋጋ እና ቦታ (Price & Location) ይጻፉልኝ**\n\n*(ምሳሌ: 17,500 ብር | Mexico)*", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id in admin_sessions and admin_sessions[m.from_user.id].get("step") == "waiting_price")
def handle_price_location(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        return

    session = admin_sessions.pop(message.from_user.id, None)
    if not session:
        return

    user_text = message.text.strip()
    
    if "|" in user_text:
        parts = user_text.split("|")
        price = parts[0].strip()
        location = parts[1].strip()
    else:
        parts = user_text.split(maxsplit=1)
        price = parts[0].strip() if len(parts) > 0 else user_text
        location = parts[1].strip() if len(parts) > 1 else "አዲስ አበባ"

    cat_key = session["cat_key"]
    identifier = session["identifier"]
    condition = session["condition"]
    tv_details = session.get("tv_details", "")
    tvstand_details = session.get("tvstand_details", "")
    centertable_details = session.get("centertable_details", "")
    wardrobe_details = session.get("wardrobe_details", "")
    
    cat_name, target_channel = CATEGORY_CHANNELS.get(cat_key, ("✨ ተጨማሪ", "@adey_market_other"))

    if cat_key == "tv" and tv_details:
        item_type_line = f"📦 **የእቃው አይነት፦** {tv_details}\n"
    elif cat_key == "tvstand" and tvstand_details:
        item_type_line = f"📦 **የእቃው አይነት፦** {tvstand_details}\n"
    elif cat_key == "centertable" and centertable_details:
        item_type_line = f"📦 **የእቃው አይነት፦** {centertable_details}\n"
    elif cat_key == "wardrobe" and wardrobe_details:
        item_type_line = f"📦 **የእቃው አይነት፦** {wardrobe_details}\n"
    else:
        item_type_line = f"📦 **የእቃው አይነት፦** {cat_name}\n"

    caption_text = (
        "🟡 **ADEY MARKET** 🏠\n\n"
        f"{item_type_line}"
        f"💰 **ዋጋ፦** {price}\n"
        f"📍 **ቦታ፦** {location}\n"
        f"☑ **ሁኔታ፦** {condition}\n"
        "📞 **ለመሸጥ፦** 0985427286\n"
        "📩 **ለInbox፦** @adeyused\n\n"
        "👇 **JOIN ያድርጉ፣ አዳዲስ እቃዎችን ያግኙ!**\n"
        f"📢 **Telegram Channel:-** {MAIN_CHANNEL_LINK}\n\n\n"
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
                sent_target = bot.send_media_group(target_channel, media_list)
                target_msg_id = sent_target[0].message_id if sent_target else None

                main_msg_id = None
                if target_channel != MAIN_CHANNEL:
                    sent_main = bot.send_media_group(MAIN_CHANNEL, media_list)
                    main_msg_id = sent_main[0].message_id if sent_main else None
                
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("🔴 ተሽጧል (Sold Out)", callback_data=f"sold_{target_channel}_{target_msg_id}_{main_msg_id}"))

                bot.reply_to(message, "✅ እቃው በትክክል ወደ ቻናሎቹ ተልኳል!\n\nይህ እቃ ሲሸጥ ከታች ያለውን ቁልፍ ይንኩ:", parse_mode="Markdown", reply_markup=markup)
        except Exception as e:
            bot.reply_to(message, f"ስህተት ተፈጥሯል: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("sold_"))
def callback_mark_sold_from_bot(call):
    if str(call.from_user.id) not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "ይህንን ለማድረግ ፈቃድ የለዎትም!", show_alert=True)
        return

    parts = call.data.split("_")
    main_msg_id = parts[-1]
    target_msg_id = parts[-2]
    target_channel = "_".join(parts[1:-2])

    success = False

    try:
        try:
            forwarded = bot.forward_message(call.message.chat.id, target_channel, int(target_msg_id))
            old_caption = forwarded.caption or forwarded.text or ""
            forwarded_id = forwarded.message_id
            bot.delete_message(call.message.chat.id, forwarded_id)

            if "🔴 [ተሽጧል]" not in old_caption and "🔴 **[ተሽጧል" not in old_caption:
                updated_caption = clean_caption_for_sold(old_caption)
                
                if forwarded.photo:
                    photo_file_id = forwarded.photo[-1].file_id
                    bot.edit_message_media(
                        chat_id=target_channel,
                        message_id=int(target_msg_id),
                        media=InputMediaPhoto(photo_file_id, caption=updated_caption, parse_mode="Markdown")
                    )
                    success = True
                else:
                    bot.edit_message_caption(
                        chat_id=target_channel,
                        message_id=int(target_msg_id),
                        caption=updated_caption,
                        parse_mode="Markdown"
                    )
                    success = True
                
                try:
                    bot.forward_message(ARCHIVE_CHANNEL, target_channel, int(target_msg_id))
                except Exception as ex:
                    print(f"Archive forward error: {ex}")

        except Exception as ex:
            print(f"Target channel update error: {ex}")

        if main_msg_id != "None" and target_channel != MAIN_CHANNEL:
            try:
                forwarded_main = bot.forward_message(call.message.chat.id, MAIN_CHANNEL, int(main_msg_id))
                old_caption_main = forwarded_main.caption or forwarded_main.text or ""
                forwarded_main_id = forwarded_main.message_id
                bot.delete_message(call.message.chat.id, forwarded_main_id)

                if "🔴 [ተሽጧል]" not in old_caption_main and "🔴 **[ተሽጧል" not in old_caption_main:
                    updated_caption_main = clean_caption_for_sold(old_caption_main)
                    
                    if forwarded_main.photo:
                        photo_file_id_main = forwarded_main.photo[-1].file_id
                        bot.edit_message_media(
                            chat_id=MAIN_CHANNEL,
                            message_id=int(main_msg_id),
                            media=InputMediaPhoto(photo_file_id_main, caption=updated_caption_main, parse_mode="Markdown")
                        )
            except Exception as ex:
                print(f"Main channel update error: {ex}")

        if success:
            bot.edit_message_text(
                "🔴 **[እቃው ተሽጧል / SOLD OUT ተብሎ ተስተካክሏል፣ ወደ Archive ቻናልም ተልኳል!]**",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=None
            )
            bot.answer_callback_query(call.id, "እቃው ተሽጧል ተብሎ ተስተካክሏል!")
        else:
            bot.answer_callback_query(call.id, "ተስተካክሏል ወይም የተፈጠረ ስህተት አለ።", show_alert=True)
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
