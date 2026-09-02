import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TOKEN = "8780198432:AAFr_2jfhXd-2jUzz_okokphj8_vSCVl-Y8"
bot = telebot.TeleBot(TOKEN)

ADMIN_CHAT_ID = "8703011579"
CHANNEL_USERNAME = "@adeymarket3"

BOT_LINK = "https://t.me/Adey_used_bot" 
ADMIN_USERNAME = "https://t.me/adeyused"
ADMIN_PHONE_LINK = "https://t.me/adeyused"

user_albums = {}
admin_editing = {}

def get_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton("🛒 እቃ ለመግዛት"), KeyboardButton("📦 እቃ ለመሸጥ"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🇪🇹 **እንኳን ወደ አደይ ማርኬት (Adey Market) በደህና መጡ!** 🙏\n\n"
        "ይህ ቦት ያገለገሉ ወይም አዲስ እቃዎችን በአስተማማኝ ሁኔታ ለመግዛት እና ለመሸጥ የሚያስችልዎ መድረክ ነው።\n\n"
        "📌 ፎቶዎችን እና መረጃውን በቀጥታ ልኩልኝ!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.message_handler(content_types=['text', 'photo'])
def handle_message(message):
    chat_id = message.chat.id
    
    # 1. አድሚኑ ኤዲት እያደረገ ከሆነ የሚሰራው
    if str(chat_id) == str(ADMIN_CHAT_ID) and chat_id in admin_editing:
        edit_info = admin_editing[chat_id]
        new_caption = message.caption if message.content_type == 'photo' else message.text
        if not new_caption:
            new_caption = message.text
            
        user_id = edit_info['user_id']
        is_album = edit_info['is_album']
        group_id = edit_info['group_id']
        
        # እዚህ ጋር የእርስዎ የቀድሞ የአድሚን ኮድ ይቀጥላል (ማለትም ማስተካከያ የሚሰራበት ክፍል)
        # (ያለዎትን የመጀመሪያ ኮድ እዚህ ላይ እንዳለ ይተዉት)
        
    # 2. ተራ ተጠቃሚዎች ስልክ ቁጥር ወይም ጽሁፍ ሲልኩ እዚህ ይገባል
    else:
        if message.text and message.text.startswith('/'):
            return
            
        text = message.text
        if text:
            # ስልክ ቁጥሩን/መረጃውን ወደ አድሚን ይልካል
            bot.send_message(
                ADMIN_CHAT_ID, 
                f"📞 ከ ተጠቃሚ (ID: {chat_id}) የደረሰ ስልክ ቁጥር/መረጃ:\n\n{text}"
            )
            # ለተጠቃሚው ማረጋገጫ ይሰጣል
            bot.send_message(
                chat_id, 
                "✅ ስልክ ቁጥርዎ/መረጃዎ በአስተዳዳሪው ዘንድ ደርሷል!"
            )
# 1. አድሚኑ ኤዲት እያደረገ ከሆነ የሚሰራው
    if str(chat_id) == str(ADMIN_CHAT_ID) and chat_id in admin_editing:
        edit_info = admin_editing[chat_id]
        new_caption = message.caption if message.content_type == 'photo' else message.text
        if not new_caption:
            new_caption = message.text
            
        user_id = edit_info['user_id']
        is_album = edit_info['is_album']
        group_id = edit_info['group_id']
        
        channel_markup = InlineKeyboardMarkup()
        btn_buy = InlineKeyboardButton("🛒 እቃ ለመግዛት", url=ADMIN_USERNAME)
        btn_sell = InlineKeyboardButton("💸 እቃ ለመሸጥ", url=BOT_LINK)
        btn_phone = InlineKeyboardButton("📞 ስልክ 0985427286", url=ADMIN_PHONE_LINK)
        channel_markup.add(btn_buy, btn_sell)
        channel_markup.add(btn_phone)
        
        try:
            if is_album and group_id in user_albums:
                media_group = []
                for idx, m in enumerate(user_albums[group_id]):
                    if idx == 0:
                        media_group.append(InputMediaPhoto(m.photo[-1].file_id, caption=new_caption))
                    else:
                        media_group.append(InputMediaPhoto(m.photo[-1].file_id))
                
                bot.send_media_group(CHANNEL_USERNAME, media_group)
                bot.send_message(CHANNEL_USERNAME, "👇 ለግዢ እና ሽያጭ ከታች ያሉትን ሊንኮች ይጠቀሙ:", reply_markup=channel_markup)
                del user_albums[group_id]
            else:
                if message.content_type == 'photo':
                    bot.send_photo(CHANNEL_USERNAME, message.photo[-1].file_id, caption=new_caption, reply_markup=channel_markup)
                else:
                    bot.send_message(CHANNEL_USERNAME, new_caption, reply_markup=channel_markup)
                    
            bot.send_message(chat_id, "✅ ማስታወቂያው ወደ ឆናሉ ተልኳል!")
            del admin_editing[chat_id]
        except Exception as e:
            bot.send_message(chat_id, f"❌ ስህተት ተፈጥሯል: {e}")

    # 2. ተራ ተጠቃሚዎች ስልክ ቁጥር ወይም ጽሁፍ ሲልኩ እዚህ ይገባል
    else:
        if message.text and message.text.startswith('/'):
            return
            
        text = message.text
        if text:
            bot.send_message(
                ADMIN_CHAT_ID, 
                f"📞 ከ ተጠቃሚ (ID: {chat_id}) የደረሰ ስልክ ቁጥር/መረጃ:\n\n{text}"
            )
            bot.send_message(
                chat_id, 
                "✅ ስልክ ቁጥርዎ/መረጃዎ በአስተዳዳሪው ዘንድ ደርሷል!"
            )
        try:
            if is_album and group_id in user_albums:
                media_group = []
                for idx, msg in enumerate(user_albums[group_id]['messages']):
                    if idx == 0:
                        media_group.append(InputMediaPhoto(msg.photo[-1].file_id, caption=new_caption))
                    else:
                        media_group.append(InputMediaPhoto(msg.photo[-1].file_id))
                
                bot.send_media_group(CHANNEL_USERNAME, media_group)
                
                user_albums.pop(group_id, None)
            else:
                msg_id = edit_info['msg_id']
                forwarded_msg = bot.forward_message(ADMIN_CHAT_ID, user_id, msg_id)
                photo_file_id = forwarded_msg.photo[-1].file_id
                bot.delete_message(ADMIN_CHAT_ID, forwarded_msg.message_id)
                
                bot.send_photo(CHANNEL_USERNAME, photo_file_id, caption=new_caption, reply_markup=channel_markup)
            
            bot.send_message(chat_id, "እቃው በአዲሱ መረጃ ተለጥፏል! ✅", reply_markup=get_main_keyboard())
        except Exception as e:
            bot.send_message(chat_id, f"ስህተት ተፈጥሯል: {e}", reply_markup=get_main_keyboard())
            
        admin_editing.pop(chat_id, None)
        return

    if message.text == "🛒 እቃ ለመግዛት":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 ቻናላችንን ጎብኝ", url="https://t.me/adeymarket3"))
        bot.send_message(chat_id, "🛒 እቃ ለመግዛት ቻናላችንን ይጎብኙ:", reply_markup=markup)
        return

    if message.text == "📦 እቃ ለመሸጥ":
        sell_prompt = (
            "📦 **እቃ ለመሸጥ የሚከተሉትን መረጃዎች አብረው ይላኩልን፦**\n\n"
            "📸 የእቃውን ፎቶ (ወይም ፎቶዎች)\n"
            "🏷 የእቃው ስም እና መግለጫ\n"
            "💰 ዋጋ\n"
            "📞 ስልክ ቁጥር\n"
            "📍 የሚገኙበት አድራሻ (ቦታ)\n\n"
            "እነዚህን ሙሉ መረጃዎች ፎቶው ጋር አያይዘው (Caption ላይ ጽፈው) ይላኩልን! 🙏"
        )
        bot.send_message(chat_id, sell_prompt, reply_markup=get_main_keyboard(), parse_mode="Markdown")
        return

    if message.content_type == 'photo':
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
                bot.send_message(chat_id, "ፎቶዎችዎ ተቀብለናል! ✅ አስተዳዳሪዎች አረጋግጠው በቅርቡ ይለጥፉታል።", reply_markup=get_main_keyboard())
                
                admin_markup = InlineKeyboardMarkup()
                post_btn = InlineKeyboardButton("✅ በነበረው ለጥፍ", callback_data=f"postalbum_{message.media_group_id}_{chat_id}")
                edit_btn = InlineKeyboardButton("✏️ አስተካክለህ ለጥፍ", callback_data=f"editalbum_{message.media_group_id}_{chat_id}")
                cancel_btn = InlineKeyboardButton("❌ ተው", callback_data=f"cancel_album_{message.media_group_id}")
                admin_markup.add(post_btn, edit_btn)
                admin_markup.add(cancel_btn)
                
                bot.forward_message(ADMIN_CHAT_ID, chat_id, message.id)
                bot.send_message(ADMIN_CHAT_ID, "🔔 አዲስ ባለብዙ ፎቶ (Album) ጥያቄ መጥቷል:", reply_markup=admin_markup)
        else:
            bot.send_message(chat_id, "ፎቶዎ ተቀብሏል! ✅ አስተዳዳሪዎች አረጋግጠው በቅርቡ ይለጥፉታል።", reply_markup=get_main_keyboard())
            admin_markup = InlineKeyboardMarkup()
            post_btn = InlineKeyboardButton("✅ በነበረው ለጥፍ", callback_data=f"postsingle_{message.id}_{chat_id}")
            edit_btn = InlineKeyboardButton("✏️ አስተካክለህ ለጥፍ", callback_data=f"editsingle_{message.id}_{chat_id}")
            cancel_btn = InlineKeyboardButton("❌ ተው", callback_data=f"cancel_single_{message.id}")
            admin_markup.add(post_btn, edit_btn)
            admin_markup.add(cancel_btn)
            
            bot.forward_message(ADMIN_CHAT_ID, chat_id, message.id)
            bot.send_message(ADMIN_CHAT_ID, "🔔 አዲስ ፎቶ ጥያቄ መጥቷል:", reply_markup=admin_markup)

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
            bot.send_message(call.from_user.id, "✏️ እባክዎ ለዚህ እቃ ማስተካከል የሚፈልጉትን አዲሱን መረጃ (Caption) አሁን ይጻፉልኝ:")
            bot.answer_callback_query(call.id)
            
        elif data.startswith("postsingle_"):
            parts = data.split("_")
            msg_id = int(parts[1])
            user_id = int(parts[2])
            
            channel_markup = InlineKeyboardMarkup()
            btn_buy = InlineKeyboardButton("🛒 እቃ ለመግዛት", url=ADMIN_USERNAME)
            btn_sell = InlineKeyboardButton("📦 እቃ ለመሸጥ", url=BOT_LINK)
            btn_phone = InlineKeyboardButton("📞 ስልክ 0985427286", url=ADMIN_PHONE_LINK)
            channel_markup.add(btn_buy, btn_sell)
            channel_markup.add(btn_phone)
            
            try:
                forwarded = bot.forward_message(ADMIN_CHAT_ID, user_id, msg_id)
                photo_file_id = forwarded.photo[-1].file_id
                caption = forwarded.caption
                bot.delete_message(ADMIN_CHAT_ID, forwarded.message_id)
                
                bot.send_photo(CHANNEL_USERNAME, photo_file_id, caption=caption, reply_markup=channel_markup)
                bot.answer_callback_query(call.id, "ተለጥፏል! ✅")
                bot.edit_message_text("✅ ተለጥፏል", call.message.chat.id, call.message.id)
            except Exception as e:
                bot.answer_callback_query(call.id, f"ስህተት: {e}", show_alert=True)
                
        elif data.startswith("postalbum_"):
            parts = data.split("_")
            group_id = parts[1]
            try:
                if group_id in user_albums:
                    media_group = []
                    for idx, msg in enumerate(user_albums[group_id]['messages']):
                        if idx == 0:
                            media_group.append(InputMediaPhoto(msg.photo[-1].file_id, caption=msg.caption))
                        else:
                            media_group.append(InputMediaPhoto(msg.photo[-1].file_id))
                    
                    bot.send_media_group(CHANNEL_USERNAME, media_group)
                    
                    channel_markup = InlineKeyboardMarkup()
                    btn_buy = InlineKeyboardButton("🛒 እቃ ለመግዛት", url=ADMIN_USERNAME)
                    btn_sell = InlineKeyboardButton("📦 እቃ ለመሸጥ", url=BOT_LINK)
                    btn_phone = InlineKeyboardButton("📞 ስልክ 0985427286", url=ADMIN_PHONE_LINK)
                    channel_markup.add(btn_buy, btn_sell)
                    channel_markup.add(btn_phone)
                    
                    bot.send_message(CHANNEL_USERNAME, ".", reply_markup=channel_markup)
                    
                    user_albums.pop(group_id, None)
                bot.answer_callback_query(call.id, "አልበሙ ተለጥፏል! ✅")
                bot.edit_message_text("✅ ተለጥፏል", call.message.chat.id, call.message.id)
            except Exception as e:
                bot.answer_callback_query(call.id, f"ስህተት: {e}", show_alert=True)
                
        elif data.startswith("cancel_"):
            bot.answer_callback_query(call.id, "ተሰርዟል ❌")
            bot.edit_message_text("❌ ውድቅ ተደርጓል", call.message.chat.id, call.message.id)

print("ቦቱ በአግባቡ እየሰራ ነው...", flush=True)
@bot.message_handler(content_types=['text'])
def handle_user_text(message):
    if message.text and message.text.startswith('/'):
        return
    
    chat_id = message.chat.id
    text = message.text
    
    # ስልክ ቁጥሩን ወይም ጽሁፉን ወደ አድሚን ይልካል
    bot.send_message(
        ADMIN_CHAT_ID, 
        f"📞 ከ ተጠቃሚ (ID: {chat_id}) የደረሰ ስልክ ቁጥር/መረጃ:\n\n{text}"
    )
    # ለተጠቃሚው ማረጋገጫ ይሰጣል
    bot.send_message(
        chat_id, 
        "✅ ስልክ ቁጥርዎ/መረጃዎ በአስተዳዳሪው ዘንድ ደርሷል!"
    )
