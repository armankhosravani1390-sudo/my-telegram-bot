import telebot
import time
import threading
from flask import Flask
import json
import os
from datetime import datetime

TOKEN = "8299446091:AAG3rkzDotNZ4KLObMy_BJ4Lm_sCBs-DHKE"
OWNER_ID = 6703121829

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
waiting_for_message = {}
tickets = {}
ticket_counter = 0
chat_sessions = {}
user_ticket_status = {}
admins = {}
admin_chat_mode = {}
admin_numbers = {}
amin_list = {}
professor_list = {}
banned_users = {}

# ========== دیتاهای جدید ==========
news_data = {}  # {'1': 'text'}
ad_data = {}    # {'1': 'text'}
donate_data = []  # [{'name': 'Ali', 'amount': 1500000, 'rank': 1}]
news_counter = 0
ad_counter = 0
news_mode = {}  # {'user_id': True/False}
ad_mode = {}    # {'user_id': True/False}
# ===================================

DATA_FILE = 'data.json'
ADMINS_FILE = 'admins.json'
ADMIN_NUMBERS_FILE = 'admin_numbers.json'
AMIN_FILE = 'amin.json'
PROFESSOR_FILE = 'professor.json'
BANNED_FILE = 'banned.json'
NEWS_FILE = 'news.json'
AD_FILE = 'ad.json'
DONATE_FILE = 'donate.json'

# ========== آماده‌سازی ==========
def init_roles():
    global admins, admin_numbers, amin_list, professor_list
    if not os.path.exists(ADMINS_FILE):
        admins = {"7307951847": "admin", "6328427378": "admin"}
        save_admins()
    else:
        load_admins()
        if "7307951847" not in admins:
            admins["7307951847"] = "admin"
        if "6328427378" not in admins:
            admins["6328427378"] = "admin"
        save_admins()
    
    if not os.path.exists(ADMIN_NUMBERS_FILE):
        admin_numbers = {"7307951847": "AmiN", "6328427378": "Professor"}
        save_admin_numbers()
    else:
        load_admin_numbers()
        if "7307951847" not in admin_numbers:
            admin_numbers["7307951847"] = "AmiN"
        if "6328427378" not in admin_numbers:
            admin_numbers["6328427378"] = "Professor"
        save_admin_numbers()
    
    if not os.path.exists(AMIN_FILE):
        amin_list = {"7307951847": "AmiN"}
        save_amin()
    else:
        load_amin()
        if "7307951847" not in amin_list:
            amin_list["7307951847"] = "AmiN"
            save_amin()
    
    if not os.path.exists(PROFESSOR_FILE):
        professor_list = {"6328427378": "Professor"}
        save_professor()
    else:
        load_professor()
        if "6328427378" not in professor_list:
            professor_list["6328427378"] = "Professor"
            save_professor()
# ===========================================

def load_data():
    global ticket_counter, tickets
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            ticket_counter = data.get('counter', 0)
            tickets = data.get('tickets', {})
    else:
        ticket_counter = 0
        tickets = {}

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump({'counter': ticket_counter, 'tickets': tickets}, f)

def load_admins():
    global admins
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'r') as f:
            admins = json.load(f)
    else:
        admins = {}

def save_admins():
    with open(ADMINS_FILE, 'w') as f:
        json.dump(admins, f)

def load_admin_numbers():
    global admin_numbers
    if os.path.exists(ADMIN_NUMBERS_FILE):
        with open(ADMIN_NUMBERS_FILE, 'r') as f:
            admin_numbers = json.load(f)
    else:
        admin_numbers = {}

def save_admin_numbers():
    with open(ADMIN_NUMBERS_FILE, 'w') as f:
        json.dump(admin_numbers, f)

def load_amin():
    global amin_list
    if os.path.exists(AMIN_FILE):
        with open(AMIN_FILE, 'r') as f:
            amin_list = json.load(f)
    else:
        amin_list = {}

def save_amin():
    with open(AMIN_FILE, 'w') as f:
        json.dump(amin_list, f)

def load_professor():
    global professor_list
    if os.path.exists(PROFESSOR_FILE):
        with open(PROFESSOR_FILE, 'r') as f:
            professor_list = json.load(f)
    else:
        professor_list = {}

def save_professor():
    with open(PROFESSOR_FILE, 'w') as f:
        json.dump(professor_list, f)

def load_banned():
    global banned_users
    if os.path.exists(BANNED_FILE):
        with open(BANNED_FILE, 'r') as f:
            banned_users = json.load(f)
    else:
        banned_users = {}

def save_banned():
    with open(BANNED_FILE, 'w') as f:
        json.dump(banned_users, f)

# ========== توابع جدید ==========
def load_news():
    global news_data, news_counter
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, 'r') as f:
            data = json.load(f)
            news_data = data.get('news', {})
            news_counter = data.get('counter', 0)
    else:
        news_data = {}
        news_counter = 0

def save_news():
    with open(NEWS_FILE, 'w') as f:
        json.dump({'news': news_data, 'counter': news_counter}, f)

def load_ad():
    global ad_data, ad_counter
    if os.path.exists(AD_FILE):
        with open(AD_FILE, 'r') as f:
            data = json.load(f)
            ad_data = data.get('ads', {})
            ad_counter = data.get('counter', 0)
    else:
        ad_data = {}
        ad_counter = 0

def save_ad():
    with open(AD_FILE, 'w') as f:
        json.dump({'ads': ad_data, 'counter': ad_counter}, f)

def load_donate():
    global donate_data
    if os.path.exists(DONATE_FILE):
        with open(DONATE_FILE, 'r') as f:
            donate_data = json.load(f)
    else:
        donate_data = []

def save_donate():
    with open(DONATE_FILE, 'w') as f:
        json.dump(donate_data, f)
# ===================================

load_data()
load_admins()
load_admin_numbers()
load_amin()
load_professor()
load_banned()
load_news()
load_ad()
load_donate()
init_roles()

def is_admin(user_id):
    return user_id == OWNER_ID or str(user_id) in admins

def is_amin(user_id):
    return str(user_id) in amin_list

def is_professor(user_id):
    return str(user_id) in professor_list

def is_banned(user_id):
    return str(user_id) in banned_users

def get_admin_number(user_id):
    if str(user_id) in admin_numbers:
        return admin_numbers[str(user_id)]
    return None

def assign_admin_number(user_id):
    if str(user_id) in admin_numbers:
        return admin_numbers[str(user_id)]
    existing_numbers = []
    for num in admin_numbers.values():
        if num.startswith('Admin '):
            try:
                existing_numbers.append(int(num.split(' ')[1]))
            except:
                pass
    next_num = 1
    while next_num in existing_numbers:
        next_num += 1
    admin_number = f"Admin {next_num}"
    admin_numbers[str(user_id)] = admin_number
    save_admin_numbers()
    return admin_number

def get_user_link(user):
    if user.username:
        return f"@{user.username}"
    else:
        return user.first_name or user.last_name or "کاربر"

# ========== پنل اصلی ==========
@bot.message_handler(commands=['panel'])
def panel(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "*** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton("📰 اخبار", callback_data="panel_news")
    btn2 = telebot.types.InlineKeyboardButton("📢 تبلیغات", callback_data="panel_ads")
    btn3 = telebot.types.InlineKeyboardButton("🤝 اتحاد ها", callback_data="panel_alliances")
    btn4 = telebot.types.InlineKeyboardButton("📺 کانال ها", callback_data="panel_channels")
    btn5 = telebot.types.InlineKeyboardButton("💰 حمایت ها", callback_data="panel_donate")
    btn6 = telebot.types.InlineKeyboardButton("👑 تیم مدیریتی", callback_data="panel_team")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    
    bot.reply_to(msg, "شما وارد پنل اصلی بات شدید برای استفاده از بات روی گزینه ها کلیک کنید تا از ویژگی های پنل استفاده کنید !", reply_markup=markup)

# ========== مدیریت دکمه‌های پنل ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith('panel_'))
def handle_panel(call):
    user_id = call.from_user.id
    if is_banned(user_id):
        bot.answer_callback_query(call.id, "شما محروم هستید")
        return
    
    if call.data == "panel_news":
        if news_data:
            response = "📰 لیست اخبار:\n\n"
            for news_id, news_text in news_data.items():
                response += f"News : {news_id}\n{news_text}\n\n"
            bot.send_message(user_id, response)
        else:
            bot.send_message(user_id, "📭 هیچ خبری وجود ندارد.")
        bot.answer_callback_query(call.id)
    
    elif call.data == "panel_ads":
        if ad_data:
            response = "📢 لیست تبلیغات:\n\n"
            for ad_id, ad_text in ad_data.items():
                response += f"Ad : {ad_id}\n{ad_text}\n\n"
            bot.send_message(user_id, response)
        else:
            bot.send_message(user_id, "📭 هیچ تبلیغی وجود ندارد.")
        bot.answer_callback_query(call.id)
    
    elif call.data == "panel_alliances":
        bot.send_message(user_id, "🤝 Coming Soon ...")
        bot.answer_callback_query(call.id)
    
    elif call.data == "panel_channels":
        bot.send_message(user_id, "📺 Coming Soon ...")
        bot.answer_callback_query(call.id)
    
    elif call.data == "panel_donate":
        if donate_data:
            response = "💰 لیست حمایت‌ها:\n\n"
            for item in donate_data:
                response += f"{item['rank']} : {item['name']}\nمبلغ : {item['amount']} T\n\n"
            bot.send_message(user_id, response)
        else:
            bot.send_message(user_id, "💰 هیچ حمایتی ثبت نشده است.")
        bot.answer_callback_query(call.id)
    
    elif call.data == "panel_team":
        response = "👑 تیم مدیریتی:\n\n"
        response += "سازنده: OWNER\n"
        if admins:
            for admin_id in admins:
                admin_num = get_admin_number(admin_id) or "بدون شماره"
                try:
                    user_info = bot.get_chat(admin_id)
                    name = user_info.first_name or user_info.username or "ناشناس"
                    if admin_num == "AmiN":
                        response += f"کاپیتان : {name}\n"
                    elif admin_num == "Professor":
                        response += f"آقای : {name}\n"
                    else:
                        response += f"{admin_num} : {name}\n"
                except:
                    response += f"{admin_num} : ناشناس\n"
        else:
            response += "هیچ ادمین دیگری وجود ندارد."
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)

# ========== دستور /news ==========
@bot.message_handler(commands=['news'])
def news_command(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID:
        return
    
    if user_id in news_mode and news_mode[user_id]:
        news_mode[user_id] = False
        bot.reply_to(msg, "❌ شما از حالت خبر خارج شدید.")
    else:
        news_mode[user_id] = True
        bot.reply_to(msg, "✅ شما وارد حالت خبر شدید. پیام خود را بفرستید تا به لیست اخبار اضافه شود.\nبرای خروج دوباره /news را بزنید.")

# ========== دستور /ad ==========
@bot.message_handler(commands=['ad'])
def ad_command(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID:
        return
    
    if user_id in ad_mode and ad_mode[user_id]:
        ad_mode[user_id] = False
        bot.reply_to(msg, "❌ شما از حالت تبلیغ خارج شدید.")
    else:
        ad_mode[user_id] = True
        bot.reply_to(msg, "✅ شما وارد حالت تبلیغ شدید. پیام خود را بفرستید تا به لیست تبلیغات اضافه شود.\nبرای خروج دوباره /ad را بزنید.")

# ========== دستور /hazfnews ==========
@bot.message_handler(commands=['hazfnews'])
def hazfnews(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID:
        return
    
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ لطفا شماره خبر را وارد کنید: /hazfnews 1")
        return
    
    try:
        news_id = parts[1]
        if news_id in news_data:
            del news_data[news_id]
            save_news()
            bot.reply_to(msg, f"✅ خبر {news_id} حذف شد.")
        else:
            bot.reply_to(msg, f"❌ خبر {news_id} وجود ندارد.")
    except:
        bot.reply_to(msg, "❌ شماره معتبر نیست.")

# ========== دستور /hazfad ==========
@bot.message_handler(commands=['hazfad'])
def hazfad(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID:
        return
    
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ لطفا شماره تبلیغ را وارد کنید: /hazfad 1")
        return
    
    try:
        ad_id = parts[1]
        if ad_id in ad_data:
            del ad_data[ad_id]
            save_ad()
            bot.reply_to(msg, f"✅ تبلیغ {ad_id} حذف شد.")
        else:
            bot.reply_to(msg, f"❌ تبلیغ {ad_id} وجود ندارد.")
    except:
        bot.reply_to(msg, "❌ شماره معتبر نیست.")

# ========== دستور /donate ==========
@bot.message_handler(commands=['donate'])
def donate_command(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID:
        return
    
    parts = msg.text.split()
    if len(parts) < 3:
        bot.reply_to(msg, "⚠️ لطفا نام و مبلغ را وارد کنید: /donate Ali 1500000")
        return
    
    name = parts[1]
    try:
        amount = int(parts[2])
    except:
        bot.reply_to(msg, "❌ مبلغ معتبر نیست.")
        return
    
    # اضافه کردن به لیست
    donate_data.append({'name': name, 'amount': amount})
    
    # مرتب سازی بر اساس مبلغ (بیشترین به کمترین)
    donate_data.sort(key=lambda x: x['amount'], reverse=True)
    
    # به‌روزرسانی رتبه‌ها
    for idx, item in enumerate(donate_data):
        item['rank'] = idx + 1
    
    save_donate()
    bot.reply_to(msg, f"✅ {name} با مبلغ {amount} T به لیست حمایت‌ها اضافه شد.")

# ========== دستور /owner ==========
@bot.message_handler(commands=['owner'])
def owner_cmds(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID:
        return
    
    response = "👑 لیست دستورات اختصاصی OWNER:\n\n"
    response += "/panel : پنل اصلی بات\n"
    response += "/news : وارد شدن به حالت خبر\n"
    response += "/hazfnews [شماره] : حذف خبر\n"
    response += "/ad : وارد شدن به حالت تبلیغ\n"
    response += "/hazfad [شماره] : حذف تبلیغ\n"
    response += "/donate [نام] [مبلغ] : اضافه کردن حمایت\n"
    response += "/update : ارسال پیام آپدیت به همه کاربران\n"
    response += "/ban [ایدی] : محروم کردن کاربر\n"
    response += "/unban [ایدی] : رفع محرومیت کاربر\n"
    response += "/ma [ایدی] : اضافه کردن ادمین\n"
    response += "/kickadmin [ایدی] : حذف ادمین\n"
    bot.reply_to(msg, response)

# ========== مدیریت پیام‌ها ==========
@bot.message_handler(func=lambda m: True)
def handle_messages(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        return
    
    # حالت خبر
    if user_id in news_mode and news_mode[user_id]:
        global news_counter
        news_counter += 1
        news_data[str(news_counter)] = msg.text
        save_news()
        bot.reply_to(msg, f"✅ خبر {news_counter} با موفقیت ثبت شد.")
        news_mode[user_id] = False
        return
    
    # حالت تبلیغ
    if user_id in ad_mode and ad_mode[user_id]:
        global ad_counter
        ad_counter += 1
        ad_data[str(ad_counter)] = msg.text
        save_ad()
        bot.reply_to(msg, f"✅ تبلیغ {ad_counter} با موفقیت ثبت شد.")
        ad_mode[user_id] = False
        return
    
    # بقیه پیام‌ها
    if is_admin(user_id):
        if user_id in admin_chat_mode and admin_chat_mode[user_id]:
            if user_id == OWNER_ID:
                display_name = "OWNER"
                user_link = ""
            elif is_amin(user_id):
                display_name = "AmiN"
                user_link = ""
            elif is_professor(user_id):
                display_name = "Professor"
                user_link = ""
            else:
                admin_num = get_admin_number(user_id) or "Admin"
                display_name = f"{admin_num}"
                user_link = get_user_link(msg.from_user)
            for admin_id in admins:
                if int(admin_id) != user_id:
                    try:
                        if user_id == OWNER_ID or is_amin(user_id) or is_professor(user_id):
                            bot.send_message(int(admin_id), f"[ Admin.Chat ] ( {display_name} ) : {msg.text}")
                        else:
                            bot.send_message(int(admin_id), f"[ Admin.Chat ] ( {display_name} ) ( {user_link} ) : {msg.text}", parse_mode='HTML')
                    except:
                        pass
            if OWNER_ID != user_id:
                try:
                    if is_amin(user_id):
                        bot.send_message(OWNER_ID, f"[ Admin.Chat ] ( AmiN ) : {msg.text}")
                    elif is_professor(user_id):
                        bot.send_message(OWNER_ID, f"[ Admin.Chat ] ( Professor ) : {msg.text}")
                    else:
                        bot.send_message(OWNER_ID, f"[ Admin.Chat ] ( {display_name} ) ( {user_link} ) : {msg.text}", parse_mode='HTML')
                except:
                    pass
            bot.reply_to(msg, "پیام شما به چت ادمین ها ارسال شد.")
            return
        else:
            bot.reply_to(msg, "برای دیدن دستورات ادمینی ابتدا دستور /cmds را بزنید.")
            return
    
    if user_id in waiting_for_message and waiting_for_message[user_id]:
        if user_id != OWNER_ID and user_id in chat_sessions and chat_sessions[user_id] == 'open':
            bot.send_message(OWNER_ID, f"از کاربر:\nنام: {msg.from_user.first_name} [آیدی: {user_id}]\nپیام: {msg.text}")
            bot.reply_to(msg, "ارسال شد")
        else:
            bot.forward_message(OWNER_ID, user_id, msg.message_id)
            bot.send_message(OWNER_ID, f"نام: {msg.from_user.first_name} (@{msg.from_user.username}) | آیدی: {user_id}")
            bot.reply_to(msg, "پیام ارسال شد")
            waiting_for_message[user_id] = False
    else:
        if not msg.text.startswith('/'):
            bot.reply_to(msg, "ابتدا دستور /info را بزنید تا دستورات بات را ببینید")

# ========== ادامه دستورات قبلی ==========
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "*** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    bot.reply_to(msg, "/info : سلام امیدوارم حالتون خوب باشه . لطفا روی این دستور کلیک کنید")

@bot.message_handler(commands=['info'])
def info(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "*** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    response = "لیست دستورات بات:\n\n"
    response += "/helpme : صحبت با سازنده در پی وی شما\n"
    response += "/close : خروج از حالت صحبت یا همان بستن حالت دستور بالایی\n"
    response += "/ticket : ارسال سوال و صحبت درون بات با ادمین\n"
    if is_admin(user_id):
        response += "/tickets : لیست بلیط های باز نشده\n"
        response += "/cmds : لیست دستورات ادمین\n"
        response += "/ac : ورود/خروج از چت ادمین ها\n"
        if user_id == OWNER_ID or is_amin(user_id) or is_professor(user_id):
            response += "/perms : نمایش دسترسی ها\n"
    if user_id == OWNER_ID:
        response += "/admins : لیست ادمین ها\n"
        response += "/panel : پنل اصلی بات\n"
    bot.reply_to(msg, response)

# ========== ادامه دستورات قبلی (فقط برای فضا) ==========
# (دستورات قبلی مانند perms, admins, cmds, ma, kickadmin, ban, unban, ac, tickets, helpme, close, ticket, open, chat, a, cc, update با همان کد قبلی)

# ========== اجرا ==========
@app.route('/')
def home():
    return "Bot is running!"

def run_bot():
    print("Robot is running...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    app.run(host='0.0.0.0', port=8080)
