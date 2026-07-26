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
amin_list = {}
professor_list = {}

DATA_FILE = 'data.json'
ADMINS_FILE = 'admins.json'
ADMIN_NUMBERS_FILE = 'admin_numbers.json'
AMIN_FILE = 'amin.json'
PROFESSOR_FILE = 'professor.json'

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

load_data()
load_admins()
load_admin_numbers()
load_amin()
load_professor()
init_roles()

def is_admin(user_id):
    return user_id == OWNER_ID or str(user_id) in admins

def is_amin(user_id):
    return str(user_id) in amin_list

def is_professor(user_id):
    return str(user_id) in professor_list

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
        if user_id == OWNER_ID or is_amin(user_id) or is_professor(user_id):
            bot.reply_to(msg, "/perms : نمایش دسترسی ها")
    if user_id == OWNER_ID:
        bot.reply_to(msg, "/admins : لیست ادمین ها")

@bot.message_handler(commands=['perms'])
def show_perms(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID and not is_amin(user_id) and not is_professor(user_id):
        return
    response = "جدول دسترسي ها:\n\n"
    response += "OWNER (سازنده):\n"
    response += "  - همه دستورات\n"
    response += "  - بدون نياز به تاييد\n\n"
    response += "AmiN (ادمین کامل):\n"
    response += "  - /ma (نياز به تاييد OWNER)\n"
    response += "  - /kickadmin (نياز به تاييد OWNER)\n"
    response += "  - /tickets\n"
    response += "  - /open\n"
    response += "  - /a\n"
    response += "  - /cc\n"
    response += "  - /ac\n"
    response += "  - /cmds\n"
    response += "  - /perms\n\n"
    response += "Professor (استاد):\n"
    response += "  - /ma (نياز به تاييد OWNER)\n"
    response += "  - /kickadmin (نياز به تاييد OWNER)\n"
    response += "  - /tickets\n"
    response += "  - /open\n"
    response += "  - /a\n"
    response += "  - /cc\n"
    response += "  - /ac\n"
    response += "  - /cmds\n"
    response += "  - /perms\n\n"
    response += "Admin (ادمین معمولی):\n"
    response += "  - /tickets\n"
    response += "  - /open\n"
    response += "  - /a\n"
    response += "  - /cc\n"
    response += "  - /ac\n"
    response += "  - /cmds\n"
    response += "  - /ma (ندارد)\n"
    response += "  - /kickadmin (ندارد)\n"
    response += "  - /perms (ندارد)\n\n"
    response += "User (کاربر عادی):\n"
    response += "  - /ticket\n"
    response += "  - /chat\n"
    response += "  - ساير دستورات را ندارد"
    bot.reply_to(msg, response)

@bot.message_handler(commands=['admins'])
def show_admins(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID and not is_amin(user_id) and not is_professor(user_id):
        return
    response = "ليست ادمين ها:\n\n"
    response += "سازنده: OWNER\n"
    if admins:
        for admin_id in admins:
            admin_num = get_admin_number(admin_id) or "بدون شماره"
            if admin_num == "AmiN":
                response += f"کاپیتان : AmiN\n"
            elif admin_num == "Professor":
                response += f"آقای : Professor\n"
            else:
                try:
                    user_info = bot.get_chat(admin_id)
                    username = user_info.username or "بدون یوزرنیم"
                    response += f"{admin_num}: {admin_id} (@{username})\n"
                except:
                    response += f"{admin_num}: {admin_id}\n"
    else:
        response += "هيچ ادمين ديگري وجود ندارد."
    bot.reply_to(msg, response)

@bot.message_handler(commands=['cmds'])
def cmds(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    response = "ليست دستورات ادمين:\n\n"
    response += "/tickets : ليست بليط هاي باز نشده\n"
    response += "/open [شماره] : باز کردن بليط\n"
    response += "/a [پيام] : ارسال پاسخ به کاربر\n"
    response += "/cc : پايان چت با کاربر\n"
    if user_id == OWNER_ID or is_amin(user_id) or is_professor(user_id):
        response += "/ma [آيدي] : اضافه کردن ادمين جديد (نياز به تاييد)\n"
        response += "/kickadmin [آيدي] : حذف ادمين (نياز به تاييد)\n"
    response += "/ac : ورود/خروج از چت ادمين ها\n"
    if user_id == OWNER_ID or is_amin(user_id) or is_professor(user_id):
        response += "/perms : نمايش دسترسي ها\n"
    bot.reply_to(msg, response)

@bot.message_handler(commands=['ma'])
def add_admin(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID and not is_amin(user_id) and not is_professor(user_id):
        return
    if user_id != OWNER_ID and (is_amin(user_id) or is_professor(user_id)):
        parts = msg.text.split()
        if len(parts) < 2:
            bot.reply_to(msg, "لطفا آيدي عددي کاربر را وارد کنيد: /ma 123456789")
            return
        try:
            new_admin_id = int(parts[1])
        except:
            bot.reply_to(msg, "آيدي عددي معتبر نيست")
            return
        if str(new_admin_id) in admins:
            bot.reply_to(msg, f"کاربر {new_admin_id} قبلا ادمين است.")
            return
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_accept = telebot.types.InlineKeyboardButton("قبول", callback_data=f"accept_ma_{new_admin_id}_{user_id}")
        btn_reject = telebot.types.InlineKeyboardButton("رد", callback_data=f"reject_{user_id}")
        markup.add(btn_accept, btn_reject)
        if is_amin(user_id):
            bot.send_message(OWNER_ID, f"Rank : AmiN Mikhahad Az Dastoor : /ma {new_admin_id} Estefadeh Konad !", reply_markup=markup)
        elif is_professor(user_id):
            bot.send_message(OWNER_ID, f"Rank : Professor Mikhahad Az Dastoor : /ma {new_admin_id} Estefadeh Konad !", reply_markup=markup)
        bot.reply_to(msg, "درخواست شما به سازنده ارسال شد. منتظر تاييد باشيد.")
        return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "لطفا آيدي عددي کاربر را وارد کنيد: /ma 123456789")
        return
    try:
        new_admin_id = int(parts[1])
    except:
        bot.reply_to(msg, "آيدي عددي معتبر نيست")
        return
    if new_admin_id == OWNER_ID:
        bot.reply_to(msg, "کاربر مورد نظر خود سازنده بات است.")
        return
    if str(new_admin_id) in admins:
        bot.reply_to(msg, f"کاربر {new_admin_id} قبلا ادمين است.")
        return
    admins[str(new_admin_id)] = 'admin'
    save_admins()
    admin_num = assign_admin_number(new_admin_id)
    bot.reply_to(msg, f"کاربر با آيدي {new_admin_id} به ليست ادمين ها اضافه شد.\nشماره: {admin_num}")

@bot.message_handler(commands=['kickadmin'])
def kick_admin(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID and not is_amin(user_id) and not is_professor(user_id):
        return
    if user_id != OWNER_ID and (is_amin(user_id) or is_professor(user_id)):
        parts = msg.text.split()
        if len(parts) < 2:
            bot.reply_to(msg, "لطفا آيدي عددي کاربر را وارد کنيد: /kickadmin 123456789")
            return
        try:
            target_id = int(parts[1])
        except:
            bot.reply_to(msg, "آيدي عددي معتبر نيست")
            return
        if target_id == OWNER_ID:
            bot.reply_to(msg, "شما نمي توانيد سازنده را حذف کنيد.")
            return
        if str(target_id) not in admins:
            bot.reply_to(msg, f"کاربر {target_id} ادمين نيست.")
            return
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_accept = telebot.types.InlineKeyboardButton("قبول", callback_data=f"accept_kick_{target_id}_{user_id}")
        btn_reject = telebot.types.InlineKeyboardButton("رد", callback_data=f"reject_{user_id}")
        markup.add(btn_accept, btn_reject)
        if is_amin(user_id):
            bot.send_message(OWNER_ID, f"Rank : AmiN Mikhahad Az Dastoor : /kickadmin {target_id} Estefadeh Konad !", reply_markup=markup)
        elif is_professor(user_id):
            bot.send_message(OWNER_ID, f"Rank : Professor Mikhahad Az Dastoor : /kickadmin {target_id} Estefadeh Konad !", reply_markup=markup)
        bot.reply_to(msg, "درخواست شما به سازنده ارسال شد. منتظر تاييد باشيد.")
        return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "لطفا آيدي عددي کاربر را وارد کنيد: /kickadmin 123456789")
        return
    try:
        target_id = int(parts[1])
    except:
        bot.reply_to(msg, "آيدي عددي معتبر نيست")
        return
    if target_id == OWNER_ID:
        bot.reply_to(msg, "شما نمي توانيد سازنده را حذف کنيد.")
        return
    if str(target_id) not in admins:
        bot.reply_to(msg, f"کاربر {target_id} ادمين نيست.")
        return
    del admins[str(target_id)]
    save_admins()
    bot.reply_to(msg, f"کاربر با آيدي {target_id} از ليست ادمين ها حذف شد.")

@bot.message_handler(commands=['ac'])
def admin_chat_toggle(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    if user_id in admin_chat_mode and admin_chat_mode[user_id]:
        admin_chat_mode[user_id] = False
        bot.reply_to(msg, "شما از حالت چت ادمين خارج شديد.")
    else:
        admin_chat_mode[user_id] = True
        if user_id != OWNER_ID:
            admin_num = get_admin_number(user_id) or "Admin"
            bot.reply_to(msg, f"شما وارد حالت چت ادمين شديد.\nشماره شما: {admin_num}\nبراي خروج دوباره /ac را بزنيد.")
        else:
            bot.reply_to(msg, "شما (OWNER) وارد حالت چت ادمين شديد.\nبراي خروج دوباره /ac را بزنيد.")

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
        bot.reply_to(msg, "هيچ بليط باز نشده اي وجود ندارد.")
        return
    response = "ليست بليط هاي باز نشده:\n\n"
    for ticket_num, data in open_tickets:
        response += f"شماره: {ticket_num}\n"
        response += f"نام: {data['first_name']} (@{data['username']})\n"
        response += f"سوال: {data['question'][:50]}...\n"
        response += f"براي باز کردن: /open {ticket_num}\n\n"
    bot.reply_to(msg, response)

@bot.message_handler(commands=['helpme'])
def helpme(msg):
    user_id = msg.from_user.id
    if user_id != OWNER_ID:
        return
    waiting_for_message[user_id] = True
    bot.reply_to(msg, "/close : شما وارد حالت ارسال پيام شديد لطفا بعد از فرستادن پيام خود براي بستن حالت از اين دستور استفاده کنيد")
    bot.reply_to(msg, "بعد از ارسال پيام خود سازنده بات به پي وي شما پيام ارسال مي کند ولي از وايس استفاده نکنيد و به صورت متن پيام خود را بفرستيد")

@bot.message_handler(commands=['close'])
def close(msg):
    user_id = msg.from_user.id
    if user_id in waiting_for_message:
        waiting_for_message[user_id] = False
        bot.reply_to(msg, "شما از حالت ارسال پيام خارج شديد")
    else:
        bot.reply_to(msg, "درحالت ارسال پيام نيستيد")

@bot.message_handler(commands=['ticket'])
def soal(msg):
    global ticket_counter
    user_id = msg.from_user.id
    if is_admin(user_id):
        bot.reply_to(msg, "شما ادمين هستيد و نمي توانيد تيکت بزنيد")
        return
    text = msg.text
    parts = text.split(maxsplit=1)
    if user_id in user_ticket_status and user_ticket_status[user_id] in tickets:
        bot.reply_to(msg, "شما يک بليط فعال داريد و نمي توانيد بليط جديد بفرستيد")
        return
    if len(parts) < 2:
        bot.reply_to(msg, "لطفا بعد از /ticket پيام خود را بنويسيد")
        bot.reply_to(msg, "مثال : /ticket سوال دارم")
        bot.reply_to(msg, "شما مي توانيد متن پايين را کپي کرده و براي بات ارسال کنيد که اين يک راه ساده تر و سريع تر است")
        bot.reply_to(msg, "/ticket سلام ميشه من رو راهنمايي کنيد ؟")
        return
    soal_text = parts[1]
    user = msg.from_user
    ticket_counter += 1
    ticket_number = ticket_counter
    tickets[ticket_number] = {
        'user_id': user_id,
        'username': user.username or 'بدون يوزرنيم',
        'first_name': user.first_name or 'ناشناس',
        'question': soal_text
    }
    user_ticket_status[user_id] = ticket_number
    save_data()
    bot.send_message(OWNER_ID, f"بليط جديد شماره: {ticket_number}\nنام: {user.first_name} (@{user.username}) [آيدي: {user_id}]\nسوال: {soal_text}\n\nبراي باز کردن: /open {ticket_number}")
    bot.reply_to(msg, "پيام شما ارسال شد")

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
        bot.reply_to(msg, "شماره معتبر نيست")
        return
    if ticket_number not in tickets:
        bot.reply_to(msg, f"بليط {ticket_number} وجود ندارد")
        return
    user_id_ticket = tickets[ticket_number]['user_id']
    chat_sessions[user_id_ticket] = 'open'
    bot.send_message(user_id_ticket, "بليط شما توسط ادمين باز شد. براي چت دستور /chat را بزنيد.")
    bot.reply_to(msg, f"چت با بليط {ticket_number} باز شد")

@bot.message_handler(commands=['chat'])
def chat_with_user(msg):
    user_id = msg.from_user.id
    if is_admin(user_id):
        bot.reply_to(msg, "شما ادمين هستيد و نمي توانيد از اين دستور استفاده کنيد")
        return
    if user_id not in chat_sessions or chat_sessions[user_id] != 'open':
        bot.reply_to(msg, "چت فعالی نداريد")
        return
    waiting_for_message[user_id] = True
    bot.reply_to(msg, "وارد چت شديد. پيام خود را بفرستيد")

@bot.message_handler(commands=['a'])
def admin_chat(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(msg, "/a پيام")
        return
    for user_id_chat, status in chat_sessions.items():
        if status == 'open':
            bot.send_message(user_id_chat, f"پاسخ ادمين:\n{parts[1]}")
            bot.reply_to(msg, f"پيام ارسال شد")
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

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data.startswith('accept_ma_'):
        parts = call.data.split('_')
        new_admin_id = int(parts[2])
        if str(new_admin_id) in admins:
            bot.send_message(OWNER_ID, f"کاربر {new_admin_id} قبلا ادمین است.")
            bot.answer_callback_query(call.id, "قبلا ادمین است")
            return
        admins[str(new_admin_id)] = 'admin'
        save_admins()
        admin_num = assign_admin_number(new_admin_id)
        bot.send_message(OWNER_ID, f"کاربر با آیدی {new_admin_id} به لیست ادمین ها اضافه شد.\nشماره: {admin_num}")
        bot.answer_callback_query(call.id, "تایید شد")
    elif call.data.startswith('accept_kick_'):
        parts = call.data.split('_')
        target_id = int(parts[2])
        if str(target_id) not in admins:
            bot.send_message(OWNER_ID, f"کاربر {target_id} ادمین نیست.")
            bot.answer_callback_query(call.id, "ادمین نیست")
            return
        del admins[str(target_id)]
        save_admins()
        bot.send_message(OWNER_ID, f"کاربر با آیدی {target_id} از لیست ادمین ها حذف شد.")
        bot.answer_callback_query(call.id, "حذف شد")
    elif call.data.startswith('reject_'):
        bot.send_message(OWNER_ID, "درخواست رد شد.")
        bot.answer_callback_query(call.id, "رد شد")

@bot.message_handler(func=lambda m: True)
def forward_all(msg):
    user_id = msg.from_user.id
    user = msg.from_user
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
                user_link = get_user_link(user)
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
