import telebot
import time
import threading
from flask import Flask
import json
import os

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

DATA_FILE = 'data.json'
ADMINS_FILE = 'admins.json'
ADMIN_NUMBERS_FILE = 'admin_numbers.json'

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

load_data()
load_admins()
load_admin_numbers()

def is_admin(user_id):
    return user_id == OWNER_ID or str(user_id) in admins

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
        @bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "/info : سلام امیدوارم حالتون خوب باشه . لطفا روی این دستور کلیک کنید")

@bot.message_handler(commands=['info'])
def info(msg):
    user_id = msg.from_user.id
    bot.reply_to(msg, "/helpme : صحبت با سازنده در پی وی شما")
    bot.reply_to(msg, "/close : خروج از حالت صحبت یا همان بستن حالت دستور بالایی")
    bot.reply_to(msg, "/ticket : ارسال سوال و صحبت درون بات با ادمین")
    if is_admin(user_id):
        bot.reply_to(msg, "/tickets : لیست بلیط های باز نشده")
        bot.reply_to(msg, "/cmds : لیست دستورات ادمین")
        bot.reply_to(msg, "/ac : ورود/خروج از چت ادمین ها")
    if user_id == OWNER_ID:
        bot.reply_to(msg, "/admins : لیست ادمین ها")

@bot.message_handler(commands=['admins'])
def show_admins(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID:
        return
    response = "لیست ادمین ها:\n\n"
    response += "سازنده: OWNER\n"
    if admins:
        for admin_id in admins:
            admin_num = get_admin_number(admin_id) or "بدون شماره"
            response += f"{admin_num}: {admin_id}\n"
    else:
        response += "هیچ ادمین دیگری وجود ندارد."
    bot.reply_to(msg, response)

@bot.message_handler(commands=['cmds'])
def cmds(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    response = "لیست دستورات ادمین:\n\n"
    response += "/tickets : لیست بلیط های باز نشده\n"
    response += "/open [شماره] : باز کردن بلیط\n"
    response += "/a [پیام] : ارسال پاسخ به کاربر\n"
    response += "/cc : پایان چت با کاربر\n"
    response += "/ma [ایدی] : اضافه کردن ادمین جدید (فقط سازنده)\n"
    response += "/ac : ورود/خروج از چت ادمین ها\n"
    bot.reply_to(msg, response)

@bot.message_handler(commands=['ma'])
def add_admin(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID:
        return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "لطفا آیدی عددی کاربر را وارد کنید: /ma 123456789")
        return
    try:
        new_admin_id = int(parts[1])
    except:
        bot.reply_to(msg, "آیدی عددی معتبر نیست")
        return
    if new_admin_id == OWNER_ID:
        bot.reply_to(msg, "کاربر مورد نظر خود سازنده بات است.")
        return
    if str(new_admin_id) in admins:
        bot.reply_to(msg, f"کاربر {new_admin_id} قبلا ادمین است.")
        return
    admins[str(new_admin_id)] = 'admin'
    save_admins()
    admin_num = assign_admin_number(new_admin_id)
    bot.reply_to(msg, f"کاربر با آیدی {new_admin_id} به لیست ادمین ها اضافه شد.\nشماره: {admin_num}")

@bot.message_handler(commands=['ac'])
def admin_chat_toggle(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    if user_id in admin_chat_mode and admin_chat_mode[user_id]:
        admin_chat_mode[user_id] = False
        bot.reply_to(msg, "شما از حالت چت ادمین خارج شدید.")
    else:
        admin_chat_mode[user_id] = True
        if user_id != OWNER_ID:
            admin_num = get_admin_number(user_id)
            if not admin_num:
                admin_num = assign_admin_number(user_id)
            bot.reply_to(msg, f"شما وارد حالت چت ادمین شدید.\nشماره شما: {admin_num}\nبرای خروج دوباره /ac را بزنید.")
        else:
            bot.reply_to(msg, "شما (OWNER) وارد حالت چت ادمین شدید.\nبرای خروج دوباره /ac را بزنید.")
            @bot.message_handler(commands=['tickets'])
def show_tickets(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    open_tickets = []
    for ticket_num, ticket_data in tickets.items():
        user_id_ticket = ticket_data['user_id']
        if user_id_ticket not in chat_sessions or chat_sessions[user_id_ticket] != 'open':
            open_tickets.append((ticket_num, ticket_data))
    if not open_tickets:
        bot.reply_to(msg, "هیچ بلیط باز نشده ای وجود ندارد.")
        return
    response = "لیست بلیط های باز نشده:\n\n"
    for ticket_num, data in open_tickets:
        response += f"شماره: {ticket_num}\n"
        response += f"نام: {data['first_name']} (@{data['username']})\n"
        response += f"سوال: {data['question'][:50]}...\n"
        response += f"برای باز کردن: /open {ticket_num}\n\n"
    bot.reply_to(msg, response)

@bot.message_handler(commands=['helpme'])
def helpme(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID:
        return
    waiting_for_message[user_id] = True
    bot.reply_to(msg, "/close : شما وارد حالت ارسال پیام شدید لطفا بعد از فرستادن پیام خود برای بستن حالت از این دستور استفاده کنید")
    bot.reply_to(msg, "بعد از ارسال پیام خود سازنده بات به پی وی شما پیام ارسال می کند ولی از ویس استفاده نکنید و به صورت متن پیام خود را بفرستید")

@bot.message_handler(commands=['close'])
def close(msg):
    user_id = msg.from_user.id
    if user_id in waiting_for_message:
        waiting_for_message[user_id] = False
        bot.reply_to(msg, "شما از حالت ارسال پیام خارج شدید")
    else:
        bot.reply_to(msg, "درحالت ارسال پیام نیستید")

@bot.message_handler(commands=['ticket'])
def soal(msg):
    global ticket_counter
    user_id = msg.from_user.id
    if is_admin(user_id):
        bot.reply_to(msg, "شما ادمین هستید و نمی توانید تیکت بزنید")
        return
    text = msg.text
    parts = text.split(maxsplit=1)
    if user_id in user_ticket_status and user_ticket_status[user_id] in tickets:
        bot.reply_to(msg, "شما یک بلیط فعال دارید و نمی توانید بلیط جدید بفرستید")
        return
    if len(parts) < 2:
        bot.reply_to(msg, "لطفا بعد از /ticket پیام خود را بنویسید")
        bot.reply_to(msg, "مثال : /ticket سوال دارم")
        bot.reply_to(msg, "شما می توانید متن پایین را کپی کرده و برای بات ارسال کنید که این یک راه ساده تر و سریع تر است")
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
    bot.send_message(OWNER_ID, f"بلیط جدید شماره: {ticket_number}\nنام: {user.first_name} (@{user.username}) [آیدی: {user_id}]\nسوال: {soal_text}\n\nبرای باز کردن: /open {ticket_number}")
    bot.reply_to(msg, "پیام شما ارسال شد")

@bot.message_handler(commands=['open'])
def open_chat(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "/open 5")
        return
    try:
        ticket_number = int(parts[1])
    except:
        bot.reply_to(msg, "شماره معتبر نیست")
        return
    if ticket_number not in tickets:
        bot.reply_to(msg, f"بلیط {ticket_number} وجود ندارد")
        return
    user_id_ticket = tickets[ticket_number]['user_id']
    chat_sessions[user_id_ticket] = 'open'
    bot.send_message(user_id_ticket, "بلیط شما توسط ادمین باز شد. برای چت دستور /chat را بزنید.")
    bot.reply_to(msg, f"چت با بلیط {ticket_number} باز شد")

@bot.message_handler(commands=['chat'])
def chat_with_user(msg):
    user_id = msg.from_user.id
    if is_admin(user_id):
        bot.reply_to(msg, "شما ادمین هستید و نمی توانید از این دستور استفاده کنید")
        return
    if user_id not in chat_sessions or chat_sessions[user_id] != 'open':
        bot.reply_to(msg, "چت فعالی ندارید")
        return
    waiting_for_message[user_id] = True
    bot.reply_to(msg, "وارد چت شدید. پیام خود را بفرستید")

@bot.message_handler(commands=['a'])
def admin_chat(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(msg, "/a پیام")
        return
    for user_id_chat, status in chat_sessions.items():
        if status == 'open':
            bot.send_message(user_id_chat, f"پاسخ ادمین:\n{parts[1]}")
            bot.reply_to(msg, f"پیام ارسال شد")
            return
    bot.reply_to(msg, "چت فعالی وجود ندارد")

@bot.message_handler(commands=['cc'])
def close_chat(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    for user_id_chat, status in chat_sessions.items():
        if status == 'open':
            chat_sessions[user_id_chat] = 'closed'
            bot.send_message(user_id_chat, "گفتگو پایان یافت")
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            btn_yes = telebot.types.InlineKeyboardButton("بله", callback_data=f"delete_{user_id_chat}")
            btn_no = telebot.types.InlineKeyboardButton("خیر", callback_data=f"keep_{user_id_chat}")
            markup.add(btn_yes, btn_no)
            bot.send_message(user_id_chat, "آیا از این گفتگو راضی بودید؟", reply_markup=markup)
            bot.reply_to(msg, f"چت پایان یافت")
            if user_id_chat in user_ticket_status:
                ticket_num = user_ticket_status[user_id_chat]
                if ticket_num in tickets:
                    del tickets[ticket_num]
                del user_ticket_status[user_id_chat]
                save_data()
            return
    bot.reply_to(msg, "چت فعالی وجود ندارد")

@bot.message_handler(func=lambda m: True)
def forward_all(msg):
    user_id = msg.from_user.id
    user = msg.from_user
    if is_admin(user_id):
        if user_id in admin_chat_mode and admin_chat_mode[user_id]:
            if user_id == OWNER_ID:
                display_name = "OWNER"
                user_link = ""
            else:
                admin_num = get_admin_number(user_id) or "Admin"
                display_name = f"{admin_num}"
                user_link = get_user_link(user)
            for admin_id in admins:
                if int(admin_id) != user_id:
                    try:
                        if user_id == OWNER_ID:
                            bot.send_message(int(admin_id), f"[ Admin.Chat ] ( {display_name} ) : {msg.text}")
                        else:
                            bot.send_message(int(admin_id), f"[ Admin.Chat ] ( {display_name} ) ( {user_link} ) : {msg.text}", parse_mode='HTML')
                    except:
                        pass
            if OWNER_ID != user_id:
                try:
                    bot.send_message(OWNER_ID, f"[ Admin.Chat ] ( {display_name} ) ( {user_link} ) : {msg.text}", parse_mode='HTML')
                except:
                    pass
            bot.reply_to(msg, "پیام شما به چت ادمین ها ارسال شد.")
            return
    if user_id in waiting_for_message and waiting_for_message[user_id]:
        if user_id != OWNER_ID and user_id in chat_sessions and chat_sessions[user_id] == 'open':
            bot.send_message(OWNER_ID, f"از کاربر:\nنام: {user.first_name} [آیدی: {user.id}]\nپیام: {msg.text}")
            bot.reply_to(msg, "ارسال شد")
        else:
            bot.forward_message(OWNER_ID, user.id, msg.message_id)
            bot.send_message(OWNER_ID, f"نام: {user.first_name} (@{user.username}) | آیدی: {user.id}")
            bot.reply_to(msg, "پیام ارسال شد")
            waiting_for_message[user_id] = False
    else:
        bot.reply_to(msg, "ابتدا /helpme را بزنید یا برای چت ادمین ها /ac را فعال کنید")
        @bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data.startswith('delete_'):
        user_id = int(call.data.split('_')[1])
        bot.send_message(user_id, "با تشکر از شما")
        bot.answer_callback_query(call.id, "با تشکر از شما")
    elif call.data.startswith('keep_'):
        user_id = int(call.data.split('_')[1])
        bot.send_message(user_id, "با تشکر از شما")
        bot.answer_callback_query(call.id, "با تشکر از شما")

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
