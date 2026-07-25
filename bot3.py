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
    bot.reply_to(msg, "/info : سلام امیدوارم حالتون خوب باشه . لطفا روی این دستور کلیک کنید 🔔")

@bot.message_handler(commands=['info'])
def info(msg):
    bot.reply_to(msg, "/helpme : صحبت با سازنده در پی وی شما ✨")
    bot.reply_to(msg, "/close : خروج از حالت صحبت یا همان بستن حالت دستور بالایی ✨")
    bot.reply_to(msg, "/ticket : ارسال سوال و صحبت درون بات با ادمین ✨")

@bot.message_handler(commands=['tickets'])
def show_tickets(msg):
    if msg.from_user.id != OWNER_ID:
        bot.reply_to(msg, "شما دسترسی ندارید ❌")
        return
    
    # پیدا کردن بلیط‌هایی که هنوز باز نشدن (چت فعال ندارن)
    open_tickets = []
    for ticket_num, ticket_data in tickets.items():
        user_id = ticket_data['user_id']
        # اگر کاربر چت فعال نداره، بلیط باز نشده
        if user_id not in chat_sessions or chat_sessions[user_id] != 'open':
            open_tickets.append((ticket_num, ticket_data))
    
    if not open_tickets:
        bot.reply_to(msg, "📭 هیچ بلیط باز نشده‌ای وجود ندارد.")
        return
    
    # ساخت لیست
    response = "📋 لیست بلیط‌های باز نشده:\n\n"
    for ticket_num, data in open_tickets:
        response += f"🎫 شماره: {ticket_num}\n"
        response += f"👤 نام: {data['first_name']} (@{data['username']})\n"
        response += f"📝 سوال: {data['question'][:50]}...\n"
        response += f"🔓 برای باز کردن: /open {ticket_num}\n\n"
    
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
        bot.reply_to(msg, "❌ شما یک بلیط فعال دارید و نمی توانید بلیط جدید بفرستید ❌")
        return
    
    if len(parts) < 2:
        bot.reply_to(msg, "لطفا بعد از /ticket پیام خود را بنویسید ⚠")
        bot.reply_to(msg, "مثال : /ticket سوال دارم")
        bot.reply_to(msg, "💠 شما می توانید متن پایین را کپی کرده و برای بات ارسال کنید که این یک راه ساده تر و سریع تر است 💠")
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
    
    bot.send_message(OWNER_ID, f":ticket: بلیط جدید شماره: {ticket_number}\n:bust_in_silhouette: نام: {user.first_name} (@{user.username}) [آیدی: {user_id}]\n:memo: سوال: {soal_text}\n\n:unlock: برای باز کردن: /open {ticket_number}")
    bot.reply_to(msg, ":white_check_mark: پیام شما ارسال شد")

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
        bot.reply_to(msg, " شماره معتبر نیست ")
        return
    
    if ticket_number not in tickets:
        bot.reply_to(msg, f"بلیط {ticket_number} وجود ندارد")
        return
    
    user_id = tickets[ticket_number]['user_id']
    chat_sessions[user_id] = 'open'
    
    bot.send_message(user_id, " بلیط شما توسط ادمین باز شد. برای چت دستور /chat را بزنید.")
    bot.reply_to(msg, f"چت با بلیط {ticket_number} باز شد")

@bot.message_handler(commands=['chat'])
def chat_with_user(msg):
    user_id = msg.from_user.id
    if user_id not in chat_sessions or chat_sessions[user_id] != 'open':
        bot.reply_to(msg, " چت فعالی ندارید ")
        return
    waiting_for_message[user_id] = True
    bot.reply_to(msg, " وارد چت شدید. پیام خود را بفرستید ")

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
            bot.send_message(user_id, f"⚜ پاسخ ادمین:\n{parts[1]}")
            bot.reply_to(msg, f" پیام ارسال شد")
            return
    
    bot.reply_to(msg, " چت فعالی وجود ندارد")

@bot.message_handler(commands=['cc'])
def close_chat(msg):
    if msg.from_user.id != OWNER_ID:
        return
    
    for user_id, status in chat_sessions.items():
        if status == 'open':
            chat_sessions[user_id] = 'closed'
            bot.send_message(user_id, " گفتگو پایان یافت ")
            
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            btn_yes = telebot.types.InlineKeyboardButton(" بله", callback_data=f"delete_{user_id}")
            btn_no = telebot.types.InlineKeyboardButton(" خیر", callback_data=f"keep_{user_id}")
            markup.add(btn_yes, btn_no)
            
            bot.send_message(user_id, "آیا از این گفتگو راضی بودید؟", reply_markup=markup)
            bot.reply_to(msg, f" چت پایان یافت")
            
            if user_id in user_ticket_status:
                ticket_num = user_ticket_status[user_id]
                if ticket_num in tickets:
                    del tickets[ticket_num]
                del user_ticket_status[user_id]
                save_data()
            return
    
    bot.reply_to(msg, " چت فعالی وجود ندارد")

@bot.message_handler(func=lambda m: True)
def forward_all(msg):
    user_id = msg.from_user.id
    user = msg.from_user
    
    if user_id in waiting_for_message and waiting_for_message[user_id]:
        if user_id != OWNER_ID and user_id in chat_sessions and chat_sessions[user_id] == 'open':
            bot.send_message(OWNER_ID, f" از کاربر:\n:: نام: {user.first_name} [آیدی: {user.id}]\n:memo: پیام: {msg.text}")
            bot.reply_to(msg, " ارسال شد :")
        else:
            bot.forward_message(OWNER_ID, user.id, msg.message_id)
            bot.send_message(OWNER_ID, f"👤 نام: {user.first_name} (@{user.username}) | آیدی: {user.id}")
            bot.reply_to(msg, "✅ پیام ارسال شد ✅")
            waiting_for_message[user_id] = False
    else:
        bot.reply_to(msg, "💢 ابتدا /helpme را بزنید 💢")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data.startswith('delete_'):
        user_id = int(call.data.split('_')[1])
        bot.send_message(user_id, "❤ با تشکر از شما ❤")
        bot.answer_callback_query(call.id, "❤ آرزوی موفقیت برای شما ❤")
    elif call.data.startswith('keep_'):
        user_id = int(call.data.split('_')[1])
        bot.send_message(user_id, "❤ با تشکر از شما ❤")
        bot.answer_callback_query(call.id, "❤ آرزوی موفقیت برای شما ❤")

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
