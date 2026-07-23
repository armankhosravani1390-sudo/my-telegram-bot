import telebot
import time

TOKEN = "8299446091:AAG3rkzDotNZ4KLObMy_BJ4Lm_sCBs-DHKE"
OWNER_ID = 6703121829

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🧑🏻‍💻 : سلام امیدوارم حالتون خوب باشه 👋🏻🙏🏻 لطفا دستور helpme/ را بزنید 🌠🧭")

@bot.message_handler(commands=['helpme'])
def helpme(msg):
    bot.reply_to(msg, "🧑🏻‍💻 : شما وارد حالت ارسال پیام به TimeLess شدید ! لطفا پیام خود را ارسال کنید و منتظر پاسخ دادن به پیامتون باشید 🙏🏻🌹🌠")

@bot.message_handler(func=lambda m: True)
def forward_all(msg):
    user = msg.from_user
    bot.forward_message(OWNER_ID, user.id, msg.message_id)
    bot.send_message(OWNER_ID, f"👤 {user.first_name} (@{user.username}) | ID: {user.id}")
    bot.reply_to(msg, "🧑🏻‍💻 : پیام شما با موفقیت ارسال شد ✅")

print("✅ Robot is running...")

while True:
    try:
        bot.polling(none_stop=True)
    except:
        print("Error, restarting...")
        time.sleep(3)