import telebot
import time
import threading
from flask import Flask
import json
import os
from datetime import datetime
import pytz

TOKEN = "8299446091:AAG3rkzDotNZ4KLObMy_BJ4Lm_sCBs-DHKE"
OWNER_ID = 6703121829

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
waiting_for_message = {}
tickets = {}
ticket_counter = 0
chat_sessions = {}
user_ticket_status = {}

DATA_FILE = 'data.json'

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

load_data()

def get_persian_date():
    try:
        tehran = pytz.timezone('Asia/Tehran')
        now = datetime.now(tehran)
        
        # محاسبه تاریخ شمسی (روش دقیق‌تر)
        year = now.year - 621
        month = now.month
        day = now.day
        
        # تنظیم ماه‌های شمسی
        if month == 1:
            persian_month = "فروردین"
        elif month == 2:
            persian_month = "اردیبهشت"
        elif month == 3:
            persian_month = "خرداد"
        elif month == 4:
            persian_month = "تیر"
        elif month == 5:
            persian_month = "مرداد"
        elif month == 6:
            persian_month = "شهریور"
        elif month == 7:
            persian_month = "مهر"
        elif month == 8:
            persian_month = "آبان"
        elif month == 9:
            persian_month = "آذر"
        elif month == 10:
            persian_month = "دی"
        elif month == 11:
            persian_month = "بهمن"
        else:
            persian_month = "اسفند"
        
        # نام روز هفته
        weekdays = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"]
        weekday_name = weekdays[now.weekday()]
        
        return f"{year}/{month}/{day}", now.strftime("%H:%M:%S"), weekday_name, persian_month
    except Exception as e:
        # اگر خطا بود، تاریخ میلادی رو نشون بده
        now = datetime.now()
        return now.strftime("%Y/%m/%d"), now.strftime("%H:%M:%S"), "", ""

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "/info : سلام امیدوارم حالتون خوب باشه . لطفا روی این دستور کلیک کنید 🔔")

@bot.message_handler(commands=['info'])
def info(msg):
    bot.reply_to(msg, "/helpme : صحبت با سازنده در پی وی شما ✨")
    bot.reply_to(msg, "/close : خروج از حالت صحبت یا همان بستن حالت دستور بالایی ✨")
    bot.reply_to(msg, "/ticket : ارسال سوال و صحبت درون بات با ادمین ✨")
    bot.reply_to(msg, "/timedate : نمایش تاریخ و ساعت ایران ✨")

@bot.message_handler(commands=['timedate'])
def timedate(msg):
    persian_date, persian_time, weekday, persian_month = get_persian_date()
    if weekday:
        response = f"📅 امروز : {weekday} هست\n🕐 ساعت : {persian_time}\n📆 تاریخ : {persian_date}"
    else:
        response = f"📅 تاریخ : {persian_date}\n🕐 ساعت : {persian_time}"
    bot.reply_to(msg, response)

@bot.message_handler(commands=['helpme'])
def helpme(msg):
    user_id = msg.from_user.id
    waiting_for_message[user_id] = True
    bot.reply_to(msg, "/close : شما وارد حالت ارسال پیام شدید لطفا بعد از فرستادن پیام خود برای بستن حالت از این دستور استفاده کنید ✅")
    bot.reply_to(msg, "🔮 بعد از ارسال پیام خود سازنده بات به پی وی شما پیام ارسال می کند ولی از ویس استفاده نکنید و به صورت متن پیام خود را بفرستید 🔮")

@bot.message_handler(commands=['close'])
def close(msg):
    user_id = msg.from_user.id
    if user_id in waiting_for_message:
        waiting_for_message[user_id] = False
        bot.reply_to(msg, "❌ شما از حالت ارسال پیام خارج شدید ❌")
    else:
        bot.reply_to(msg, "✅ درحالت ارسال پیام نیستید ✅")
        @bot.message_handler(commands=['ticket'])
def soal(msg):
    global ticket_counter
    user_id = msg.from_user.id
    text = msg.text
    parts = text.split(maxsplit=1)
    
    if user_id in user_ticket_status and user_ticket_status[user_id] in tickets:
        bot.reply_to(msg, ":x: شما یک بلیط فعال دارید و نمی توانید بلیط جدید بفرستید :x:")
        return
    
    if len(parts) < 2:
        bot.reply_to(msg, "لطفا بعد از /ticket پیام خود را بنویسید :warning:")
        bot.reply_to(msg, "مثال : /ticket سوال دارم")
        bot.reply_to(msg, ":diamond_shape_with_a_dot_inside: شما می توانید متن پایین را کپی کرده و برای بات ارسال کنید که این یک راه ساده تر و سریع تر است :diamond_shape_with_a_dot_inside:")
        bot.reply_to(msg, "/ticket سلام میشه من رو راهنمایی کنید ؟")
        return
    
    soal_text = parts[1]
    user = msg.from_user
    ticket_counter += 1
    ticket_number = ticket_counter
    
    tickets[ticket_number] = {
        'user_id': user_id,
        'username': user.username or 'بدون یوزرنیم',
        'first_name': user.first_name or 'ناشناس',
        'question': soal_text
    }
    user_ticket_status[user_id] = ticket_number
    save_data()
    
    bot.send_message(OWNER_ID, f"بلیط جدید شماره: {ticket_number}\nنام: {user.first_name} ({user.username}) [آیدی: {user_id}]\nسوال: {soal_text}\n\nبرای باز کردن چت: /open {ticket_number}")
    bot.reply_to(msg, "پیام شما ارسال شد")

@bot.message_handler(commands=['open'])
def open_chat(msg):
    if msg.from_user.id != OWNER_ID:
        bot.reply_to(msg, "شما دسترسی ندارید")
        return
    
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "/open 5")
        return
    
    try:
        ticket_number = int(parts[1])
    except:
        bot.reply_to(msg, ":x: شماره معتبر نیست :x:")
        return
    
    if ticket_number not in tickets:
        bot.reply_to(msg, f"بلیط {ticket_number} وجود ندارد")
        return
    
    user_id = tickets[ticket_number]['user_id']
    chat_sessions[user_id] = 'open'
    
    bot.send_message(user_id, "/chat : بلیط شما توسط ادمین بات قبول شد برای چت روی این دستور کلیک کنید :white_check_mark:")
    bot.reply_to(msg, f"چت با بلیط {ticket_number} باز شد")

@bot.message_handler(commands=['chat'])
def chat_with_user(msg):
    user_id = msg.from_user.id
    if user_id not in chat_sessions or chat_sessions[user_id] != 'open':
        bot.reply_to(msg, ":x: چت فعالی ندارید :x:")
        return
    waiting_for_message[user_id] = True
    bot.reply_to(msg, ":white_check_mark: وارد چت شدید. پیام خود را بفرستید :white_check_mark:")

@bot.message_handler(commands=['a'])
def admin_chat(msg):
    if msg.from_user.id != OWNER_ID:
        return
    
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(msg, "/a پیام")
        return
    
    for user_id, status in chat_sessions.items():
        if status == 'open':
            bot.send_message(user_id, f"⚜ پاسخ ادمین به شما :\n{parts[1]}")
            bot.reply_to(msg, f"پیام ارسال شد")
            return
    
    bot.reply_to(msg, "چت فعالی وجود ندارد")

@bot.message_handler(commands=['cc'])
def close_chat(msg):
    if msg.from_user.id != OWNER_ID:
        return
    
    for user_id, status in chat_sessions.items():
        if status == 'open':
            chat_sessions[user_id] = 'closed'
            bot.send_message(user_id, ":boom: گفتگو پایان یافت :boom:")
            
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            btn_yes = telebot.types.InlineKeyboardButton(":white_check_mark: بله :white_check_mark:", callback_data=f"delete_{user_id}")
            btn_no = telebot.types.InlineKeyboardButton(":x: خیر :x:", callback_data=f"delete_{user_id}")
            markup.add(btn_yes, btn_no)
            
            bot.send_message(user_id, "آیا از این گفت و گو راضی بودید ؟ :diamond_shape_with_a_dot_inside:", reply_markup=markup)
            bot.reply_to(msg, f":boom: چت پایان یافت :boom:")
            
            if user_id in user_ticket_status:ticket_num = user_ticket_status[user_id]
                if ticket_num in tickets:
                    del tickets[ticket_num]
                del user_ticket_status[user_id]
                save_data()
            return
    
    bot.reply_to(msg, "چت فعالی وجود ندارد")

@bot.message_handler(func=lambda m: True)
def forward_all(msg):
    user_id = msg.from_user.id
    user = msg.from_user
    
    if user_id in waiting_for_message and waiting_for_message[user_id]:
        if user_id != OWNER_ID and user_id in chat_sessions and chat_sessions[user_id] == 'open':
            bot.send_message(OWNER_ID, f"از کاربر:\nنام: {user.first_name} [آیدی: {user.id}]\nپیام: {msg.text}")
            bot.reply_to(msg, "✅ ارسال شد ✅")
        else:
            bot.forward_message(OWNER_ID, user.id, msg.message_id)
            bot.send_message(OWNER_ID, f"نام: {user.first_name} ({user.username}) | آیدی: {user.id}")
            bot.reply_to(msg, "✅ پیام ارسال شد ✅")
            waiting_for_message[user_id] = False
    else:
        bot.reply_to(msg, "💢 ابتدا /helpme را بزنید 💢")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data.startswith('delete_'):
        user_id = int(call.data.split('_')[1])
        bot.send_message(user_id, "❤ با تشکر از شما ❤")
        bot.answer_callback_query(call.id, "❤ آرزویه موفقیت برای شما ❤")
    elif call.data.startswith('keep_'):
        user_id = int(call.data.split('_')[1])
        bot.send_message(user_id, "❤ با تشکر از شما ❤")
        bot.answer_callback_query(call.id, "❤ آرزویه موفقیت برای شما ❤")

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
