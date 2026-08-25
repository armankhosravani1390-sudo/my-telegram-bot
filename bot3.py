import telebot
import time
import threading
from flask import Flask
import json
import os
from datetime import datetime
import random

TOKEN = "8299446091:AAG3rkzDotNZ4KLObMy_BJ4Lm_sCBs-DHKE"
OWNER_ID = 6703121829
FOUNDER_ID = 6703121829
OWNER2_ID = 6328427378
FOUNDER_NAME = "꧁ I R A N ꧂"

REQUIRED_CHANNELS = [
    {"name": "@VoltaRolePlay", "link": "https://t.me/VoltaRolePlay"},
    {"name": "@X4NeZuKO", "link": "https://t.me/X4NeZuKO"}
]

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
banned_users = {}
private_chat_mode = {}
clans = {}
creating_clan = {}
news_data = {}
ad_data = {}
donate_data = []
news_counter = 0
ad_counter = 0
news_mode = {}
ad_mode = {}

games = {}
game_players = {}
game_scores = {}
waiting_games = []
choice_timers = {}
rps_password_temp = {}
rps_join_temp = {}

ttt_games = {}
ttt_game_players = {}
ttt_waiting_games = []
ttt_password_temp = {}
ttt_join_temp = {}
ttt_game_scores = {}

auto_reply_users = {}
auto_reply_timers = {}
auto_reply_enabled = True
broadcast_mode = {}
all_users_data = {}

DATA_FILE = 'data.json'
ADMINS_FILE = 'admins.json'
ADMIN_NUMBERS_FILE = 'admin_numbers.json'
BANNED_FILE = 'banned.json'
NEWS_FILE = 'news.json'
AD_FILE = 'ad.json'
DONATE_FILE = 'donate.json'
CLANS_FILE = 'clans.json'
GAMES_FILE = 'games.json'
TTT_GAMES_FILE = 'ttt_games.json'
USERS_FILE = 'users.json'

def init_roles():
    global admins, admin_numbers
    if not os.path.exists(ADMINS_FILE):
        admins = {"6703121829": "admin", "6328427378": "admin", "8892499079": "admin"}
        save_admins()
    else:
        load_admins()
        if "6703121829" not in admins:
            admins["6703121829"] = "admin"
        if "6328427378" not in admins:
            admins["6328427378"] = "admin"
        if "8892499079" not in admins:
            admins["8892499079"] = "admin"
        save_admins()
    if not os.path.exists(ADMIN_NUMBERS_FILE):
        admin_numbers = {"6703121829": "Founder", "6328427378": "Owner"}
        save_admin_numbers()
    else:
        load_admin_numbers()
        if "6703121829" not in admin_numbers:
            admin_numbers["6703121829"] = "Founder"
        if "6328427378" not in admin_numbers:
            admin_numbers["6328427378"] = "Owner"
        save_admin_numbers()

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

def load_news():
    global news_data, news_counter
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, 'r') as f:
            data = json.load(f)
            news_data = data.get('news', {})
            news_counter = data.get('counter', 0)
    else:
        news_data = {
            "1": "🎨 توی پنل اصلی بات که در قسمت Menu و حتی با زدن دستور : panel/\nشما می توانید از ویژگی های پنل استفاده کنید و حتی می توانید اخبار و حتی تبلیغات را آنجا ارسال کنید و حتی از ما حمایت کنید و اتحاد تشکیل دهید ❗\n🌐 GOD POWER 🌐"
        }
        news_counter = 1

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
        ad_data = {
            "1": "🌿 سرور NightFall با افتخار تقدیم میکند\n\nNightFall Nights 🌔\n\n📍اگه دنبال تجربه خفن از یه سرور خفن هستی همین الان به سرور ما بپیوند 🌏\n\n🏆 تازه ترین و بهینه ترین سرور اِم تی اِی 🏆\n\n⚡𝐒𝐞𝐫𝐯𝐞𝐫 𝐈𝐏 :\nMtaSa://5.42.223.61:22003\n\n      𝐒𝐨𝐜𝐢𝐚𝐥 𝐦𝐞𝐝𝐢𝐚👇\n\n🌐 𝐓𝐞𝐚𝐦𝐒𝐩𝐞𝐚𝐤 : ts63.ir:11439\n((5.57.39.100:11439))\n\n📱 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 : @NightFall_MTA\n\n✈ 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 : @NightFall_MTA\n\n💻 𝐑𝐮𝐛𝐢𝐤𝐚 : @NightFall_RPG\n\n🎥 𝐀𝐩𝐚𝐫𝐚𝐭 : 𝐂𝐨𝐦𝐢𝐧𝐠 𝐒𝐨𝐨𝐧\n\n🛒 𝐒𝐡𝐨𝐩 : 𝐂𝐨𝐦𝐢𝐧𝐠 𝐒𝐨𝐨𝐧\n\n🧑‍💻 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 𝗦𝗲𝗿𝘃𝗲𝗿 : @NightFall_RPG\n\n🧡𝐅𝐨𝐥𝐥𝐨𝐰 𝐔𝐬 ....🧡"
        }
        ad_counter = 1

def save_ad():
    with open(AD_FILE, 'w') as f:
        json.dump({'ads': ad_data, 'counter': ad_counter}, f)

def load_donate():
    global donate_data
    if os.path.exists(DONATE_FILE):
        with open(DONATE_FILE, 'r') as f:
            donate_data = json.load(f)
    else:
        donate_data = [
            {"name": "Tinkerbell", "amount": 6500000, "rank": 1},
            {"name": "Dot", "amount": 3000000, "rank": 2}
        ]

def save_donate():
    with open(DONATE_FILE, 'w') as f:
        json.dump(donate_data, f)

def load_clans():
    global clans
    if os.path.exists(CLANS_FILE):
        with open(CLANS_FILE, 'r') as f:
            clans = json.load(f)
    else:
        clans = {
            "🌐 GOD POWER 🌐": {
                "description": "⭐ سلام دوستان عزیز و کاربرانی که درحال استفاده از این بات هستند خیلی خوشحالیم که شما از بات ما استفاده می کنید و قول میدیم که آپدیت های خیلی جذاب و فان رو به بات اضافه کنیم 🤩🌸\nممنون که تا اینجا با ما همراه بودید 🙏🏻💎",
                "creator": 6703121829
            }
        }

def save_clans():
    with open(CLANS_FILE, 'w') as f:
        json.dump(clans, f)

def load_games():
    global games, game_players, waiting_games
    if os.path.exists(GAMES_FILE):
        with open(GAMES_FILE, 'r') as f:
            data = json.load(f)
            games = data.get('games', {})
            game_players = data.get('game_players', {})
            waiting_games = data.get('waiting_games', [])
    else:
        games = {}
        game_players = {}
        waiting_games = []

def save_games():
    with open(GAMES_FILE, 'w') as f:
        json.dump({'games': games, 'game_players': game_players, 'waiting_games': waiting_games}, f)

def load_ttt_games():
    global ttt_games, ttt_game_players, ttt_waiting_games
    if os.path.exists(TTT_GAMES_FILE):
        with open(TTT_GAMES_FILE, 'r') as f:
            data = json.load(f)
            ttt_games = data.get('ttt_games', {})
            ttt_game_players = data.get('ttt_game_players', {})
            ttt_waiting_games = data.get('ttt_waiting_games', [])
    else:
        ttt_games = {}
        ttt_game_players = {}
        ttt_waiting_games = []

def save_ttt_games():
    with open(TTT_GAMES_FILE, 'w') as f:
        json.dump({'ttt_games': ttt_games, 'ttt_game_players': ttt_game_players, 'ttt_waiting_games': ttt_waiting_games}, f)

def load_users():
    global all_users_data
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            all_users_data = json.load(f)
    else:
        all_users_data = {}

def save_users():
    with open(USERS_FILE, 'w') as f:
        json.dump(all_users_data, f)

load_data()
load_admins()
load_admin_numbers()
load_banned()
load_news()
load_ad()
load_donate()
load_clans()
load_games()
load_ttt_games()
load_users()
init_roles()

def is_founder(user_id):
    return user_id == FOUNDER_ID

def is_owner(user_id):
    return user_id == OWNER2_ID

def is_admin(user_id):
    return user_id == FOUNDER_ID or user_id == OWNER2_ID or str(user_id) in admins

def is_banned(user_id):
    return str(user_id) in banned_users

def get_admin_number(user_id):
    if str(user_id) in admin_numbers:
        return admin_numbers[str(user_id)]
    return assign_admin_number(user_id)

def assign_admin_number(user_id):
    if str(user_id) in admin_numbers:
        return admin_numbers[str(user_id)]
    existing_numbers = []
    for uid, num in admin_numbers.items():
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

def get_winner(choice1, choice2):
    if choice1 == choice2:
        return 'draw'
    if (choice1 == 'سنگ' and choice2 == 'قیچی') or (choice1 == 'کاغذ' and choice2 == 'سنگ') or (choice1 == 'قیچی' and choice2 == 'کاغذ'):
        return 'player1'
    return 'player2'

def create_game(player1_id):
    game_id = str(len(games) + 1)
    games[game_id] = {
        'player1': player1_id,
        'player2': None,
        'password': None,
        'status': 'waiting',
        'round': 0
    }
    game_players[str(player1_id)] = game_id
    waiting_games.append(game_id)
    save_games()
    return game_id

def delete_game(game_id):
    if game_id in games:
        for user_id in [games[game_id]['player1'], games[game_id]['player2']]:
            if user_id and str(user_id) in game_players:
                del game_players[str(user_id)]
        if game_id in waiting_games:
            waiting_games.remove(game_id)
        if game_id in games:
            del games[game_id]
        save_games()
        return True
    return False

def start_rps_game(game_id):
    if game_id not in games:
        return
    player1 = games[game_id]['player1']
    player2 = games[game_id]['player2']
    if not player1 or not player2:
        return
    
    game_scores[str(player1)] = {'score': 0, 'round': 0, 'game_id': game_id, 'choice': None}
    game_scores[str(player2)] = {'score': 0, 'round': 0, 'game_id': game_id, 'choice': None}
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    btn1 = telebot.types.InlineKeyboardButton("🪨 سنگ", callback_data=f"rps_move_{game_id}_سنگ")
    btn2 = telebot.types.InlineKeyboardButton("📄 کاغذ", callback_data=f"rps_move_{game_id}_کاغذ")
    btn3 = telebot.types.InlineKeyboardButton("✂️ قیچی", callback_data=f"rps_move_{game_id}_قیچی")
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(player1, "🎮 بازی سنگ، کاغذ، قیچی شروع شد!\n📌 اولین کسی که 3 امتیاز بگیره برنده است.\n\n🔰 انتخاب خود را بکنید:", reply_markup=markup)
    bot.send_message(player2, "🎮 بازی سنگ، کاغذ، قیچی شروع شد!\n📌 اولین کسی که 3 امتیاز بگیره برنده است.\n\n🔰 انتخاب خود را بکنید:", reply_markup=markup)

def check_rps_round(game_id):
    if game_id not in games:
        return
    player1 = games[game_id]['player1']
    player2 = games[game_id]['player2']
    
    if str(player1) not in game_scores:
        game_scores[str(player1)] = {'score': 0, 'round': 0, 'game_id': game_id, 'choice': None}
    if str(player2) not in game_scores:
        game_scores[str(player2)] = {'score': 0, 'round': 0, 'game_id': game_id, 'choice': None}
    
    if game_scores[str(player1)]['choice'] is not None and game_scores[str(player2)]['choice'] is not None:
        choice1 = game_scores[str(player1)]['choice']
        choice2 = game_scores[str(player2)]['choice']
        
        winner = get_winner(choice1, choice2)
        
        emoji_map = {'سنگ': '🪨', 'کاغذ': '📄', 'قیچی': '✂️'}
        
        if winner == 'player1':
            game_scores[str(player1)]['score'] += 1
            bot.send_message(player1, f"✅ شما این دست را بردید! {emoji_map[choice1]} > {emoji_map[choice2]}")
            bot.send_message(player2, f"❌ حریف این دست را برد! {emoji_map[choice2]} < {emoji_map[choice1]}")
        elif winner == 'player2':
            game_scores[str(player2)]['score'] += 1
            bot.send_message(player2, f"✅ شما این دست را بردید! {emoji_map[choice2]} > {emoji_map[choice1]}")
            bot.send_message(player1, f"❌ حریف این دست را برد! {emoji_map[choice1]} < {emoji_map[choice2]}")
        else:
            bot.send_message(player1, f"🤝 مساوی! هر دو {emoji_map[choice1]} زدید!")
            bot.send_message(player2, f"🤝 مساوی! هر دو {emoji_map[choice2]} زدید!")
        
        game_scores[str(player1)]['choice'] = None
        game_scores[str(player2)]['choice'] = None
        
        score1 = game_scores[str(player1)]['score']
        score2 = game_scores[str(player2)]['score']
        
        if score1 >= 3:
            bot.send_message(player1, f"🏆 شما بازی را بردید! تبریک! 🎉\nامتیاز نهایی: شما {score1} - حریف {score2}")
            bot.send_message(player2, f"😔 شما بازی را باختید! دفعه بعد تلاش کن!\nامتیاز نهایی: شما {score2} - حریف {score1}")
            delete_game(game_id)
            return
        elif score2 >= 3:
            bot.send_message(player2, f"🏆 شما بازی را بردید! تبریک! 🎉\nامتیاز نهایی: شما {score2} - حریف {score1}")
            bot.send_message(player1, f"😔 شما بازی را باختید! دفعه بعد تلاش کن!\nامتیاز نهایی: شما {score1} - حریف {score2}")
            delete_game(game_id)
            return
        
        round_num = game_scores[str(player1)]['round'] + 1
        game_scores[str(player1)]['round'] = round_num
        game_scores[str(player2)]['round'] = round_num
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=3)
        btn1 = telebot.types.InlineKeyboardButton("🪨 سنگ", callback_data=f"rps_move_{game_id}_سنگ")
        btn2 = telebot.types.InlineKeyboardButton("📄 کاغذ", callback_data=f"rps_move_{game_id}_کاغذ")
        btn3 = telebot.types.InlineKeyboardButton("✂️ قیچی", callback_data=f"rps_move_{game_id}_قیچی")
        markup.add(btn1, btn2, btn3)
        
        bot.send_message(player1, f"🎮 دور {round_num} - امتیاز: شما {score1} - حریف {score2}\nانتخاب خود را بکنید:", reply_markup=markup)
        bot.send_message(player2, f"🎮 دور {round_num} - امتیاز: شما {score2} - حریف {score1}\nانتخاب خود را بکنید:", reply_markup=markup)

def create_ttt_game(player1_id):
    game_id = str(len(ttt_games) + 1)
    ttt_games[game_id] = {
        'player1': player1_id,
        'player2': None,
        'password': None,
        'status': 'waiting',
        'board': ['⬜'] * 9,
        'turn': None,
        'player1_symbol': None,
        'player2_symbol': None,
        'winner': None
    }
    ttt_game_players[str(player1_id)] = game_id
    ttt_waiting_games.append(game_id)
    save_ttt_games()
    return game_id

def delete_ttt_game(game_id):
    if game_id in ttt_games:
        for user_id in [ttt_games[game_id]['player1'], ttt_games[game_id]['player2']]:
            if user_id and str(user_id) in ttt_game_players:
                del ttt_game_players[str(user_id)]
        if game_id in ttt_waiting_games:
            ttt_waiting_games.remove(game_id)
        if game_id in ttt_games:
            del ttt_games[game_id]
        save_ttt_games()
        return True
    return False

def check_ttt_winner(board):
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2] and board[i] != '⬜':
            return board[i]
    for i in range(3):
        if board[i] == board[i+3] == board[i+6] and board[i] != '⬜':
            return board[i]
    if board[0] == board[4] == board[8] and board[0] != '⬜':
        return board[0]
    if board[2] == board[4] == board[6] and board[2] != '⬜':
        return board[2]
    if '⬜' not in board:
        return 'draw'
    return None

def get_ttt_board_markup(game_id, user_id):
    board = ttt_games[game_id]['board']
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    
    row1 = []
    for i in range(3):
        btn = telebot.types.InlineKeyboardButton(board[i], callback_data=f"ttt_move_{game_id}_{i}")
        row1.append(btn)
    markup.row(*row1)
    
    row2 = []
    for i in range(3, 6):
        btn = telebot.types.InlineKeyboardButton(board[i], callback_data=f"ttt_move_{game_id}_{i}")
        row2.append(btn)
    markup.row(*row2)
    
    row3 = []
    for i in range(6, 9):
        btn = telebot.types.InlineKeyboardButton(board[i], callback_data=f"ttt_move_{game_id}_{i}")
        row3.append(btn)
    markup.row(*row3)
    
    return markup

def start_ttt_game(game_id):
    if game_id not in ttt_games:
        return
    player1 = ttt_games[game_id]['player1']
    player2 = ttt_games[game_id]['player2']
    if not player1 or not player2:
        return
    
    symbols = ['⭕', '❌']
    random.shuffle(symbols)
    ttt_games[game_id]['player1_symbol'] = symbols[0]
    ttt_games[game_id]['player2_symbol'] = symbols[1]
    ttt_games[game_id]['turn'] = player1
    
    bot.send_message(player1, f"🎮 بازی Tic Tac Toe شروع شد!\nشکل شما: {symbols[0]}\nشکل حریف: {symbols[1]}\n\nشما اول هستید! ⚡")
    bot.send_message(player2, f"🎮 بازی Tic Tac Toe شروع شد!\nشکل شما: {symbols[1]}\nشکل حریف: {symbols[0]}\n\nحریف اول است! ⚡")
    
    markup = get_ttt_board_markup(game_id, player1)
    bot.send_message(player1, "باید یکی از این دکمه‌ها را انتخاب کنید تا انتخاب شما ثبت شود ⚡", reply_markup=markup)
    bot.send_message(player2, "منتظر حرکت حریف باشید... ⏳")

def is_user_in_channels(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel["name"], user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False, channel["name"], channel["link"]
        except:
            return False, channel["name"], channel["link"]
    return True, None, None

def check_and_ask_join(user_id, message=None):
    """چک کردن عضویت و ارسال پیام درخواست عضویت برای همه از جمله Founder و Owner"""
    
    # Founder و Owner هم پیام عضویت رو میبینن ولی نیازی به عضویت ندارن
    is_member, channel_name, channel_link = is_user_in_channels(user_id)
    
    # Founder و Owner همیشه میتونن تایید کنن
    if is_founder(user_id) or is_owner(user_id):
        # پیام عضویت رو نشون بده ولی با دکمه تایید مستقیم
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton("📢 عضویت", url=REQUIRED_CHANNELS[0]["link"])
        btn2 = telebot.types.InlineKeyboardButton("📢 عضویت", url=REQUIRED_CHANNELS[1]["link"])
        btn3 = telebot.types.InlineKeyboardButton("✅ تایید عضویت", callback_data="check_membership_owner")
        markup.add(btn1, btn2, btn3)
        
        bot.send_message(
            user_id,
            f"🔰 لطفاً برای استفاده از بات، در هر دو کانال زیر عضو شوید:\n\n"
            f"📌 کانال ۱: {REQUIRED_CHANNELS[0]['name']}\n"
            f"📌 کانال ۲: {REQUIRED_CHANNELS[1]['name']}\n\n"
            f"✅ بعد از عضویت، روی دکمه «تایید عضویت» کلیک کنید.",
            reply_markup=markup
        )
        return False
    
    if is_member:
        return True
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton("📢 عضویت", url=REQUIRED_CHANNELS[0]["link"])
    btn2 = telebot.types.InlineKeyboardButton("📢 عضویت", url=REQUIRED_CHANNELS[1]["link"])
    btn3 = telebot.types.InlineKeyboardButton("✅ تایید عضویت", callback_data="check_membership")
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(
        user_id,
        f"🔰 لطفاً برای استفاده از بات، در هر دو کانال زیر عضو شوید:\n\n"
        f"📌 کانال ۱: {REQUIRED_CHANNELS[0]['name']}\n"
        f"📌 کانال ۲: {REQUIRED_CHANNELS[1]['name']}\n\n"
        f"✅ بعد از عضویت در هر دو کانال، روی دکمه «تایید عضویت» کلیک کنید.",
        reply_markup=markup
    )
    return False

def send_all_users_list(user_id):
    if not is_founder(user_id) and not is_owner(user_id):
        return
    
    response = "📋 لیست همه کاربران بات:\n\n"
    response += "━━━━━━━━━━━━━━━━━━━━\n"
    
    for admin_id in admins:
        try:
            user_info = bot.get_chat(int(admin_id))
            name = user_info.first_name or user_info.username or "ناشناس"
            username = f"@{user_info.username}" if user_info.username else "بدون یوزرنیم"
            rank = get_admin_number(int(admin_id)) or "Admin"
            response += f"🆔 {admin_id}\n"
            response += f"👤 {name}\n"
            response += f"📌 {username}\n"
            response += f"🏷️ رنک: {rank}\n"
            response += "━━━━━━━━━━━━━━━━━━━━\n"
        except:
            pass
    
    for user_id in all_users_data:
        if str(user_id) not in admins:
            try:
                user_info = bot.get_chat(int(user_id))
                name = user_info.first_name or user_info.username or "ناشناس"
                username = f"@{user_info.username}" if user_info.username else "بدون یوزرنیم"
                response += f"🆔 {user_id}\n"
                response += f"👤 {name}\n"
                response += f"📌 {username}\n"
                response += f"🏷️ رنک: کاربر عادی\n"
                response += "━━━━━━━━━━━━━━━━━━━━\n"
            except:
                pass
    
    if len(response) > 4000:
        parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for part in parts:
            bot.send_message(user_id, part)
    else:
        bot.send_message(user_id, response)

@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    
    if str(user_id) not in all_users_data:
        all_users_data[str(user_id)] = {
            'first_name': msg.from_user.first_name or 'ناشناس',
            'username': msg.from_user.username or 'بدون يوزرنيم',
            'joined_date': str(datetime.now())
        }
        save_users()
    
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    
    # همه کاربران از جمله Founder و Owner باید عضویت رو چک کنن
    if not check_and_ask_join(user_id, msg):
        return
    
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("🏠 پنل اصلی")
    btn2 = telebot.types.KeyboardButton("🎮 بازی ها")
    btn3 = telebot.types.KeyboardButton("🎫 تیکت جدید")
    btn4 = telebot.types.KeyboardButton("🚪 خروج از چت")
    markup.add(btn1, btn2, btn3, btn4)
    
    if is_admin(user_id):
        btn5 = telebot.types.KeyboardButton("⚙️ پنل مدیریت")
        markup.add(btn5)
    
    bot.reply_to(msg, "🔰 سلام! به بات خوش آمدید!\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(commands=['fpanel'])
def founder_panel(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id):
        return
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton("📰 ارسال خبر", callback_data="founder_news")
    btn2 = telebot.types.InlineKeyboardButton("📢 ارسال تبلیغ", callback_data="founder_ad")
    btn3 = telebot.types.InlineKeyboardButton("🗑️ حذف خبر", callback_data="founder_delete_news")
    btn4 = telebot.types.InlineKeyboardButton("🗑️ حذف تبلیغ", callback_data="founder_delete_ad")
    btn5 = telebot.types.InlineKeyboardButton("🤝 مدیریت اتحادها", callback_data="founder_clans")
    btn6 = telebot.types.InlineKeyboardButton("💰 مدیریت حمایت‌ها", callback_data="founder_donate")
    btn7 = telebot.types.InlineKeyboardButton("👑 مدیریت ادمین‌ها", callback_data="founder_admins")
    btn8 = telebot.types.InlineKeyboardButton("⛔ مدیریت محرومیت", callback_data="founder_bans")
    btn9 = telebot.types.InlineKeyboardButton("📊 گزارش بات", callback_data="founder_botup")
    btn10 = telebot.types.InlineKeyboardButton("🔄 آپدیت بات", callback_data="founder_update")
    btn11 = telebot.types.InlineKeyboardButton("📋 دسترسی‌ها", callback_data="founder_perms")
    btn12 = telebot.types.InlineKeyboardButton("📢 ارسال به همه", callback_data="founder_broadcast")
    btn13 = telebot.types.InlineKeyboardButton("📋 لیست همه کاربران", callback_data="founder_all_users")
    btn14 = telebot.types.InlineKeyboardButton("🔙 بازگشت", callback_data="founder_back")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12, btn13, btn14)
    
    bot.reply_to(msg, "👑 پنل مدیریت بنیانگذار:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(commands=['opanel'])
def owner_panel(msg):
    user_id = msg.from_user.id
    if not is_owner(user_id):
        return
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton("📰 ارسال خبر", callback_data="owner_news")
    btn2 = telebot.types.InlineKeyboardButton("📢 ارسال تبلیغ", callback_data="owner_ad")
    btn3 = telebot.types.InlineKeyboardButton("🗑️ حذف خبر", callback_data="owner_delete_news")
    btn4 = telebot.types.InlineKeyboardButton("🗑️ حذف تبلیغ", callback_data="owner_delete_ad")
    btn5 = telebot.types.InlineKeyboardButton("🤝 مدیریت اتحادها", callback_data="owner_clans")
    btn6 = telebot.types.InlineKeyboardButton("💰 مدیریت حمایت‌ها", callback_data="owner_donate")
    btn7 = telebot.types.InlineKeyboardButton("👑 مدیریت ادمین‌ها", callback_data="owner_admins")
    btn8 = telebot.types.InlineKeyboardButton("⛔ مدیریت محرومیت", callback_data="owner_bans")
    btn9 = telebot.types.InlineKeyboardButton("📊 گزارش بات", callback_data="owner_botup")
    btn10 = telebot.types.InlineKeyboardButton("🔄 آپدیت بات", callback_data="owner_update")
    btn11 = telebot.types.InlineKeyboardButton("📋 دسترسی‌ها", callback_data="owner_perms")
    btn12 = telebot.types.InlineKeyboardButton("📢 ارسال به همه", callback_data="owner_broadcast")
    btn13 = telebot.types.InlineKeyboardButton("📋 لیست همه کاربران", callback_data="owner_all_users")
    btn14 = telebot.types.InlineKeyboardButton("🔙 بازگشت", callback_data="owner_back")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12, btn13, btn14)
    
    bot.reply_to(msg, "👑 پنل مدیریت سازنده:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(commands=['apanel'])
def admin_panel(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        bot.reply_to(msg, "⛔ شما دسترسی ادمین ندارید!")
        return
    
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton("🎫 لیست تیکت‌ها", callback_data="admin_tickets")
    btn2 = telebot.types.InlineKeyboardButton("💬 چت ادمین‌ها", callback_data="admin_chat")
    btn3 = telebot.types.InlineKeyboardButton("📋 دستورات ادمین", callback_data="admin_cmds")
    btn4 = telebot.types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.reply_to(msg, "⚙️ پنل مدیریت ادمین:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🏠 پنل اصلی")
def user_panel(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton("📰 اخبار", callback_data="user_news")
    btn2 = telebot.types.InlineKeyboardButton("📢 تبلیغات", callback_data="user_ads")
    btn3 = telebot.types.InlineKeyboardButton("🤝 اتحاد ها", callback_data="user_alliances")
    btn4 = telebot.types.InlineKeyboardButton("📺 کانال ها", callback_data="user_channels")
    btn5 = telebot.types.InlineKeyboardButton("💰 حمایت ها", callback_data="user_donate")
    btn6 = telebot.types.InlineKeyboardButton("👑 تیم مدیریتی", callback_data="user_team")
    btn7 = telebot.types.InlineKeyboardButton("🎮 بازی ها", callback_data="user_games")
    btn8 = telebot.types.InlineKeyboardButton("📋 راهنما", callback_data="user_help")
    btn9 = telebot.types.InlineKeyboardButton("🎫 تیکت جدید", callback_data="user_new_ticket")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
    bot.reply_to(msg, "🏠 پنل اصلی کاربران:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎮 بازی ها")
def games_menu(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn1 = telebot.types.InlineKeyboardButton("🪨 سنگ، کاغذ، قیچی 🪨", callback_data="game_rps")
    btn2 = telebot.types.InlineKeyboardButton("❌⭕ Tic Tac Toe", callback_data="game_ttt")
    btn3 = telebot.types.InlineKeyboardButton("🎲 بازی ۳", callback_data="game_coming_soon")
    btn4 = telebot.types.InlineKeyboardButton("🏆 بازی ۴", callback_data="game_coming_soon")
    markup.add(btn1, btn2, btn3, btn4)
    bot.reply_to(msg, "🎮 لیست بازی‌ها:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🎫 تیکت جدید")
def new_ticket(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    
    if is_admin(user_id):
        bot.reply_to(msg, "⛔ شما ادمین هستید و نمی توانید تیکت بزنید")
        return
    
    bot.reply_to(msg, "📝 لطفاً سوال یا مشکل خود را به صورت متن ارسال کنید تا تیکت شما ثبت شود.")
    waiting_for_message[user_id] = 'ticket'

@bot.message_handler(func=lambda m: m.text == "🚪 خروج از چت")
def close_chat(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    if user_id in waiting_for_message:
        waiting_for_message[user_id] = False
        bot.reply_to(msg, "❌ شما از حالت ارسال پيام خارج شديد")
    else:
        bot.reply_to(msg, "✅ شما در حالت ارسال پيام نيستيد")

@bot.message_handler(func=lambda m: m.text == "⚙️ پنل مدیریت")
def admin_panel_button(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    if not is_admin(user_id):
        return
    admin_panel(msg)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    
    # ========== چک کردن عضویت برای کاربر عادی ==========
    if call.data == "check_membership":
        if is_founder(user_id) or is_owner(user_id):
            bot.answer_callback_query(call.id, "✅ شما دسترسی کامل دارید!")
            return
        
        is_member, channel_name, channel_link = is_user_in_channels(user_id)
        if is_member:
            bot.send_message(user_id, "✅ عضویت شما در هر دو کانال تایید شد! حالا می‌توانید از بات استفاده کنید.")
            bot.answer_callback_query(call.id, "✅ عضویت تایید شد")
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ شما هنوز در یکی از کانال‌ها عضو نشده‌اید!")
            bot.send_message(
                user_id,
                f"❌ شما هنوز در کانال {channel_name} عضو نشده‌اید!\n"
                f"لطفاً ابتدا عضو شوید و سپس روی دکمه تایید کلیک کنید."
            )
        return
    
    # ========== چک کردن عضویت برای Founder و Owner ==========
    if call.data == "check_membership_owner":
        if not is_founder(user_id) and not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ شما دسترسی ندارید!")
            return
        
        # Founder و Owner نیازی به عضویت ندارن، مستقیم تایید میشن
        bot.send_message(user_id, "✅ دسترسی شما تایید شد! خوش آمدید.")
        bot.answer_callback_query(call.id, "✅ تایید شد")
        start(call.message)
        return
    
    # ========== Founder Panel ==========
    if call.data == "founder_news":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        news_command(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_ad":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        ad_command(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_delete_news":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        hazfnews(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_delete_ad":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        hazfad(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_clans":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton("➕ ساخت اتحاد", callback_data="founder_create_clan")
        btn2 = telebot.types.InlineKeyboardButton("🗑️ حذف اتحاد", callback_data="founder_delete_clan")
        btn3 = telebot.types.InlineKeyboardButton("📋 لیست اتحادها", callback_data="founder_list_clans")
        btn4 = telebot.types.InlineKeyboardButton("🔙 بازگشت", callback_data="founder_back")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(user_id, "🤝 مدیریت اتحادها:", reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_create_clan":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        bot.send_message(user_id, "📝 لطفاً نام اتحاد را وارد کنید:\n/createclan [نام اتحاد]")
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_delete_clan":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        if not clans:
            bot.send_message(user_id, "🤝 هیچ اتحادی برای حذف وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        response = "🤝 لیست اتحادها:\n\n"
        for clan_name in clans.keys():
            response += f"📌 {clan_name}\n"
        response += "\n📌 برای حذف: /deleteclan [نام اتحاد]"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_list_clans":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        if not clans:
            bot.send_message(user_id, "🤝 هیچ اتحادی وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        response = "🤝 لیست اتحادها:\n\n"
        for clan_name, clan_data in clans.items():
            response += f"📌 {clan_name}\n"
            response += f"📋 {clan_data['description'][:100]}...\n"
            response += f"👑 سازنده: {clan_data['creator']}\n\n"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_donate":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        if donate_data:
            response = "💰 لیست حمایت‌ها:\n\n"
            for item in donate_data:
                response += f"🏅 {item['rank']} : {item['name']}\n💵 مبلغ : {item['amount']} T\n\n"
            bot.send_message(user_id, response)
        else:
            bot.send_message(user_id, "💰 هیچ حمایتی ثبت نشده است.")
        bot.send_message(user_id, "📌 برای اضافه کردن: /donate [نام] [مبلغ]\n📌 برای حذف: /removedonate [نام]")
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_admins":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        response = "📋 ليست ادمين ها:\n\n"
        response += "👑 بنیانگذار: Founder\n"
        response += "👑 سازنده: Owner\n"
        if admins:
            for admin_id in admins:
                if int(admin_id) != FOUNDER_ID and int(admin_id) != OWNER2_ID:
                    admin_num = get_admin_number(int(admin_id)) or "بدون شماره"
                    try:
                        user_info = bot.get_chat(admin_id)
                        name = user_info.first_name or user_info.username or "ناشناس"
                        response += f"{admin_num} : {name}\n"
                    except:
                        response += f"{admin_num}: {admin_id}\n"
        else:
            response += "❌ هيچ ادمين ديگري وجود ندارد."
        bot.send_message(user_id, response)
        bot.send_message(user_id, "📌 برای اضافه کردن: /ma [ایدی]\n📌 برای حذف: /kickadmin [ایدی]")
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_bans":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        if banned_users:
            response = "⛔ لیست کاربران محروم:\n\n"
            for banned_id in banned_users:
                response += f"🆔 {banned_id}\n"
            bot.send_message(user_id, response)
        else:
            bot.send_message(user_id, "✅ هیچ کاربری محروم نیست.")
        bot.send_message(user_id, "📌 برای محروم کردن: /ban [ایدی]\n📌 برای رفع محرومیت: /unban [ایدی]")
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_botup":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        botup(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_update":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        update_bot(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_perms":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        show_perms(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_broadcast":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        broadcast_mode[user_id] = True
        bot.send_message(user_id, "📢 وارد حالت ارسال پیام به همه شدید!\n\n📝 هر پیامی که بفرستید، برای همه کاربران ارسال خواهد شد.\n❌ برای خروج، دستور /cancelbroadcast را بزنید.")
        bot.answer_callback_query(call.id, "✅ وارد حالت ارسال شدید")
    
    elif call.data == "founder_all_users":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        send_all_users_list(user_id)
        bot.answer_callback_query(call.id)
    
    elif call.data == "founder_back":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        founder_panel(call.message)
        bot.answer_callback_query(call.id)
    
    # ========== Owner Panel ==========
    elif call.data == "owner_news":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        news_command(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_ad":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        ad_command(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_delete_news":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        hazfnews(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_delete_ad":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        hazfad(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_clans":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton("➕ ساخت اتحاد", callback_data="owner_create_clan")
        btn2 = telebot.types.InlineKeyboardButton("🗑️ حذف اتحاد", callback_data="owner_delete_clan")
        btn3 = telebot.types.InlineKeyboardButton("📋 لیست اتحادها", callback_data="owner_list_clans")
        btn4 = telebot.types.InlineKeyboardButton("🔙 بازگشت", callback_data="owner_back")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(user_id, "🤝 مدیریت اتحادها:", reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_create_clan":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        bot.send_message(user_id, "📝 لطفاً نام اتحاد را وارد کنید:\n/createclan [نام اتحاد]")
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_delete_clan":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        if not clans:
            bot.send_message(user_id, "🤝 هیچ اتحادی برای حذف وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        response = "🤝 لیست اتحادها:\n\n"
        for clan_name in clans.keys():
            response += f"📌 {clan_name}\n"
        response += "\n📌 برای حذف: /deleteclan [نام اتحاد]"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_list_clans":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        if not clans:
            bot.send_message(user_id, "🤝 هیچ اتحادی وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        response = "🤝 لیست اتحادها:\n\n"
        for clan_name, clan_data in clans.items():
            response += f"📌 {clan_name}\n"
            response += f"📋 {clan_data['description'][:100]}...\n"
            response += f"👑 سازنده: {clan_data['creator']}\n\n"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_donate":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        if donate_data:
            response = "💰 لیست حمایت‌ها:\n\n"
            for item in donate_data:
                response += f"🏅 {item['rank']} : {item['name']}\n💵 مبلغ : {item['amount']} T\n\n"
            bot.send_message(user_id, response)
        else:
            bot.send_message(user_id, "💰 هیچ حمایتی ثبت نشده است.")
        bot.send_message(user_id, "📌 برای اضافه کردن: /donate [نام] [مبلغ]\n📌 برای حذف: /removedonate [نام]")
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_admins":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        response = "📋 ليست ادمين ها:\n\n"
        response += "👑 بنیانگذار: Founder\n"
        response += "👑 سازنده: Owner\n"
        if admins:
            for admin_id in admins:
                if int(admin_id) != FOUNDER_ID and int(admin_id) != OWNER2_ID:
                    admin_num = get_admin_number(int(admin_id)) or "بدون شماره"
                    try:
                        user_info = bot.get_chat(admin_id)
                        name = user_info.first_name or user_info.username or "ناشناس"
                        response += f"{admin_num} : {name}\n"
                    except:
                        response += f"{admin_num}: {admin_id}\n"
        else:
            response += "❌ هيچ ادمين ديگري وجود ندارد."
        bot.send_message(user_id, response)
        bot.send_message(user_id, "📌 برای اضافه کردن: /ma [ایدی]\n📌 برای حذف: /kickadmin [ایدی]")
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_bans":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        if banned_users:
            response = "⛔ لیست کاربران محروم:\n\n"
            for banned_id in banned_users:
                response += f"🆔 {banned_id}\n"
            bot.send_message(user_id, response)
        else:
            bot.send_message(user_id, "✅ هیچ کاربری محروم نیست.")
        bot.send_message(user_id, "📌 برای محروم کردن: /ban [ایدی]\n📌 برای رفع محرومیت: /unban [ایدی]")
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_botup":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        botup(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_update":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        update_bot(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_perms":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        show_perms(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_broadcast":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        broadcast_mode[user_id] = True
        bot.send_message(user_id, "📢 وارد حالت ارسال پیام به همه شدید!\n\n📝 هر پیامی که بفرستید، برای همه کاربران ارسال خواهد شد.\n❌ برای خروج، دستور /cancelbroadcast را بزنید.")
        bot.answer_callback_query(call.id, "✅ وارد حالت ارسال شدید")
    
    elif call.data == "owner_all_users":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        send_all_users_list(user_id)
        bot.answer_callback_query(call.id)
    
    elif call.data == "owner_back":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        owner_panel(call.message)
        bot.answer_callback_query(call.id)
    
    # ========== Admin Panel ==========
    elif call.data == "admin_tickets":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما ادمین نیستید!")
            return
        show_tickets(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "admin_chat":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما ادمین نیستید!")
            return
        admin_chat_toggle(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "admin_cmds":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما ادمین نیستید!")
            return
        cmds(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "admin_back":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما ادمین نیستید!")
            return
        admin_panel(call.message)
        bot.answer_callback_query(call.id)
    
    # ========== User Panel ==========
    elif call.data == "user_news":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if news_data:
            response = "📰 لیست اخبار:\n\n"
            for news_id, news_text in news_data.items():
                response += f"🔹 News : {news_id}\n{news_text}\n\n"
            bot.send_message(user_id, response)
        else:
            bot.send_message(user_id, "📭 هیچ خبری وجود ندارد.")
        bot.answer_callback_query(call.id)
    
    elif call.data == "user_ads":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if ad_data:
            response = "📢 لیست تبلیغات:\n\n"
            for ad_id, ad_text in ad_data.items():
                response += f"🔸 Ad : {ad_id}\n{ad_text}\n\n"
            bot.send_message(user_id, response)
        else:
            bot.send_message(user_id, "📭 هیچ تبلیغی وجود ندارد.")
        bot.answer_callback_query(call.id)
    
    elif call.data == "user_alliances":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if not clans:
            bot.send_message(user_id, "🤝 هیچ اتحادی وجود ندارد.")
        else:
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            for clan_name in clans.keys():
                btn = telebot.types.InlineKeyboardButton(clan_name, callback_data=f"clan_{clan_name}")
                markup.add(btn)
            bot.send_message(user_id, "🤝 لیست اتحادها:", reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data.startswith("clan_"):
        clan_name = call.data.replace("clan_", "")
        if clan_name in clans:
            bot.send_message(user_id, f"📋 توضیحات اتحاد «{clan_name}»:\n\n{clans[clan_name]['description']}")
        else:
            bot.send_message(user_id, "❌ این اتحاد وجود ندارد.")
        bot.answer_callback_query(call.id)
    
    elif call.data == "user_channels":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        bot.send_message(user_id, "📺 کانال‌های ما:\n\n📌 @VoltaRolePlay\n📌 @X4NeZuKO")
        bot.answer_callback_query(call.id)
    
    elif call.data == "user_donate":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if donate_data:
            response = "💰 لیست حمایت‌ها:\n\n"
            for item in donate_data:
                response += f"🏅 {item['rank']} : {item['name']}\n💵 مبلغ : {item['amount']} T\n\n"
            bot.send_message(user_id, response)
        else:
            bot.send_message(user_id, "💰 هیچ حمایتی ثبت نشده است.")
        bot.answer_callback_query(call.id)
    
    elif call.data == "user_team":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        response = "👑 تیم مدیریتی:\n\n"
        response += "👑 بنیانگذار: Founder\n"
        response += "👑 سازنده: Owner\n"
        if admins:
            for admin_id in admins:
                if int(admin_id) != FOUNDER_ID and int(admin_id) != OWNER2_ID:
                    admin_num = get_admin_number(int(admin_id)) or "بدون شماره"
                    try:
                        user_info = bot.get_chat(admin_id)
                        name = user_info.first_name or user_info.username or "ناشناس"
                        response += f"{admin_num} : {name}\n"
                    except:
                        response += f"{admin_num} : ناشناس\n"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
    
    elif call.data == "user_games":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        games_menu(call.message)
        bot.answer_callback_query(call.id)
    
    elif call.data == "user_help":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        response = "📋 راهنمای کاربران:\n\n"
        response += "🏠 پنل اصلی: مشاهده همه امکانات\n"
        response += "🎮 بازی ها: بازی سنگ، کاغذ، قیچی و Tic Tac Toe\n"
        response += "🎫 تیکت جدید: ثبت سوال یا مشکل\n"
        response += "🚪 خروج از چت: خروج از حالت مکالمه\n"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
    
    elif call.data == "user_new_ticket":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if is_admin(user_id):
            bot.send_message(user_id, "⛔ شما ادمین هستید و نمی توانید تیکت بزنید")
            bot.answer_callback_query(call.id)
            return
        bot.send_message(user_id, "📝 لطفاً سوال یا مشکل خود را به صورت متن ارسال کنید تا تیکت شما ثبت شود.")
        waiting_for_message[user_id] = 'ticket'
        bot.answer_callback_query(call.id, "✅ لطفاً پیام خود را بفرستید")
    
    # ========== Game Callbacks ==========
    elif call.data == "game_rps":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if str(user_id) in game_players:
            bot.send_message(user_id, "❌ شما در حال حاضر در یک بازی هستید.")
            bot.answer_callback_query(call.id)
            return
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton("🪨 ساخت اتاق", callback_data="create_room_menu")
        btn2 = telebot.types.InlineKeyboardButton("🚪 لیست اتاق‌ها", callback_data="show_rooms_menu")
        btn3 = telebot.types.InlineKeyboardButton("🚪 خروج از اتاق", callback_data="leave_room_callback")
        btn4 = telebot.types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_games")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(user_id, "🎮 بازی سنگ، کاغذ، قیچی\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data == "game_ttt":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if str(user_id) in ttt_game_players:
            bot.send_message(user_id, "❌ شما در حال حاضر در یک بازی هستید.")
            bot.answer_callback_query(call.id)
            return
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton("🪨 ساخت اتاق", callback_data="ttt_create_room_menu")
        btn2 = telebot.types.InlineKeyboardButton("🚪 لیست اتاق‌ها", callback_data="ttt_show_rooms")
        btn3 = telebot.types.InlineKeyboardButton("🚪 خروج از اتاق", callback_data="ttt_leave_room")
        btn4 = telebot.types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_games")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(user_id, "🎮 بازی Tic Tac Toe\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data == "game_coming_soon":
        bot.answer_callback_query(call.id, "⏳ Coming Soon ...")
        bot.send_message(user_id, "⏳ این بازی به زودی اضافه خواهد شد!")
    
    elif call.data == "back_to_games":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        games_menu(call.message)
        bot.answer_callback_query(call.id)
    
    # ========== RPS Room ==========
    elif call.data == "create_room_menu":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if str(user_id) in game_players:
            bot.send_message(user_id, "❌ شما در حال حاضر در یک بازی هستید.")
            bot.answer_callback_query(call.id)
            return
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton("✅ بله", callback_data="create_room_with_pass")
        btn2 = telebot.types.InlineKeyboardButton("❌ خیر", callback_data="create_room_no_pass")
        markup.add(btn1, btn2)
        bot.send_message(user_id, "🔐 آیا می‌خواهید برای اتاق خود رمز بگذارید؟", reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data == "create_room_no_pass":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if str(user_id) in game_players:
            bot.answer_callback_query(call.id, "❌ شما در حال حاضر در یک بازی هستید")
            return
        game_id = create_game(user_id)
        bot.send_message(user_id, f"✅ اتاق سنگ ، کاغذ ، قیچی شما ساخته شد !\n🆔 ایدی اتاق : {game_id}\n🔄 منتظر حریف باشید...")
        bot.answer_callback_query(call.id, "✅ اتاق ساخته شد")
    
    elif call.data == "create_room_with_pass":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if str(user_id) in game_players:
            bot.answer_callback_query(call.id, "❌ شما در حال حاضر در یک بازی هستید")
            return
        rps_password_temp[user_id] = {'game_id': None, 'step': 'waiting_password'}
        bot.send_message(user_id, "🔑 لطفاً رمز مورد نظر خود را وارد کنید:")
        bot.answer_callback_query(call.id, "🔑 لطفاً رمز را وارد کنید")
    
    elif call.data == "show_rooms_menu":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if not waiting_games:
            bot.send_message(user_id, "❌ هیچ اتاق خالی برای ملحق شدن وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        found = False
        for game_id in waiting_games:
            if game_id in games and games[game_id]['player1'] != user_id:
                found = True
                btn_text = f"🆔 اتاق {game_id}"
                if games[game_id]['password']:
                    btn_text += " 🔑"
                btn = telebot.types.InlineKeyboardButton(btn_text, callback_data=f"join_room_{game_id}")
                markup.add(btn)
        
        if not found:
            bot.send_message(user_id, "❌ هیچ اتاق خالی برای ملحق شدن وجود ندارد.")
        else:
            btn_back = telebot.types.InlineKeyboardButton("🔙 بازگشت", callback_data="game_rps")
            markup.add(btn_back)
            bot.send_message(user_id, "🚪 لیست اتاق‌های خالی:\n\nلطفاً روی اتاق مورد نظر کلیک کنید:", reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data.startswith("join_room_"):
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        game_id = call.data.replace("join_room_", "")
        if game_id not in games:
            bot.send_message(user_id, "❌ این اتاق وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        if games[game_id]['player2'] is not None:
            bot.send_message(user_id, "❌ این اتاق پر است.")
            bot.answer_callback_query(call.id)
            return
        if games[game_id]['player1'] == user_id:
            bot.send_message(user_id, "❌ شما نمی‌توانید به اتاق خودتان ملحق شوید!")
            bot.answer_callback_query(call.id)
            return
        
        if games[game_id]['password']:
            rps_join_temp[user_id] = {'game_id': game_id, 'step': 'waiting_password'}
            bot.send_message(user_id, f"🔑 این اتاق دارای رمز است.\nلطفاً رمز را وارد کنید:")
            bot.answer_callback_query(call.id, "🔑 لطفاً رمز را وارد کنید")
            return
        
        games[game_id]['player2'] = user_id
        games[game_id]['status'] = 'playing'
        game_players[str(user_id)] = game_id
        if game_id in waiting_games:
            waiting_games.remove(game_id)
        save_games()
        bot.send_message(user_id, f"✅ شما به اتاق {game_id} ملحق شدید!")
        bot.send_message(games[game_id]['player1'], f"✅ حریف شما به اتاق {game_id} ملحق شد!")
        start_rps_game(game_id)
        bot.answer_callback_query(call.id, "✅ وارد شدید")
    
    elif call.data == "leave_room_callback":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        
        if str(user_id) not in game_players:
            bot.send_message(user_id, "❌ شما در هیچ اتاق سنگ کاغذ قیچی نیستید!")
            bot.answer_callback_query(call.id)
            return
        
        game_id = game_players[str(user_id)]
        if game_id not in games:
            bot.send_message(user_id, "❌ اتاق شما وجود ندارد!")
            bot.answer_callback_query(call.id)
            return
        
        game_data = games[game_id]
        player1 = game_data['player1']
        player2 = game_data['player2']
        opponent_id = player2 if player1 == user_id else player1
        
        delete_game(game_id)
        bot.send_message(user_id, "✅ شما با موفقیت از اتاق سنگ کاغذ قیچی خارج شدید!")
        if opponent_id:
            try:
                bot.send_message(opponent_id, f"❌ حریف شما از اتاق خارج شد!\nشما نیز از بازی خارج شدید.")
            except:
                pass
        if str(user_id) in game_scores:
            del game_scores[str(user_id)]
        if opponent_id and str(opponent_id) in game_scores:
            del game_scores[str(opponent_id)]
        bot.answer_callback_query(call.id, "✅ خارج شدید")
    
    # ========== TTT Room ==========
    elif call.data == "ttt_create_room_menu":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if str(user_id) in ttt_game_players:
            bot.send_message(user_id, "❌ شما در حال حاضر در یک بازی هستید.")
            bot.answer_callback_query(call.id)
            return
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton("✅ بله", callback_data="ttt_create_room_with_pass")
        btn2 = telebot.types.InlineKeyboardButton("❌ خیر", callback_data="ttt_create_room_no_pass")
        markup.add(btn1, btn2)
        bot.send_message(user_id, "🔐 آیا می‌خواهید برای اتاق خود رمز بگذارید؟", reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data == "ttt_create_room_no_pass":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if str(user_id) in ttt_game_players:
            bot.answer_callback_query(call.id, "❌ شما در حال حاضر در یک بازی هستید")
            return
        game_id = create_ttt_game(user_id)
        bot.send_message(user_id, f"✅ اتاق Tic Tac Toe شما ساخته شد !\n🆔 ایدی اتاق : {game_id}\n🔄 منتظر حریف باشید...")
        bot.answer_callback_query(call.id, "✅ اتاق ساخته شد")
    
    elif call.data == "ttt_create_room_with_pass":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if str(user_id) in ttt_game_players:
            bot.answer_callback_query(call.id, "❌ شما در حال حاضر در یک بازی هستید")
            return
        ttt_password_temp[user_id] = {'game_id': None, 'step': 'waiting_password'}
        bot.send_message(user_id, "🔑 لطفاً رمز مورد نظر خود را وارد کنید:")
        bot.answer_callback_query(call.id, "🔑 لطفاً رمز را وارد کنید")
    
    elif call.data == "ttt_show_rooms":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if not ttt_waiting_games:
            bot.send_message(user_id, "❌ هیچ اتاق خالی برای ملحق شدن وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        found = False
        for game_id in ttt_waiting_games:
            if game_id in ttt_games and ttt_games[game_id]['player1'] != user_id:
                found = True
                btn_text = f"🆔 اتاق {game_id}"
                if ttt_games[game_id]['password']:
                    btn_text += " 🔑"
                btn = telebot.types.InlineKeyboardButton(btn_text, callback_data=f"ttt_join_room_{game_id}")
                markup.add(btn)
        
        if not found:
            bot.send_message(user_id, "❌ هیچ اتاق خالی برای ملحق شدن وجود ندارد.")
        else:
            btn_back = telebot.types.InlineKeyboardButton("🔙 بازگشت", callback_data="game_ttt")
            markup.add(btn_back)
            bot.send_message(user_id, "🚪 لیست اتاق‌های خالی Tic Tac Toe:\n\nلطفاً روی اتاق مورد نظر کلیک کنید:", reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data.startswith("ttt_join_room_"):
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        game_id = call.data.replace("ttt_join_room_", "")
        if game_id not in ttt_games:
            bot.send_message(user_id, "❌ این اتاق وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        if ttt_games[game_id]['player2'] is not None:
            bot.send_message(user_id, "❌ این اتاق پر است.")
            bot.answer_callback_query(call.id)
            return
        if ttt_games[game_id]['player1'] == user_id:
            bot.send_message(user_id, "❌ شما نمی‌توانید به اتاق خودتان ملحق شوید!")
            bot.answer_callback_query(call.id)
            return
        
        if ttt_games[game_id]['password']:
            ttt_join_temp[user_id] = {'game_id': game_id, 'step': 'waiting_password'}
            bot.send_message(user_id, f"🔑 این اتاق دارای رمز است.\nلطفاً رمز را وارد کنید:")
            bot.answer_callback_query(call.id, "🔑 لطفاً رمز را وارد کنید")
            return
        
        ttt_games[game_id]['player2'] = user_id
        ttt_games[game_id]['status'] = 'playing'
        ttt_game_players[str(user_id)] = game_id
        if game_id in ttt_waiting_games:
            ttt_waiting_games.remove(game_id)
        save_ttt_games()
        bot.send_message(user_id, f"✅ شما به اتاق {game_id} ملحق شدید!")
        bot.send_message(ttt_games[game_id]['player1'], f"✅ حریف شما به اتاق {game_id} ملحق شد!")
        start_ttt_game(game_id)
        bot.answer_callback_query(call.id, "✅ وارد شدید")
    
    elif call.data == "ttt_leave_room":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        
        if str(user_id) not in ttt_game_players:
            bot.send_message(user_id, "❌ شما در هیچ اتاق Tic Tac Toe نیستید!")
            bot.answer_callback_query(call.id)
            return
        
        game_id = ttt_game_players[str(user_id)]
        if game_id not in ttt_games:
            bot.send_message(user_id, "❌ اتاق شما وجود ندارد!")
            bot.answer_callback_query(call.id)
            return
        
        game_data = ttt_games[game_id]
        player1 = game_data['player1']
        player2 = game_data['player2']
        opponent_id = player2 if player1 == user_id else player1
        
        delete_ttt_game(game_id)
        bot.send_message(user_id, "✅ شما با موفقیت از اتاق Tic Tac Toe خارج شدید!")
        if opponent_id:
            try:
                bot.send_message(opponent_id, f"❌ حریف شما از اتاق خارج شد!\nشما نیز از بازی خارج شدید.")
            except:
                pass
        bot.answer_callback_query(call.id, "✅ خارج شدید")
    
    elif call.data.startswith("ttt_move_"):
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        
        parts = call.data.split("_")
        game_id = parts[2]
        position = int(parts[3])
        
        if game_id not in ttt_games:
            bot.answer_callback_query(call.id, "❌ بازی وجود ندارد")
            return
        
        game = ttt_games[game_id]
        if game['winner'] is not None:
            bot.answer_callback_query(call.id, "❌ این بازی تمام شده است!")
            return
        
        if game['turn'] != user_id:
            bot.answer_callback_query(call.id, "❌ نوبت شما نیست!")
            return
        
        if game['board'][position] != '⬜':
            bot.answer_callback_query(call.id, "❌ این خانه قبلاً پر شده است!")
            return
        
        if user_id == game['player1']:
            symbol = game['player1_symbol']
        else:
            symbol = game['player2_symbol']
        
        game['board'][position] = symbol
        
        winner = check_ttt_winner(game['board'])
        
        if winner == 'draw':
            game['winner'] = 'draw'
            bot.send_message(game['player1'], "🤝 بازی مساوی شد!")
            bot.send_message(game['player2'], "🤝 بازی مساوی شد!")
            delete_ttt_game(game_id)
            bot.answer_callback_query(call.id, "🤝 مساوی")
            return
        
        if winner is not None:
            game['winner'] = winner
            if winner == game['player1_symbol']:
                bot.send_message(game['player1'], "🏆 شما برنده شدید! تبریک! 🎉")
                bot.send_message(game['player2'], f"😔 شما باختید! برنده: {game['player1_symbol']}")
            else:
                bot.send_message(game['player2'], "🏆 شما برنده شدید! تبریک! 🎉")
                bot.send_message(game['player1'], f"😔 شما باختید! برنده: {game['player2_symbol']}")
            delete_ttt_game(game_id)
            bot.answer_callback_query(call.id, "🏆 بازی تمام شد")
            return
        
        if game['turn'] == game['player1']:
            game['turn'] = game['player2']
        else:
            game['turn'] = game['player1']
        
        save_ttt_games()
        
        markup = get_ttt_board_markup(game_id, game['turn'])
        bot.send_message(game['turn'], "نوبت شماست! ⚡", reply_markup=markup)
        opponent = game['player1'] if game['turn'] == game['player2'] else game['player2']
        bot.send_message(opponent, "منتظر حرکت حریف باشید... ⏳")
        bot.answer_callback_query(call.id, "✅ حرکت ثبت شد")
    
    elif call.data.startswith("rps_move_"):
        parts = call.data.split("_")
        game_id = parts[2]
        choice = parts[3]
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if game_id not in games:
            bot.answer_callback_query(call.id, "❌ بازی وجود ندارد")
            return
        if user_id not in [games[game_id]['player1'], games[game_id]['player2']]:
            bot.answer_callback_query(call.id, "❌ شما در این بازی نیستید")
            return
        
        if str(user_id) not in game_scores:
            game_scores[str(user_id)] = {'score': 0, 'round': 0, 'game_id': game_id, 'choice': None}
        game_scores[str(user_id)]['choice'] = choice
        bot.answer_callback_query(call.id, f"✅ انتخاب شما ثبت شد: {choice}")
        
        check_rps_round(game_id)

@bot.message_handler(commands=['cancelbroadcast'])
def cancel_broadcast(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    
    if user_id in broadcast_mode:
        del broadcast_mode[user_id]
        bot.reply_to(msg, "❌ شما از حالت ارسال به همه خارج شدید.")
    else:
        bot.reply_to(msg, "✅ شما در حالت ارسال به همه نیستید.")

@bot.message_handler(commands=['botup'])
def botup(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    response = "📋 گزارش کامل اطلاعات بات:\n\n"
    response += "👑 لیست ادمین‌ها:\n"
    if admins:
        for admin_id in admins:
            admin_num = get_admin_number(int(admin_id)) or "بدون شماره"
            if admin_num == "Founder":
                response += f"  بنیانگذار: {admin_id}\n"
            elif admin_num == "Owner":
                response += f"  سازنده: {admin_id}\n"
            else:
                response += f"  {admin_num}: {admin_id}\n"
    else:
        response += "  هیچ ادمینی وجود ندارد.\n"
    response += "\n⛔ لیست کاربران محروم شده:\n"
    if banned_users:
        for banned_id in banned_users:
            response += f"  {banned_id}\n"
    else:
        response += "  هیچ کاربری محروم نشده است.\n"
    response += "\n💰 لیست حمایت‌ها:\n"
    if donate_data:
        for item in donate_data:
            response += f"  {item['rank']} : {item['name']} - {item['amount']} T\n"
    else:
        response += "  هیچ حمایتی ثبت نشده است.\n"
    response += "\n📰 لیست اخبار:\n"
    if news_data:
        for news_id, news_text in news_data.items():
            response += f"  News {news_id}: {news_text[:100]}...\n"
    else:
        response += "  هیچ خبری ثبت نشده است.\n"
    response += "\n📢 لیست تبلیغات:\n"
    if ad_data:
        for ad_id, ad_text in ad_data.items():
            response += f"  Ad {ad_id}: {ad_text[:100]}...\n"
    else:
        response += "  هیچ تبلیغی ثبت نشده است.\n"
    response += "\n🤝 لیست کلن‌ها:\n"
    if clans:
        for clan_name, clan_data in clans.items():
            response += f"  {clan_name}: {clan_data['description'][:100]}...\n"
    else:
        response += "  هیچ کلنی ثبت نشده است.\n"
    response += "\n🎫 لیست تیکت‌ها:\n"
    if tickets:
        for ticket_num, ticket_data in tickets.items():
            response += f"  Ticket {ticket_num}: {ticket_data['question'][:50]}...\n"
    else:
        response += "  هیچ تیکتی ثبت نشده است.\n"
    response += "\n🎮 لیست بازی‌ها:\n"
    response += "🎮 سنگ کاغذ قیچی:\n"
    if games:
        for game_id, game_data in games.items():
            status = "منتظر حریف" if game_data['status'] == 'waiting' else "در حال بازی"
            response += f"  Game {game_id}: {status}\n"
    else:
        response += "  هیچ بازی فعالی وجود ندارد.\n"
    response += "\n❌⭕ Tic Tac Toe:\n"
    if ttt_games:
        for game_id, game_data in ttt_games.items():
            status = "منتظر حریف" if game_data['status'] == 'waiting' else "در حال بازی"
            response += f"  Game {game_id}: {status}\n"
    else:
        response += "  هیچ بازی فعالی وجود ندارد.\n"
    response += "\n📌 تمام اطلاعات بالا را کپی کنید و برای من بفرستید تا در کد جدید قرار دهم."
    bot.send_message(user_id, response)
    bot.reply_to(msg, "✅ اطلاعات کامل بات برای شما ارسال شد.")

@bot.message_handler(commands=['update'])
def update_bot(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    
    all_users = set()
    for user_id in waiting_for_message.keys():
        all_users.add(user_id)
    for user_id in tickets.keys():
        all_users.add(user_id)
    for user_id in chat_sessions.keys():
        all_users.add(user_id)
    for user_id in user_ticket_status.keys():
        all_users.add(user_id)
    for user_id in admins.keys():
        try:
            all_users.add(int(user_id))
        except:
            pass
    for user_id in banned_users.keys():
        try:
            all_users.add(int(user_id))
        except:
            pass
    
    count = 0
    for user in all_users:
        try:
            bot.send_message(user, "*** [ Bot.DataBase ] : درحال آپدیت ***")
            count += 1
        except:
            pass
    
    try:
        bot.send_message(user_id, f"✅ پیام آپدیت به {count} کاربر ارسال شد!")
    except:
        pass

@bot.message_handler(commands=['show_perms'])
def show_perms(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    
    response = "📋 جدول دسترسي ها:\n\n"
    response += "👑 بنیانگذار (Founder):\n"
    response += "  ✅ همه دستورات\n"
    response += "  ✅ بدون نياز به تاييد\n\n"
    response += "👑 سازنده (Owner):\n"
    response += "  ✅ همه دستورات\n"
    response += "  ✅ بدون نياز به تاييد\n\n"
    response += "🛡️ Admin (ادمین معمولی):\n"
    response += "  ✅ /tickets\n"
    response += "  ✅ /open\n"
    response += "  ✅ /a\n"
    response += "  ✅ /cc\n"
    response += "  ✅ /ac\n"
    response += "  ✅ /cmds\n"
    response += "  ❌ /ma\n"
    response += "  ❌ /kickadmin\n"
    response += "  ❌ /ban\n"
    response += "  ❌ /unban\n\n"
    response += "👤 User (کاربر عادی):\n"
    response += "  ✅ /ticket\n"
    response += "  ✅ /chat\n"
    response += "  ❌ ساير دستورات را ندارد"
    bot.reply_to(msg, response)

@bot.message_handler(commands=['ma'])
def add_admin(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ لطفا آيدي عددي کاربر را وارد کنيد: /ma 123456789")
        return
    try:
        new_admin_id = int(parts[1])
    except:
        bot.reply_to(msg, "❌ آيدي عددي معتبر نيست")
        return
    if new_admin_id == FOUNDER_ID or new_admin_id == OWNER2_ID:
        bot.reply_to(msg, "ℹ️ این کاربر قبلاً ادمین است.")
        return
    if str(new_admin_id) in admins:
        bot.reply_to(msg, f"ℹ️ کاربر {new_admin_id} قبلا ادمين است.")
        return
    admins[str(new_admin_id)] = 'admin'
    save_admins()
    admin_num = assign_admin_number(new_admin_id)
    bot.reply_to(msg, f"✅ کاربر با آيدي {new_admin_id} به ليست ادمين ها اضافه شد.\n📌 شماره: {admin_num}")

@bot.message_handler(commands=['kickadmin'])
def kick_admin(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ لطفا آيدي عددي کاربر را وارد کنيد: /kickadmin 123456789")
        return
    try:
        target_id = int(parts[1])
    except:
        bot.reply_to(msg, "❌ آيدي عددي معتبر نيست")
        return
    if target_id == FOUNDER_ID or target_id == OWNER2_ID:
        bot.reply_to(msg, "⛔ شما نمي توانيد بنیانگذار یا سازنده را حذف کنيد.")
        return
    if str(target_id) not in admins:
        bot.reply_to(msg, f"ℹ️ کاربر {target_id} ادمين نيست.")
        return
    del admins[str(target_id)]
    save_admins()
    bot.reply_to(msg, f"✅ کاربر با آيدي {target_id} از ليست ادمين ها حذف شد.")

@bot.message_handler(commands=['ban'])
def ban_user(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ لطفا آيدي عددي کاربر را وارد کنيد: /ban 123456789")
        return
    try:
        target_id = int(parts[1])
    except:
        bot.reply_to(msg, "❌ آيدي عددي معتبر نيست")
        return
    if target_id == FOUNDER_ID or target_id == OWNER2_ID:
        bot.reply_to(msg, "⛔ شما نمي توانيد بنیانگذار یا سازنده را محروم کنيد.")
        return
    if str(target_id) in admins:
        bot.reply_to(msg, "⛔ شما نمي توانيد ادمين را محروم کنيد.")
        return
    if is_banned(target_id):
        bot.reply_to(msg, f"ℹ️ کاربر {target_id} قبلا محروم شده است.")
        return
    banned_users[str(target_id)] = True
    save_banned()
    bot.send_message(target_id, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
    bot.reply_to(msg, f"✅ کاربر با آیدی {target_id} محروم شد.")

@bot.message_handler(commands=['unban'])
def unban_user(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ لطفا آيدي عددي کاربر را وارد کنيد: /unban 123456789")
        return
    try:
        target_id = int(parts[1])
    except:
        bot.reply_to(msg, "❌ آيدي عددي معتبر نيست")
        return
    if not is_banned(target_id):
        bot.reply_to(msg, f"ℹ️ کاربر {target_id} محروم نیست.")
        return
    del banned_users[str(target_id)]
    save_banned()
    bot.send_message(target_id, "✅ *** [ Ban.System ] : شما از حالت محرومیت خارج شدید ***\n\n🔰 اکنون میتوانید از تمام دستورات بات استفاده کنید.\n📌 برای مشاهده دستورات، دستور /info را بزنید.")
    bot.reply_to(msg, f"✅ کاربر با آیدی {target_id} از محرومیت خارج شد.")

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
        bot.reply_to(msg, "📭 هيچ بليط باز نشده اي وجود ندارد.")
        return
    
    for ticket_num, data in open_tickets:
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn_accept = telebot.types.InlineKeyboardButton("✅ قبول تیکت", callback_data=f"accept_ticket_{ticket_num}")
        markup.add(btn_accept)
        
        response = f"🎫 شماره: {ticket_num}\n"
        response += f"👤 نام: {data['first_name']} (@{data['username']})\n"
        response += f"📝 سوال: {data['question'][:100]}"
        bot.send_message(user_id, response, reply_markup=markup)

@bot.message_handler(commands=['open'])
def open_chat(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ /open 5")
        return
    try:
        ticket_number = int(parts[1])
    except:
        bot.reply_to(msg, "❌ شماره معتبر نيست")
        return
    if ticket_number not in tickets:
        bot.reply_to(msg, f"❌ بليط {ticket_number} وجود ندارد")
        return
    user_id_ticket = tickets[ticket_number]['user_id']
    chat_sessions[user_id_ticket] = 'open'
    bot.send_message(user_id_ticket, "✅ بليط شما توسط ادمين باز شد. براي چت دستور /chat را بزنید.")
    bot.reply_to(msg, f"✅ چت با بليط {ticket_number} باز شد")

@bot.message_handler(commands=['chat'])
def chat_with_user(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    if is_admin(user_id):
        bot.reply_to(msg, "⛔ شما ادمين هستيد و نمي توانيد از اين دستور استفاده کنيد")
        return
    if user_id not in chat_sessions or chat_sessions[user_id] != 'open':
        bot.reply_to(msg, "❌ چت فعالی نداريد")
        return
    waiting_for_message[user_id] = True
    bot.reply_to(msg, "✅ وارد چت شديد. پيام خود را بفرستيد")

@bot.message_handler(commands=['a'])
def admin_chat(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ /a پيام")
        return
    for user_id_chat, status in chat_sessions.items():
        if status == 'open':
            bot.send_message(user_id_chat, f"⚜ پاسخ ادمين:\n{parts[1]}")
            bot.reply_to(msg, f"✅ پيام ارسال شد")
            return
    bot.reply_to(msg, "❌ چت فعالی وجود ندارد")

@bot.message_handler(commands=['ac'])
def admin_chat_toggle(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    if user_id in admin_chat_mode and admin_chat_mode[user_id]:
        admin_chat_mode[user_id] = False
        bot.reply_to(msg, "❌ شما از حالت چت ادمين خارج شديد.")
    else:
        admin_chat_mode[user_id] = True
        if user_id != FOUNDER_ID and user_id != OWNER2_ID:
            admin_num = get_admin_number(user_id) or "Admin"
            bot.reply_to(msg, f"✅ شما وارد حالت چت ادمين شديد.\n📌 شماره شما: {admin_num}\n🔄 براي خروج دوباره /ac را بزنيد.")
        else:
            bot.reply_to(msg, "✅ شما وارد حالت چت ادمين شديد.\n🔄 براي خروج دوباره /ac را بزنيد.")

@bot.message_handler(commands=['cmds'])
def cmds(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    
    response = "📋 ليست دستورات ادمين:\n\n"
    response += "📌 /tickets : ليست بليط هاي باز نشده\n"
    response += "📌 /open [شماره] : باز کردن بليط\n"
    response += "📌 /a [پيام] : ارسال پاسخ به کاربر\n"
    response += "📌 /cc : پايان چت با کاربر\n"
    if is_founder(user_id) or is_owner(user_id):
        response += "📌 /ma [آيدي] : اضافه کردن ادمين جديد\n"
        response += "📌 /kickadmin [آيدي] : حذف ادمين\n"
        response += "📌 /ban [آيدي] : محروم کردن کاربر\n"
        response += "📌 /unban [آيدي] : رفع محروميت کاربر\n"
    response += "📌 /ac : ورود/خروج از چت ادمين ها\n"
    bot.reply_to(msg, response)

@bot.message_handler(commands=['cc'])
def close_chat(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    for user_id_chat, status in chat_sessions.items():
        if status == 'open':
            chat_sessions[user_id_chat] = 'closed'
            bot.send_message(user_id_chat, "💥 گفتگو پایان یافت")
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            btn_yes = telebot.types.InlineKeyboardButton("✅ بله", callback_data=f"delete_{user_id_chat}")
            btn_no = telebot.types.InlineKeyboardButton("❌ خیر", callback_data=f"keep_{user_id_chat}")
            markup.add(btn_yes, btn_no)
            bot.send_message(user_id_chat, "❓ آیا از این گفتگو راضی بودید؟", reply_markup=markup)
            bot.reply_to(msg, f"✅ چت پایان یافت")
            if user_id_chat in user_ticket_status:
                ticket_num = user_ticket_status[user_id_chat]
                if ticket_num in tickets:
                    del tickets[ticket_num]
                del user_ticket_status[user_id_chat]
                save_data()
            return
    bot.reply_to(msg, "❌ چت فعالی وجود ندارد")

@bot.message_handler(commands=['createclan'])
def create_clan(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ لطفا نام کلن را وارد کنید: /createclan 🧭 BadBoys 🧭")
        return
    clan_name = parts[1].strip()
    if clan_name in clans:
        bot.reply_to(msg, f"❌ کلن با نام «{clan_name}» قبلا وجود دارد.")
        return
    creating_clan[user_id] = {'clan_name': clan_name}
    bot.reply_to(msg, f"✅ کلن «{clan_name}» در حال ایجاد است.\n📝 لطفا متن توضیحات این کلن را ارسال کنید.")

@bot.message_handler(commands=['deleteclan'])
def delete_clan(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ لطفا نام کلن را وارد کنید: /deleteclan BadBoys")
        return
    clan_name = parts[1].strip()
    if clan_name not in clans:
        bot.reply_to(msg, f"❌ کلن با نام «{clan_name}» وجود ندارد.")
        return
    del clans[clan_name]
    save_clans()
    bot.reply_to(msg, f"✅ کلن «{clan_name}» با موفقیت حذف شد.")

@bot.message_handler(commands=['donate'])
def donate_command(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
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
    for item in donate_data:
        if item['name'].lower() == name.lower():
            bot.reply_to(msg, f"❌ نام {name} قبلا در لیست حمایت‌ها وجود دارد.")
            return
    donate_data.append({'name': name, 'amount': amount})
    donate_data.sort(key=lambda x: x['amount'], reverse=True)
    for idx, item in enumerate(donate_data):
        item['rank'] = idx + 1
    save_donate()
    bot.reply_to(msg, f"✅ {name} با مبلغ {amount} T به لیست حمایت‌ها اضافه شد.")

@bot.message_handler(commands=['removedonate'])
def remove_donate(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ لطفا نام شخص مورد نظر را وارد کنید: /removedonate Ali")
        return
    name = parts[1]
    found = False
    for item in donate_data[:]:
        if item['name'].lower() == name.lower():
            donate_data.remove(item)
            found = True
            break
    if not found:
        bot.reply_to(msg, f"❌ شخص با نام {name} در لیست حمایت‌ها وجود ندارد.")
        return
    donate_data.sort(key=lambda x: x['amount'], reverse=True)
    for idx, item in enumerate(donate_data):
        item['rank'] = idx + 1
    save_donate()
    bot.reply_to(msg, f"✅ {name} از لیست حمایت‌ها حذف شد.")

@bot.message_handler(commands=['hazfnews'])
def hazfnews(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
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

@bot.message_handler(commands=['hazfad'])
def hazfad(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
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

@bot.message_handler(commands=['news'])
def news_command(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    if user_id in news_mode and news_mode[user_id]:
        news_mode[user_id] = False
        bot.reply_to(msg, "❌ شما از حالت خبر خارج شدید.")
    else:
        news_mode[user_id] = True
        bot.reply_to(msg, "✅ شما وارد حالت خبر شدید. پیام خود را بفرستید تا به لیست اخبار اضافه شود.\n🔄 برای خروج دوباره /news را بزنید.")

@bot.message_handler(commands=['ad'])
def ad_command(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    if user_id in ad_mode and ad_mode[user_id]:
        ad_mode[user_id] = False
        bot.reply_to(msg, "❌ شما از حالت تبلیغ خارج شدید.")
    else:
        ad_mode[user_id] = True
        bot.reply_to(msg, "✅ شما وارد حالت تبلیغ شدید. پیام خود را بفرستید تا به لیست تبلیغات اضافه شود.\n🔄 برای خروج دوباره /ad را بزنید.")

@bot.message_handler(commands=['ticket'])
def ticket(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    if is_admin(user_id):
        bot.reply_to(msg, "⛔ شما ادمين هستيد و نمي توانيد تيکت بزنيد")
        return
    text = msg.text
    parts = text.split(maxsplit=1)
    if user_id in user_ticket_status and user_ticket_status[user_id] in tickets:
        bot.reply_to(msg, "❌ شما يک بليط فعال داريد و نمي توانيد بليط جديد بفرستيد")
        return
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ لطفا بعد از /ticket پيام خود را بنويسيد")
        bot.reply_to(msg, "📌 مثال : /ticket سوال دارم")
        return
    soal_text = parts[1]
    user = msg.from_user
    global ticket_counter
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
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn_accept = telebot.types.InlineKeyboardButton("✅ قبول تیکت", callback_data=f"accept_ticket_{ticket_number}")
    markup.add(btn_accept)
    
    bot.send_message(FOUNDER_ID, f"🎫 بليط جديد شماره: {ticket_number}\n👤 نام: {user.first_name} (@{user.username}) [آيدي: {user_id}]\n📝 سوال: {soal_text}", reply_markup=markup)
    if OWNER2_ID:
        bot.send_message(OWNER2_ID, f"🎫 بليط جديد شماره: {ticket_number}\n👤 نام: {user.first_name} (@{user.username}) [آيدي: {user_id}]\n📝 سوال: {soal_text}", reply_markup=markup)
    for admin_id in admins:
        if int(admin_id) != FOUNDER_ID and int(admin_id) != OWNER2_ID:
            try:
                bot.send_message(int(admin_id), f"🎫 بليط جديد شماره: {ticket_number}\n👤 نام: {user.first_name} (@{user.username}) [آيدي: {user_id}]\n📝 سوال: {soal_text}", reply_markup=markup)
            except:
                pass
    
    bot.reply_to(msg, "✅ پيام شما ارسال شد. منتظر پاسخ ادمین باشید.")

@bot.callback_query_handler(func=lambda call: True)
def handle_accept_ticket(call):
    user_id = call.from_user.id
    if call.data.startswith("accept_ticket_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما ادمین نیستید!")
            return
        
        ticket_number = int(call.data.replace("accept_ticket_", ""))
        if ticket_number not in tickets:
            bot.answer_callback_query(call.id, "❌ تیکت وجود ندارد!")
            return
        
        user_id_ticket = tickets[ticket_number]['user_id']
        chat_sessions[user_id_ticket] = 'open'
        
        admin_name = "ادمین"
        try:
            admin_info = bot.get_chat(user_id)
            admin_name = admin_info.first_name or admin_info.username or "ادمین"
        except:
            pass
        
        bot.send_message(
            user_id_ticket, 
            f"✅ تیکت شما توسط ادمین : {admin_name} باز شد 🎫\n"
            f"📌 برای شروع مکالمه، لطفاً روی دستور زیر کلیک کنید:\n"
            f"/chat"
        )
        
        bot.send_message(
            user_id, 
            f"✅ تیکت {ticket_number} باز شد! شما در حالت چت با کاربر هستید. 💬"
        )
        
        bot.answer_callback_query(call.id, "✅ تیکت باز شد")

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_messages(msg):
    user_id = msg.from_user.id
    
    if user_id in broadcast_mode and broadcast_mode[user_id]:
        all_users = set()
        for user_id in waiting_for_message.keys():
            all_users.add(user_id)
        for user_id in tickets.keys():
            all_users.add(user_id)
        for user_id in chat_sessions.keys():
            all_users.add(user_id)
        for user_id in user_ticket_status.keys():
            all_users.add(user_id)
        for user_id in admins.keys():
            try:
                all_users.add(int(user_id))
            except:
                pass
        for user_id in banned_users.keys():
            try:
                all_users.add(int(user_id))
            except:
                pass
        
        count = 0
        for user in all_users:
            try:
                bot.send_message(user, msg.text)
                count += 1
            except:
                pass
        
        bot.send_message(user_id, f"✅ پیام شما به {count} کاربر ارسال شد!")
        del broadcast_mode[user_id]
        return
    
    if is_banned(user_id):
        return
    
    if user_id in waiting_for_message and waiting_for_message[user_id] == 'ticket':
        global ticket_counter
        if is_admin(user_id):
            bot.reply_to(msg, "⛔ شما ادمین هستید و نمی توانید تیکت بزنید")
            waiting_for_message[user_id] = False
            return
        if user_id in user_ticket_status and user_ticket_status[user_id] in tickets:
            bot.reply_to(msg, "❌ شما يک بليط فعال داريد و نمي توانيد بليط جديد بفرستيد")
            waiting_for_message[user_id] = False
            return
        
        soal_text = msg.text
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
        waiting_for_message[user_id] = False
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn_accept = telebot.types.InlineKeyboardButton("✅ قبول تیکت", callback_data=f"accept_ticket_{ticket_number}")
        markup.add(btn_accept)
        
        bot.send_message(FOUNDER_ID, f"🎫 بليط جديد شماره: {ticket_number}\n👤 نام: {user.first_name} (@{user.username}) [آيدي: {user_id}]\n📝 سوال: {soal_text}", reply_markup=markup)
        if OWNER2_ID:
            bot.send_message(OWNER2_ID, f"🎫 بليط جديد شماره: {ticket_number}\n👤 نام: {user.first_name} (@{user.username}) [آيدي: {user_id}]\n📝 سوال: {soal_text}", reply_markup=markup)
        for admin_id in admins:
            if int(admin_id) != FOUNDER_ID and int(admin_id) != OWNER2_ID:
                try:
                    bot.send_message(int(admin_id), f"🎫 بليط جديد شماره: {ticket_number}\n👤 نام: {user.first_name} (@{user.username}) [آيدي: {user_id}]\n📝 سوال: {soal_text}", reply_markup=markup)
                except:
                    pass
        
        bot.reply_to(msg, "✅ پيام شما ارسال شد. منتظر پاسخ ادمین باشید.")
        return
    
    if user_id in rps_password_temp and rps_password_temp[user_id].get('step') == 'waiting_password':
        password = msg.text
        game_id = create_game(user_id)
        games[game_id]['password'] = password
        save_games()
        del rps_password_temp[user_id]
        bot.reply_to(msg, f"✅ اتاق سنگ ، کاغذ ، قیچی شما با رمز ساخته شد !\n🆔 ایدی اتاق : {game_id}\n🔑 رمز: {password}\n🔄 منتظر حریف باشید...")
        return
    
    if user_id in ttt_password_temp and ttt_password_temp[user_id].get('step') == 'waiting_password':
        password = msg.text
        game_id = create_ttt_game(user_id)
        ttt_games[game_id]['password'] = password
        save_ttt_games()
        del ttt_password_temp[user_id]
        bot.reply_to(msg, f"✅ اتاق Tic Tac Toe شما با رمز ساخته شد !\n🆔 ایدی اتاق : {game_id}\n🔑 رمز: {password}\n🔄 منتظر حریف باشید...")
        return
    
    if user_id in rps_join_temp and rps_join_temp[user_id].get('step') == 'waiting_password':
        password = msg.text
        game_id = rps_join_temp[user_id]['game_id']
        if game_id not in games:
            bot.reply_to(msg, "❌ این اتاق وجود ندارد.")
            del rps_join_temp[user_id]
            return
        if games[game_id]['player2'] is not None:
            bot.reply_to(msg, "❌ این اتاق پر است.")
            del rps_join_temp[user_id]
            return
        if games[game_id]['password'] != password:
            bot.reply_to(msg, "❌ رمز اشتباه است. دوباره تلاش کنید:")
            return
        games[game_id]['player2'] = user_id
        games[game_id]['status'] = 'playing'
        game_players[str(user_id)] = game_id
        if game_id in waiting_games:
            waiting_games.remove(game_id)
        save_games()
        del rps_join_temp[user_id]
        bot.reply_to(msg, f"✅ شما به اتاق {game_id} ملحق شدید!")
        bot.send_message(games[game_id]['player1'], f"✅ حریف شما به اتاق {game_id} ملحق شد!")
        start_rps_game(game_id)
        return
    
    if user_id in ttt_join_temp and ttt_join_temp[user_id].get('step') == 'waiting_password':
        password = msg.text
        game_id = ttt_join_temp[user_id]['game_id']
        if game_id not in ttt_games:
            bot.reply_to(msg, "❌ این اتاق وجود ندارد.")
            del ttt_join_temp[user_id]
            return
        if ttt_games[game_id]['player2'] is not None:
            bot.reply_to(msg, "❌ این اتاق پر است.")
            del ttt_join_temp[user_id]
            return
        if ttt_games[game_id]['password'] != password:
            bot.reply_to(msg, "❌ رمز اشتباه است. دوباره تلاش کنید:")
            return
        ttt_games[game_id]['player2'] = user_id
        ttt_games[game_id]['status'] = 'playing'
        ttt_game_players[str(user_id)] = game_id
        if game_id in ttt_waiting_games:
            ttt_waiting_games.remove(game_id)
        save_ttt_games()
        del ttt_join_temp[user_id]
        bot.reply_to(msg, f"✅ شما به اتاق {game_id} ملحق شدید!")
        bot.send_message(ttt_games[game_id]['player1'], f"✅ حریف شما به اتاق {game_id} ملحق شد!")
        start_ttt_game(game_id)
        return
    
    if user_id in creating_clan:
        clan_name = creating_clan[user_id]['clan_name']
        description = msg.text
        clans[clan_name] = {'description': description, 'creator': user_id}
        save_clans()
        del creating_clan[user_id]
        bot.reply_to(msg, f"✅ کلن «{clan_name}» با موفقیت ایجاد شد.\n📋 توضیحات: {description}")
        return
    
    if user_id in private_chat_mode:
        partner_id = private_chat_mode[user_id]
        try:
            if msg.text:
                bot.send_message(partner_id, msg.text)
            bot.reply_to(msg, "✅ پیام شما ارسال شد.")
        except Exception as e:
            bot.reply_to(msg, f"❌ خطا در ارسال پیام: {e}")
        return
    
    if user_id in news_mode and news_mode[user_id]:
        global news_counter
        news_counter += 1
        news_data[str(news_counter)] = msg.text
        save_news()
        bot.reply_to(msg, f"✅ خبر {news_counter} با موفقیت ثبت شد.")
        news_mode[user_id] = False
        return
    
    if user_id in ad_mode and ad_mode[user_id]:
        global ad_counter
        ad_counter += 1
        ad_data[str(ad_counter)] = msg.text
        save_ad()
        bot.reply_to(msg, f"✅ تبلیغ {ad_counter} با موفقیت ثبت شد.")
        ad_mode[user_id] = False
        return
    
    if is_admin(user_id):
        if user_id in admin_chat_mode and admin_chat_mode[user_id]:
            if user_id == FOUNDER_ID:
                display_name = "بنیانگذار"
            elif user_id == OWNER2_ID:
                display_name = "سازنده"
            else:
                admin_num = get_admin_number(user_id) or "Admin"
                display_name = f"{admin_num}"
            for admin_id in admins:
                if int(admin_id) != user_id:
                    try:
                        bot.send_message(int(admin_id), f"[ Admin.Chat ] ( {display_name} ) : {msg.text}")
                    except:
                        pass
            bot.reply_to(msg, "✅ پیام شما به چت ادمین ها ارسال شد.")
            return
        else:
            if not msg.text.startswith('/'):
                if user_id == FOUNDER_ID:
                    bot.reply_to(msg, "سلام سرورم 🙏🏻❤️\nامیدوارم حالتون خوب باشه 👋🏻\nلطفا دستور :\n/fpanel\nرا بزنید 🌠")
                elif user_id == OWNER2_ID:
                    bot.reply_to(msg, "سلام سرورم 🙏🏻❤️\nامیدوارم حالتون خوب باشه 👋🏻\nلطفا دستور :\n/opanel\nرا بزنید 🌠")
                else:
                    bot.reply_to(msg, "👋 سلام ادمین عزیز!\nلطفاً برای ورود به پنل مدیریت، دستور زیر را بزنید:\n/apanel")
                return
    
    if user_id in waiting_for_message and waiting_for_message[user_id] == True:
        if user_id != FOUNDER_ID and user_id != OWNER2_ID and user_id in chat_sessions and chat_sessions[user_id] == 'open':
            bot.send_message(FOUNDER_ID, f"💬 از کاربر:\n👤 نام: {msg.from_user.first_name} [آیدی: {user_id}]\n📝 پیام: {msg.text}")
            if OWNER2_ID:
                bot.send_message(OWNER2_ID, f"💬 از کاربر:\n👤 نام: {msg.from_user.first_name} [آیدی: {user_id}]\n📝 پیام: {msg.text}")
            bot.reply_to(msg, "✅ ارسال شد")
        else:
            bot.forward_message(FOUNDER_ID, user_id, msg.message_id)
            bot.send_message(FOUNDER_ID, f"👤 نام: {msg.from_user.first_name} (@{msg.from_user.username}) | آیدی: {user_id}")
            if OWNER2_ID:
                bot.forward_message(OWNER2_ID, user_id, msg.message_id)
                bot.send_message(OWNER2_ID, f"👤 نام: {msg.from_user.first_name} (@{msg.from_user.username}) | آیدی: {user_id}")
            bot.reply_to(msg, "✅ پیام ارسال شد")
            waiting_for_message[user_id] = False
    else:
        if not msg.text.startswith('/'):
            bot.reply_to(msg, "ℹ️ ابتدا دستور /start را بزنید تا منوی اصلی را ببینید")

@app.route('/')
def home():
    return "Bot is running!"

def run_bot():
    print("✅ Robot is running...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    app.run(host='0.0.0.0', port=8080)
