import telebot
import time
import threading
from flask import Flask
import json
import os
import requests

TOKEN = "8299446091:AAG3rkzDotNZ4KLObMy_BJ4Lm_sCBs-DHKE"
OWNER_ID = 6703121829

DEEPSEEK_API_KEY = "sk-77b182c88f9841d29fef0dd80bb1e6da"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
waiting_for_message = {}
tickets = {}
ticket_counter = 0
chat_sessions = {}
user_ticket_status = {}
ai_mode = {}

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

def ask_deepseek(question):
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": question}],
            "stream": False
        }
        response = requests.post(DEEPSEEK_URL, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "خطا در ارتباط با هوش مصنوعي. لطفا بعدا تلاش کنيد."
    except Exception as e:
        return f"خطا: {str(e)}"

@bot.message_handler(commands=['ai'])
def ai_command(msg):
    user_id = msg.from_user.id
    if user_id in ai_mode and ai_mode[user_id]:
        ai_mode[user_id] = False
        bot.reply_to(msg, "حالت هوش مصنوعي غيرفعال شد.")
    else:
        ai_mode[user_id] = True
        bot.reply_to(msg, "حالت هوش مصنوعي فعال شد. سوال خود را بپرسيد.")
        bot.reply_to(msg, "براي غيرفعال کردن، دوباره /ai را بزنيد.")

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "/info : سلام اميدوارم حالتون خوب باشه . لطفا روي اين دستور کليک کنيد")
    bot.reply_to(msg, "براي استفاده از هوش مصنوعي، /ai را بزنيد")

@bot.message_handler(commands=['info'])
def info(msg):
    bot.reply_to(msg, "/helpme : صحبت با سازنده در پي وي شما")
    bot.reply_to(msg, "/close : خروج از حالت صحبت يا همان بستن حالت دستور بالايي")
    bot.reply_to(msg, "/ticket : ارسال سوال و صحبت درون بات با ادمين")
    bot.reply_to(msg, "/ai : فعال/غيرفعال کردن هوش مصنوعي")

@bot.message_handler(commands=['helpme'])
def helpme(msg):
    user_id = msg.from_user.id
    waiting_for_message[user_id] = True
    bot.reply_to(msg, "شما وارد حالت ارسال پيام شديد. لطفا پيام خود را بفرستيد.")
    bot.reply_to(msg, "براي خروج از اين حالت، /close را بزنيد.")

@bot.message_handler(commands=['close'])
def close(msg):
    user_id = msg.from_user.id
    if user_id in waiting_for_message:
        waiting_for_message[user_id] = False
        bot.reply_to(msg, "شما از حالت ارسال پيام خارج شديد.")
    else:
        bot.reply_to(msg, "شما در حالت ارسال پيام نيستيد.")

@bot.message_handler(commands=['ticket'])
def soal(msg):
    global ticket_counter
    user_id = msg.from_user.id
    text = msg.text
    parts = text.split(maxsplit=1)
    if user_id in user_ticket_status and user_ticket_status[user_id] in tickets:
        bot.reply_to(msg, "شما يک بليط فعال داريد و نمي توانيد بليط جديد بفرستيد.")
        return
    if len(parts) < 2:
        bot.reply_to(msg, "لطفا بعد از /ticket پيام خود را بنويسيد.")
        bot.reply_to(msg, "مثال: /ticket سلام ميشه من رو راهنمايي کنيد ؟")
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
    bot.send_message(OWNER_ID, f"بليط جديد شماره: {ticket_number}\nنام: {user.first_name} ({user.username}) [آيدي: {user_id}]\nسوال: {soal_text}\n\nبراي باز کردن چت: /open {ticket_number}")
    bot.reply_to(msg, "پيام شما ارسال شد.")

@bot.message_handler(commands=['open'])
def open_chat(msg):
    if msg.from_user.id != OWNER_ID:
        bot.reply_to(msg, "شما دسترسي نداريد.")
        return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "لطفا شماره بليط را وارد کنيد: /open 5")
        return
    try:
        ticket_number = int(parts[1])
    except:
        bot.reply_to(msg, "شماره معتبر نيست.")
        return
    if ticket_number not in tickets:
        bot.reply_to(msg, f"بليط {ticket_number} وجود ندارد.")
        return
    user_id = tickets[ticket_number]['user_id']
    chat_sessions[user_id] = 'open'
    bot.send_message(user_id, "بليط شما توسط ادمين بات قبول شد. براي چت، دستور /chat را بزنيد.")
    bot.reply_to(msg, f"چت با بليط {ticket_number} باز شد.")

@bot.message_handler(commands=['chat'])
def chat_with_user(msg):
    user_id = msg.from_user.id
    if user_id not in chat_sessions or chat_sessions[user_id] != 'open':
        bot.reply_to(msg, "چت فعالی نداريد.")
        return
    waiting_for_message[user_id] = True
    bot.reply_to(msg, "وارد چت شديد. پيام خود را بفرستيد.")

@bot.message_handler(commands=['a'])
def admin_chat(msg):
    if msg.from_user.id != OWNER_ID:
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(msg, "لطفا پيام خود را بعد از /a بنويسيد.")
        return
    for user_id, status in chat_sessions.items():
        if status == 'open':
            bot.send_message(user_id, f"پاسخ ادمين:\n{parts[1]}")
            bot.reply_to(msg, "پيام ارسال شد.")
            return
    bot.reply_to(msg, "چت فعالی وجود ندارد.")

@bot.message_handler(commands=['cc'])
def close_chat(msg):
    if msg.from_user.id != OWNER_ID:
        return
    for user_id, status in chat_sessions.items():
        if status == 'open':
            chat_sessions[user_id] = 'closed'
            bot.send_message(user_id, "گفتگو پایان یافت.")
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            btn_yes = telebot.types.InlineKeyboardButton("بله", callback_data=f"delete_{user_id}")
            btn_no = telebot.types.InlineKeyboardButton("خیر", callback_data=f"keep_{user_id}")
            markup.add(btn_yes, btn_no)
            bot.send_message(user_id, "آیا از این گفتگو راضی بودید؟", reply_markup=markup)
            bot.reply_to(msg, "چت پایان یافت.")
            if user_id in user_ticket_status:
                ticket_num = user_ticket_status[user_id]
                if ticket_num in tickets:
                    del tickets[ticket_num]
                del user_ticket_status[user_id]
                save_data()
            return
    bot.reply_to(msg, "چت فعالی وجود ندارد.")

@bot.message_handler(func=lambda m: True)
def forward_all(msg):
    user_id = msg.from_user.id
    user = msg.from_user
    if user_id in ai_mode and ai_mode[user_id]:
        if not msg.text.startswith('/'):
            bot.reply_to(msg, "در حال پردازش سوال شما با هوش مصنوعي...")
            answer = ask_deepseek(msg.text)
            bot.reply_to(msg, f"پاسخ هوش مصنوعي:\n\n{answer}")
            return
    if user_id in waiting_for_message and waiting_for_message[user_id]:
        if user_id != OWNER_ID and user_id in chat_sessions and chat_sessions[user_id] == 'open':
            bot.send_message(OWNER_ID, f"از کاربر:\nنام: {user.first_name} [آيدي: {user.id}]\nپيام: {msg.text}")
            bot.reply_to(msg, "پيام ارسال شد.")
        else:
            bot.forward_message(OWNER_ID, user.id, msg.message_id)
            bot.send_message(OWNER_ID, f"نام: {user.first_name} ({user.username}) | آيدي: {user.id}")
            bot.reply_to(msg, "پيام ارسال شد.")
            waiting_for_message[user_id] = False
    else:
        if not msg.text.startswith('/'):
            bot.reply_to(msg, "ابتدا /helpme را بزنيد يا براي هوش مصنوعي /ai را فعال کنيد.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data.startswith('delete_'):
        user_id = int(call.data.split('_')[1])
        bot.send_message(user_id, "با تشکر از شما.")
        bot.answer_callback_query(call.id, "با تشکر از شما.")
    elif call.data.startswith('keep_'):
        user_id = int(call.data.split('_')[1])
        bot.send_message(user_id, "با تشکر از شما.")
        bot.answer_callback_query(call.id, "با تشکر از شما.")

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
