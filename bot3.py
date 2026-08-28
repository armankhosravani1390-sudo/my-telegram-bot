import telebot
import time
import threading
from flask import Flask
import json
import os
import zipfile
import shutil
from datetime import datetime, timezone, timedelta
import random

TOKEN = "8299446091:AAHVWDgncWd9qeU0eoNQ8GV-mX1yON-fMsM"
OWNER_ID = 6703121829
FOUNDER_ID = 6703121829
OWNER2_ID = 6328427378
FOUNDER_NAME = "꧁ I R A N ꧂"

# ========== تنظیمات گروه بک‌آپ ==========
GROUP_ID = -1004326536729
TOPIC_IDS = {
    'admins':        2,
    'clans':         19,
    'news':          18,
    'ads':           31,
    'donate':        9,
    'tickets':       8,
    'games':         None,
    'media_photos':  12,
    'media_videos':  14,
    'media_audios':  15,
    'users':         22,
    'banned':        69,
    'backup_files':  None,
    'channels':      20,
}

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
console_mode = {}

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

media_data = {
    'photos': [],
    'videos': [],
    'audios': []
}
upload_mode = {}
restore_mode = {}

# ========== سیستم چت مخفی (پیام‌های ناشناس برای بنیانگذار) ==========
pending_stealth = {}   # user_id(str) -> {'name':..., 'username':...}  پیام‌های در انتظار باز شدن
stealth_sessions = {}  # user_id(str) -> True/False  آیا چت مخفی با این کاربر فعال است
stealth_chat_mode = {} # founder_id -> target_user_id  بنیانگذار الان با چه کسی در چت مخفی است

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
MEDIA_FILE = 'media.json'
ANTIVIRUS_FILE = 'antivirus.json'

JSON_FILES = [
    DATA_FILE, ADMINS_FILE, ADMIN_NUMBERS_FILE, BANNED_FILE,
    NEWS_FILE, AD_FILE, DONATE_FILE, CLANS_FILE,
    GAMES_FILE, TTT_GAMES_FILE, USERS_FILE, MEDIA_FILE, ANTIVIRUS_FILE
]

MEDIA_BACKUP_DIR = 'media_backup_tmp'

CONSOLE_ACCESS_CODE = "1390"
CONSOLE_DECODE_TRIGGER = "1360"
HASH_OFFSET = 133

antivirus_enabled = True

# ========== تاریخ و ساعت ایران ==========
IRAN_TZ = timezone(timedelta(hours=3, minutes=30))
PERSIAN_MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                  'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
PERSIAN_WEEKDAYS = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه', 'یکشنبه']

def gregorian_to_jalali(gy, gm, gd):
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1
    g_day_no = 365 * gy2 + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400
    for i in range(gm2):
        g_day_no += g_days_in_month[i]
    if gm2 > 1 and ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
        g_day_no += 1
    g_day_no += gd2
    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365
    jm = 12
    jd = j_day_no + 1
    for i in range(11):
        if j_day_no < j_days_in_month[i]:
            jm = i + 1
            jd = j_day_no + 1
            break
        j_day_no -= j_days_in_month[i]
    return jy, jm, jd

def get_jalali_numeric_date():
    now_ir = datetime.now(IRAN_TZ)
    jy, jm, jd = gregorian_to_jalali(now_ir.year, now_ir.month, now_ir.day)
    return f"{jy}/{jm}/{jd}"

def get_iran_datetime_text():
    now_ir = datetime.now(IRAN_TZ)
    jy, jm, jd = gregorian_to_jalali(now_ir.year, now_ir.month, now_ir.day)
    wd = PERSIAN_WEEKDAYS[now_ir.weekday()]
    time_str = now_ir.strftime('%H:%M:%S')
    jalali_numeric = f"{jy}/{jm}/{jd}"
    text = (
        f"🕒 ساعت به وقت ایران: {time_str}\n\n"
        f"📅 امروز: {wd}، {jd} {PERSIAN_MONTHS[jm-1]} {jy}\n"
        f"🔢 تاریخ شمسی (عددی): {jalali_numeric}\n"
        f"🗓 شما در ماه «{PERSIAN_MONTHS[jm-1]}» هستید.\n\n"
        f"📆 تاریخ میلادی: {now_ir.strftime('%Y-%m-%d')}"
    )
    return text

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
            "1": "🌿 سرور NightFall با افتخار تقدیم میکند\n\nNightFall Nights 🌔\n\n📍اگه دنبال تجربه خفن از یه سرور خفن هستی همین الان به سرور ما بپیوند 🌏\n\n🏆 تازه ترین و بهینه ترین سرور اِم تی اِی 🏆\n\n⚡𝐒𝐞𝐫𝐯𝐞𝐫 𝐈𝐏 :\nMtaSa://5.42.223.61:22003\n\n      𝐒𝐨𝐜𝐢𝐚𝐥 𝐦𝐞𝐝𝐢𝐚👇\n\n🌐 𝐓𝐞𝐚𝐦𝐒𝐩𝐞𝐚𝐤 : ts63.ir:11439\n((5.57.39.100:11439))\n\n📱 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 : @NightFall_MTA\n\n✈ 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 : @NightFall_MTA\n\n💻 𝐑𝐮𝐛𝐢𝐤𝐚 : @NightFall_RPG\n\n🎥 𝐀𝐩𝐚𝐫𝐚𝐭 : 𝐂𝐨𝐦𝐢𝐧𝐠 𝐒𝐨𝐨𝐧\n\n🛒 𝐒𝐡𝐨𝐩 : 𝐂𝐨𝐦𝐢𝐧𝐠 𝐒𝐨𝐨𝐧\n\n🧑‍💻 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 𝗦𝗲𝗿𝘃𝗲𝗿 : @NightFall_RPG\n\n🧡𝐅𝐨𝐥𝐥𝐨𝐰 𝐔𝐬 ....🧡"
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

def load_media():
    global media_data
    if os.path.exists(MEDIA_FILE):
        with open(MEDIA_FILE, 'r') as f:
            media_data = json.load(f)
    else:
        media_data = {
            'photos': [],
            'videos': [],
            'audios': []
        }

def save_media():
    with open(MEDIA_FILE, 'w') as f:
        json.dump(media_data, f)

def load_antivirus():
    global antivirus_enabled
    if os.path.exists(ANTIVIRUS_FILE):
        with open(ANTIVIRUS_FILE, 'r') as f:
            data = json.load(f)
            antivirus_enabled = data.get('enabled', True)
    else:
        antivirus_enabled = True

def save_antivirus():
    with open(ANTIVIRUS_FILE, 'w') as f:
        json.dump({'enabled': antivirus_enabled}, f)

def hash_text(text):
    return '-'.join(str(ord(ch) + HASH_OFFSET) for ch in text)

def unhash_text(hashed):
    try:
        parts = hashed.strip().split('-')
        if not parts or parts == ['']:
            return None
        return ''.join(chr(int(p) - HASH_OFFSET) for p in parts)
    except:
        return None

# ========== دانلود واقعی مدیاها برای اینکه توی ZIP قرار بگیرن ==========
def download_all_media_for_backup():
    if os.path.exists(MEDIA_BACKUP_DIR):
        shutil.rmtree(MEDIA_BACKUP_DIR)
    os.makedirs(os.path.join(MEDIA_BACKUP_DIR, 'photos'), exist_ok=True)
    os.makedirs(os.path.join(MEDIA_BACKUP_DIR, 'videos'), exist_ok=True)
    os.makedirs(os.path.join(MEDIA_BACKUP_DIR, 'audios'), exist_ok=True)

    for item in media_data.get('photos', []):
        try:
            file_info = bot.get_file(item['file_id'])
            downloaded = bot.download_file(file_info.file_path)
            ext = os.path.splitext(file_info.file_path)[1] or '.jpg'
            path = os.path.join(MEDIA_BACKUP_DIR, 'photos', f"{item['id']}{ext}")
            with open(path, 'wb') as f:
                f.write(downloaded)
        except Exception as e:
            print(f"❌ خطا در دانلود عکس {item.get('id')}: {e}")

    for item in media_data.get('videos', []):
        try:
            file_info = bot.get_file(item['file_id'])
            downloaded = bot.download_file(file_info.file_path)
            ext = os.path.splitext(file_info.file_path)[1] or '.mp4'
            path = os.path.join(MEDIA_BACKUP_DIR, 'videos', f"{item['id']}{ext}")
            with open(path, 'wb') as f:
                f.write(downloaded)
        except Exception as e:
            print(f"❌ خطا در دانلود فیلم {item.get('id')}: {e}")

    for item in media_data.get('audios', []):
        try:
            file_info = bot.get_file(item['file_id'])
            downloaded = bot.download_file(file_info.file_path)
            ext = os.path.splitext(file_info.file_path)[1] or '.mp3'
            path = os.path.join(MEDIA_BACKUP_DIR, 'audios', f"{item['id']}{ext}")
            with open(path, 'wb') as f:
                f.write(downloaded)
        except Exception as e:
            print(f"❌ خطا در دانلود آهنگ {item.get('id')}: {e}")

    return MEDIA_BACKUP_DIR

def create_backup_zip(include_media=True):
    now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_path = f"backup_{now_str}.zip"

    media_dir = None
    if include_media:
        media_dir = download_all_media_for_backup()

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in JSON_FILES:
            if os.path.exists(file_path):
                zf.write(file_path)
        if media_dir and os.path.exists(media_dir):
            for root, dirs, files in os.walk(media_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, '.')
                    zf.write(full_path, arcname)

    if media_dir and os.path.exists(media_dir):
        shutil.rmtree(media_dir)

    return zip_path, now_str

def send_zip_backup(sender_id):
    if not GROUP_ID:
        bot.send_message(sender_id, "⚠️ GROUP_ID هنوز تنظیم نشده!\nابتدا بات رو به گروه اضافه کن، توی هر تاپیک /getgroupid بزن و مقادیر رو توی کد پر کن.")
        return
    zip_path = None
    try:
        bot.send_message(sender_id, "⏳ در حال دانلود مدیاها (عکس/فیلم/آهنگ) و ساخت بک‌آپ کامل ZIP...\nبستگی به تعداد مدیاها ممکن است کمی طول بکشد ⏳")
        zip_path, now_str = create_backup_zip(include_media=True)
        thread_id = TOPIC_IDS.get('backup_files')
        caption = f"🗄 بک‌آپ کامل فایل‌های بات (ZIP) + مدیا\n🕐 زمان آپلود: {now_str}\n🔢 تاریخ شمسی: {get_jalali_numeric_date()}"
        with open(zip_path, 'rb') as f:
            if thread_id:
                sent = bot.send_document(GROUP_ID, f, caption=caption, message_thread_id=thread_id)
            else:
                sent = bot.send_document(GROUP_ID, f, caption=caption)
        try:
            bot.pin_chat_message(GROUP_ID, sent.message_id, disable_notification=True)
        except Exception as e:
            bot.send_message(sender_id, f"⚠️ فایل بک‌آپ ارسال شد ولی پین نشد (باید بات ادمین گروه با دسترسی پین باشه): {e}")
        bot.send_message(sender_id, f"✅ بک‌آپ ZIP کامل (همراه با مدیای واقعی) ساخته، ارسال و پین شد!\n🕐 زمان: {now_str}")
    except Exception as e:
        bot.send_message(sender_id, f"❌ خطا در ساخت/ارسال بک‌آپ ZIP: {e}")
    finally:
        if zip_path and os.path.exists(zip_path):
            os.remove(zip_path)

def get_database_invite_link():
    try:
        invite = bot.create_chat_invite_link(GROUP_ID, name="DataBase Access")
        return invite.invite_link
    except Exception as e:
        print(f"❌ خطا در ساخت لینک دعوت گروه دیتابیس: {e}")
        return None

def restore_backup_zip(msg, sender_id):
    global tickets, ticket_counter, admins, admin_numbers, banned_users, news_data, news_counter
    global ad_data, ad_counter, donate_data, clans, games, game_players, waiting_games
    global ttt_games, ttt_game_players, ttt_waiting_games, all_users_data, media_data, antivirus_enabled

    file_info = bot.get_file(msg.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    temp_zip_path = f"restore_{msg.document.file_id}.zip"
    with open(temp_zip_path, 'wb') as f:
        f.write(downloaded)

    extract_dir = "restore_extracted"
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(temp_zip_path, 'r') as zf:
        zf.extractall(extract_dir)

    restored_files = []
    for json_file in JSON_FILES:
        src = os.path.join(extract_dir, json_file)
        if os.path.exists(src):
            shutil.copy(src, json_file)
            restored_files.append(json_file)

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
    load_media()
    load_antivirus()
    init_roles()

    media_root = os.path.join(extract_dir, MEDIA_BACKUP_DIR)
    uploaded_count = {'photos': 0, 'videos': 0, 'audios': 0}

    if os.path.exists(media_root):
        photos_dir = os.path.join(media_root, 'photos')
        if os.path.exists(photos_dir):
            for item in media_data.get('photos', []):
                for fname in os.listdir(photos_dir):
                    if fname.startswith(f"{item['id']}."):
                        try:
                            with open(os.path.join(photos_dir, fname), 'rb') as f:
                                sent = bot.send_photo(sender_id, f, caption=item.get('caption', ''))
                            item['file_id'] = sent.photo[-1].file_id
                            uploaded_count['photos'] += 1
                        except Exception as e:
                            print(f"❌ خطا در آپلود مجدد عکس {item.get('id')}: {e}")
                        break

        videos_dir = os.path.join(media_root, 'videos')
        if os.path.exists(videos_dir):
            for item in media_data.get('videos', []):
                for fname in os.listdir(videos_dir):
                    if fname.startswith(f"{item['id']}."):
                        try:
                            with open(os.path.join(videos_dir, fname), 'rb') as f:
                                sent = bot.send_video(sender_id, f, caption=item.get('caption', ''))
                            item['file_id'] = sent.video.file_id
                            uploaded_count['videos'] += 1
                        except Exception as e:
                            print(f"❌ خطا در آپلود مجدد فیلم {item.get('id')}: {e}")
                        break

        audios_dir = os.path.join(media_root, 'audios')
        if os.path.exists(audios_dir):
            for item in media_data.get('audios', []):
                for fname in os.listdir(audios_dir):
                    if fname.startswith(f"{item['id']}."):
                        try:
                            with open(os.path.join(audios_dir, fname), 'rb') as f:
                                sent = bot.send_audio(sender_id, f, caption=item.get('caption', ''))
                            item['file_id'] = sent.audio.file_id
                            uploaded_count['audios'] += 1
                        except Exception as e:
                            print(f"❌ خطا در آپلود مجدد آهنگ {item.get('id')}: {e}")
                        break

        save_media()

    if os.path.exists(temp_zip_path):
        os.remove(temp_zip_path)
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)

    response = "✅ بازیابی بک‌آپ با موفقیت انجام شد!\n\n"
    response += f"📄 فایل‌های اطلاعاتی بازیابی شده: {len(restored_files)}\n"
    response += f"📸 عکس‌های بازیابی شده: {uploaded_count['photos']}\n"
    response += f"🎥 فیلم‌های بازیابی شده: {uploaded_count['videos']}\n"
    response += f"🎵 آهنگ‌های بازیابی شده: {uploaded_count['audios']}\n"
    bot.send_message(sender_id, response)

def send_backup_to_group(sender_id):
    if not GROUP_ID:
        bot.send_message(sender_id, "⚠️ GROUP_ID هنوز تنظیم نشده!\nابتدا بات رو به گروه اضافه کن، توی هر تاپیک /getgroupid بزن و مقادیر رو توی کد پر کن.")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def send_to_topic(topic_key, text, parse_mode=None):
        thread_id = TOPIC_IDS.get(topic_key)
        try:
            if thread_id:
                bot.send_message(GROUP_ID, text, message_thread_id=thread_id, parse_mode=parse_mode)
            else:
                bot.send_message(GROUP_ID, f"[{topic_key}]\n{text}", parse_mode=parse_mode)
        except Exception as e:
            bot.send_message(sender_id, f"❌ خطا در ارسال به تاپیک {topic_key}: {e}")

    admin_text = f"👑 لیست ادمین‌ها — {now}\n{'━'*25}\n"
    for admin_id, role in admins.items():
        num = admin_numbers.get(admin_id, role)
        admin_text += f"🆔 {admin_id} | {num}\n"
    send_to_topic('admins', admin_text)

    banned_text = f"⛔ کاربران محروم — {now}\n{'━'*25}\n"
    if banned_users:
        for bid in banned_users:
            banned_text += f"🆔 {bid}\n"
    else:
        banned_text += "هیچ کاربری محروم نیست.\n"
    send_to_topic('banned', banned_text)

    clan_text = f"🤝 اتحادها — {now}\n{'━'*25}\n"
    if clans:
        for cname, cdata in clans.items():
            clan_text += f"\n📌 نام: {cname}\n"
            clan_text += f"📋 توضیحات:\n{cdata['description']}\n"
            clan_text += f"👑 سازنده: {cdata['creator']}\n"
            clan_text += "─"*20 + "\n"
    else:
        clan_text += "هیچ اتحادی وجود ندارد.\n"
    if len(clan_text) > 4000:
        parts = [clan_text[i:i+4000] for i in range(0, len(clan_text), 4000)]
        for part in parts:
            send_to_topic('clans', part)
    else:
        send_to_topic('clans', clan_text)

    news_text = f"📰 اخبار — {now}\n{'━'*25}\n"
    if news_data:
        for nid, ntext in news_data.items():
            news_text += f"\n🔹 News {nid}:\n{ntext}\n" + "─"*20 + "\n"
    else:
        news_text += "هیچ خبری وجود ندارد.\n"
    if len(news_text) > 4000:
        parts = [news_text[i:i+4000] for i in range(0, len(news_text), 4000)]
        for part in parts:
            send_to_topic('news', part)
    else:
        send_to_topic('news', news_text)

    ad_text = f"📢 تبلیغات — {now}\n{'━'*25}\n"
    if ad_data:
        for aid, atext in ad_data.items():
            ad_text += f"\n🔸 Ad {aid}:\n{atext}\n" + "─"*20 + "\n"
    else:
        ad_text += "هیچ تبلیغی وجود ندارد.\n"
    if len(ad_text) > 4000:
        parts = [ad_text[i:i+4000] for i in range(0, len(ad_text), 4000)]
        for part in parts:
            send_to_topic('ads', part)
    else:
        send_to_topic('ads', ad_text)

    # ========== کانال‌های اجباری ==========
    channels_text = f"📺 کانال‌های اجباری — {now}\n{'━'*25}\n"
    if REQUIRED_CHANNELS:
        for ch in REQUIRED_CHANNELS:
            channels_text += f"📌 نام: {ch['name']}\n🔗 لینک: {ch['link']}\n" + "─"*20 + "\n"
    else:
        channels_text += "هیچ کانالی تنظیم نشده است.\n"
    send_to_topic('channels', channels_text)

    donate_text = f"💰 حمایت‌ها — {now}\n{'━'*25}\n"
    if donate_data:
        for item in donate_data:
            donate_text += f"🏅 رتبه {item['rank']}: {item['name']} — {item['amount']} T\n"
    else:
        donate_text += "هیچ حمایتی ثبت نشده.\n"
    send_to_topic('donate', donate_text)

    ticket_text = f"🎫 تیکت‌ها — {now}\n{'━'*25}\n"
    if tickets:
        for tnum, tdata in tickets.items():
            ticket_text += f"\n🎫 شماره {tnum}\n"
            ticket_text += f"👤 {tdata['first_name']} (@{tdata['username']}) | آیدی: {tdata['user_id']}\n"
            ticket_text += f"📝 سوال: {tdata['question']}\n" + "─"*20 + "\n"
    else:
        ticket_text += "هیچ تیکتی وجود ندارد.\n"
    if len(ticket_text) > 4000:
        parts = [ticket_text[i:i+4000] for i in range(0, len(ticket_text), 4000)]
        for part in parts:
            send_to_topic('tickets', part)
    else:
        send_to_topic('tickets', ticket_text)

    game_text = f"🎮 بازی‌ها — {now}\n{'━'*25}\n"
    game_text += "🪨 سنگ کاغذ قیچی:\n"
    if games:
        for gid, gdata in games.items():
            status = "منتظر حریف" if gdata['status'] == 'waiting' else "در حال بازی"
            game_text += f"  Game {gid}: {status}\n"
    else:
        game_text += "  بازی فعالی وجود ندارد.\n"
    game_text += "\n❌⭕ Tic Tac Toe:\n"
    if ttt_games:
        for gid, gdata in ttt_games.items():
            status = "منتظر حریف" if gdata['status'] == 'waiting' else "در حال بازی"
            game_text += f"  Game {gid}: {status}\n"
    else:
        game_text += "  بازی فعالی وجود ندارد.\n"
    send_to_topic('games', game_text)

    photos_thread = TOPIC_IDS.get('media_photos')
    photos_text = f"📸 عکس‌ها — {now}\n{'━'*25}\nتعداد: {len(media_data['photos'])} عدد\n"
    send_to_topic('media_photos', photos_text)
    for photo in media_data['photos']:
        try:
            if photos_thread:
                bot.send_photo(GROUP_ID, photo['file_id'], caption=f"📸 {photo.get('caption','')}", message_thread_id=photos_thread)
            else:
                bot.send_photo(GROUP_ID, photo['file_id'], caption=f"📸 {photo.get('caption','')}")
        except:
            pass

    videos_thread = TOPIC_IDS.get('media_videos')
    videos_text = f"🎥 فیلم‌ها — {now}\n{'━'*25}\nتعداد: {len(media_data['videos'])} عدد\n"
    send_to_topic('media_videos', videos_text)
    for video in media_data['videos']:
        try:
            if videos_thread:
                bot.send_video(GROUP_ID, video['file_id'], caption=f"🎥 {video.get('caption','')}", message_thread_id=videos_thread)
            else:
                bot.send_video(GROUP_ID, video['file_id'], caption=f"🎥 {video.get('caption','')}")
        except:
            pass

    audios_thread = TOPIC_IDS.get('media_audios')
    audios_text = f"🎵 آهنگ‌ها — {now}\n{'━'*25}\nتعداد: {len(media_data['audios'])} عدد\n"
    send_to_topic('media_audios', audios_text)
    for audio in media_data['audios']:
        try:
            if audios_thread:
                bot.send_audio(GROUP_ID, audio['file_id'], caption=f"🎵 {audio.get('caption','')}", message_thread_id=audios_thread)
            else:
                bot.send_audio(GROUP_ID, audio['file_id'], caption=f"🎵 {audio.get('caption','')}")
        except:
            pass

    users_text = f"📋 لیست همه کاربران بات — {now}\n{'━'*25}\n"
    for admin_id in admins:
        try:
            user_info = bot.get_chat(int(admin_id))
            name = user_info.first_name or user_info.username or "ناشناس"
            username = f"@{user_info.username}" if user_info.username else "بدون یوزرنیم"
            rank = get_admin_number(int(admin_id)) or "Admin"
            users_text += f"🆔 {admin_id}\n👤 {name}\n📌 {username}\n🏷️ رنک: {rank}\n" + "─"*20 + "\n"
        except:
            pass
    for user_id_temp in all_users_data:
        if str(user_id_temp) not in admins:
            try:
                user_info = bot.get_chat(int(user_id_temp))
                name = user_info.first_name or user_info.username or "ناشناس"
                username = f"@{user_info.username}" if user_info.username else "بدون یوزرنیم"
                users_text += f"🆔 {user_id_temp}\n👤 {name}\n📌 {username}\n🏷️ رنک: کاربر عادی\n" + "─"*20 + "\n"
            except:
                pass
    if len(users_text) > 4000:
        parts = [users_text[i:i+4000] for i in range(0, len(users_text), 4000)]
        for part in parts:
            send_to_topic('users', part)
    else:
        send_to_topic('users', users_text)

    bot.send_message(sender_id, "✅ تمام اطلاعات بات با موفقیت به گروه بک‌آپ ارسال شد!")


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
load_media()
load_antivirus()
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
    is_member, channel_name, channel_link = is_user_in_channels(user_id)
    if is_founder(user_id) or is_owner(user_id):
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
        bot.send_message(user_id, "⛔ شما دسترسی ندارید!")
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
    for user_id_temp in all_users_data:
        if str(user_id_temp) not in admins:
            try:
                user_info = bot.get_chat(int(user_id_temp))
                name = user_info.first_name or user_info.username or "ناشناس"
                username = f"@{user_info.username}" if user_info.username else "بدون یوزرنیم"
                response += f"🆔 {user_id_temp}\n"
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

@bot.message_handler(commands=['cancel'])
def cancel_mode(msg):
    user_id = msg.from_user.id
    canceled = False
    if user_id in news_mode and news_mode[user_id]:
        news_mode[user_id] = False
        canceled = True
    if user_id in ad_mode and ad_mode[user_id]:
        ad_mode[user_id] = False
        canceled = True
    if user_id in broadcast_mode and broadcast_mode[user_id]:
        del broadcast_mode[user_id]
        canceled = True
    if user_id in console_mode and console_mode[user_id]:
        del console_mode[user_id]
        canceled = True
    if user_id in upload_mode:
        del upload_mode[user_id]
        canceled = True
    if user_id in restore_mode:
        del restore_mode[user_id]
        canceled = True
    if user_id in stealth_chat_mode:
        del stealth_chat_mode[user_id]
        canceled = True
    if user_id in admin_chat_mode and admin_chat_mode[user_id]:
        admin_chat_mode[user_id] = False
        canceled = True
    if canceled:
        bot.reply_to(msg, "✅ شما از حالت خارج شدید!")
    else:
        bot.reply_to(msg, "ℹ️ شما در هیچ حالتی نیستید!")

@bot.message_handler(commands=['getgroupid'])
def get_group_id(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    chat = msg.chat
    thread_id = msg.message_thread_id if msg.is_topic_message else None
    response = f"📊 اطلاعات چت:\n\n"
    response += f"🆔 chat_id: `{chat.id}`\n"
    response += f"📝 نوع: {chat.type}\n"
    if chat.title:
        response += f"📌 نام: {chat.title}\n"
    if thread_id:
        response += f"🧵 thread_id (تاپیک فعلی): `{thread_id}`\n"
    else:
        response += f"🧵 thread_id: این پیام توی تاپیک نیست (یا گروه Topic نداره)\n"
    response += f"\n📌 این مقادیر رو توی کد توی GROUP_ID و TOPIC_IDS پر کن."
    bot.reply_to(msg, response, parse_mode='Markdown')

@bot.message_handler(commands=['zipbackup'])
def zip_backup_command(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id):
        return
    bot.reply_to(msg, "⏳ در حال ساخت و ارسال بک‌آپ ZIP...")
    send_zip_backup(user_id)

# ========== پنل اصلی کاربران (شامل دکمه پنل مدیریت/ادمینی بسته به نقش) ==========
def build_main_user_markup(user_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton("📰 اخبار", callback_data="user_news")
    btn2 = telebot.types.InlineKeyboardButton("📢 تبلیغات", callback_data="user_ads")
    btn3 = telebot.types.InlineKeyboardButton("🤝 اتحادها", callback_data="user_alliances")
    btn4 = telebot.types.InlineKeyboardButton("📺 کانال‌ها", callback_data="user_channels")
    btn5 = telebot.types.InlineKeyboardButton("💰 حمایت‌ها", callback_data="user_donate")
    btn6 = telebot.types.InlineKeyboardButton("👑 تیم مدیریتی", callback_data="user_team")
    btn7 = telebot.types.InlineKeyboardButton("🎮 بازی‌ها", callback_data="user_games")
    btn8 = telebot.types.InlineKeyboardButton("📋 راهنما", callback_data="user_help")
    btn9 = telebot.types.InlineKeyboardButton("🎫 تیکت جدید", callback_data="user_new_ticket")
    btn10 = telebot.types.InlineKeyboardButton("🎬 Media's", callback_data="user_media")
    btn11 = telebot.types.InlineKeyboardButton("📅 تاریخ و ساعت", callback_data="user_datetime")
    btn12 = telebot.types.InlineKeyboardButton("⛏️ معدن", callback_data="user_mine")
    btn13 = telebot.types.InlineKeyboardButton("🍳 آشپزخانه", callback_data="user_kitchen")
    btn14 = telebot.types.InlineKeyboardButton("⚠️ گزارش مشکل", callback_data="user_report_issue")
    buttons = [btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12, btn13, btn14]
    if is_founder(user_id) or is_owner(user_id):
        buttons.append(telebot.types.InlineKeyboardButton("👑 پنل مدیریت", callback_data="open_management_panel"))
    elif is_admin(user_id):
        buttons.append(telebot.types.InlineKeyboardButton("⚙️ پنل ادمینی", callback_data="open_admin_panel"))
    markup.add(*buttons)
    return markup

def show_user_panel(user_id):
    bot.send_message(user_id, "🏠 پنل اصلی:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=build_main_user_markup(user_id))

def build_admin_panel_markup():
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn1 = telebot.types.InlineKeyboardButton("🎫 لیست تیکت‌ها", callback_data="admin_tickets")
    btn2 = telebot.types.InlineKeyboardButton("💬 چت ادمین‌ها", url="https://t.me/+W0cz_z1Zjko2MjRk")
    markup.add(btn1, btn2)
    return markup

# ========== کیبورد ثابت پایین صفحه ==========
# دکمه «پنل اصلی بات» همیشه هست و همیشه پنل کاربری عادی را باز می‌کند.
# بسته به نقش، یک دکمه دومِ اختصاصی هم اضافه می‌شود:
#   - ادمین معمولی  -> «⚙️ پنل ادمینی»
#   - سازنده/بنیانگذار -> «👑 پنل مدیریتی»
def build_main_reply_keyboard(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_main = telebot.types.KeyboardButton("🏠 پنل اصلی بات")
    markup.add(btn_main)
    if is_founder(user_id) or is_owner(user_id):
        btn_manage = telebot.types.KeyboardButton("👑 پنل مدیریتی")
        markup.add(btn_manage)
    elif is_admin(user_id):
        btn_admin = telebot.types.KeyboardButton("⚙️ پنل ادمینی")
        markup.add(btn_admin)
    return markup

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
    if not check_and_ask_join(user_id, msg):
        return
    bot.reply_to(msg, "🔰 سلام! به بات خوش آمدید!", reply_markup=build_main_reply_keyboard(user_id))
    show_user_panel(user_id)

# ========== پنل بنیانگذار ==========
def build_founder_markup():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton("📰 ارسال خبر", callback_data="founder_news")
    btn2 = telebot.types.InlineKeyboardButton("📢 ارسال تبلیغ", callback_data="founder_ad")
    btn3 = telebot.types.InlineKeyboardButton("🗑️ حذف خبر", callback_data="founder_delete_news")
    btn4 = telebot.types.InlineKeyboardButton("🗑️ حذف تبلیغ", callback_data="founder_delete_ad")
    btn5 = telebot.types.InlineKeyboardButton("💰 مدیریت حمایت‌ها", callback_data="founder_donate")
    btn6 = telebot.types.InlineKeyboardButton("🤝 مدیریت اتحادها", callback_data="founder_clans")
    btn7 = telebot.types.InlineKeyboardButton("⛔ مدیریت محرومیت", callback_data="founder_bans")
    btn8 = telebot.types.InlineKeyboardButton("👑 مدیریت ادمین‌ها", callback_data="founder_admins")
    btn9 = telebot.types.InlineKeyboardButton("🔄 آپدیت بات", callback_data="founder_update")
    btn10 = telebot.types.InlineKeyboardButton("📊 گزارش بات", callback_data="founder_botup")
    btn11 = telebot.types.InlineKeyboardButton("📢 ارسال به همه", callback_data="founder_broadcast")
    btn12 = telebot.types.InlineKeyboardButton("🖥️ کنسول", callback_data="founder_console")
    btn13 = telebot.types.InlineKeyboardButton("🎬 مدیریت Media", callback_data="founder_media")
    btn14 = telebot.types.InlineKeyboardButton("📋 لیست کاربران", callback_data="founder_all_users")
    av_status = "🟢 روشن" if antivirus_enabled else "🔴 خاموش"
    btn15 = telebot.types.InlineKeyboardButton(f"🛡 Antivirus ({av_status})", callback_data="founder_antivirus_toggle")
    btn16 = telebot.types.InlineKeyboardButton("🗄 بک‌آپ کامل ZIP", callback_data="founder_zip_backup")
    btn17 = telebot.types.InlineKeyboardButton("📥 بازیابی بک‌آپ ZIP", callback_data="founder_upload_zip_backup")
    btn18 = telebot.types.InlineKeyboardButton("🗄 DataBase", callback_data="founder_database")
    btn19 = telebot.types.InlineKeyboardButton("❓ ???", callback_data="founder_stealth_list")
    btn20 = telebot.types.InlineKeyboardButton("🎫 لیست تیکت‌ها", callback_data="admin_tickets")
    btn21 = telebot.types.InlineKeyboardButton("💬 چت ادمین‌ها", url="https://t.me/+W0cz_z1Zjko2MjRk")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11, btn12, btn13, btn14, btn15, btn16, btn17, btn18, btn19, btn20, btn21)
    return markup

def show_founder_panel(user_id):
    bot.send_message(user_id, "👑 پنل مدیریت بنیانگذار:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=build_founder_markup())

@bot.message_handler(commands=['fpanel'])
def founder_panel(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id):
        bot.reply_to(msg, "⛔ فقط بنیانگذار دسترسی دارد!")
        return
    show_founder_panel(user_id)

# ========== پنل سازنده ==========
def build_owner_markup():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton("📰 ارسال خبر", callback_data="owner_news")
    btn2 = telebot.types.InlineKeyboardButton("📢 ارسال تبلیغ", callback_data="owner_ad")
    btn3 = telebot.types.InlineKeyboardButton("🗑️ حذف خبر", callback_data="owner_delete_news")
    btn4 = telebot.types.InlineKeyboardButton("🗑️ حذف تبلیغ", callback_data="owner_delete_ad")
    btn5 = telebot.types.InlineKeyboardButton("💰 مدیریت حمایت‌ها", callback_data="owner_donate")
    btn6 = telebot.types.InlineKeyboardButton("🤝 مدیریت اتحادها", callback_data="owner_clans")
    btn7 = telebot.types.InlineKeyboardButton("⛔ مدیریت محرومیت", callback_data="owner_bans")
    btn8 = telebot.types.InlineKeyboardButton("👑 مدیریت ادمین‌ها", callback_data="owner_admins")
    btn9 = telebot.types.InlineKeyboardButton("🔄 آپدیت بات", callback_data="owner_update")
    btn11 = telebot.types.InlineKeyboardButton("📢 ارسال به همه", callback_data="owner_broadcast")
    btn12 = telebot.types.InlineKeyboardButton("🖥️ کنسول", callback_data="owner_console")
    btn13 = telebot.types.InlineKeyboardButton("🎬 مدیریت Media", callback_data="owner_media")
    btn14 = telebot.types.InlineKeyboardButton("📋 لیست کاربران", callback_data="owner_all_users")
    btn15 = telebot.types.InlineKeyboardButton("🎫 لیست تیکت‌ها", callback_data="admin_tickets")
    btn16 = telebot.types.InlineKeyboardButton("💬 چت ادمین‌ها", url="https://t.me/+W0cz_z1Zjko2MjRk")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn11, btn12, btn13, btn14, btn15, btn16)
    return markup

def show_owner_panel(user_id):
    bot.send_message(user_id, "👑 پنل مدیریت سازنده:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=build_owner_markup())

@bot.message_handler(commands=['opanel'])
def owner_panel(msg):
    user_id = msg.from_user.id
    if not is_owner(user_id):
        bot.reply_to(msg, "⛔ فقط سازنده دسترسی دارد!")
        return
    show_owner_panel(user_id)

@bot.message_handler(commands=['apanel'])
def admin_panel(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        bot.reply_to(msg, "⛔ شما دسترسی ادمین ندارید!")
        return
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    bot.reply_to(msg, "⚙️ پنل مدیریت ادمین:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=build_admin_panel_markup())

def show_games_menu(user_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn1 = telebot.types.InlineKeyboardButton("🪨 سنگ، کاغذ، قیچی", callback_data="game_rps")
    btn2 = telebot.types.InlineKeyboardButton("❌⭕ Tic Tac Toe", callback_data="game_ttt")
    btn3 = telebot.types.InlineKeyboardButton("🎲 بازی ۳", callback_data="game_coming_soon")
    btn4 = telebot.types.InlineKeyboardButton("🏆 بازی ۴", callback_data="game_coming_soon")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(user_id, "🎮 لیست بازی‌ها:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    global antivirus_enabled
    user_id = call.from_user.id
    data = call.data

    if data == "check_membership":
        if is_founder(user_id) or is_owner(user_id):
            bot.answer_callback_query(call.id, "✅ شما دسترسی کامل دارید!")
            return
        is_member, channel_name, channel_link = is_user_in_channels(user_id)
        if is_member:
            bot.send_message(user_id, "✅ عضویت شما در هر دو کانال تایید شد! حالا می‌توانید از بات استفاده کنید.", reply_markup=build_main_reply_keyboard(user_id))
            bot.answer_callback_query(call.id, "✅ عضویت تایید شد")
            show_user_panel(user_id)
        else:
            bot.answer_callback_query(call.id, "❌ شما هنوز در یکی از کانال‌ها عضو نشده‌اید!")
            bot.send_message(user_id, f"❌ شما هنوز در کانال {channel_name} عضو نشده‌اید!\nلطفاً ابتدا عضو شوید و سپس روی دکمه تایید کلیک کنید.")
        return

    if data == "check_membership_owner":
        if not is_founder(user_id) and not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ شما دسترسی ندارید!")
            return
        bot.send_message(user_id, "✅ دسترسی شما تایید شد! خوش آمدید.", reply_markup=build_main_reply_keyboard(user_id))
        bot.answer_callback_query(call.id, "✅ تایید شد")
        show_user_panel(user_id)
        return

    if data == "open_admin_panel":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما ادمین نیستید!")
            return
        bot.send_message(user_id, "⚙️ پنل ادمینی:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=build_admin_panel_markup())
        bot.answer_callback_query(call.id)
        return

    if data == "open_management_panel":
        if is_founder(user_id):
            show_founder_panel(user_id)
        elif is_owner(user_id):
            show_owner_panel(user_id)
        else:
            bot.answer_callback_query(call.id, "⛔ دسترسی ندارید!")
            return
        bot.answer_callback_query(call.id)
        return

    if data.startswith("stealth_open_"):
        if user_id != FOUNDER_ID:
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        target_id_str = data.replace("stealth_open_", "")
        try:
            target_id = int(target_id_str)
        except:
            bot.answer_callback_query(call.id, "❌ خطا!")
            return
        stealth_chat_mode[FOUNDER_ID] = target_id
        stealth_sessions[target_id_str] = True
        if target_id_str in pending_stealth:
            del pending_stealth[target_id_str]
        bot.send_message(FOUNDER_ID, f"✅ وارد چت مخفی با کاربر {target_id} شدید.\n📝 هر پیامی که بفرستید مستقیم و بدون نام برای او ارسال می‌شود.\n❌ برای خروج: /cancel")
        bot.answer_callback_query(call.id, "✅ وارد چت شدید")
        return

    if data == "founder_stealth_list":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        if not pending_stealth:
            bot.send_message(user_id, "📭 هیچ پیام جدیدی در انتظار نیست.")
            bot.answer_callback_query(call.id)
            return
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        for uid, info in pending_stealth.items():
            label = f"👤 {info.get('name','ناشناس')} | {uid}"
            btn = telebot.types.InlineKeyboardButton(label, callback_data=f"stealth_open_{uid}")
            markup.add(btn)
        bot.send_message(user_id, "❓ لیست پیام‌های در انتظار:\nروی هرکدام بزنید تا وارد چت مخفی با او شوید.", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data == "founder_news":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        bot.send_message(user_id, "✅ وارد حالت ارسال خبر شدید!\n📝 لطفاً متن خبر را ارسال کنید:\n❌ برای خروج: /cancel")
        news_mode[user_id] = True
        bot.answer_callback_query(call.id, "✅ لطفاً خبر را بفرستید")
        return

    if data == "founder_ad":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        bot.send_message(user_id, "✅ وارد حالت ارسال تبلیغ شدید!\n📝 لطفاً متن تبلیغ را ارسال کنید:\n❌ برای خروج: /cancel")
        ad_mode[user_id] = True
        bot.answer_callback_query(call.id, "✅ لطفاً تبلیغ را بفرستید")
        return

    if data == "founder_delete_news":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        if not news_data:
            bot.send_message(user_id, "📭 هیچ خبری برای حذف وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        response = "🗑️ لیست اخبار:\n\n"
        for news_id, news_text in news_data.items():
            response += f"📌 News {news_id}: {news_text[:50]}...\n"
        response += "\n📌 برای حذف: /hazfnews [شماره]"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
        return

    if data == "founder_delete_ad":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        if not ad_data:
            bot.send_message(user_id, "📭 هیچ تبلیغی برای حذف وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        response = "🗑️ لیست تبلیغات:\n\n"
        for ad_id, ad_text in ad_data.items():
            response += f"📌 Ad {ad_id}: {ad_text[:50]}...\n"
        response += "\n📌 برای حذف: /hazfad [شماره]"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
        return

    if data == "founder_donate":
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
        return

    if data == "founder_clans":
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
        return

    if data == "founder_create_clan":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        bot.send_message(user_id, "📝 لطفاً نام اتحاد را وارد کنید:\n/createclan [نام اتحاد]")
        bot.answer_callback_query(call.id)
        return

    if data == "founder_delete_clan":
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
        return

    if data == "founder_list_clans":
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
        return

    if data == "founder_bans":
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
        return

    if data == "founder_admins":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        av_status = "🟢 روشن" if antivirus_enabled else "🔴 خاموش"
        response = "📋 ليست ادمين ها:\n\n"
        response += f"🛡 نگهبان : GP-GUARD ( {av_status} )\n\n"
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
        return

    if data == "founder_update":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        bot.answer_callback_query(call.id, "🔄 در حال آپدیت...")
        perform_bot_update(user_id)
        return

    if data == "founder_botup":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        bot.answer_callback_query(call.id, "📊 در حال ارسال گزارش به گروه...")
        send_botup_report(user_id)
        send_backup_to_group(user_id)
        return

    if data == "founder_broadcast":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        broadcast_mode[user_id] = True
        bot.send_message(user_id, "📢 وارد حالت ارسال پیام به همه شدید!\n\n📝 هر پیامی که بفرستید، برای همه کاربران ارسال خواهد شد.\n❌ برای خروج: /cancel")
        bot.answer_callback_query(call.id, "✅ وارد حالت ارسال شدید")
        return

    if data == "founder_console":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        console_mode[user_id] = {'step': 'active'}
        bot.send_message(user_id, "🖥️ **وارد کنسول Hash شدید!**\n\n"
                                   "📝 هر متنی بنویسید، به صورت Hash (رشته‌ای از اعداد) برایتان نمایش داده می‌شود.\n"
                                   f"🔓 برای بازگردانی یک متن Hash شده: ابتدا عدد {CONSOLE_DECODE_TRIGGER} را بفرستید، سپس متن Hash شده را ارسال کنید.\n\n"
                                   "❌ برای خروج: /cancel")
        bot.answer_callback_query(call.id, "✅ وارد کنسول شدید")
        return

    if data == "founder_media":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton("📸 آپلود عکس", callback_data="founder_upload_photo")
        btn2 = telebot.types.InlineKeyboardButton("🎥 آپلود فیلم", callback_data="founder_upload_video")
        btn3 = telebot.types.InlineKeyboardButton("🎵 آپلود آهنگ", callback_data="founder_upload_audio")
        btn4 = telebot.types.InlineKeyboardButton("🗑️ حذف مدیا", callback_data="founder_delete_media")
        btn5 = telebot.types.InlineKeyboardButton("🔙 بازگشت", callback_data="founder_back")
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(user_id, "🎬 مدیریت Media:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data == "founder_upload_photo":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        upload_mode[user_id] = 'photo'
        bot.send_message(user_id, "📸 لطفاً عکس مورد نظر خود را ارسال کنید:\n❌ برای خروج: /cancel")
        bot.answer_callback_query(call.id, "✅ منتظر عکس هستم")
        return

    if data == "founder_upload_video":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        upload_mode[user_id] = 'video'
        bot.send_message(user_id, "🎥 لطفاً فیلم مورد نظر خود را ارسال کنید:\n❌ برای خروج: /cancel")
        bot.answer_callback_query(call.id, "✅ منتظر فیلم هستم")
        return

    if data == "founder_upload_audio":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        upload_mode[user_id] = 'audio'
        bot.send_message(user_id, "🎵 لطفاً آهنگ مورد نظر خود را ارسال کنید:\n❌ برای خروج: /cancel")
        bot.answer_callback_query(call.id, "✅ منتظر آهنگ هستم")
        return

    if data == "founder_delete_media":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        if not media_data['photos'] and not media_data['videos'] and not media_data['audios']:
            bot.send_message(user_id, "📭 هیچ مدیایی برای حذف وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        response = "🗑️ لیست مدیاها برای حذف:\n\n"
        if media_data['photos']:
            response += "📸 عکس‌ها:\n"
            for idx, item in enumerate(media_data['photos']):
                response += f"  {idx+1}. ID: {item['id']} - {item['caption']}\n"
        if media_data['videos']:
            response += "🎥 فیلم‌ها:\n"
            for idx, item in enumerate(media_data['videos']):
                response += f"  {idx+1}. ID: {item['id']} - {item['caption']}\n"
        if media_data['audios']:
            response += "🎵 آهنگ‌ها:\n"
            for idx, item in enumerate(media_data['audios']):
                response += f"  {idx+1}. ID: {item['id']} - {item['caption']}\n"
        response += "\n📌 برای حذف: /deletemedia [id]"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
        return

    if data == "founder_all_users":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        send_all_users_list(user_id)
        bot.answer_callback_query(call.id)
        return

    if data == "founder_back":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        show_founder_panel(user_id)
        bot.answer_callback_query(call.id)
        return

    if data == "founder_antivirus_toggle":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        antivirus_enabled = not antivirus_enabled
        save_antivirus()
        status_text = "🟢 روشن" if antivirus_enabled else "🔴 خاموش"
        try:
            bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=build_founder_markup())
        except:
            pass
        bot.answer_callback_query(call.id, f"🛡 Antivirus اکنون {status_text} است")
        return

    if data == "founder_zip_backup":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        bot.answer_callback_query(call.id, "⏳ در حال ساخت بک‌آپ...")
        send_zip_backup(user_id)
        return

    if data == "founder_upload_zip_backup":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        restore_mode[user_id] = True
        bot.send_message(user_id, "📥 لطفاً فایل بک‌آپ ZIP را ارسال کنید تا بازیابی شود.\n\n⚠️ توجه: با این کار، اطلاعات فعلی بات با اطلاعات داخل فایل ZIP جایگزین خواهد شد.\n❌ برای خروج: /cancel")
        bot.answer_callback_query(call.id, "📥 منتظر فایل ZIP هستم")
        return

    if data == "founder_database":
        if not is_founder(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط بنیانگذار!")
            return
        invite_link = get_database_invite_link()
        if invite_link:
            markup = telebot.types.InlineKeyboardMarkup()
            btn_join = telebot.types.InlineKeyboardButton("🗄 ورود به گروه دیتابیس", url=invite_link)
            markup.add(btn_join)
            bot.send_message(user_id, "🗄 برای ورود به گروه دیتابیس روی دکمه زیر بزنید:", reply_markup=markup)
            bot.send_message(user_id, f"📥 شما وارد گروه دیتابیس شدید!\n\n{get_iran_datetime_text()}")
        else:
            bot.send_message(user_id, "❌ خطا در ساخت لینک دعوت گروه دیتابیس!\nبررسی کنید بات در گروه ادمین با دسترسی «دعوت کاربران از طریق لینک» باشد.")
        bot.answer_callback_query(call.id, "🗄 DataBase")
        return

    if data == "owner_zip_backup" or data == "owner_upload_zip_backup":
        bot.answer_callback_query(call.id, "⛔ این بخش برای سازنده غیرفعال شده است!")
        return

    if data == "owner_news":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        bot.send_message(user_id, "✅ وارد حالت ارسال خبر شدید!\n📝 لطفاً متن خبر را ارسال کنید:\n❌ برای خروج: /cancel")
        news_mode[user_id] = True
        bot.answer_callback_query(call.id, "✅ لطفاً خبر را بفرستید")
        return

    if data == "owner_ad":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        bot.send_message(user_id, "✅ وارد حالت ارسال تبلیغ شدید!\n📝 لطفاً متن تبلیغ را ارسال کنید:\n❌ برای خروج: /cancel")
        ad_mode[user_id] = True
        bot.answer_callback_query(call.id, "✅ لطفاً تبلیغ را بفرستید")
        return

    if data == "owner_delete_news":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        if not news_data:
            bot.send_message(user_id, "📭 هیچ خبری برای حذف وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        response = "🗑️ لیست اخبار:\n\n"
        for news_id, news_text in news_data.items():
            response += f"📌 News {news_id}: {news_text[:50]}...\n"
        response += "\n📌 برای حذف: /hazfnews [شماره]"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
        return

    if data == "owner_delete_ad":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        if not ad_data:
            bot.send_message(user_id, "📭 هیچ تبلیغی برای حذف وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        response = "🗑️ لیست تبلیغات:\n\n"
        for ad_id, ad_text in ad_data.items():
            response += f"📌 Ad {ad_id}: {ad_text[:50]}...\n"
        response += "\n📌 برای حذف: /hazfad [شماره]"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
        return

    if data == "owner_donate":
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
        return

    if data == "owner_clans":
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
        return

    if data == "owner_create_clan":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        bot.send_message(user_id, "📝 لطفاً نام اتحاد را وارد کنید:\n/createclan [نام اتحاد]")
        bot.answer_callback_query(call.id)
        return

    if data == "owner_delete_clan":
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
        return

    if data == "owner_list_clans":
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
        return

    if data == "owner_bans":
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
        return

    if data == "owner_admins":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        av_status = "🟢 روشن" if antivirus_enabled else "🔴 خاموش"
        response = "📋 ليست ادمين ها:\n\n"
        response += f"🛡 نگهبان : GP-GUARD ( {av_status} )\n\n"
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
        return

    if data == "owner_update":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        bot.answer_callback_query(call.id, "🔄 در حال آپدیت...")
        perform_bot_update(user_id)
        return

    if data == "owner_botup":
        bot.answer_callback_query(call.id, "⛔ این بخش برای سازنده غیرفعال شده است!")
        return

    if data == "owner_broadcast":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        broadcast_mode[user_id] = True
        bot.send_message(user_id, "📢 وارد حالت ارسال پیام به همه شدید!\n\n📝 هر پیامی که بفرستید، برای همه کاربران ارسال خواهد شد.\n❌ برای خروج: /cancel")
        bot.answer_callback_query(call.id, "✅ وارد حالت ارسال شدید")
        return

    if data == "owner_console":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        console_mode[user_id] = {'step': 'waiting_code'}
        bot.send_message(user_id, "🔒 برای ورود به کنسول، لطفاً کد دسترسی را وارد کنید:\n❌ برای خروج: /cancel")
        bot.answer_callback_query(call.id, "🔒 کد دسترسی را وارد کنید")
        return

    if data == "owner_media":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton("📸 آپلود عکس", callback_data="owner_upload_photo")
        btn2 = telebot.types.InlineKeyboardButton("🎥 آپلود فیلم", callback_data="owner_upload_video")
        btn3 = telebot.types.InlineKeyboardButton("🎵 آپلود آهنگ", callback_data="owner_upload_audio")
        btn4 = telebot.types.InlineKeyboardButton("🗑️ حذف مدیا", callback_data="owner_delete_media")
        btn5 = telebot.types.InlineKeyboardButton("🔙 بازگشت", callback_data="owner_back")
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(user_id, "🎬 مدیریت Media:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data == "owner_upload_photo":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        upload_mode[user_id] = 'photo'
        bot.send_message(user_id, "📸 لطفاً عکس مورد نظر خود را ارسال کنید:\n❌ برای خروج: /cancel")
        bot.answer_callback_query(call.id, "✅ منتظر عکس هستم")
        return

    if data == "owner_upload_video":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        upload_mode[user_id] = 'video'
        bot.send_message(user_id, "🎥 لطفاً فیلم مورد نظر خود را ارسال کنید:\n❌ برای خروج: /cancel")
        bot.answer_callback_query(call.id, "✅ منتظر فیلم هستم")
        return

    if data == "owner_upload_audio":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        upload_mode[user_id] = 'audio'
        bot.send_message(user_id, "🎵 لطفاً آهنگ مورد نظر خود را ارسال کنید:\n❌ برای خروج: /cancel")
        bot.answer_callback_query(call.id, "✅ منتظر آهنگ هستم")
        return

    if data == "owner_delete_media":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        if not media_data['photos'] and not media_data['videos'] and not media_data['audios']:
            bot.send_message(user_id, "📭 هیچ مدیایی برای حذف وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        response = "🗑️ لیست مدیاها برای حذف:\n\n"
        if media_data['photos']:
            response += "📸 عکس‌ها:\n"
            for idx, item in enumerate(media_data['photos']):
                response += f"  {idx+1}. ID: {item['id']} - {item['caption']}\n"
        if media_data['videos']:
            response += "🎥 فیلم‌ها:\n"
            for idx, item in enumerate(media_data['videos']):
                response += f"  {idx+1}. ID: {item['id']} - {item['caption']}\n"
        if media_data['audios']:
            response += "🎵 آهنگ‌ها:\n"
            for idx, item in enumerate(media_data['audios']):
                response += f"  {idx+1}. ID: {item['id']} - {item['caption']}\n"
        response += "\n📌 برای حذف: /deletemedia [id]"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
        return

    if data == "owner_all_users":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        send_all_users_list(user_id)
        bot.answer_callback_query(call.id)
        return

    if data == "owner_back":
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "⛔ فقط سازنده!")
            return
        show_owner_panel(user_id)
        bot.answer_callback_query(call.id)
        return

    if data == "admin_tickets":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما ادمین نیستید!")
            return
        send_tickets_list(user_id)
        bot.answer_callback_query(call.id)
        return

    if data == "admin_back_to_main":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما ادمین نیستید!")
            return
        show_user_panel(user_id)
        bot.answer_callback_query(call.id, "✅ بازگشت به پنل اصلی")
        return

    if data.startswith("accept_ticket_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما ادمین نیستید!")
            return
        ticket_number = int(data.replace("accept_ticket_", ""))
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
            f"✅ تیکت {ticket_number} باز شد! شما در حالت چت با کاربر هستید. 💬\n"
            f"📌 برای پایان چت از دستور /cc استفاده کنید."
        )
        bot.answer_callback_query(call.id, "✅ تیکت باز شد")
        return

    if data == "user_news":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if not news_data:
            bot.send_message(user_id, "📭 هیچ خبری وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        for news_id in news_data.keys():
            btn = telebot.types.InlineKeyboardButton(f"خبر {news_id}", callback_data=f"news_item_{news_id}")
            markup.add(btn)
        bot.send_message(user_id, "📰 لیست اخبار:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data.startswith("news_item_"):
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        news_id = data.replace("news_item_", "")
        if news_id in news_data:
            bot.send_message(user_id, f"🔹 خبر {news_id}:\n\n{news_data[news_id]}")
        else:
            bot.send_message(user_id, "❌ این خبر وجود ندارد.")
        bot.answer_callback_query(call.id)
        return

    if data == "user_ads":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if not ad_data:
            bot.send_message(user_id, "📭 هیچ تبلیغی وجود ندارد.")
            bot.answer_callback_query(call.id)
            return
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        for ad_id in ad_data.keys():
            btn = telebot.types.InlineKeyboardButton(f"تبلیغ {ad_id}", callback_data=f"ad_item_{ad_id}")
            markup.add(btn)
        bot.send_message(user_id, "📢 لیست تبلیغات:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data.startswith("ad_item_"):
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        ad_id = data.replace("ad_item_", "")
        if ad_id in ad_data:
            bot.send_message(user_id, f"🔸 تبلیغ {ad_id}:\n\n{ad_data[ad_id]}")
        else:
            bot.send_message(user_id, "❌ این تبلیغ وجود ندارد.")
        bot.answer_callback_query(call.id)
        return

    if data == "user_alliances":
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
        return

    if data.startswith("clan_"):
        clan_name = data.replace("clan_", "")
        if clan_name in clans:
            bot.send_message(user_id, f"📋 توضیحات اتحاد «{clan_name}»:\n\n{clans[clan_name]['description']}")
        else:
            bot.send_message(user_id, "❌ این اتحاد وجود ندارد.")
        bot.answer_callback_query(call.id)
        return

    if data == "user_channels":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        for ch in REQUIRED_CHANNELS:
            btn = telebot.types.InlineKeyboardButton(ch['name'], url=ch['link'])
            markup.add(btn)
        bot.send_message(user_id, "📺 کانال‌های ما:\nبرای عضویت روی هرکدام کلیک کنید:", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data == "user_donate":
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
        return

    if data == "user_team":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        av_status = "🟢 روشن" if antivirus_enabled else "🔴 خاموش"
        response = "👑 تیم مدیریتی:\n\n"
        response += f"🛡 نگهبان : GP-GUARD ( {av_status} )\n\n"
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
        return

    if data == "user_games":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        show_games_menu(user_id)
        bot.answer_callback_query(call.id)
        return

    if data == "user_help":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        response = "📋 راهنمای کاربران:\n\n"
        response += "🏠 پنل اصلی: مشاهده همه امکانات\n"
        response += "🎮 بازی ها: بازی سنگ، کاغذ، قیچی و Tic Tac Toe\n"
        response += "🎫 تیکت جدید: ثبت سوال یا مشکل\n"
        response += "📅 تاریخ و ساعت: نمایش تاریخ و ساعت ایران\n"
        bot.send_message(user_id, response)
        bot.answer_callback_query(call.id)
        return

    if data == "user_datetime":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        bot.send_message(user_id, get_iran_datetime_text())
        bot.answer_callback_query(call.id)
        return

    if data == "user_mine":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        bot.send_message(user_id, "⛏️ بخش معدن\n\n🔧 این بخش هنوز درست نشده، لطفاً منتظر آپدیت بعدی بمانید.")
        bot.answer_callback_query(call.id)
        return

    if data == "user_kitchen":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        bot.send_message(user_id, "🍳 بخش آشپزخانه\n\n🔧 این بخش هنوز درست نشده، لطفاً منتظر آپدیت بعدی بمانید.")
        bot.answer_callback_query(call.id)
        return

    if data == "user_report_issue":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        bot.send_message(user_id, "⚠️ گزارش مشکل\n\n🔧 این بخش هنوز درست نشده لطفا منتظر آپدیت بعدی بمانید.")
        bot.answer_callback_query(call.id)
        return

    if data == "user_new_ticket":
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
        return

    if data == "user_media":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn1 = telebot.types.InlineKeyboardButton("📸 عکس‌ها", callback_data="user_media_photos")
        btn2 = telebot.types.InlineKeyboardButton("🎥 فیلم‌ها", callback_data="user_media_videos")
        btn3 = telebot.types.InlineKeyboardButton("🎵 آهنگ‌ها", callback_data="user_media_audios")
        btn4 = telebot.types.InlineKeyboardButton("🔙 بازگشت", callback_data="user_media_back")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(user_id, "🎬 Media's:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if data == "user_media_photos":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if not media_data['photos']:
            bot.send_message(user_id, "📭 هیچ عکسی موجود نیست.")
            bot.answer_callback_query(call.id)
            return
        for photo in media_data['photos']:
            try:
                bot.send_photo(user_id, photo['file_id'], caption=f"📸 {photo.get('caption', 'عکس')}")
            except:
                bot.send_message(user_id, f"❌ خطا در نمایش عکس: {photo.get('id')}")
        bot.answer_callback_query(call.id)
        return

    if data == "user_media_videos":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if not media_data['videos']:
            bot.send_message(user_id, "📭 هیچ فیلمی موجود نیست.")
            bot.answer_callback_query(call.id)
            return
        for video in media_data['videos']:
            try:
                bot.send_video(user_id, video['file_id'], caption=f"🎥 {video.get('caption', 'فیلم')}")
            except:
                bot.send_message(user_id, f"❌ خطا در نمایش فیلم: {video.get('id')}")
        bot.answer_callback_query(call.id)
        return

    if data == "user_media_audios":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if not media_data['audios']:
            bot.send_message(user_id, "📭 هیچ آهنگی موجود نیست.")
            bot.answer_callback_query(call.id)
            return
        for audio in media_data['audios']:
            try:
                bot.send_audio(user_id, audio['file_id'], caption=f"🎵 {audio.get('caption', 'آهنگ')}")
            except:
                bot.send_message(user_id, f"❌ خطا در نمایش آهنگ: {audio.get('id')}")
        bot.answer_callback_query(call.id)
        return

    if data == "user_media_back":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        show_user_panel(user_id)
        bot.answer_callback_query(call.id)
        return

    if data == "game_rps":
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
        return

    if data == "game_ttt":
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
        return

    if data == "game_coming_soon":
        bot.answer_callback_query(call.id, "⏳ Coming Soon ...")
        bot.send_message(user_id, "⏳ این بازی به زودی اضافه خواهد شد! ✨")
        return

    if data == "back_to_games":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        show_games_menu(user_id)
        bot.answer_callback_query(call.id)
        return

    if data == "create_room_menu":
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
        return

    if data == "create_room_no_pass":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if str(user_id) in game_players:
            bot.answer_callback_query(call.id, "❌ شما در حال حاضر در یک بازی هستید")
            return
        game_id = create_game(user_id)
        bot.send_message(user_id, f"✅ اتاق سنگ ، کاغذ ، قیچی شما ساخته شد !\n🆔 ایدی اتاق : {game_id}\n🔄 منتظر حریف باشید...")
        bot.answer_callback_query(call.id, "✅ اتاق ساخته شد")
        return

    if data == "create_room_with_pass":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if str(user_id) in game_players:
            bot.answer_callback_query(call.id, "❌ شما در حال حاضر در یک بازی هستید")
            return
        rps_password_temp[user_id] = {'game_id': None, 'step': 'waiting_password'}
        bot.send_message(user_id, "🔑 لطفاً رمز مورد نظر خود را وارد کنید:")
        bot.answer_callback_query(call.id, "🔑 لطفاً رمز را وارد کنید")
        return

    if data == "show_rooms_menu":
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
        return

    if data.startswith("join_room_"):
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        game_id = data.replace("join_room_", "")
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
        return

    if data == "leave_room_callback":
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
        return

    if data == "ttt_create_room_menu":
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
        return

    if data == "ttt_create_room_no_pass":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if str(user_id) in ttt_game_players:
            bot.answer_callback_query(call.id, "❌ شما در حال حاضر در یک بازی هستید")
            return
        game_id = create_ttt_game(user_id)
        bot.send_message(user_id, f"✅ اتاق Tic Tac Toe شما ساخته شد !\n🆔 ایدی اتاق : {game_id}\n🔄 منتظر حریف باشید...")
        bot.answer_callback_query(call.id, "✅ اتاق ساخته شد")
        return

    if data == "ttt_create_room_with_pass":
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        if str(user_id) in ttt_game_players:
            bot.answer_callback_query(call.id, "❌ شما در حال حاضر در یک بازی هستید")
            return
        ttt_password_temp[user_id] = {'game_id': None, 'step': 'waiting_password'}
        bot.send_message(user_id, "🔑 لطفاً رمز مورد نظر خود را وارد کنید:")
        bot.answer_callback_query(call.id, "🔑 لطفاً رمز را وارد کنید")
        return

    if data == "ttt_show_rooms":
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
        return

    if data.startswith("ttt_join_room_"):
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        game_id = data.replace("ttt_join_room_", "")
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
        return

    if data == "ttt_leave_room":
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
        return

    if data.startswith("ttt_move_"):
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "⛔ شما محروم هستید")
            return
        parts = data.split("_")
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
        return

    if data.startswith("rps_move_"):
        parts = data.split("_")
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
        return

    else:
        bot.answer_callback_query(call.id, "❌ این دکمه کار نمی‌کند!")
        bot.send_message(user_id, "❌ این دکمه کار نمی‌کند!\nلطفاً از دکمه‌های دیگر استفاده کنید.")
        return

@bot.message_handler(commands=['deletemedia'])
def delete_media(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        bot.reply_to(msg, "⛔ فقط بنیانگذار و سازنده دسترسی دارند!")
        return
    parts = msg.text.split()
    if len(parts) < 2:
        bot.reply_to(msg, "⚠️ لطفاً ID مدیا را وارد کنید: /deletemedia [id]")
        return
    media_id = parts[1]
    found = False
    for item in media_data['photos'][:]:
        if item['id'] == media_id:
            media_data['photos'].remove(item)
            found = True
            break
    if not found:
        for item in media_data['videos'][:]:
            if item['id'] == media_id:
                media_data['videos'].remove(item)
                found = True
                break
    if not found:
        for item in media_data['audios'][:]:
            if item['id'] == media_id:
                media_data['audios'].remove(item)
                found = True
                break
    if found:
        save_media()
        bot.reply_to(msg, f"✅ مدیا با ID {media_id} حذف شد.")
    else:
        bot.reply_to(msg, f"❌ مدیا با ID {media_id} پیدا نشد.")

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

def send_botup_report(user_id):
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
    response += "\n🎬 لیست مدیاها:\n"
    response += f"  📸 عکس‌ها: {len(media_data['photos'])} عدد\n"
    response += f"  🎥 فیلم‌ها: {len(media_data['videos'])} عدد\n"
    response += f"  🎵 آهنگ‌ها: {len(media_data['audios'])} عدد\n"
    bot.send_message(user_id, response)

@bot.message_handler(commands=['botup'])
def botup(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id):
        return
    send_botup_report(user_id)

def perform_bot_update(user_id):
    all_users = set()
    for user_id_temp in waiting_for_message.keys():
        all_users.add(user_id_temp)
    for user_id_temp in tickets.keys():
        all_users.add(user_id_temp)
    for user_id_temp in chat_sessions.keys():
        all_users.add(user_id_temp)
    for user_id_temp in user_ticket_status.keys():
        all_users.add(user_id_temp)
    for admin_id in admins.keys():
        try:
            all_users.add(int(admin_id))
        except:
            pass
    for banned_id in banned_users.keys():
        try:
            all_users.add(int(banned_id))
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

@bot.message_handler(commands=['update'])
def update_bot(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    perform_bot_update(user_id)

@bot.message_handler(commands=['show_perms'])
def show_perms(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id) and not is_admin(user_id):
        return
    response = "📋 جدول دسترسي ها:\n\n"
    response += "👑 بنیانگذار (Founder):\n"
    response += "  ✅ همه دستورات\n"
    response += "  ✅ بدون نياز به تاييد\n\n"
    response += "👑 سازنده (Owner):\n"
    response += "  ✅ اکثر دستورات مدیریتی\n"
    response += "  ⛔ بدون دسترسی به بک‌آپ / گزارش بات / دیتابیس / چت مخفی\n\n"
    response += "🛡️ Admin (ادمین معمولی):\n"
    response += "  ✅ /tickets\n"
    response += "  ✅ /open\n"
    response += "  ✅ /a\n"
    response += "  ✅ /cc\n"
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

def send_tickets_list(user_id):
    open_tickets = []
    for ticket_num, ticket_data in tickets.items():
        user_id_ticket = ticket_data['user_id']
        if user_id_ticket not in chat_sessions or chat_sessions[user_id_ticket] != 'open':
            open_tickets.append((ticket_num, ticket_data))
    if not open_tickets:
        bot.send_message(user_id, "📭 هیچ تیکتی وجود ندارد.")
        return
    for ticket_num, data in open_tickets:
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn_accept = telebot.types.InlineKeyboardButton("✅ قبول تیکت", callback_data=f"accept_ticket_{ticket_num}")
        markup.add(btn_accept)
        response = f"🎫 **شماره تیکت:** {ticket_num}\n"
        response += f"━━━━━━━━━━━━━━━━━━━━\n"
        response += f"👤 **نام:** {data['first_name']}\n"
        response += f"📌 **یوزرنیم:** @{data['username']}\n"
        response += f"🆔 **آیدی:** {data['user_id']}\n"
        response += f"📝 **سوال:**\n{data['question']}\n"
        response += f"━━━━━━━━━━━━━━━━━━━━"
        bot.send_message(user_id, response, reply_markup=markup)

@bot.message_handler(commands=['tickets'])
def show_tickets(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        return
    send_tickets_list(user_id)

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
        bot.reply_to(msg, "⚠️ لطفاً پیام خود را وارد کنید: /a [پیام]")
        return
    admin_chat_mode[user_id] = True
    found_user = None
    for user_id_chat, status in chat_sessions.items():
        if status == 'open':
            found_user = user_id_chat
            break
    if found_user:
        bot.send_message(found_user, f"⚜ **پاسخ ادمین:**\n{parts[1]}")
        bot.reply_to(msg, f"✅ پیام ارسال شد! شما در حالت چت هستید.\n📌 برای ارسال پیام بعدی، فقط متن را تایپ کنید (نیازی به /a نیست).\n❌ برای خروج: /cancel")
    else:
        bot.reply_to(msg, "❌ چت فعالی وجود ندارد!")

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
    response += "📌 /a [پيام] : ارسال پاسخ به کاربر (وارد حالت چت میشوید)\n"
    response += "📌 /cc : پايان چت با کاربر\n"
    if is_founder(user_id) or is_owner(user_id):
        response += "📌 /ma [آيدي] : اضافه کردن ادمين جديد\n"
        response += "📌 /kickadmin [آيدي] : حذف ادمين\n"
        response += "📌 /ban [آيدي] : محروم کردن کاربر\n"
        response += "📌 /unban [آيدي] : رفع محروميت کاربر\n"
    if is_founder(user_id):
        response += "📌 /zipbackup : ساخت و ارسال بک‌آپ کامل ZIP\n"
        response += "📌 /botup : گزارش کامل بات\n"
    response += "📌 /ac : ورود/خروج از چت ادمين ها\n"
    response += "📌 /getgroupid : گرفتن آیدی گروه و تاپیک (فقط توی گروه)\n"
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
    bot.reply_to(msg, "✅ از دکمه «ارسال خبر» در پنل استفاده کنید.")

@bot.message_handler(commands=['ad'])
def ad_command(msg):
    user_id = msg.from_user.id
    if not is_founder(user_id) and not is_owner(user_id):
        return
    bot.reply_to(msg, "✅ از دکمه «ارسال تبلیغ» در پنل استفاده کنید.")

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

# ========== هندلر دکمه‌های ثابت کیبورد پایین صفحه ==========
@bot.message_handler(func=lambda m: m.text == "🏠 پنل اصلی بات")
def main_panel_button_handler(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    # این دکمه همیشه پنل کاربری عادی را باز می‌کند، فارغ از نقش کاربر
    show_user_panel(user_id)

@bot.message_handler(func=lambda m: m.text == "👑 پنل مدیریتی")
def management_panel_button_handler(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    if is_founder(user_id):
        show_founder_panel(user_id)
    elif is_owner(user_id):
        show_owner_panel(user_id)
    else:
        bot.reply_to(msg, "⛔ شما دسترسی به این پنل را ندارید!")

@bot.message_handler(func=lambda m: m.text == "⚙️ پنل ادمینی")
def admin_panel_button_handler(msg):
    user_id = msg.from_user.id
    if is_banned(user_id):
        bot.reply_to(msg, "⛔ *** [ Ban.System ] : شما از بات محروم شدید ***")
        return
    if is_founder(user_id):
        show_founder_panel(user_id)
    elif is_owner(user_id):
        show_owner_panel(user_id)
    elif is_admin(user_id):
        bot.send_message(user_id, "⚙️ پنل ادمینی:\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=build_admin_panel_markup())
    else:
        bot.reply_to(msg, "⛔ شما دسترسی به این پنل را ندارید!")

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'audio', 'document'])
def handle_messages(msg):
    user_id = msg.from_user.id

    if user_id in console_mode:
        step = console_mode[user_id].get('step')
        if step == 'waiting_code':
            entered_code = (msg.text or "").strip()
            if entered_code == CONSOLE_ACCESS_CODE:
                console_mode[user_id] = {'step': 'active'}
                bot.reply_to(msg, "✅ کد صحیح بود! وارد کنسول Hash شدید.\n\n"
                                   "📝 هر متنی بنویسید، به صورت Hash نمایش داده می‌شود.\n"
                                   f"🔓 برای بازگردانی: ابتدا عدد {CONSOLE_DECODE_TRIGGER} را بفرستید، سپس متن Hash شده را ارسال کنید.\n\n"
                                   "❌ برای خروج: /cancel")
            else:
                bot.reply_to(msg, "❌ کد اشتباه است!\nلطفاً دوباره تلاش کنید یا برای خروج /cancel را بزنید.")
            return
        if step == 'active':
            text_in = msg.text or ""
            if text_in.strip() == CONSOLE_DECODE_TRIGGER:
                console_mode[user_id]['step'] = 'waiting_decode'
                bot.reply_to(msg, "🔓 حالا متن Hash شده را ارسال کنید تا برایتان بازگردانده شود:")
                return
            hashed = hash_text(text_in)
            bot.reply_to(msg, f"🔐 **متن Hash شده:**\n`{hashed}`")
            return
        if step == 'waiting_decode':
            text_in = msg.text or ""
            decoded = unhash_text(text_in)
            console_mode[user_id]['step'] = 'active'
            if decoded is not None:
                bot.reply_to(msg, f"🔓 **متن بازگردانی‌شده:**\n{decoded}")
            else:
                bot.reply_to(msg, "❌ فرمت Hash نامعتبر است! دوباره تلاش کنید.")
            return

    # ========== بنیانگذار در حالت چت مخفی است ==========
    if user_id == FOUNDER_ID and FOUNDER_ID in stealth_chat_mode:
        if msg.content_type == 'text' and msg.text and not msg.text.startswith('/'):
            target_id = stealth_chat_mode[FOUNDER_ID]
            try:
                bot.send_message(target_id, msg.text)
                bot.reply_to(msg, "✅ ارسال شد (مخفی).")
            except Exception as e:
                bot.reply_to(msg, f"❌ خطا در ارسال: {e}")
            return

    # ========== حالت بازیابی بک‌آپ ZIP (فقط بنیانگذار) ==========
    if user_id in restore_mode and restore_mode[user_id]:
        if not is_founder(user_id):
            del restore_mode[user_id]
            return
        if msg.content_type != 'document':
            bot.reply_to(msg, "❌ لطفاً یک فایل ZIP ارسال کنید!\n❌ برای خروج: /cancel")
            return
        file_name = msg.document.file_name or ""
        if not file_name.lower().endswith('.zip'):
            bot.reply_to(msg, "❌ فایل ارسالی باید با فرمت ZIP باشد!\n❌ برای خروج: /cancel")
            return
        bot.reply_to(msg, "⏳ در حال دریافت و بازیابی فایل بک‌آپ... لطفاً صبر کنید ⏳")
        try:
            restore_backup_zip(msg, user_id)
        except Exception as e:
            bot.send_message(user_id, f"❌ خطا در بازیابی بک‌آپ: {e}")
        del restore_mode[user_id]
        return

    if user_id in upload_mode:
        media_type = upload_mode[user_id]
        if media_type == 'photo' and msg.content_type == 'photo':
            file_id = msg.photo[-1].file_id
            media_data['photos'].append({
                'id': str(len(media_data['photos']) + 1),
                'file_id': file_id,
                'caption': msg.caption or f"عکس {len(media_data['photos']) + 1}",
                'date': str(datetime.now())
            })
            save_media()
            del upload_mode[user_id]
            bot.reply_to(msg, "✅ عکس با موفقیت آپلود شد!")
            return
        elif media_type == 'video' and msg.content_type == 'video':
            file_id = msg.video.file_id
            media_data['videos'].append({
                'id': str(len(media_data['videos']) + 1),
                'file_id': file_id,
                'caption': msg.caption or f"فیلم {len(media_data['videos']) + 1}",
                'date': str(datetime.now())
            })
            save_media()
            del upload_mode[user_id]
            bot.reply_to(msg, "✅ فیلم با موفقیت آپلود شد!")
            return
        elif media_type == 'audio' and msg.content_type == 'audio':
            file_id = msg.audio.file_id
            media_data['audios'].append({
                'id': str(len(media_data['audios']) + 1),
                'file_id': file_id,
                'caption': msg.caption or f"آهنگ {len(media_data['audios']) + 1}",
                'date': str(datetime.now())
            })
            save_media()
            del upload_mode[user_id]
            bot.reply_to(msg, "✅ آهنگ با موفقیت آپلود شد!")
            return
        else:
            bot.reply_to(msg, f"❌ لطفاً یک {media_type} معتبر ارسال کنید!")
            return

    if user_id in broadcast_mode and broadcast_mode[user_id]:
        all_users = set()
        for user_id_temp in waiting_for_message.keys():
            all_users.add(user_id_temp)
        for user_id_temp in tickets.keys():
            all_users.add(user_id_temp)
        for user_id_temp in chat_sessions.keys():
            all_users.add(user_id_temp)
        for user_id_temp in user_ticket_status.keys():
            all_users.add(user_id_temp)
        for admin_id in admins.keys():
            try:
                all_users.add(int(admin_id))
            except:
                pass
        for banned_id in banned_users.keys():
            try:
                all_users.add(int(banned_id))
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
            if msg.text and not msg.text.startswith('/'):
                found_user = None
                for user_id_chat, status in chat_sessions.items():
                    if status == 'open':
                        found_user = user_id_chat
                        break
                if found_user:
                    bot.send_message(found_user, f"⚜ **پاسخ ادمین:**\n{msg.text}")
                    bot.reply_to(msg, "✅ پیام ارسال شد!")
                else:
                    bot.reply_to(msg, "❌ چت فعالی وجود ندارد!")
                return
        # ========== به جای باز کردن خودکار پنل، فقط راهنمایی به دکمه کیبورد ==========
        if msg.text and not msg.text.startswith('/'):
            if is_founder(user_id) or is_owner(user_id):
                bot.reply_to(msg, "ℹ️ برای دسترسی به پنل مدیریتی، روی دکمه «👑 پنل مدیریتی» در کیبورد پایین صفحه کلیک کنید.\n📌 برای پنل کاربری عادی: «🏠 پنل اصلی بات»")
            else:
                bot.reply_to(msg, "ℹ️ برای دسترسی به پنل ادمینی، روی دکمه «⚙️ پنل ادمینی» در کیبورد پایین صفحه کلیک کنید.\n📌 برای پنل کاربری عادی: «🏠 پنل اصلی بات»")
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
        # ========== سیستم چت مخفی برای کاربران عادی + راهنمایی به پنل ==========
        if msg.content_type == 'text' and msg.text and not msg.text.startswith('/'):
            uid_str = str(user_id)
            if stealth_sessions.get(uid_str):
                try:
                    bot.send_message(FOUNDER_ID, f"💬 [چت مخفی] {msg.from_user.first_name} (@{msg.from_user.username}):\n{msg.text}")
                except:
                    pass
            else:
                pending_stealth[uid_str] = {
                    'name': msg.from_user.first_name or 'ناشناس',
                    'username': msg.from_user.username or ''
                }
                markup = telebot.types.InlineKeyboardMarkup()
                btn = telebot.types.InlineKeyboardButton("???", callback_data=f"stealth_open_{user_id}")
                markup.add(btn)
                try:
                    bot.send_message(FOUNDER_ID, f"📩 پیام جدید:\n👤 نام: {msg.from_user.first_name} (@{msg.from_user.username}) | آیدی: {user_id}\n📝 متن: {msg.text}", reply_markup=markup)
                except:
                    pass
            # راهنمایی به کاربر عادی برای استفاده از پنل اصلی بات
            bot.reply_to(msg, "ℹ️ برای باز کردن پنل اصلی بات، لطفاً روی دکمه «🏠 پنل اصلی بات» در پایین صفحه کلیک کنید.")

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
