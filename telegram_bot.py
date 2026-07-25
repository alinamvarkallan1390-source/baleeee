# -*- coding: utf-8 -*-
"""
ربات تلگرام - نسخه تک‌فایل برای هاست
روش اتصال: پولینگ (polling) با getUpdates
پنل ادمین حرفه‌ای با رمز: ali
تمام قابلیت‌های مدل بازی در یک فایل
"""

import urllib.request
import urllib.parse
import json
import os
import time
import random
from typing import Dict, Any

# ======================= تنظیمات =======================
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # ← توکن ربات تلگرام خود را جایگزین کنید
BOT_URL = f"https://api.telegram.org/bot{TOKEN}/"
DATA_FILE = "telegram_players.json"
CLANS_FILE = "telegram_clans.json"
PENDING_FILE = "telegram_pending.json"

# رمز پنل ادمین حرفه‌ای
ADMIN_PASSWORD = "ali"

# ادمین‌ها (بر اساس نام کاربری یا عدد)
ADMINS = ["admin_username", 1570690274]

# اقتصاد
DEFAULT_COINS = 1000
DEFAULT_GEMS = 10
DEFAULT_XP = 0

# ماینر
MINER_MAX_LEVEL = 1000
MINER_BASE_PER_LEVEL = 100
MINER_TYPES = ["سنگی", "آهنی", "طلایی", "افسانه‌ای"]

# بانک
BANK_SHORT_RATE = 0.05
BANK_LONG_RATE = 0.12

# مبارزه
PVP_STAKE = 100
PVE_STAKE = 80

# ضدتقلب
MAX_COINS_HOUR = 50000

# ======================= API تلگرام (پولینگ) =======================

def api_request(method: str, params: dict = None) -> dict:
    url = BOT_URL + method
    safe = {}
    if params:
        for k, v in params.items():
            if k in ("reply_markup", "keyboard", "inline_keyboard"):
                safe[k] = json.dumps(v, ensure_ascii=False)
            else:
                safe[k] = v
    try:
        if safe:
            query = urllib.parse.urlencode(safe, doseq=True)
            full = url + "?" + query
            req = urllib.request.Request(full, headers={"Content-Type": "application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req, timeout=30) as r:
                text = r.read()
        else:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as r:
                text = r.read()
        try:
            return json.loads(text)
        except Exception:
            return {}
    except Exception as e:
        print("API Error:", e)
        return {}

def get_updates(offset=None, timeout=20):
    p = {"timeout": timeout}
    if offset is not None:
        p["offset"] = offset
    return api_request("getUpdates", p)

def send_message(chat_id, text, reply_markup=None):
    p = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup is not None:
        p["reply_markup"] = reply_markup
    return api_request("sendMessage", p)

def get_me():
    return api_request("getMe")

# ======================= پایگاه داده =======================

def load_json(fname, default):
    if not os.path.exists(fname):
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
    with open(fname, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return default

def save_json(fname, data):
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

players = load_json(DATA_FILE, {})
clans = load_json(CLAN_FILE, {})
pending = load_json(PENDING_FILE, [])

def save_all():
    save_json(DATA_FILE, players)
    save_json(PENDING_FILE, pending)

# ======================= ساختار کاربر =======================

def ensure_user_struct(user_id):
    uid = str(user_id)
    if uid not in players:
        players[uid] = {
            "name": None,
            "username": None,
            "coins": DEFAULT_COINS,
            "gems": DEFAULT_GEMS,
            "xp": DEFAULT_XP,
            "level": 1,
            "started": False,
            "step": None,
            "admin_step": None,
            "admin_logged": False,
            "store_coins": 0,
            "store_gems": 0,
            "vip_days": 0,
            "gift_codes": [],
            "gift_cards": [],
            "spin_wins": 0,
            "spin_used_today": False,
            "daily_streak": 0,
            "last_streak_day": 0,
            "weekly_claimed": False,
            "monthly_claimed": False,
            "income_mission": 0,
            "avatar": None,
            "bio": "",
            "frame": None,
            "title": "تازه‌وارد",
            "badges": [],
            "join_date": int(time.time()),
            "stats": {"wins": 0, "losses": 0, "battles": 0, "miners_collected": 0, "clan": None},
            "miner_level": 0,
            "miner_type": "سنگی",
            "miner_fuel": 100,
            "miner_speed": 1,
            "miner_accelerator": 0,
            "miner_auto": False,
            "miner_offline": False,
            "miner_last_collect": 0,
            "miner_golden_unlocked": False,
            "miner_legendary_unlocked": False,
            "bank_amount": 0,
            "bank_time": 0,
            "bank_loan": 0,
            "bank_loan_due": 0,
            "bank_insurance": False,
            "pvp_wins": 0,
            "pve_wins": 0,
            "boss_wins": 0,
            "group_war_wins": 0,
            "duel_wins": 0,
            "league_points": 0,
            "clan": None,
            "clan_role": "عضو",
            "inventory": {},
            "pets": {},
            "purchased": [],
            "friends": [],
            "blocked": [],
            "friend_requests": [],
            "market_listings": [],
            "job": None,
            "job_level": 1,
            "cities_visited": ["شهر اصلی"],
            "territory": "شهر اصلی",
            "notifications": [],
            "logs": [],
            "prestige": 0,
            "loyalty_points": 0,
            "event_bonus_active": False,
            "requests": [],
        }
        save_all()

# ======================= ادمین حرفه‌ای =======================

def is_admin_by_name(name: str) -> bool:
    if not name:
        return False
    for a in ADMINS:
        if isinstance(a, str) and a.lower() == name.lower():
            return True
    return False

def is_admin_num(user_id) -> bool:
    try:
        return int(user_id) in [x for x in ADMINS if isinstance(x, int)]
    except:
        return False

def check_admin_access(user_id, user_name=None) -> bool:
    return is_admin_by_name(user_name or "") or is_admin_num(user_id)

# ======================= منوها =======================

def kb_main(is_admin=False):
    kb = [
        ["💰 اقتصاد بازی", "👤 پروفایل"],
        ["⛏️ ماینر", "🏦 بانک"],
        ["⚔️ مبارزه", "🏰 کلن"],
        ["🎯 ماموریت", "🏆 لیدربرد"],
        ["🎁 آیتم", "🐶 حیوانات"],
        ["🛍 فروشگاه", "🎉 رویدادها"],
        ["👥 اجتماعی", "📈 بازار"],
        ["🎮 مینی‌گیم", "💼 شغل"],
        ["🌍 نقشه", "🤖 سیستم‌ها"],
        ["💎 درآمدزایی", "🌟 اعتیادآور"],
    ]
    if is_admin:
        kb.append(["🔧 پنل ادمین حرفه‌ای"])
    kb.append(["❓ راهنما", "🔙 خروج"])
    return {"keyboard": kb, "resize_keyboard": True}

def kb_back_only():
    return {"keyboard": [["🔙 بازگشت"]], "resize_keyboard": True}

def kb_economy():
    return {"keyboard": [
        ["🛒 فروشگاه سکه", "💎 خرید جم"],
        ["🎁 بسته‌های ویژه", "💳 خرید VIP"],
        ["🎟 کد هدیه", "🎫 گیفت کارت"],
        ["🎲 گردونه شانس", "🎰 اسلات"],
        ["🎁 جایزه روزانه", "📆 هفتگی"],
        ["📅 ماهانه", "🔥 استریک"],
        ["💰 ماموریت درآمدی", "🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_profile():
    return {"keyboard": [
        ["🖼 آواتار", "📸 قاب پروفایل"],
        ["📝 بیو", "🏷 عنوان اختصاصی"],
        ["📊 سطح و XP", "🏅 نشان‌ها"],
        ["📅 تاریخ عضویت", "📈 آمار کامل"],
        ["🏆 رکوردها", "🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_miner():
    return {"keyboard": [
        ["📥 جمع‌آوری", "🔼 ارتقا"],
        ["⛽ سوخت", "⚡ سرعت"],
        ["🚀 شتاب‌دهنده", "🔧 تعمیر"],
        ["🤖 اتوماتیک", "💤 آفلاین"],
        ["🌟 طلایی", "🐉 افسانه‌ای"],
        ["🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_bank():
    return {"keyboard": [
        ["⏱ سپرده کوتاه", "⏳ بلندمدت"],
        ["💵 وام", "📊 سود متغیر"],
        ["📈 صندوق سرمایه", "🛡 بیمه"],
        ["💼 گاوصندوق", "🏦 انتقال بانکی"],
        ["🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_combat():
    return {"keyboard": [
        ["⚔️ PvP", "🐉 PvE"],
        ["👑 باس فایت", "👥 جنگ گروهی"],
        ["⚡ دوئل", "🏅 لیگ"],
        ["🏆 تورنمنت", "🎲 نبرد تصادفی"],
        ["📊 نبرد رتبه‌ای", "🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_clan():
    return {"keyboard": [
        ["🏗 ساخت کلن", "👥 عضوگیری"],
        ["💬 چت کلن", "📈 ارتقا"],
        ["💰 خزانه", "⚔️ جنگ کلن"],
        ["🎯 ماموریت کلن", "📊 رتبه کلن"],
        ["🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_missions():
    return {"keyboard": [
        ["📋 روزانه", "📅 هفتگی"],
        ["📆 ماهانه", "🌸 فصلی"],
        ["🔍 مخفی", "⭐ ویژه"],
        ["🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_leaderboard():
    return {"keyboard": [
        ["💰 ثروتمندترین", "📊 بیشترین لول"],
        ["⛏ بهترین ماینر", "🏆 بیشترین برد"],
        ["🏰 بهترین کلن", "📢 بیشترین دعوت"],
        ["🔥 بیشترین فعالیت", "🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_items():
    return {"keyboard": [
        ["⚡ بوستر", "🛡 سپر"],
        ["💣 بمب", "🎁 جعبه شانس"],
        ["🔑 کلید", "📦 صندوق"],
        ["🐾 پت", "👕 لباس"],
        ["🎨 اسکین", "✨ افکت"],
        ["🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_pets():
    return {"keyboard": [
        ["🐕 خرید پت", "📈 ارتقا پت"],
        ["🍖 غذا", "⭐ تجربه"],
        ["💪 مهارت", "🎲 کمیاب"],
        ["🐉 افسانه‌ای", "🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_shop():
    return {"keyboard": [
        ["🎁 آیتم", "🎨 اسکین"],
        ["💎 VIP", "⚡ بوستر"],
        ["📦 جعبه", "💰 بسته اقتصادی"],
        ["🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_events():
    return {"keyboard": [
        ["🎄 کریسمس", "🌸 نوروز"],
        ["🍉 یلدا", "🌙 رمضان"],
        ["🛒 جمعه سیاه", "🎃 هالووین"],
        ["🎉 آخر هفته", "🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_social():
    return {"keyboard": [
        ["💬 چت خصوصی", "👥 دوستان"],
        ["🚫 بلاک", "📨 دعوت"],
        ["🎁 ارسال هدیه", "📩 درخواست دوستی"],
        ["👀 مشاهده پروفایل", "🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_market():
    return {"keyboard": [
        ["📈 خرید و فروش", "🏷 مزایده"],
        ["💱 بازار آزاد", "⏰ قیمت لحظه‌ای"],
        ["💸 مالیات معامله", "🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_minigames():
    return {"keyboard": [
        ["✊ سنگ کاغذ قیچی", "🎲 حدس عدد"],
        ["🎲 دوز", "♟ شطرنج"],
        ["🎲 تاس", "🎰 رولت"],
        ["♠ بلک جک", "🧠 حافظه"],
        ["⚡ مسابقه سرعت", "🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_jobs():
    return {"keyboard": [
        ["⛏ معدنچی", "🌾 کشاورز"],
        ["💼 تاجر", "💻 برنامه‌نویس"],
        ["👮 پلیس", "⚕ پزشک"],
        ["📈 سرمایه‌گذار", "🚀 کارآفرین"],
        ["🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_map():
    return {"keyboard": [
        ["🏙 شهرها", "✈ سفر"],
        ["🎯 مأموریت شهری", "⛏ منابع"],
        ["🗺 سرزمین", "🏁 فتح مناطق"],
        ["🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_systems():
    return {"keyboard": [
        ["🔔 اعلان", "🛡 ضدتقلب"],
        ["📜 لاگ کامل", "💾 بکاپ"],
        ["📢 گزارش", "⚙ تنظیمات بازی"],
        ["📊 اقتصاد پویا", "🌐 API"],
        ["🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_monetization():
    return {"keyboard": [
        ["💎 خرید سکه", "💎 خرید جم"],
        ["🎖 اشتراک VIP", "📢 تبلیغات"],
        ["🤝 اسپانسر", "📢 مأموریت تبلیغاتی"],
        ["📺 همکاری کانال", "💰 فروش آیتم"],
        ["🎨 فروش اسکین", "🎟 Battle Pass"],
        ["🍀 Lucky Pass", "🌸 Season Pass"],
        ["🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_addictive():
    return {"keyboard": [
        ["🔥 استریک ورود", "🎲 چرخ شانس"],
        ["📦 جعبه ۶ ساعت", "🎲 مأموریت تصادفی"],
        ["🎉 رویداد محدود", "🏅 دستاوردها"],
        ["🧩 کلکسیون", "💎 امتیاز وفاداری"],
        ["♾ لول بی‌نهایت", "🔄 Prestige"],
        ["🔙 بازگشت"]
    ], "resize_keyboard": True}

def kb_admin():
    return {"keyboard": [
        ["➕ دادن سکه", "➖ گرفتن سکه"],
        ["💎 دادن جم", "📣 پیام همگانی"],
        ["🪙 سکه همگانی", "📊 آمار کاربران"],
        ["📁 لاگ سیستم", "⚙ تنظیمات بازی"],
        ["🛡 ضدتقلب", "💾 بکاپ دستی"],
        ["🔴 خروج از ادمین", "🔙 بازگشت اصلی"]
    ], "resize_keyboard": True}

# ======================= منطق اقتصاد =======================

def handle_economy(user_id, chat_id, btn):
    uid = str(user_id)
    user = players.get(uid)
    if not user:
        return send_message(chat_id, "❗ خطا در بارگذاری داده")
    msg = ""
    if btn == "🛒 فروشگاه سکه":
        msg = f"💰 فروشگاه سکه<br>سکه فعلی: {user['coins']}<br>بسته‌ها: ۵۰۰۰ سکه = ۱۰۰ سکه | ۲۰۰۰۰ = ۳۰۰ سکه"
    elif btn == "💎 خرید جم":
        msg = f"💎 خرید جم<br>جم فعلی: {user['gems']}<br>قیمت: هر جم ≈ ۱۰ سکه"
    elif btn == "🎁 بسته‌های ویژه":
        msg = "🎁 بسته‌های ویژه<br>- بسته طلایی<br>- بسته الماس<br>- بسته ویژه فصلی"
    elif btn == "💳 خرید VIP":
        user['vip_days'] = user.get('vip_days', 0) + 30
        save_all()
        msg = "✅ VIP شما برای ۳۰ روز فعال شد!"
    elif btn == "🎟 کد هدیه":
        msg = "🎟 کد هدیه خود را وارد کنید:<br>مثال: GIFT123"
    elif btn == "🎫 گیفت کارت":
        msg = "🎫 گیفت کارت فعال است. ۵۰۰ سکه به حساب شما اضافه شد."
        user['coins'] += 500
    elif btn == "🎲 گردونه شانس":
        if user.get('spin_used_today'):
            msg = "❌ گردونه امروز استفاده شده"
        else:
            r = random.randint(1, 100)
            prize = 50 if r < 20 else (200 if r < 50 else 500)
            user['coins'] += prize
            user['spin_used_today'] = True
            msg = f"🎲 گردونه شانس! شما برنده <b>{prize}</b> سکه شدید!"
    elif btn == "🎰 اسلات":
        slots = ["🍒", "🍋", "🍇", "🍊"]
        s1, s2, s3 = random.choice(slots), random.choice(slots), random.choice(slots)
        if s1 == s2 == s3:
            user['coins'] += 300
            msg = f"🎰 <b>{s1}{s2}{s3}</b> برنده شدید! +۳۰۰ سکه"
        else:
            msg = f"🎰 {s1}{s2}{s3} باختید!"
    elif btn == "🎁 جایزه روزانه":
        user['daily_streak'] = user.get('daily_streak', 0) + 1
        user['coins'] += 100
        msg = f"🎁 جایزه روزانه! استریک شما: <b>{user['daily_streak']}</b> (+۱۰۰ سکه)"
    elif btn == "📆 هفتگی":
        if user.get('weekly_claimed'):
            msg = "❌ هفتگی قبلاً دریافت شده"
        else:
            user['weekly_claimed'] = True
            user['coins'] += 500
            msg = "📆 جایزه هفتگی دریافت شد! +۵۰۰ سکه"
    elif btn == "📅 ماهانه":
        if user.get('monthly_claimed'):
            msg = "❌ ماهانه قبلاً دریافت شده"
        else:
            user['monthly_claimed'] = True
            user['coins'] += 2000
            msg = "📅 جایزه ماهانه دریافت شد! +۲۰۰۰ سکه"
    elif btn == "🔥 استریک":
        msg = f"🔥 استریک ورود روزانه شما: <b>{user.get('daily_streak', 0)}</b> روز"
    elif btn == "💰 ماموریت درآمدی":
        user['income_mission'] = user.get('income_mission', 0) + 1
        user['coins'] += 200
        msg = f"💰 ماموریت درآمدی شماره <b>{user['income_mission']}</b> تکمیل شد! +۲۰۰ سکه"
    else:
        msg = "💰 اقتصاد بازی را انتخاب کنید."
    save_all()
    send_message(chat_id, msg, reply_markup=kb_economy())

# ======================= منطق پروفایل =======================

def handle_profile(user_id, chat_id, btn):
    uid = str(user_id)
    user = players.get(uid)
    if not user:
        return send_message(chat_id, "❗ خطا در بارگذاری داده")
    msg = ""
    if btn == "🖼 آواتار":
        msg = f"🖼 آواتار فعلی: {'تنظیم شده' if user.get('avatar') else 'پیش‌فرض'}"
    elif btn == "📸 قاب پروفایل":
        user['frame'] = "طلایی"
        msg = "📸 قاب طلایی فعال شد!"
    elif btn == "📝 بیو":
        msg = f"📝 بیو فعلی: {user.get('bio', 'خالی')}"
    elif btn == "🏷 عنوان اختصاصی":
        msg = f"🏷 عنوان: {user.get('title', 'تازه‌وارد')}"
    elif btn == "📊 سطح و XP":
        msg = f"📊 سطح: <b>{user.get('level', 1)}</b> | XP: <b>{user.get('xp', 0)}</b>"
    elif btn == "🏅 نشان‌ها":
        badges = user.get('badges', [])
        msg = f"🏅 نشان‌ها: {', '.join(badges) if badges else 'ندارید'}"
    elif btn == "📅 تاریخ عضویت":
        msg = f"📅 تاریخ عضویت: {time.strftime('%Y/%m/%d', time.localtime(user.get('join_date', 0)))}"
    elif btn == "📈 آمار کامل":
        s = user.get('stats', {})
        msg = (f"📊 برد: <b>{s.get('wins', 0)}</b> | باخت: <b>{s.get('losses', 0)}</b><br>"
               f"⚔ نبرد: <b>{s.get('battles', 0)}</b> | ماینر جمع‌شده: <b>{s.get('miners_collected', 0)}</b>")
    elif btn == "🏆 رکوردها":
        msg = f"🏆 رکورد شخصی: سطح <b>{user.get('level', 1)}</b> | لول ماینر <b>{user.get('miner_level', 0)}</b>"
    else:
        msg = "👤 پروفایل خود را مدیریت کنید."
    save_all()
    send_message(chat_id, msg, reply_markup=kb_profile())

# ======================= منطق ماینر =======================

def handle_miner(user_id, chat_id, btn):
    uid = str(user_id)
    user = players.get(uid)
    if not user:
        return send_message(chat_id, "❗ خطا")
    msg = ""
    if btn == "📥 جمع‌آوری":
        level = user.get('miner_level', 0)
        if level <= 0:
            msg = "❌ ماینر شما ارتقا نیافته"
        else:
            last = user.get('miner_last_collect', 0)
            now = time.time()
            hours = max(0, int((now - last) // 3600))
            amt = hours * MINER_BASE_PER_LEVEL * level
            if amt <= 0:
                msg = "⛏ هنوز چیزی برای جمع‌آوری نیست."
            else:
                user['coins'] += amt
                user['miner_last_collect'] = int(now)
                user['stats']['miners_collected'] = user.get('stats', {}).get('miners_collected', 0) + 1
                msg = f"⛏ +{amt} سکه از ماینر جمع‌آوری شد!"
    elif btn == "🔼 ارتقا":
        cost = (user.get('miner_level', 0) + 1) * 200
        if user['coins'] >= cost:
            user['coins'] -= cost
            user['miner_level'] += 1
            msg = f"🔼 ماینر ارتقا یافت! سطح جدید: <b>{user['miner_level']}</b>"
        else:
            msg = f"❌ سکه کافی نیست. نیاز: <b>{cost}</b>"
    elif btn == "⛽ سوخت":
        msg = f"⛽ سوخت ماینر: <b>{user.get('miner_fuel', 100)}%</b>"
    elif btn == "⚡ سرعت":
        msg = f"⚡ سرعت استخراج: <b>{user.get('miner_speed', 1)}x</b>"
    elif btn == "🚀 شتاب‌دهنده":
        user['miner_accelerator'] = user.get('miner_accelerator', 0) + 1
        msg = "🚀 شتاب‌دهنده فعال شد! (+۱ ساعت سرعت دوبرابر)"
    elif btn == "🔧 تعمیر":
        user['miner_fuel'] = 100
        msg = "🔧 ماینر تعمیر شد. سوخت ۱۰۰%"
    elif btn == "🤖 اتوماتیک":
        user['miner_auto'] = True
        msg = "🤖 ارتقای اتوماتیک فعال شد!"
    elif btn == "💤 آفلاین":
        user['miner_offline'] = True
        msg = "💤 استخراج آفلاین فعال شد!"
    elif btn == "🌟 طلایی":
        if user.get('miner_level', 0) >= 500:
            user['miner_type'] = "طلایی"
            user['miner_golden_unlocked'] = True
            msg = "🌟 ماینر طلایی فعال شد!"
        else:
            msg = "❌ برای طلایی شدن به سطح ۵۰۰ ماینر نیاز دارید."
    elif btn == "🐉 افسانه‌ای":
        if user.get('miner_level', 0) >= 900:
            user['miner_type'] = "افسانه‌ای"
            user['miner_legendary_unlocked'] = True
            msg = "🐉 ماینر افسانه‌ای فعال شد!"
        else:
            msg = "❌ برای افسانه‌ای شدن به سطح ۹۰۰ ماینر نیاز دارید."
    else:
        msg = "⛏ ماینر خود را مدیریت کنید."
    save_all()
    send_message(chat_id, msg, reply_markup=kb_miner())

# ======================= منطق بانک =======================

def handle_bank(user_id, chat_id, btn):
    uid = str(user_id)
    user = players.get(uid)
    if not user:
        return send_message(chat_id, "❗ خطا")
    msg = ""
    if btn == "⏱ سپرده کوتاه":
        amount = 500
        if user['coins'] >= amount:
            user['coins'] -= amount
            user['bank_amount'] = amount
            user['bank_time'] = time.time()
            msg = f"💰 <b>{amount}</b> سکه در سپرده کوتاه‌مدت با سود {int(BANK_SHORT_RATE*100)}% قرار گرفت."
        else:
            msg = "❌ سکه کافی نیست."
    elif btn == "⏳ بلندمدت":
        amount = 2000
        if user['coins'] >= amount:
            user['coins'] -= amount
            user['bank_amount'] = amount
            user['bank_time'] = time.time()
            msg = f"💰 <b>{amount}</b> سکه در سپرده بلندمدت با سود {int(BANK_LONG_RATE*100)}% قرار گرفت."
        else:
            msg = "❌ سکه کافی نیست."
    elif btn == "💵 وام":
        if user.get('bank_loan', 0) <= 0:
            user['bank_loan'] = 1000
            user['coins'] += 1000
            msg = "💵 وام <b>۱۰۰۰</b> سکه دریافت شد. باید بازپرداخت کنید."
        else:
            msg = "❌ وام فعلی دارید."
    elif btn == "📊 سود متغیر":
        msg = f"📊 سود کوتاه: <b>{int(BANK_SHORT_RATE*100)}%</b> | بلند: <b>{int(BANK_LONG_RATE*100)}%</b>"
    elif btn == "📈 صندوق سرمایه":
        msg = "📈 صندوق سرمایه فعال است. سود روزانه به حساب شما اضافه می‌شود."
    elif btn == "🛡 بیمه":
        user['bank_insurance'] = True
        msg = "🛡 بیمه سرمایه فعال شد."
    elif btn == "💼 گاوصندوق":
        msg = "💼 گاوصندوق امن است. هیچ مالیاتی از سپرده شما کسر نمی‌شود."
    elif btn == "🏦 انتقال بانکی":
        msg = "🏦 انتقال بانکی بین کاربران فعال است. شماره کاربر مقصد را وارد کنید."
    else:
        msg = "🏦 بانک را انتخاب کنید."
    # پرداخت سود خودکار
    if user.get('bank_amount', 0) > 0 and user.get('bank_time', 0) > 0:
        if time.time() - user['bank_time'] >= 24*3600:
            deposit = user['bank_amount']
            rate = BANK_LONG_RATE if deposit >= 1000 else BANK_SHORT_RATE
            interest = int(deposit * rate)
            user['coins'] += deposit + interest
            user['bank_amount'] = 0
            user['bank_time'] = 0
            msg += f"<br>📢 سود بانکی پرداخت شد: +<b>{deposit + interest}</b> سکه"
    save_all()
    send_message(chat_id, msg, reply_markup=kb_bank())

# ======================= منطق مبارزه =======================

def handle_combat(user_id, chat_id, btn):
    uid = str(user_id)
    user = players.get(uid)
    if not user:
        return send_message(chat_id, "❗ خطا")
    msg = ""
    if btn == "⚔️ PvP":
        if user['coins'] >= PVP_STAKE:
            user['coins'] -= PVP_STAKE
            win = random.random() > 0.4
            user['stats']['battles'] = user.get('stats', {}).get('battles', 0) + 1
            if win:
                user['coins'] += PVP_STAKE * 2
                user['pvp_wins'] = user.get('pvp_wins', 0) + 1
                user['stats']['wins'] = user.get('stats', {}).get('wins', 0) + 1
                msg = "⚔️ PvP برنده شدید! +۲۰۰ سکه"
            else:
                user['stats']['losses'] = user.get('stats', {}).get('losses', 0) + 1
                msg = "⚔️ PvP باختید!"
        else:
            msg = "❌ سکه کافی برای PvP ندارید."
    elif btn == "🐉 PvE":
        if user['coins'] >= PVE_STAKE:
            user['coins'] -= PVE_STAKE
            win = random.random() > 0.3
            if win:
                user['coins'] += PVE_STAKE * 1.5
                user['pve_wins'] = user.get('pve_wins', 0) + 1
                msg = "🐉 PvE برنده شدید!"
            else:
                msg = "🐉 PvE باختید."
        else:
            msg = "❌ سکه کافی ندارید."
    elif btn == "👑 باس فایت":
        msg = "👑 باس فایت در حال برگزاری است. برای ورود ۵۰۰ سکه نیاز است."
    elif btn == "👥 جنگ گروهی":
        msg = "👥 جنگ گروهی فعال است. به کلن خود بپیوندید."
    elif btn == "⚡ دوئل":
        msg = "⚡ دوئل با بازیکن تصادفی شروع شد! منتظر پاسخ حریف باشید."
    elif btn == "🏅 لیگ":
        msg = f"🏅 رتبه لیگ شما: <b>{user.get('league_points', 0)}</b> امتیاز"
    elif btn == "🏆 تورنمنت":
        msg = "🏆 تورنمنت هفتگی در حال برگزاری است."
    elif btn == "🎲 نبرد تصادفی":
        msg = "🎲 نبرد تصادفی با بازیکن تصادفی آغاز شد."
    elif btn == "📊 نبرد رتبه‌ای":
        msg = f"📊 رتبه نبرد شما: <b>{user.get('league_points', 0)}</b> امتیاز"
    else:
        msg = "⚔️ مبارزه خود را انتخاب کنید."
    save_all()
    send_message(chat_id, msg, reply_markup=kb_combat())

# ======================= منطق کلن =======================

def handle_clan(user_id, chat_id, btn):
    uid = str(user_id)
    user = players.get(uid)
    if not user:
        return send_message(chat_id, "❗ خطا")
    msg = ""
    if btn == "🏗 ساخت کلن":
        if not user.get('clan'):
            user['clan'] = f"کلن_{user['name'] or user_id[:4]}"
            user['clan_role'] = "رهبر"
            msg = f"🏰 کلن <b>{user['clan']}</b> ساخته شد!"
        else:
            msg = "❌ شما قبلاً در یک کلن هستید."
    elif btn == "👥 عضوگیری":
        msg = "👥 دعوت به کلن ارسال شد. منتظر پذیرش باشید."
    elif btn == "💬 چت کلن":
        msg = f"💬 چت کلن <b>{user.get('clan', 'ندارید')}</b> فعال است."
    elif btn == "📈 ارتقا":
        msg = "📈 کلن ارتقا یافت. سطح جدید: ۲"
    elif btn == "💰 خزانه":
        msg = f"💰 خزانه کلن: <b>۵۰۰۰</b> سکه"
    elif btn == "⚔️ جنگ کلن":
        msg = "⚔️ جنگ کلن با کلن رقیب آغاز شد!"
    elif btn == "🎯 ماموریت کلن":
        msg = "🎯 ماموریت کلن: جمع‌آوری ۱۰۰۰ سکه از ماینر."
    elif btn == "📊 رتبه کلن":
        msg = "📊 رتبه کلن شما: <b>۱۵</b>"
    else:
        msg = "🏰 کلن خود را مدیریت کنید."
    save_all()
    send_message(chat_id, msg, reply_markup=kb_clan())

# ======================= منطق ماموریت =======================

def handle_missions(user_id, chat_id, btn):
    msg = ""
    if btn == "📋 روزانه":
        msg = "📋 ماموریت روزانه: جمع‌آوری ۵۰۰ سکه از ماینر. جایزه: ۲۰۰ سکه"
    elif btn == "📅 هفتگی":
        msg = "📅 ماموریت هفتگی: برنده شدن در ۳ مبارزه. جایزه: ۱۰۰۰ سکه"
    elif btn == "📆 ماهانه":
        msg = "📆 ماموریت ماهانه: ارتقا ماینر تا سطح ۱۰. جایزه: ۵۰۰۰ سکه"
    elif btn == "🌸 فصلی":
        msg = "🌸 ماموریت فصلی: رسیدن به سطح ۵۰. جایزه: ۱۰۰۰۰ سکه + اسکین"
    elif btn == "🔍 مخفی":
        msg = "🔍 ماموریت مخفی: پیدا کردن کلید طلایی در بازار."
    elif btn == "⭐ ویژه":
        msg = "⭐ ماموریت ویژه: دعوت ۱۰ دوست به ربات. جایزه: VIP یک ماهه"
    else:
        msg = "🎯 ماموریت‌ها را انتخاب کنید."
    send_message(chat_id, msg, reply_markup=kb_missions())

# ======================= منطق لیدربرد =======================

def handle_leaderboard(user_id, chat_id, btn):
    msg = ""
    if btn == "💰 ثروتمندترین":
        msg = "💰 ثروتمندترین بازیکنان:<br>۱. کاربر A - ۹۹۹۹۹ سکه"
    elif btn == "📊 بیشترین لول":
        msg = "📊 بیشترین لول:<br>۱. کاربر B - سطح ۹۹"
    elif btn == "⛏ بهترین ماینر":
        msg = "⛏ بهترین ماینر:<br>۱. کاربر C - سطح ۹۵۰"
    elif btn == "🏆 بیشترین برد":
        msg = "🏆 بیشترین برد:<br>۱. کاربر D - ۵۰۰ برد"
    elif btn == "🏰 بهترین کلن":
        msg = "🏰 بهترین کلن:<br>۱. کلن شاهین"
    elif btn == "📢 بیشترین دعوت":
        msg = "📢 بیشترین دعوت:<br>۱. کاربر E - ۱۲۰ دعوت"
    elif btn == "🔥 بیشترین فعالیت":
        msg = "🔥 بیشترین فعالیت:<br>۱. کاربر F - ۹۹۹ امتیاز"
    else:
        msg = "🏆 لیدربرد را انتخاب کنید."
    send_message(chat_id, msg, reply_markup=kb_leaderboard())

# ======================= منطق آیتم =======================

def handle_items(user_id, chat_id, btn):
    msg = ""
    if btn == "⚡ بوستر":
        msg = "⚡ بوستر سرعت ماینر به مدت ۱ ساعت فعال است."
    elif btn == "🛡 سپر":
        msg = "🛡 سپر محافظت در مبارزه فعال است."
    elif btn == "💣 بمب":
        msg = "💣 بمب برای آسیب به حریف در مبارزه آماده است."
    elif btn == "🎁 جعبه شانس":
        msg = "🎁 جعبه شانس باز شد. شما برنده یک آیتم تصادفی شدید."
    elif btn == "🔑 کلید":
        msg = "🔑 کلید برای باز کردن صندوق طلایی استفاده می‌شود."
    elif btn == "📦 صندوق":
        msg = "📦 صندوق باز شد. جایزه: ۳۰۰ سکه."
    elif btn == "🐾 پت":
        msg = "🐾 پت شما در حال پرورش است."
    elif btn == "👕 لباس":
        msg = "👕 لباس ورزشی به پروفایل شما اضافه شد."
    elif btn == "🎨 اسکین":
        msg = "🎨 اسکین طلایی فعال شد."
    elif btn == "✨ افکت":
        msg = "✨ افکت آتش به پیام‌های شما اضافه شد."
    else:
        msg = "🎁 آیتم‌ها را انتخاب کنید."
    send_message(chat_id, msg, reply_markup=kb_items())

# ======================= منطق پت =======================

def handle_pets(user_id, chat_id, btn):
    msg = ""
    if btn == "🐕 خرید پت":
        msg = "🐕 پت سگ عادی به قیمت ۲۰۰ سکه خریداری شد."
    elif btn == "📈 ارتقا پت":
        msg = "📈 پت شما ارتقا یافت. سطح جدید: ۵"
    elif btn == "🍖 غذا":
        msg = "🍖 پت شما تغذیه شد. سلامت ۱۰۰%"
    elif btn == "⭐ تجربه":
        msg = "⭐ پت شما تجربه کسب کرد. XP: ۵۰"
    elif btn == "💪 مهارت":
        msg = "💪 مهارت جدید: دفاع قوی"
    elif btn == "🎲 کمیاب":
        msg = "🎲 پت کمیاب: گربه کمیاب فعال است."
    elif btn == "🐉 افسانه‌ای":
        msg = "🐉 پت افسانه‌ای: اژدها فعال است."
    else:
        msg = "🐶 پت‌های خود را مدیریت کنید."
    send_message(chat_id, msg, reply_markup=kb_pets())

# ======================= منطق فروشگاه =======================

def handle_shop(user_id, chat_id, btn):
    msg = ""
    if btn == "🎁 آیتم":
        msg = "🎁 آیتم‌ها در فروشگاه: بوستر، سپر، بمب، جعبه شانس"
    elif btn == "🎨 اسکین":
        msg = "🎨 اسکین‌ها: طلایی، الماسی، افسانه‌ای"
    elif btn == "💎 VIP":
        msg = "💎 VIP یک ماهه: ۲۰۰ سکه"
    elif btn == "⚡ بوستر":
        msg = "⚡ بوستر: ۵۰ سکه"
    elif btn == "📦 جعبه":
        msg = "📦 جعبه شانس: ۱۰۰ سکه"
    elif btn == "💰 بسته اقتصادی":
        msg = "💰 بسته اقتصادی: ۳۰۰ سکه (۵۰۰۰ سکه + ۵۰ جم)"
    else:
        msg = "🛍 فروشگاه را انتخاب کنید."
    send_message(chat_id, msg, reply_markup=kb_shop())

# ======================= منطق رویداد =======================

def handle_events(user_id, chat_id, btn):
    msg = ""
    events = {
        "🎄 کریسمس": "🎄 رویداد کریسمس فعال است. جوایز دوبرابر!",
        "🌸 نوروز": "🌸 نوروز مبارک! جوایز ویژه فصلی.",
        "🍉 یلدا": "🍉 شب یلدا! جوایز شبانه.",
        "🌙 رمضان": "🌙 رمضان مبارک! روزه‌داری مجازی فعال است.",
        "🛒 جمعه سیاه": "🛒 جمعه سیاه! تخفیف ۵۰% در فروشگاه.",
        "🎃 هالووین": "🎃 هالووین! جوایز ترسناک!",
        "🎉 آخر هفته": "🎉 رویداد آخر هفته! امتیاز دوبرابر.",
    }
    msg = events.get(btn, "🎉 رویدادها را انتخاب کنید.")
    send_message(chat_id, msg, reply_markup=kb_events())

# ======================= منطق اجتماعی =======================

def handle_social(user_id, chat_id, btn):
    msg = ""
    if btn == "💬 چت خصوصی":
        msg = "💬 چت خصوصی با دوستان فعال است."
    elif btn == "👥 دوستان":
        msg = "👥 لیست دوستان: کاربر A, کاربر B"
    elif btn == "🚫 بلاک":
        msg = "🚫 لیست بلاک شده‌ها خالی است."
    elif btn == "📨 دعوت":
        msg = "📨 دعوت دوستان ارسال شد. لینک ربات برای آنها فرستاده شد."
    elif btn == "🎁 ارسال هدیه":
        msg = "🎁 هدیه برای دوست ارسال شد. (+۱۰۰ سکه)"
    elif btn == "📩 درخواست دوستی":
        msg = "📩 درخواست دوستی جدید: کاربر X"
    elif btn == "👀 مشاهده پروفایل":
        msg = "👀 پروفایل کاربر A را مشاهده می‌کنید."
    else:
        msg = "👥 اجتماعی را انتخاب کنید."
    send_message(chat_id, msg, reply_markup=kb_social())

# ======================= منطق بازار =======================

def handle_market(user_id, chat_id, btn):
    msg = ""
    if btn == "📈 خرید و فروش":
        msg = "📈 بازار فعال است. آیتم‌های خود را بفروشید یا بخرید."
    elif btn == "🏷 مزایده":
        msg = "🏷 مزایده در حال برگزاری است. پیشنهاد خود را ثبت کنید."
    elif btn == "💱 بازار آزاد":
        msg = "💱 بازار آزاد: قیمت‌ها توسط کاربران تعیین می‌شود."
    elif btn == "⏰ قیمت لحظه‌ای":
        msg = "⏰ قیمت سکه: ۱ سکه = ۱ سکه | جم: ۱۰ سکه"
    elif btn == "💸 مالیات معامله":
        msg = "💸 مالیات معامله: ۵% از هر معامله"
    else:
        msg = "📈 بازار را انتخاب کنید."
    send_message(chat_id, msg, reply_markup=kb_market())

# ======================= منطق مینی‌گیم =======================

def handle_minigames(user_id, chat_id, btn):
    msg = ""
    if btn == "✊ سنگ کاغذ قیچی":
        choices = ["✊", "✋", "✌️"]
        user_c, bot_c = random.choice(choices), random.choice(choices)
        if user_c == bot_c:
            msg = f"✊ شما: {user_c} | ربات: {bot_c} | مساوی!"
        elif (user_c == "✊" and bot_c == "✌️") or (user_c == "✋" and bot_c == "✊") or (user_c == "✌️" and bot_c == "✋"):
            msg = f"✊ شما: {user_c} | ربات: {bot_c} | برنده!"
        else:
            msg = f"✊ شما: {user_c} | ربات: {bot_c} | باخت!"
    elif btn == "🎲 حدس عدد":
        num = random.randint(1, 10)
        msg = f"🎲 عدد من بین ۱ تا ۱۰ است. حدس بزنید: <b>{num}</b>"
    elif btn == "🎲 دوز":
        msg = "🎲 بازی دوز شروع شد. تاس بیندازید!"
    elif btn == "♟ شطرنج":
        msg = "♟ شطرنج با ربات. حرکت خود را بگویید."
    elif btn == "🎲 تاس":
        msg = f"🎲 تاس: <b>{random.randint(1, 6)}</b>"
    elif btn == "🎰 رولت":
        msg = f"🎰 رولت: عدد <b>{random.randint(0, 36)}</b>"
    elif btn == "♠ بلک جک":
        msg = "♠ بلک جک: کارت شما ۱۸ است. بمانید یا بکشید؟"
    elif btn == "🧠 حافظه":
        msg = "🧠 حافظه: کارت‌های جفت را پیدا کنید!"
    elif btn == "⚡ مسابقه سرعت":
        msg = "⚡ مسابقه سرعت: سریع‌ترین کلیک برنده است."
    else:
        msg = "🎮 مینی‌گیم‌ها را انتخاب کنید."
    send_message(chat_id, msg, reply_markup=kb_minigames())

# ======================= منطق شغل =======================

def handle_jobs(user_id, chat_id, btn):
    msg = ""
    jobs_text = {
        "⛏ معدنچی": "⛏ معدنچی: استخراج سکه با سرعت بالا",
        "🌾 کشاورز": "🌾 کشاورز: کشت محصولات و فروش",
        "💼 تاجر": "💼 تاجر: خرید و فروش در بازار",
        "💻 برنامه‌نویس": "💻 برنامه‌نویس: ساخت ربات و ابزار",
        "👮 پلیس": "👮 پلیس: حفاظت از کلن و مبارزه",
        "⚕ پزشک": "⚕ پزشک: درمان و بهبود سلامت",
        "📈 سرمایه‌گذار": "📈 سرمایه‌گذار: سود از بانک و بازار",
        "🚀 کارآفرین": "🚀 کارآفرین: راه‌اندازی کسب‌وکار جدید",
    }
    msg = jobs_text.get(btn, "💼 شغل خود را انتخاب کنید.")
    send_message(chat_id, msg, reply_markup=kb_jobs())

# ======================= منطق نقشه =======================

def handle_map(user_id, chat_id, btn):
    msg = ""
    if btn == "🏙 شهرها":
        msg = "🏙 شهرها: تهران، اصفهان، شیراز، مشهد، تبریز"
    elif btn == "✈ سفر":
        msg = "✈ سفر به شهر جدید آغاز شد. هزینه: ۱۰۰ سکه"
    elif btn == "🎯 مأموریت شهری":
        msg = "🎯 مأموریت شهری: جمع‌آوری منابع در شهر جدید."
    elif btn == "⛏ منابع":
        msg = "⛏ منابع شهر: آهن، طلا، الماس"
    elif btn == "🗺 سرزمین":
        msg = "🗺 سرزمین شما: شهر اصلی + ۳ منطقه فتح شده"
    elif btn == "🏁 فتح مناطق":
        msg = "🏁 فتح مناطق جدید با مبارزه با دشمنان منطقه"
    else:
        msg = "🌍 نقشه را انتخاب کنید."
    send_message(chat_id, msg, reply_markup=kb_map())

# ======================= منطق سیستم =======================

def handle_systems(user_id, chat_id, btn):
    msg = ""
    if btn == "🔔 اعلان":
        msg = "🔔 اعلان‌های جدید: جایزه روزانه آماده است!"
    elif btn == "🛡 ضدتقلب":
        msg = "🛡 سیستم ضدتقلب فعال است. رفتار مشکوک ثبت می‌شود."
    elif btn == "📜 لاگ کامل":
        msg = "📜 لاگ سیستم: آخرین ورود: ۱۴۰۳/۰۵/۰۱"
    elif btn == "💾 بکاپ":
        msg = "💾 بکاپ دستی انجام شد. داده‌ها ذخیره شدند."
    elif btn == "📢 گزارش":
        msg = "📢 گزارش مشکل: لطفاً متن گزارش را وارد کنید."
    elif btn == "⚙ تنظیمات بازی":
        msg = "⚙ تنظیمات بازی: زبان فارسی | صدا روشن | اعلان روشن"
    elif btn == "📊 اقتصاد پویا":
        msg = "📊 اقتصاد پویا فعال است. قیمت‌ها بر اساس عرضه و تقاضا تغییر می‌کنند."
    elif btn == "🌐 API":
        msg = "🌐 API ربات فعال است. مستندات در کانال موجود است."
    else:
        msg = "🤖 سیستم‌ها را انتخاب کنید."
    send_message(chat_id, msg, reply_markup=kb_systems())

# ======================= منطق درآمدزایی =======================

def handle_monetization(user_id, chat_id, btn):
    msg = ""
    if btn == "💎 خرید سکه":
        msg = "💎 خرید سکه: ۱۰۰۰ سکه = ۱۰,۰۰۰ تومان"
    elif btn == "💎 خرید جم":
        msg = "💎 خرید جم: ۵۰ جم = ۵۰,۰۰۰ تومان"
    elif btn == "🎖 اشتراک VIP":
        msg = "🎖 اشتراک VIP ماهانه: ۵۰,۰۰۰ تومان"
    elif btn == "📢 تبلیغات":
        msg = "📢 تبلیغات در کانال ربات: ۱۰۰,۰۰۰ تومان در روز"
    elif btn == "🤝 اسپانسر":
        msg = "🤝 اسپانسر شدن: همکاری با برندها و دریافت سکه"
    elif btn == "📢 مأموریت تبلیغاتی":
        msg = "📢 مأموریت تبلیغاتی: دعوت ۵ نفر به کانال ربات = ۵۰۰ سکه"
    elif btn == "📺 همکاری کانال":
        msg = "📺 همکاری با کانال‌ها: تبلیغ متقابل"
    elif btn == "💰 فروش آیتم":
        msg = "💰 فروش آیتم در بازار آزاد. مالیات ۵%"
    elif btn == "🎨 فروش اسکین":
        msg = "🎨 فروش اسکین‌های کمیاب در مزایده"
    elif btn == "🎟 Battle Pass":
        msg = "🎟 Battle Pass فصلی: جوایز انحصاری"
    elif btn == "🍀 Lucky Pass":
        msg = "🍀 Lucky Pass: جوایز تصادفی روزانه"
    elif btn == "🌸 Season Pass":
        msg = "🌸 Season Pass: جوایز فصلی و اسکین انحصاری"
    else:
        msg = "💎 درآمدزایی را انتخاب کنید."
    send_message(chat_id, msg, reply_markup=kb_monetization())

# ======================= منطق اعتیادآور =======================

def handle_addictive(user_id, chat_id, btn):
    uid = str(user_id)
    user = players.get(uid)
    if not user:
        return send_message(chat_id, "❗ خطا")
    msg = ""
    if btn == "🔥 استریک ورود":
        user['daily_streak'] = user.get('daily_streak', 0) + 1
        msg = f"🔥 استریک ورود: <b>{user['daily_streak']}</b> روز پیاپی! (+۵۰ سکه)"
    elif btn == "🎲 چرخ شانس":
        r = random.randint(1, 100)
        prize = 100 if r < 20 else (300 if r < 50 else 800)
        user['coins'] += prize
        msg = f"🎲 چرخ شانس! برنده <b>{prize}</b> سکه!"
    elif btn == "📦 جعبه ۶ ساعت":
        msg = "📦 جعبه رایگان هر ۶ ساعت آماده است! باز کنید."
    elif btn == "🎲 مأموریت تصادفی":
        msg = "🎲 مأموریت تصادفی جدید: برنده شدن در ۲ مبارزه (+۲۰۰ سکه)"
    elif btn == "🎉 رویداد محدود":
        msg = "🎉 رویداد محدود تا پایان هفته فعال است. شرکت کنید!"
    elif btn == "🏅 دستاوردها":
        msg = f"🏅 دستاوردها: سطح <b>{user.get('level', 1)}</b> | ماینر <b>{user.get('miner_level', 0)}</b>"
    elif btn == "🧩 کلکسیون":
        msg = f"🧩 کلکسیون آیتم شما: <b>{len(user.get('inventory', {}))}</b> آیتم"
    elif btn == "💎 امتیاز وفاداری":
        user['loyalty_points'] = user.get('loyalty_points', 0) + 10
        msg = f"💎 امتیاز وفاداری: <b>{user['loyalty_points']}</b> امتیاز"
    elif btn == "♾ لول بی‌نهایت":
        msg = "♾ سیستم لول بی‌نهایت فعال است. هر لول جدید سخت‌تر می‌شود."
    elif btn == "🔄 Prestige":
        user['prestige'] = user.get('prestige', 0) + 1
        user['coins'] += 5000
        msg = f"🔄 Prestige شماره <b>{user['prestige']}</b>! پاداش: ۵۰۰۰ سکه"
    else:
        msg = "🌟 قابلیت‌های اعتیادآور را انتخاب کنید."
    save_all()
    send_message(chat_id, msg, reply_markup=kb_addictive())

# ======================= منطق ادمین حرفه‌ای =======================

def handle_admin(user_id, chat_id, btn):
    msg = ""
    uid = str(user_id)
    if btn == "➕ دادن سکه":
        msg = "➕ مقدار سکه و شناسه کاربر را وارد کنید.<br>مثال: 500 123456"
    elif btn == "➖ گرفتن سکه":
        msg = "➖ گرفتن سکه از کاربر: مقدار و شناسه را وارد کنید."
    elif btn == "💎 دادن جم":
        msg = "💎 دادن جم به کاربر: مقدار و شناسه را وارد کنید."
    elif btn == "📣 پیام همگانی":
        msg = "📣 متن پیام همگانی را وارد کنید."
    elif btn == "🪙 سکه همگانی":
        msg = "🪙 سکه همگانی برای همه کاربران ارسال شد: +۱۰۰ سکه"
    elif btn == "📊 آمار کاربران":
        msg = f"📊 تعداد کاربران: <b>{len(players)}</b>"
    elif btn == "📁 لاگ سیستم":
        msg = "📁 لاگ سیستم: آخرین خطاها و فعالیت‌ها موجود است."
    elif btn == "⚙ تنظیمات بازی":
        msg = "⚙ تنظیمات بازی در فایل تنظیمات قابل ویرایش است."
    elif btn == "🛡 ضدتقلب":
        msg = "🛡 ضدتقلب فعال است. کاربران مشکوک مسدود می‌شوند."
    elif btn == "💾 بکاپ دستی":
        msg = "💾 بکاپ دستی انجام شد."
    elif btn == "🔴 خروج از ادمین":
        user_data = players.get(uid, {})
        user_data['admin_logged'] = False
        save_all()
        msg = "🔴 از پنل ادمین حرفه‌ای خارج شدید."
        send_message(chat_id, msg, reply_markup=kb_main(check_admin_access(user_id)))
        return
    elif btn == "🔙 بازگشت اصلی":
        msg = "🔙 بازگشت به منوی اصلی"
        send_message(chat_id, msg, reply_markup=kb_main(check_admin_access(user_id)))
        return
    else:
        msg = "🔧 پنل ادمین حرفه‌ای را انتخاب کنید."
    send_message(chat_id, msg, reply_markup=kb_admin())

# ======================= راهنما =======================

def show_help(user_id, chat_id):
    text = ("📚 راهنمای ربات تلگرام<br>"
            "💰 اقتصاد بازی: فروشگاه، خرید، جوایز<br>"
            "⛏ ماینر: جمع‌آوری و ارتقا تا سطح ۱۰۰۰<br>"
            "🏦 بانک: سپرده، وام، سود متغیر<br>"
            "⚔️ مبارزه: PvP، PvE، باس، جنگ گروهی<br>"
            "🏰 کلن: ساخت، عضوگیری، جنگ، خزانه<br>"
            "🎯 ماموریت: روزانه، هفتگی، ماهانه، فصلی<br>"
            "🏆 لیدربرد: ثروت، لول، ماینر، برد<br>"
            "🎁 آیتم: بوستر، سپر، بمب، جعبه، کلید، صندوق<br>"
            "🐶 حیوانات: خرید، ارتقا، غذا، مهارت<br>"
            "🛍 فروشگاه: آیتم، اسکین، VIP، بوستر، جعبه، بسته<br>"
            "🎉 رویدادها: کریسمس، نوروز، یلدا، رمضان، جمعه سیاه، هالووین<br>"
            "👥 اجتماعی: دوستان، دعوت، هدیه، پروفایل<br>"
            "📈 بازار: خرید/فروش، مزایده، بازار آزاد، مالیات<br>"
            "🎮 مینی‌گیم: سنگ کاغذ قیچی، حدس عدد، دوز، شطرنج، تاس، رولت، بلک جک، حافظه<br>"
            "💼 شغل: معدنچی، کشاورز، تاجر، برنامه‌نویس، پلیس، پزشک، سرمایه‌گذار، کارآفرین<br>"
            "🌍 نقشه: شهرها، سفر، مأموریت شهری، منابع، فتح مناطق<br>"
            "🤖 سیستم‌ها: اعلان، ضدتقلب، لاگ، بکاپ، گزارش، تنظیمات، اقتصاد پویا، API<br>"
            "💎 درآمدزایی: خرید سکه/جم، VIP، تبلیغات، اسپانسر، همکاری، فروش<br>"
            "🌟 اعتیادآور: استریک، چرخ شانس، جعبه ۶ ساعت، دستاوردها، Prestige")
    send_message(chat_id, text, reply_markup=kb_main(check_admin_access(user_id)))

# ======================= حلقه اصلی (پولینگ تلگرام) =======================

def main():
    print("ربات تلگرام راه‌اندازی شد. در حال پولینگ...")
    offset = None
    while True:
        try:
            updates = get_updates(offset=offset, timeout=20)
            result = updates.get("result", [])
            if isinstance(result, list) and result:
                for update in result:
                    update_id = update.get("update_id", 0)
                    offset = update_id + 1
                    message = update.get("message", {})
                    if not message:
                        continue
                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text", "")
                    user_obj = message.get("from", {})
                    user_id = user_obj.get("id")
                    user_name = user_obj.get("first_name", user_obj.get("username", ""))
                    username = user_obj.get("username", "")
                    if not user_id or not chat_id:
                        continue
                    ensure_user_struct(user_id)
                    user_data = players.get(str(user_id), {})
                    user_data['name'] = user_name or user_data.get('name', 'کاربر')
                    user_data['username'] = username or user_data.get('username', '')
                    is_adm = check_admin_access(user_id, user_name) or check_admin_access(user_id, username)
                    # ذخیره نام و نام کاربری برای بررسی ادمین
                    if user_name:
                        user_data['name'] = user_name
                    if username:
                        user_data['username'] = username

                    # دستورات اولیه
                    if text.startswith("/") or text.startswith("!"):
                        cmd = text.lower()
                        if cmd in ("/start", "/start", "شروع", "استارت"):
                            user_data['started'] = True
                            send_message(chat_id, f"🎮 خوش آمدید <b>{user_name or 'دوست عزیز'}</b>! ربات بازی و اقتصاد فعال است.", reply_markup=kb_main(is_adm))
                        elif cmd in ("/admin", "ادمین", "/panel", "/admin_panel"):
                            if is_adm:
                                user_data['admin_logged'] = True
                                send_message(chat_id, "🔐 رمز پنل ادمین حرفه‌ای را وارد کنید (رمز: <b>ali</b>)", reply_markup={"keyboard": [["🔑 ورود با رمز"], ["🔙 بازگشت"]], "resize_keyboard": True})
                            else:
                                send_message(chat_id, "❌ شما ادمین نیستید یا رمز را وارد نکرده‌اید.", reply_markup=kb_main(is_adm))
                        elif cmd == "/help" or cmd == "راهنما":
                            show_help(user_id, chat_id)
                        else:
                            send_message(chat_id, "❓ دستور ناشناخته. از منو استفاده کنید.", reply_markup=kb_main(is_adm))
                    else:
                        # بررسی ورود رمز برای ادمین
                        if text == "ali" or (isinstance(text, str) and text.lower() == "ali"):
                            if user_data.get('step') == "admin_login" or text == "ali":
                                user_data['admin_logged'] = True
                                user_data['step'] = None
                                send_message(chat_id, "✅ رمز صحیح است. به پنل ادمین حرفه‌ای خوش آمدید.", reply_markup=kb_admin())
                                save_all()
                                continue
                        # بررسی دکمه‌های اصلی
                        btn_map = {
                            "💰 اقتصاد بازی": ("economy", lambda: handle_economy(user_id, chat_id, text)),
                            "👤 پروفایل": ("profile", lambda: handle_profile(user_id, chat_id, text)),
                            "⛏️ ماینر": ("miner", lambda: handle_miner(user_id, chat_id, text)),
                            "🏦 بانک": ("bank", lambda: handle_bank(user_id, chat_id, text)),
                            "⚔️ مبارزه": ("combat", lambda: handle_combat(user_id, chat_id, text)),
                            "🏰 کلن": ("clan", lambda: handle_clan(user_id, chat_id, text)),
                            "🎯 ماموریت": ("mission", lambda: handle_missions(user_id, chat_id, text)),
                            "🏆 لیدربرد": ("leaderboard", lambda: handle_leaderboard(user_id, chat_id, text)),
                            "🎁 آیتم": ("items", lambda: handle_items(user_id, chat_id, text)),
                            "🐶 حیوانات": ("pets", lambda: handle_pets(user_id, chat_id, text)),
                            "🛍 فروشگاه": ("shop", lambda: handle_shop(user_id, chat_id, text)),
                            "🎉 رویدادها": ("events", lambda: handle_events(user_id, chat_id, text)),
                            "👥 اجتماعی": ("social", lambda: handle_social(user_id, chat_id, text)),
                            "📈 بازار": ("market", lambda: handle_market(user_id, chat_id, text)),
                            "🎮 مینی‌گیم": ("minigame", lambda: handle_minigames(user_id, chat_id, text)),
                            "💼 شغل": ("jobs", lambda: handle_jobs(user_id, chat_id, text)),
                            "🌍 نقشه": ("map", lambda: handle_map(user_id, chat_id, text)),
                            "🤖 سیستم‌ها": ("systems", lambda: handle_systems(user_id, chat_id, text)),
                            "💎 درآمدزایی": ("monetization", lambda: handle_monetization(user_id, chat_id, text)),
                            "🌟 اعتیادآور": ("addictive", lambda: handle_addictive(user_id, chat_id, text)),
                            "🔧 پنل ادمین حرفه‌ای": ("admin", lambda: handle_admin(user_id, chat_id, text)),
                        }
                        matched = False
                        for k, v in btn_map.items():
                            if text == k:
                                user_data['prev'] = v[0]
                                user_data['step'] = v[0]
                                v[1]()
                                matched = True
                                break
                        if not matched:
                            if user_data.get('prev') or user_data.get('step'):
                                prev = user_data.get('prev') or user_data.get('step')
                                if prev == "economy":
                                    handle_economy(user_id, chat_id, text)
                                elif prev == "profile":
                                    handle_profile(user_id, chat_id, text)
                                elif prev == "miner":
                                    handle_miner(user_id, chat_id, text)
                                elif prev == "bank":
                                    handle_bank(user_id, chat_id, text)
                                elif prev == "combat":
                                    handle_combat(user_id, chat_id, text)
                                elif prev == "clan":
                                    handle_clan(user_id, chat_id, text)
                                elif prev == "mission":
                                    handle_missions(user_id, chat_id, text)
                                elif prev == "leaderboard":
                                    handle_leaderboard(user_id, chat_id, text)
                                elif prev == "items":
                                    handle_items(user_id, chat_id, text)
                                elif prev == "pets":
                                    handle_pets(user_id, chat_id, text)
                                elif prev == "shop":
                                    handle_shop(user_id, chat_id, text)
                                elif prev == "events":
                                    handle_events(user_id, chat_id, text)
                                elif prev == "social":
                                    handle_social(user_id, chat_id, text)
                                elif prev == "market":
                                    handle_market(user_id, chat_id, text)
                                elif prev == "minigame":
                                    handle_minigames(user_id, chat_id, text)
                                elif prev == "jobs":
                                    handle_jobs(user_id, chat_id, text)
                                elif prev == "map":
                                    handle_map(user_id, chat_id, text)
                                elif prev == "systems":
                                    handle_systems(user_id, chat_id, text)
                                elif prev == "monetization":
                                    handle_monetization(user_id, chat_id, text)
                                elif prev == "addictive":
                                    handle_addictive(user_id, chat_id, text)
                                elif prev == "admin":
                                    if user_data.get('admin_logged'):
                                        handle_admin(user_id, chat_id, text)
                                    else:
                                        user_data['step'] = "admin_login"
                                        send_message(chat_id, "🔑 برای ورود به پنل ادمین حرفه‌ای، رمز را وارد کنید (رمز: <b>ali</b>)", reply_markup={"keyboard": [["ali"], ["🔙 بازگشت"]], "resize_keyboard": True})
                                else:
                                    send_message(chat_id, "❓ لطفاً از منو انتخاب کنید.", reply_markup=kb_main(is_adm))
                            else:
                                # بررسی دوباره دکمه اصلی
                                for k in btn_map:
                                    if text == k:
                                        user_data['prev'] = btn_map[k][0]
                                        user_data['step'] = btn_map[k][0]
                                        btn_map[k][1]()
                                        matched = True
                                        break
                                if not matched:
                                    send_message(chat_id, "❓ لطفاً از منو انتخاب کنید.", reply_markup=kb_main(is_adm))
        except Exception as e:
            print("Loop error:", e)
            time.sleep(2)

if __name__ == "__main__":
    main()
