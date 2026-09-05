import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# --- 1. የድር ሰርቨር (Render ፖርት እንዲያገኝ እና ቦቱ እንዳይተኛ የሚያደርግ) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ሰርቨሩን በጀርባ ማስጀመር
server_thread = threading.Thread(target=run_web_server)
server_thread.daemon = True
server_thread.start()
# -------------------------------------------------------------------

TOKEN = "8780198432:AAFcQyfiyo8q1AtXbNS_XYt8ufHwXIFjyyA"
bot = telebot.TeleBot(TOKEN)

ADMIN_CHAT_ID = "8703011579"
CHANNEL_USERNAME = "@adeymarket3"

BOT_LINK = "https://t.me/Adey_used_bot"
ADMIN_USERNAME = "https://t.me/adeyused"
ADMIN_PHONE_LINK = "https://t.me/adeyused"
SELL_ACCOUNT_LINK = "https://t.me/usedmarket19"

user_albums = {}
admin_editing = {}

def get_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton("🛒 እቃ ለመግዛት"), KeyboardButton("📞 እቃ ለመሸጥ"))
    return markup

# 2. የ /start ትዕዛዝ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🇪🇹 **እንኳን ወደ አደይ ማርኬት (Adey Market) በደህና መጡ!** 🛒\n\n"
        "• እዚህ መድረክ ላይ አዲስ እና ጥራት ያላቸው እቃዎችን 🛒 በቀላሉ መግዛት ወይም 📞 መሸጥ ይችላሉ!\n"
        "• ጥራት ያላቸው እቃዎችና ምርቶች በታማኝነት ይገኙበታል ✨\n\n"
        "👇 እባክዎ ከታች ካሉት አማራጮች አንዱን ይምረጡ፡"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# 3. የጽሁፍ መልዕክቶች ማስተናገጃ
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    
    if str(chat_id) == str(ADMIN_CHAT_ID) and chat_id in admin_editing:
        edit_info = admin_editing[chat_id]
        new_caption = message.text
        
        user_id = edit_info['user_id']
        is_album = edit_info['is_album']
        group_id = edit_info['group_id']
        
        channel_markup = InlineKeyboardMarkup()
        btn_buy = InlineKeyboardButton("🛒 እቃ ለመግዛት", url=ADMIN_USERNAME)
        btn_sell = InlineKeyboardButton("💸 እቃ ለመሸጥ", url=SELL_ACCOUNT_LINK)
        btn_phone = InlineKeyboardButton("📞 ስልክ 0985427286", url=ADMIN_PHONE_LINK)
        channel_markup.add(btn_buy, btn_sell)
        channel_markup.add(btn_phone)
        
        try:
            if is_album and group_id in user_albums:
                media_group = []
                for idx, msg in enumerate(user_albums[group_id]['messages']):
                    if idx == 0:
                        media_group.append(InputMediaPhoto(msg.photo[-1].file_id, caption=new_caption))
                    else:
                        media_group.append(InputMediaPhoto(msg.photo[-1].file_id))
                
                bot.send_media_group(CHANNEL_USERNAME, media_group)
                bot.send_message(CHANNEL_USERNAME reply_markup=channel_markup)
                user_albums.pop(group_id, None)
            
            bot.send_message(chat_id, "✅ ማስታወቂያው ወደ ቻናል ተልኳል!", reply_markup=get_main_keyboard())
        except Exception as e:
            bot.send_message(chat_id, f"❌ ስህተት ተፈጥሯል: {e}", reply_markup=get_main_keyboard())
            
        admin_editing.pop(chat_id, None)
        return

    if message.text == "🛒 እቃ ለመግዛት":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🛒 ከናንተ ለመግዛት", url=ADMIN_USERNAME))
        bot.send_message(chat_id, "🛒 እቃ ለመግዛት የሚከተለውን ሊንክ ይጠቀሙ:", reply_markup=markup)
        return
    elif message.text == "📞 እቃ ለመሸጥ":
        sell_markup = InlineKeyboardMarkup()
        sell_markup.add(InlineKeyboardButton("📞 እቃ ለመሸጥ (ሊንኩን ይጫኑ)", url=SELL_ACCOUNT_LINK))
        
        sell_prompt = (
            "📞 **እቃ ለመሸጥ ከታች ያለውን ቁልፍ በመጫን በቀጥታ ያነጋገሩን!**\n\n"
            "👉 *ሊንኩን በመጫን ወደ ራሳችን የቴሌግራም አካውንት ይወሰዳሉ።*"
        )
        bot.send_message(chat_id, sell_prompt, reply_markup=sell_markup, parse_mode="Markdown")
        return
    else:
        if str(chat_id) != str(ADMIN_CHAT_ID):
            bot.forward_message(ADMIN_CHAT_ID, chat_id, message.id)
            bot.send_message(chat_id, "✅ መረጃዎ/ስልክ ቁጥርዎ ወደ አድሚን ተላልፏል! እናመሰግናለን።", reply_markup=get_main_keyboard())

# 4. የፎቶ መልዕክቶች ማስተናገጃ
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    
    if str(chat_id) == str(ADMIN_CHAT_ID) and chat_id in admin_editing:
        edit_info = admin_editing[chat_id]
        new_caption = message.caption if message.caption else ""
        user_id = edit_info['user_id']
        is_album = edit_info['is_album']
        group_id = edit_info['group_id']
        
        channel_markup = InlineKeyboardMarkup()
        btn_buy = InlineKeyboardButton("🛒 እቃ ለመግዛት", url=ADMIN_USERNAME)
        btn_sell = InlineKeyboardButton("💸 እቃ ለመሸጥ", url=SELL_ACCOUNT_LINK)
        btn_phone = InlineKeyboardButton("📞 ስልክ 0985427286", url=ADMIN_PHONE_LINK)
        channel_markup.add(btn_buy, btn_sell)
        channel_markup.add(btn_phone)
        
        try:
            msg_id = edit_info['msg_id']
            forwarded = bot.forward_message(ADMIN_CHAT_ID, user_id, msg_id)
            photo_file_id = forwarded.photo[-1].file_id
            bot.delete_message(ADMIN_CHAT_ID, forwarded.message_id)
            
            bot.send_photo(CHANNEL_USERNAME, photo_file_id, caption=new_caption, reply_markup=channel_markup)
            bot.send_message(chat_id, "✅ ፖስቱ በተሳካ ሁኔታ ተለጥፏል!", reply_markup=get_main_keyboard())
        except Exception as e:
            bot.send_message(chat_id, f"❌ ስህተት ተፈጥሯል: {e}", reply_markup=get_main_keyboard())
            
        admin_editing.pop(chat_id, None)
        return

    if message.media_group_id:
        if message.media_group_id not in user_albums:
            user_albums[message.media_group_id] = {
                'messages': [],
                'sent_admin': False,
                'user_id': chat_id
            }
        user_albums[message.media_group_id]['messages'].append(message)
        
        if not user_albums[message.media_group_id]['sent_admin']:
            user_albums[message.media_group_id]['sent_admin'] = True
            bot.send_message(chat_id, "✅ ፎቶዎችዎ ተቀብለዋል! አድሚኖች አሁንም በፍጥነት ይከታተላሉ።", reply_markup=get_main_keyboard())
            
            admin_markup = InlineKeyboardMarkup()
            post_btn = InlineKeyboardButton("📢 ፖስት አድርግ", callback_data=f"postalbum_{message.media_group_id}_{chat_id}")
            edit_btn = InlineKeyboardButton("✏️ አስተካክልና ፖስት", callback_data=f"editalbum_{message.media_group_id}_{chat_id}")
            cancel_btn = InlineKeyboardButton("❌ ተወው", callback_data=f"cancel_album_{message.media_group_id}")
            admin_markup.add(post_btn, edit_btn)
            admin_markup.add(cancel_btn)
            
            bot.forward_message(ADMIN_CHAT_ID, chat_id, message.id)
            bot.send_message(ADMIN_CHAT_ID, "📸 አዲስ አልበም (Album) የያዘ መልዕክት:", reply_markup=admin_markup)
    else:
        forwarded = bot.forward_message(ADMIN_CHAT_ID, chat_id, message.id)
        admin_markup = InlineKeyboardMarkup()
        post_btn = InlineKeyboardButton("📢 ፖስት አድርግ", callback_data=f"postsingle_{message.id}_{chat_id}")
        edit_btn = InlineKeyboardButton("✏️ አስተካክልና ፖስት", callback_data=f"editsingle_{message.id}_{chat_id}")
        cancel_btn = InlineKeyboardButton("❌ ተወው", callback_data=f"cancel_{message.id}")
        admin_markup.add(post_btn, edit_btn)
        admin_markup.add(cancel_btn)
        
        bot.send_message(ADMIN_CHAT_ID, "📸 አዲስ የተላከ ፎቶ (Single) ከምስል ጋር:", reply_markup=admin_markup)

# 5. የአድሚን ቁልፍ መቆጣጠሪያ
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.message:
        data = call.data
        if data.startswith("editsingle_") or data.startswith("editalbum_"):
            parts = data.split("_")
            group_or_id = parts[1]
            user_id = int(parts[2])
            is_album = data.startswith("editalbum_")
            
            msg_id = None
            if not is_album:
                msg_id = int(group_or_id)
                
            admin_editing[call.from_user.id] = {
                'user_id': user_id,
                'msg_id': msg_id,
                'is_album': is_album,
                'group_id': group_or_id if is_album else None
            }
            bot.answer_callback_query(call.from_user.id, "✍️ አሁን አዲስ ማስተካከያ የሚደረግበትን ጽሁፍ ይላኩኝ።")
            
        elif data.startswith("postsingle_"):
            parts = data.split("_")
            msg_id = int(parts[1])
            user_id = int(parts[2])
            
            channel_markup = InlineKeyboardMarkup()
            channel_markup.add(InlineKeyboardButton("🛒 እቃ ለመግዛት", url=ADMIN_USERNAME), InlineKeyboardButton("💸 እቃ ለመሸጥ", url=SELL_ACCOUNT_LINK))
            channel_markup.add(InlineKeyboardButton("📞 ስልክ 0985427286", url=ADMIN_PHONE_LINK))
            
            try:
                forwarded = bot.forward_message(ADMIN_CHAT_ID, user_id, msg_id)
                photo_file_id = forwarded.photo[-1].file_id
                caption = forwarded.caption if forwarded.caption else ""
                bot.delete_message(ADMIN_CHAT_ID, forwarded.message_id)
                
                bot.send_photo(CHANNEL_USERNAME, photo_file_id, caption=caption, reply_markup=channel_markup)
                bot.answer_callback_query(call.id, "✅ ፖስት ተደርጓል!")
                bot.edit_message_text("✅ ፖስቱ በተሳካ ሁኔታ ወደ ቻናል ተልኳል!", call.message.chat.id, call.message.message_id)
            except Exception as e:
                bot.answer_callback_query(call.id, f"❌ ስህተት: {e}", show_alert=True)
                
        elif data.startswith("postalbum_"):
            parts = data.split("_")
            group_id = parts[1]
            try:
                if group_id in user_albums:
                    media_group = []
                    for idx, msg in enumerate(user_albums[group_id]['messages']):
                        if idx == 0:
                            media_group.append(InputMediaPhoto(msg.photo[-1].file_id, caption=msg.caption if msg.caption else ""))
                        else:
                            media_group.append(InputMediaPhoto(msg.photo[-1].file_id))
                    
                    channel_markup = InlineKeyboardMarkup()
                    channel_markup.add(InlineKeyboardButton("🛒 እቃ ለመግዛት", url=ADMIN_USERNAME), InlineKeyboardButton("💸 እቃ ለመሸጥ", url=SELL_ACCOUNT_LINK))
                    channel_markup.add(InlineKeyboardButton("📞 ስልክ 0985427286", url=ADMIN_PHONE_LINK))
                    
                    bot.send_media_group(CHANNEL_USERNAME, media_group)
                    bot.send_message(CHANNEL_USERNAME, "👇 ለግዢ እና ሽያጭ ከታች ያሉትን ሊንኮች ይጠቀሙ:", reply_markup=channel_markup)
                    user_albums.pop(group_id, None)
                    
                bot.answer_callback_query(call.id, "✅ አልበሙ ተለጥፏል!")
                bot.edit_message_text("✅ አልበሙ በተሳካ ሁኔታ ወደ ቻናል ተልኳል!", call.message.chat.id, call.message.message_id)
            except Exception as e:
                bot.answer_callback_query(call.id, f"❌ ስህተት: {e}", show_alert=True)
                
        elif data.startswith("cancel_") or data.startswith("cancel_album_"):
            bot.answer_callback_query(call.id, "❌ ተሰርዟል")
            bot.edit_message_text("❌ ይህ ልዕክ ተሰርዟልና ጠፍቷል።", call.message.chat.id, call.message.message_id)

# Bot polling runner
print("ቦቱ በሂደት ላይ ነው...", flush=True)
bot.infinity_polling(none_stop=True)
