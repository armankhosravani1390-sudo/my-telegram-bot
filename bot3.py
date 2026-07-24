import telebot
import time
import threading
from flask import Flask
from datetime import datetime
import pytz
import json
import os

TOKEN = "8299446091:AAG3rkzDotNZ4KLObMy_BJ4Lm_sCBs-DHKE"
OWNER_ID = 6703121829

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# دیکشنری‌ها
waiting_for_message = {}
tickets = {}  # {ticket_number: {'user_id': , 'username': , 'first_name': , 'time': , 'date': }}
ticket_counter = 0
chat_sessions = {}  # {user_id: 'open' or 'closed'}
user_ticket_status = {}  # {user_id: ticket_number}

# فایل برای ذخیره شمارنده تیکت‌ها
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

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🧑🏻:computer: : سلام امیدوارم حالتون خوب باشه :wave:🏻:pray:🏻 لطفا دستور helpme/ را بزنید :stars:🧭")
    bot.reply_to(msg, "🧑🏻:computer: : برای دیدن بقیه دستورات لطفا دستور Info/ را بزنید و بقیه دستورات بات را مشاهده کنید :stars::pray:🏻")
    bot.reply_to(msg, "🧑🏻:computer: : بعد از تمام شدن سوالتون با زدن دستور Close/ می توانید از حالت helpme/ خارج شوید 🧭:dizzy:")
    bot.reply_to(msg, "🧑🏻:computer: : و اگر سوالی دارید لطفا از دستور Soal/ و جلوی این دستور متن خود را بنویسید :herb:⛓:boom:")

@bot.message_handler(commands=['info'])
def info(msg):
    bot.reply_to(msg, ":pushpin: /helpme : برای صحبت با ادمین")
    bot.reply_to(msg, ":pushpin: /Info : برای دیدن لیست دستورات بات")
    bot.reply_to(msg, ":pushpin: /DateTime : برای دیدن تاریخ و ساعت امروز")
    bot.reply_to(msg, ":pushpin: /Close : برای خروج از حالت helpme")
    bot.reply_to(msg, ":pushpin: /Soal : برای ارسال سوال به ادمین")
    bot.reply_to(msg, ":pushpin: /Open : باز کردن چت با کاربر (با شماره تیکت)")

@bot.message_handler(commands=['helpme'])
def helpme(msg):
    user_id = msg.from_user.id
    waiting_for_message[user_id] = True
    bot.reply_to(msg, "🧑🏻:computer: : شما وارد حالت ارسال پیام به TimeLess شدید ! لطفا پیام خود را ارسال کنید و منتظر پاسخ دادن به پیامتون باشید :pray:🏻:rose::stars:")

@bot.message_handler(commands=['close'])
def close(msg):
    user_id = msg.from_user.id
    if user_id in waiting_for_message:
        waiting_for_message[user_id] = False
        bot.reply_to(msg, "🧑🏻:computer: : شما از حالت ارسال پیام خارج شدید. برای ارسال مجدد، دوباره دستور helpme/ را بزنید :rose:")
    else:
        bot.reply_to(msg, "🧑🏻:computer: : شما در حالت ارسال پیام نیستید :x:")

@bot.message_handler(commands=['datetime'])
def datetime_cmd(msg):
    try:
        tehran_tz = pytz.timezone('Asia/Tehran')
        now = datetime.now(tehran_tz)
        date_str = now.strftime("%Y/%m/%d")
        time_str = now.strftime("%H:%M")
        bot.reply_to(msg, f"🧑🏻:computer: : امروز : {date_str} هستش و ساعت {time_str} است :coffee:")
    except:
        now = datetime.now()
        bot.reply_to(msg, f"🧑🏻:computer: : امروز : {now.strftime('%Y/%m/%d')} هستش و ساعت {now.strftime('%H:%M')} است :coffee:")

@bot.message_handler(commands=['soal'])
def soal(msg):
    global ticket_counter
    user_id = msg.from_user.id
    text = msg.text
    parts = text.split(maxsplit=1)
    
    # چک کن که کاربر قبلاً تیکت ارسال کرده یا نه
    if user_id in user_ticket_status and user_ticket_status[user_id] in tickets:
        bot.reply_to(msg, "🧑🏻:computer: : شما یک بلیط از قبل ارسال کردید و نمی توانید بلیط دیگری ارسال کنید :bust_in_silhouette:")
        return
    
    if len(parts) < 2:
        bot.reply_to(msg, "🧑🏻:computer: : لطفا بعد از زدن Soal/ پیام خود را جلو این دستور بنویسید تا بتوانید از این دستور استفاده کنید :gem:")
        bot.reply_to(msg, "[ Tips ] : /Soal Hi :wave:🏻")
else:
        soal_text = parts[1]
        user = msg.from_user
        
        # افزایش شمارنده تیکت
        ticket_counter += 1
        ticket_number = ticket_counter
        
        # ذخیره اطلاعات تیکت
        now = datetime.now(pytz.timezone('Asia/Tehran'))
        tickets[ticket_number] = {
            'user_id': user_id,
            'username': user.username or 'بدون یوزرنیم',
            'first_name': user.first_name or 'ناشناس',
            'question': soal_text,
            'time': now.strftime("%H:%M"),
            'date': now.strftime("%Y/%m/%d")
        }
        user_ticket_status[user_id] = ticket_number
        save_data()
        
        # ارسال اطلاعات تیکت به صاحب بات
        bot.send_message(OWNER_ID, f":ticket: بلیط جدید شماره: {ticket_number}\n:bust_in_silhouette: {user.first_name} (@{user.username}) [ID: {user_id}]\n:memo: سوال: {soal_text}\n:date: تاریخ: {now.strftime('%Y/%m/%d')} ساعت: {now.strftime('%H:%M')}\n\n:unlock: برای باز کردن چت: /open {ticket_number}")
        
        # پاسخ به کاربر
        bot.reply_to(msg, "🧑🏻:computer: : سوال شما با موفقیت ارسال شد. بعد از پاسخ، به شما اطلاع داده خواهد شد :white_check_mark:")

@bot.message_handler(commands=['open'])
def open_chat(msg):
    if msg.from_user.id != OWNER_ID:
        bot.reply_to(msg, "شما دسترسی ندارید :x:")
        return
    
    text = msg.text
    parts = text.split()
    
    if len(parts) < 2:
        bot.reply_to(msg, "🧑🏻:computer: : لطفا شماره بلیط را وارد کنید: /open 5")
        return
    
    try:
        ticket_number = int(parts[1])
    except:
        bot.reply_to(msg, "🧑🏻:computer: : شماره بلیط معتبر نیست :x:")
        return
    
    if ticket_number not in tickets:
        bot.reply_to(msg, f"🧑🏻:computer: : بلیط شماره {ticket_number} وجود ندارد :x:")
        return
    
    user_id = tickets[ticket_number]['user_id']
    chat_sessions[user_id] = 'open'
    
    # پیام به کاربر
    bot.send_message(user_id, "🧑🏻:computer: : بلیط صحبت با ادمین باز شد :white_check_mark: الان می توانید با زدن دستور chat/ با این شخص صحبت کنید")
    bot.send_message(user_id, ":pushpin: برای شروع گفتگو، دستور chat/ را بزنید.")
    
    # پیام به ادمین
    bot.reply_to(msg, f"🧑🏻:computer: : چت با کاربر بلیط {ticket_number} باز شد :white_check_mark:")

@bot.message_handler(commands=['chat'])
def chat_with_user(msg):
    user_id = msg.from_user.id
    
    if user_id not in chat_sessions or chat_sessions[user_id] != 'open':
        bot.reply_to(msg, "🧑🏻:computer: : شما در حال حاضر چت فعالی ندارید :x:")
        return
    
    # ورود به حالت چت
    waiting_for_message[user_id] = True
    bot.reply_to(msg, "🧑🏻:computer: : شما وارد حالت چت شدید. پیام خود را بفرستید.")

@bot.message_handler(commands=['a'])
def admin_chat(msg):
    if msg.from_user.id != OWNER_ID:
        return
    
    text = msg.text
    parts = text.split(maxsplit=1)
    
    if len(parts) < 2:
        bot.reply_to(msg, "🧑🏻:computer: : لطفا پیام خود را بعد از /a بنویسید")
        return
    
    # پیدا کردن کاربری که چت فعال داره
    for user_id, status in chat_sessions.items():
        if status == 'open':
            bot.send_message(user_id, f"🧑🏻:computer: : پاسخ ادمین:\n\n{parts[1]}")
            bot.reply_to(msg, f":white_check_mark: پیام به کاربر {user_id} ارسال شد")
            return
    
    bot.reply_to(msg, "🧑🏻:computer: : هیچ چت فعالی وجود ندارد :x:")

@bot.message_handler(commands=['cc'])
def close_chat(msg):
    if msg.from_user.id != OWNER_ID:
        return
    
    # پیدا کردن کاربری که چت فعال داره
    for user_id, status in chat_sessions.items():
        if status == 'open':
            chat_sessions[user_id] = 'closed'
            
            # ارسال پیام پایان چت به کاربر
            bot.send_message(user_id, "🧑🏻:computer: : گفت‌وگو پایان یافت ⛓:boom::stars:")
            
            # دکمه‌های پاک کردن تاریخچه
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            btn_yes = telebot.types.InlineKeyboardButton(":white_check_mark: بله", callback_data=f"delete_{user_id}")
btn_no = telebot.types.InlineKeyboardButton(":x: خیر", callback_data=f"keep_{user_id}")
            markup.add(btn_yes, btn_no)
            
            bot.send_message(user_id, "🧑🏻:computer: : آیا می‌خواهید نوشته‌های گفت‌وگو را پاک کنید؟", reply_markup=markup)
            
            bot.reply_to(msg, f":white_check_mark: چت با کاربر {user_id} پایان یافت")
            
            # حذف تیکت کاربر
            if user_id in user_ticket_status:
                ticket_num = user_ticket_status[user_id]
                if ticket_num in tickets:
                    del tickets[ticket_num]
                del user_ticket_status[user_id]
                save_data()
            
            return
    
    bot.reply_to(msg, "🧑🏻:computer: : هیچ چت فعالی وجود ندارد :x:")

@bot.message_handler(func=lambda m: True)
def forward_all(msg):
    user_id = msg.from_user.id
    
    # چک کن که آیا کاربر در حالت چت هست یا نه
    if user_id in waiting_for_message and waiting_for_message[user_id]:
        # اگه کاربر OWNER نباشه و چت فعال داشته باشه، پیام رو به ادمین بفرست
        if user_id != OWNER_ID and user_id in chat_sessions and chat_sessions[user_id] == 'open':
            user = msg.from_user
            bot.send_message(OWNER_ID, f":speech_balloon: پیام از کاربر در چت:\n:bust_in_silhouette: {user.first_name} (@{user.username}) [ID: {user.id}]\n:memo: {msg.text}")
            bot.reply_to(msg, ":white_check_mark: پیام شما به ادمین ارسال شد")
        else:
            # پیام معمولی (حالت helpme)
            user = msg.from_user
            bot.forward_message(OWNER_ID, user.id, msg.message_id)
            bot.send_message(OWNER_ID, f":bust_in_silhouette: {user.first_name} (@{user.username}) | ID: {user.id}")
            bot.reply_to(msg, "🧑🏻:computer: : پیام شما با موفقیت ارسال شد :white_check_mark:")
            waiting_for_message[user_id] = False
    else:
        bot.reply_to(msg, "🧑🏻:computer: : اگر که می‌خواید با TimeLess صحبت کنید باید از دستور helpme/ استفاده کنید :gem:")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data.startswith('delete_'):
        user_id = int(call.data.split('_')[1])
        bot.send_message(user_id, "🧑🏻:computer: : تاریخچه گفت‌وگو پاک شد :white_check_mark:")
        bot.answer_callback_query(call.id, "تاریخچه پاک شد")
        
    elif call.data.startswith('keep_'):
        user_id = int(call.data.split('_')[1])
        bot.send_message(user_id, "🧑🏻:computer: : تاریخچه گفت‌وگو نگهداری شد :white_check_mark:")
        bot.answer_callback_query(call.id, "تاریخچه نگهداری شد")

@app.route('/')
def home():
    return "Bot is running!"

def run_bot():
    print(":white_check_mark: Robot is running...")
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
