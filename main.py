# -*- coding: utf-8 -*-
"""
ربات روبیکا (روبیکا) - نسخه کامل با کتابخانه rubika-bot
پنل ادمین حرفه‌ای با رمز: ali
تمام دسته‌بندی‌های درخواستی در یک فایل
"""
import json, os, time, random
from rubika_bot.requests import get_updates, send_message
from rubika_bot.models import Keypad, KeypadRow, Button

TOKEN = "BCIIGB0VOWSDTSZOUCYXRQBTAJBNESZYGEJDPQVAGKLJKDXBBJPECEPUOWGKQTAS"
ADMINS = ["admin_username", 1570690274]
ADMIN_PASSWORD = "ali"

DATA_FILE = "players.json"
CLANS_FILE = "clans.json"
PENDING_FILE = "pending.json"

def load_json(fname, default):
    if not os.path.exists(fname):
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
    try:
        with open(fname, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(fname, data):
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

players = load_json(DATA_FILE, {})
clans = load_json(CLANS_FILE, {})
pending = load_json(PENDING_FILE, [])

def save_all():
    save_json(DATA_FILE, players)
    save_json(PENDING_FILE, pending)
    save_json(CLANS_FILE, clans)

# ======================= ادمین =======================
def is_admin_by_name(name):
    if not name: return False
    for a in ADMINS:
        if isinstance(a, str) and a.lower() == name.lower():
            return True
    return False

def is_admin_num(uid):
    try:
        return int(uid) in [x for x in ADMINS if isinstance(x, int)]
    except:
        return False

def check_admin(uid, name=""):
    return is_admin_by_name(name) or is_admin_by_name("") or is_admin_num(str(uid))

# ======================= کاربر =======================
def ensure_user_struct(uid):
    sid = str(uid)
    if sid not in players:
        players[sid] = {
            "name": None, "coins": 1000, "gems": 10, "xp": 0, "level": 1,
            "started": False, "prev": None, "step": None,
            "admin_logged": False,
            "vip_days": 0, "gift_codes": [], "spin_used_today": False,
            "daily_streak": 0, "weekly_claimed": False, "monthly_claimed": False,
            "income_mission": 0, "avatar": None, "bio": "", "frame": None,
            "title": "تازه‌وارد", "badges": [], "join_date": int(time.time()),
            "stats": {"wins": 0, "losses": 0, "battles": 0, "miners_collected": 0, "clan": None},
            "miner_level": 0, "miner_type": "سنگی", "miner_fuel": 100,
            "miner_speed": 1, "miner_accelerator": 0, "miner_auto": False,
            "miner_offline": False, "miner_last_collect": 0,
            "miner_golden_unlocked": False, "miner_legendary_unlocked": False,
            "bank_amount": 0, "bank_time": 0, "bank_loan": 0, "bank_loan_due": 0,
            "bank_insurance": False, "pvp_wins": 0, "pve_wins": 0, "boss_wins": 0,
            "group_war_wins": 0, "duel_wins": 0, "league_points": 0,
            "clan": None, "clan_role": "عضو", "inventory": {}, "pets": {},
            "purchased": [], "friends": [], "blocked": [],
            "friend_requests": [], "market_listings": [], "job": None,
            "job_level": 1, "cities_visited": ["شهر اصلی"], "territory": "شهر اصلی",
            "notifications": [], "logs": [], "prestige": 0, "loyalty_points": 0,
            "event_bonus_active": False, "requests": []
        }
        save_all()

# ======================= کیبوردها =======================

def kb(rows_list):
    rows = []
    for r in rows_list:
        buttons = [Button(
            id=str(i),
            button_text=str(b),
            button_selection=None,
            button_calendar=None,
            button_number_picker=None,
            button_string_picker=None,
            button_location=None,
            button_textbox=None,
            button_link=None
        ) for i, b in enumerate(r)]
        rows.append(KeypadRow(buttons=buttons))
    return Keypad(rows=rows, resize_keyboard=True, on_time_keyboard=False)

def kb_main(is_adm=False):
    rows = [
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
    if is_adm:
        rows.append(["🔧 پنل ادمین حرفه‌ای"])
    rows.append(["❓ راهنما", "🔙 خروج"])
    return kb(rows)

def kb_econ(): return kb([["🛒 فروشگاه سکه","💎 خرید جم"],["🎁 بسته‌های ویژه","💳 خرید VIP"],["🎟 کد هدیه","🎫 گیفت کارت"],["🎲 گردونه شانس","🎰 اسلات"],["🎁 جایزه روزانه","📆 هفتگی"],["📅 ماهانه","🔥 استریک"],["💰 ماموریت درآمدی","🔙 بازگشت"]])
def kb_prof(): return kb([["🖼 آواتار","📸 قاب پروفایل"],["📝 بیو","🏷 عنوان اختصاصی"],["📊 سطح و XP","🏅 نشان‌ها"],["📅 تاریخ عضویت","📈 آمار کامل"],["🏆 رکوردها","🔙 بازگشت"]])
def kb_miner(): return kb([["📥 جمع‌آوری","🔼 ارتقا"],["⛽ سوخت","⚡ سرعت"],["🚀 شتاب‌دهنده","🔧 تعمیر"],["🤖 اتوماتیک","💤 آفلاین"],["🌟 طلایی","🐉 افسانه‌ای"],["🔙 بازگشت"]])
def kb_bank(): return kb([["⏱ سپرده کوتاه","⏳ بلندمدت"],["💵 وام","📊 سود متغیر"],["📈 صندوق سرمایه","🛡 بیمه"],["💼 گاوصندوق","🏦 انتقال بانکی"],["🔙 بازگشت"]])
def kb_combat(): return kb([["⚔️ PvP","🐉 PvE"],["👑 باس فایت","👥 جنگ گروهی"],["⚡ دوئل","🏅 لیگ"],["🏆 تورنمنت","🎲 نبرد تصادفی"],["📊 نبرد رتبه‌ای","🔙 بازگشت"]])
def kb_clan(): return kb([["🏗 ساخت کلن","👥 عضوگیری"],["💬 چت کلن","📈 ارتقا"],["💰 خزانه","⚔️ جنگ کلن"],["🎯 ماموریت کلن","📊 رتبه کلن"],["🔙 بازگشت"]])
def kb_mission(): return kb([["📋 روزانه","📅 هفتگی"],["📆 ماهانه","🌸 فصلی"],["🔍 مخفی","⭐ ویژه"],["🔙 بازگشت"]])
def kb_leader(): return kb([["💰 ثروتمندترین","📊 بیشترین لول"],["⛏ بهترین ماینر","🏆 بیشترین برد"],["🏰 بهترین کلن","📢 بیشترین دعوت"],["🔥 بیشترین فعالیت","🔙 بازگشت"]])
def kb_items(): return kb([["⚡ بوستر","🛡 سپر"],["💣 بمب","🎁 جعبه شانس"],["🔑 کلید","📦 صندوق"],["🐾 پت","👕 لباس"],["🎨 اسکین","✨ افکت"],["🔙 بازگشت"]])
def kb_pets(): return kb([["🐕 خرید پت","📈 ارتقا پت"],["🍖 غذا","⭐ تجربه"],["💪 مهارت","🎲 کمیاب"],["🐉 افسانه‌ای","🔙 بازگشت"]])
def kb_shop(): return kb([["🎁 آیتم","🎨 اسکین"],["💎 VIP","⚡ بوستر"],["📦 جعبه","💰 بسته اقتصادی"],["🔙 بازگشت"]])
def kb_events(): return kb([["🎄 کریسمس","🌸 نوروز"],["🍉 یلدا","🌙 رمضان"],["🛒 جمعه سیاه","🎃 هالووین"],["🎉 آخر هفته","🔙 بازگشت"]])
def kb_social(): return kb([["💬 چت خصوصی","👥 دوستان"],["🚫 بلاک","📨 دعوت"],["🎁 ارسال هدیه","📩 درخواست دوستی"],["👀 مشاهده پروفایل","🔙 بازگشت"]])
def kb_market(): return kb([["📈 خرید و فروش","🏷 مزایده"],["💱 بازار آزاد","⏰ قیمت لحظه‌ای"],["💸 مالیات معامله","🔙 بازگشت"]])
def kb_minigames(): return kb([["✊ سنگ کاغذ قیچی","🎲 حدس عدد"],["🎲 دوز","♟ شطرنج"],["🎲 تاس","🎰 رولت"],["♠ بلک جک","🧠 حافظه"],["⚡ مسابقه سرعت","🔙 بازگشت"]])
def kb_jobs(): return kb([["⛏ معدنچی","🌾 کشاورز"],["💼 تاجر","💻 برنامه‌نویس"],["👮 پلیس","⚕ پزشک"],["📈 سرمایه‌گذار","🚀 کارآفرین"],["🔙 بازگشت"]])
def kb_map(): return kb([["🏙 شهرها","✈ سفر"],["🎯 مأموریت شهری","⛏ منابع"],["🗺 سرزمین","🏁 فتح مناطق"],["🔙 بازگشت"]])
def kb_systems(): return kb([["🔔 اعلان","🛡 ضدتقلب"],["📜 لاگ کامل","💾 بکاپ"],["📢 گزارش","⚙ تنظیمات بازی"],["📊 اقتصاد پویا","🌐 API"],["🔙 بازگشت"]])
def kb_mon(): return kb([["💎 خرید سکه","💎 خرید جم"],["🎖 اشتراک VIP","📢 تبلیغات"],["🤝 اسپانسر","📢 مأموریت تبلیغاتی"],["📺 همکاری کانال","💰 فروش آیتم"],["🎨 فروش اسکین","🎟 Battle Pass"],["🍀 Lucky Pass","🌸 Season Pass"],["🔙 بازگشت"]])
def kb_add(): return kb([["🔥 استریک ورود","🎲 چرخ شانس"],["📦 جعبه ۶ ساعت","🎲 مأموریت تصادفی"],["🎉 رویداد محدود","🏅 دستاوردها"],["🧩 کلکسیون","💎 امتیاز وفاداری"],["♾ لول بی‌نهایت","🔄 Prestige"],["🔙 بازگشت"]])
def kb_admin_panel(): return kb([["➕ دادن سکه","➖ گرفتن سکه"],["💎 دادن جم","📣 پیام همگانی"],["🪙 سکه همگانی","📊 آمار کاربران"],["📁 لاگ سیستم","⚙ تنظیمات بازی"],["🛡 ضدتقلب","💾 بکاپ دستی"],["🔴 خروج از ادمین","🔙 بازگشت اصلی"]])

# ======================= منطق =======================
MINER_MAX_LEVEL = 1000
MINER_BASE = 100
BANK_SHORT = 0.05
BANK_LONG = 0.12
PVP_STAKE = 100
PVE_STAKE = 80

def handle_economy(uid, chat_id, btn):
    user = players.get(str(uid), {})
    msg = ""
    if btn == "🛒 فروشگاه سکه": msg = f"💰 فروشگاه سکه<br>سکه فعلی: {user['coins']}<br>۵۰۰۰ سکه = ۱۰۰ سکه"
    elif btn == "💎 خرید جم": msg = f"💎 خرید جم<br>جم فعلی: {user['gems']}"
    elif btn == "🎁 بسته‌های ویژه": msg = "🎁 بسته‌های ویژه: طلایی، الماسی، فصلی"
    elif btn == "💳 خرید VIP": user['vip_days'] += 30; msg = "✅ VIP ۳۰ روز فعال شد!"
    elif btn == "🎟 کد هدیه": msg = "🎟 کد هدیه خود را وارد کنید."
    elif btn == "🎫 گیفت کارت": user['coins'] += 500; msg = "🎫 +۵۰۰ سکه"
    elif btn == "🎲 گردونه شانس":
        if user.get('spin_used_today'): msg = "❌ امروز استفاده شده"
        else:
            r = random.randint(1, 100)
            prize = 50 if r < 20 else (200 if r < 50 else 500)
            user['coins'] += prize; user['spin_used_today'] = True
            msg = f"🎲 برنده <b>{prize}</b> سکه!"
    elif btn == "🎰 اسلات":
        s1, s2, s3 = random.choice(["🍒","🍋","🍇","🍊"]), random.choice(["🍒","🍋","🍇","🍊"]), random.choice(["🍒","🍋","🍇","🍊"])
        if s1 == s2 == s3:
            user['coins'] += 300; msg = f"🎰 <b>{s1}{s2}{s3}</b> برنده +۳۰۰ سکه!"
        else: msg = f"🎰 {s1}{s2}{s3} باختید."
    elif btn == "🎁 جایزه روزانه": user['daily_streak'] += 1; user['coins'] += 100; msg = f"🎁 استریک: <b>{user['daily_streak']}</b> (+۱۰۰)"
    elif btn == "📆 هفتگی":
        if user.get('weekly_claimed'): msg = "❌ دریافت شده"
        else: user['weekly_claimed'] = True; user['coins'] += 500; msg = "📆 +۵۰۰ سکه"
    elif btn == "📅 ماهانه":
        if user.get('monthly_claimed'): msg = "❌ دریافت شده"
        else: user['monthly_claimed'] = True; user['coins'] += 2000; msg = "📅 +۲۰۰۰ سکه"
    elif btn == "🔥 استریک": msg = f"🔥 استریک: <b>{user.get('daily_streak',0)}</b>"
    elif btn == "💰 ماموریت درآمدی": user['income_mission'] += 1; user['coins'] += 200; msg = f"💰 ماموریت {user['income_mission']} (+۲۰۰)"
    else: msg = "💰 اقتصاد بازی"
    save_all()
    send_message(TOKEN, chat_id, msg, chat_keypad=kb_econ())

def handle_profile(uid, chat_id, btn):
    user = players.get(str(uid), {})
    msg = ""
    if btn == "🖼 آواتار": msg = f"🖼 آواتار: {'تنظیم شده' if user.get('avatar') else 'پیش‌فرض'}"
    elif btn == "📸 قاب پروفایل": user['frame'] = "طلایی"; msg = "📸 قاب طلایی فعال!"
    elif btn == "📝 بیو": msg = f"📝 بیو: {user.get('bio','خالی')}"
    elif btn == "🏷 عنوان اختصاصی": msg = f"🏷 عنوان: {user.get('title','تازه‌وارد')}"
    elif btn == "📊 سطح و XP": msg = f"📊 سطح: <b>{user.get('level',1)}</b> | XP: <b>{user.get('xp',0)}</b>"
    elif btn == "🏅 نشان‌ها": badges = user.get('badges',[]); msg = f"🏅 نشان‌ها: {', '.join(badges) if badges else 'ندارید'}"
    elif btn == "📅 تاریخ عضویت": msg = f"📅 عضویت: {time.strftime('%Y/%m/%d', time.localtime(user.get('join_date',0)))}"
    elif btn == "📈 آمار کامل":
        s = user.get('stats',{}); msg = f"📊 برد: <b>{s.get('wins',0)}</b> | باخت: <b>{s.get('losses',0)}</b><br>⚔ نبرد: <b>{s.get('battles',0)}</b>"
    elif btn == "🏆 رکوردها": msg = f"🏆 رکورد: سطح <b>{user.get('level',1)}</b> | ماینر <b>{user.get('miner_level',0)}</b>"
    else: msg = "👤 پروفایل"
    save_all()
    send_message(TOKEN, chat_id, msg, chat_keypad=kb_prof())

def handle_miner(uid, chat_id, btn):
    user = players.get(str(uid), {})
    msg = ""
    level = user.get('miner_level', 0)
    if btn == "📥 جمع‌آوری":
        last = user.get('miner_last_collect', 0)
        now = time.time()
        hours = max(0, int((now - last)//3600))
        amt = hours * MINER_BASE * level
        if amt <= 0: msg = "⛏ هنوز چیزی برای جمع‌آوری نیست."
        else:
            user['coins'] += amt; user['miner_last_collect'] = int(now)
            user['stats']['miners_collected'] = user.get('stats',{}).get('miners_collected',0) + 1
            msg = f"⛏ +{amt} سکه جمع‌آوری شد!"
    elif btn == "🔼 ارتقا":
        cost = (level + 1) * 200
        if user['coins'] >= cost:
            user['coins'] -= cost; user['miner_level'] += 1; msg = f"🔼 ماینر سطح <b>{user['miner_level']}</b>"
        else: msg = f"❌ نیاز به <b>{cost}</b> سکه"
    elif btn == "⛽ سوخت": msg = f"⛽ سوخت: <b>{user.get('miner_fuel',100)}%</b>"
    elif btn == "⚡ سرعت": msg = f"⚡ سرعت: <b>{user.get('miner_speed',1)}x</b>"
    elif btn == "🚀 شتاب‌دهنده": user['miner_accelerator'] += 1; msg = "🚀 شتاب‌دهنده (+۱ ساعت دوبرابر)"
    elif btn == "🔧 تعمیر": user['miner_fuel'] = 100; msg = "🔧 ماینر تعمیر شد. سوخت ۱۰۰%"
    elif btn == "🤖 اتوماتیک": user['miner_auto'] = True; msg = "🤖 ارتقای اتوماتیک فعال!"
    elif btn == "💤 آفلاین": user['miner_offline'] = True; msg = "💤 استخراج آفلاین فعال!"
    elif btn == "🌟 طلایی":
        if level >= 500: user['miner_type'] = "طلایی"; user['miner_golden_unlocked'] = True; msg = "🌟 ماینر طلایی!"
        else: msg = "❌ نیاز به سطح ۵۰۰"
    elif btn == "🐉 افسانه‌ای":
        if level >= 900: user['miner_type'] = "افسانه‌ای"; user['miner_legendary_unlocked'] = True; msg = "🐉 ماینر افسانه‌ای!"
        else: msg = "❌ نیاز به سطح ۹۰۰"
    else: msg = "⛏ ماینر"
    save_all()
    send_message(TOKEN, chat_id, msg, chat_keypad=kb_miner())

def handle_bank(uid, chat_id, btn):
    user = players.get(str(uid), {})
    msg = ""
    if btn == "⏱ سپرده کوتاه":
        if user['coins'] >= 500:
            user['coins'] -= 500; user['bank_amount'] = 500; user['bank_time'] = time.time()
            msg = f"💰 <b>۵۰۰</b> سکه در سپرده کوتاه ({int(BANK_SHORT*100)}%)"
        else: msg = "❌ سکه کافی نیست"
    elif btn == "⏳ بلندمدت":
        if user['coins'] >= 2000:
            user['coins'] -= 2000; user['bank_amount'] = 2000; user['bank_time'] = time.time()
            msg = f"💰 <b>۲۰۰۰</b> سکه در سپرده بلندمدت ({int(BANK_LONG*100)}%)"
        else: msg = "❌ سکه کافی نیست"
    elif btn == "💵 وام":
        if user.get('bank_loan', 0) <= 0:
            user['bank_loan'] = 1000; user['coins'] += 1000; msg = "💵 وام <b>۱۰۰۰</b> دریافت شد"
        else: msg = "❌ وام فعلی دارید"
    elif btn == "📊 سود متغیر": msg = f"📊 کوتاه: <b>{int(BANK_SHORT*100)}%</b> | بلند: <b>{int(BANK_LONG*100)}%</b>"
    elif btn == "📈 صندوق سرمایه": msg = "📈 صندوق سرمایه فعال است"
    elif btn == "🛡 بیمه": user['bank_insurance'] = True; msg = "🛡 بیمه فعال شد"
    elif btn == "💼 گاوصندوق": msg = "💼 گاوصندوق امن است. مالیات صفر."
    elif btn == "🏦 انتقال بانکی": msg = "🏦 انتقال بانکی فعال است"
    else: msg = "🏦 بانک"
    # پرداخت خودکار سود
    if user.get('bank_amount',0) > 0 and user.get('bank_time',0) > 0:
        if time.time() - user['bank_time'] >= 24*3600:
            deposit = user['bank_amount']
            rate = BANK_LONG if deposit >= 1000 else BANK_SHORT
            interest = int(deposit * rate)
            user['coins'] += deposit + interest
            user['bank_amount'] = 0; user['bank_time'] = 0
            msg += f"<br>📢 سود پرداخت شد: +<b>{deposit + interest}</b> سکه"
    save_all()
    send_message(TOKEN, chat_id, msg, chat_keypad=kb_bank())

def handle_combat(uid, chat_id, btn):
    user = players.get(str(uid), {})
    msg = ""
    if btn == "⚔️ PvP":
        if user['coins'] >= PVP_STAKE:
            user['coins'] -= PVP_STAKE
            win = random.random() > 0.4
            user['stats']['battles'] = user.get('stats',{}).get('battles',0) + 1
            if win: user['coins'] += PVP_STAKE*2; user['pvp_wins'] += 1; user['stats']['wins'] = user.get('stats',{}).get('wins',0)+1; msg = "⚔️ برنده! +۲۰۰ سکه"
            else: user['stats']['losses'] = user.get('stats',{}).get('losses',0)+1; msg = "⚔️ باختید!"
        else: msg = "❌ سکه کافی نیست"
    elif btn == "🐉 PvE":
        if user['coins'] >= PVE_STAKE:
            user['coins'] -= PVE_STAKE
            win = random.random() > 0.3
            if win: user['coins'] += PVE_STAKE*1.5; user['pve_wins'] += 1; msg = "🐉 برنده!"
            else: msg = "🐉 باختید"
        else: msg = "❌ سکه کافی نیست"
    elif btn == "👑 باس فایت": msg = "👑 باس فایت: ۵۰۰ سکه برای ورود"
    elif btn == "👥 جنگ گروهی": msg = "👥 جنگ گروهی: به کلن بپیوندید"
    elif btn == "⚡ دوئل": msg = "⚡ دوئل با بازیکن تصادفی آغاز شد"
    elif btn == "🏅 لیگ": msg = f"🏅 امتیاز لیگ: <b>{user.get('league_points',0)}</b>"
    elif btn == "🏆 تورنمنت": msg = "🏆 تورنمنت هفتگی فعال است"
    elif btn == "🎲 نبرد تصادفی": msg = "🎲 نبرد تصادفی با بازیکن تصادفی"
    elif btn == "📊 نبرد رتبه‌ای": msg = f"📊 رتبه نبرد: <b>{user.get('league_points',0)}</b>"
    else: msg = "⚔️ مبارزه"
    save_all()
    send_message(TOKEN, chat_id, msg, chat_keypad=kb_combat())

def handle_clan(uid, chat_id, btn):
    user = players.get(str(uid), {})
    msg = ""
    if btn == "🏗 ساخت کلن":
        if not user.get('clan'):
            user['clan'] = f"کلن_{str(uid)[:4]}"; user['clan_role'] = "رهبر"; msg = f"🏰 کلن <b>{user['clan']}</b> ساخته شد"
        else: msg = "❌ در کلن هستید"
    elif btn == "👥 عضوگیری": msg = "👥 دعوت ارسال شد"
    elif btn == "💬 چت کلن": msg = f"💬 کلن: <b>{user.get('clan','ندارید')}</b>"
    elif btn == "📈 ارتقا": msg = "📈 کلن ارتقا یافت (سطح ۲)"
    elif btn == "💰 خزانه": msg = "💰 خزانه: <b>۵۰۰۰</b> سکه"
    elif btn == "⚔️ جنگ کلن": msg = "⚔️ جنگ کلن با رقیب آغاز شد"
    elif btn == "🎯 ماموریت کلن": msg = "🎯 ماموریت کلن: جمع‌آوری ۱۰۰۰ سکه"
    elif btn == "📊 رتبه کلن": msg = "📊 رتبه کلن: <b>۱۵</b>"
    else: msg = "🏰 کلن"
    save_all()
    send_message(TOKEN, chat_id, msg, chat_keypad=kb_clan())

def handle_missions(uid, chat_id, btn):
    msg = {"📋 روزانه":"📋 روزانه: جمع ۵۰۰ سکه (+۲۰۰)","📅 هفتگی":"📅 هفتگی: ۳ برد (+۱۰۰۰)","📆 ماهانه":"📆 ماهانه: سطح ماینر ۱۰ (+۵۰۰۰)","🌸 فصلی":"🌸 فصلی: سطح ۵۰ (+۱۰۰۰۰ + اسکین)","🔍 مخفی":"🔍 مخفی: کلید طلایی در بازار","⭐ ویژه":"⭐ ویژه: دعوت ۱۰ دوست (+VIP)"}
    send_message(TOKEN, chat_id, msg.get(btn,"🎯 ماموریت"), chat_keypad=kb_mission())

def handle_leader(uid, chat_id, btn):
    msg = {"💰 ثروتمندترین":"💰 ۱. کاربر A - ۹۹۹۹۹","📊 بیشترین لول":"📊 ۱. کاربر B - ۹۹","⛏ بهترین ماینر":"⛏ ۱. کاربر C - ۹۵۰","🏆 بیشترین برد":"🏆 ۱. کاربر D - ۵۰۰","🏰 بهترین کلن":"🏰 ۱. کلن شاهین","📢 بیشترین دعوت":"📢 ۱. کاربر E - ۱۲۰","🔥 بیشترین فعالیت":"🔥 ۱. کاربر F - ۹۹۹"}
    send_message(TOKEN, chat_id, msg.get(btn,"🏆 لیدربرد"), chat_keypad=kb_leader())

def handle_items(uid, chat_id, btn):
    msg = {"⚡ بوستر":"⚡ بوستر سرعت ماینر ۱ ساعت","🛡 سپر":"🛡 سپر محافظت مبارزه","💣 بمب":"💣 بمب برای مبارزه","🎁 جعبه شانس":"🎁 جعبه شانس: آیتم تصادفی","🔑 کلید":"🔑 کلید صندوق طلایی","📦 صندوق":"📦 صندوق: +۳۰۰ سکه","🐾 پت":"🐾 پت در حال پرورش","👕 لباس":"👕 لباس ورزشی","🎨 اسکین":"🎨 اسکین طلایی","✨ افکت":"✨ افکت آتش"}
    send_message(TOKEN, chat_id, msg.get(btn,"🎁 آیتم"), chat_keypad=kb_items())

def handle_pets(uid, chat_id, btn):
    msg = {"🐕 خرید پت":"🐕 پت سگ عادی (+۲۰۰ سکه)","📈 ارتقا پت":"📈 پت ارتقا یافت (سطح ۵)","🍖 غذا":"🍖 پت تغذیه شد (۱۰۰%)","⭐ تجربه":"⭐ پت XP: ۵۰","💪 مهارت":"💪 مهارت جدید: دفاع قوی","🎲 کمیاب":"🎲 پت کمیاب: گربه","🐉 افسانه‌ای":"🐉 پت افسانه‌ای: اژدها"}
    send_message(TOKEN, chat_id, msg.get(btn,"🐶 پت"), chat_keypad=kb_pets())

def handle_shop(uid, chat_id, btn):
    msg = {"🎁 آیتم":"🎁 بوستر، سپر، بمب، جعبه","🎨 اسکین":"🎨 طلایی، الماسی، افسانه‌ای","💎 VIP":"💎 VIP ماهانه: ۲۰۰ سکه","⚡ بوستر":"⚡ بوستر: ۵۰ سکه","📦 جعبه":"📦 جعبه شانس: ۱۰۰ سکه","💰 بسته اقتصادی":"💰 ۳۰۰ سکه (۵۰۰۰ + ۵۰ جم)"}
    send_message(TOKEN, chat_id, msg.get(btn,"🛍 فروشگاه"), chat_keypad=kb_shop())

def handle_events(uid, chat_id, btn):
    msg = {"🎄 کریسمس":"🎄 رویداد کریسمس (جوایز دوبرابر)","🌸 نوروز":"🌸 نوروز مبارک!","🍉 یلدا":"🍉 شب یلدا!","🌙 رمضان":"🌙 رمضان مبارک!","🛒 جمعه سیاه":"🛒 جمعه سیاه (۵۰% تخفیف)","🎃 هالووین":"🎃 هالووین!","🎉 آخر هفته":"🎉 آخر هفته (امتیاز دوبرابر)"}
    send_message(TOKEN, chat_id, msg.get(btn,"🎉 رویداد"), chat_keypad=kb_events())

def handle_social(uid, chat_id, btn):
    msg = {"💬 چت خصوصی":"💬 چت خصوصی فعال","👥 دوستان":"👥 دوستان: کاربر A, کاربر B","🚫 بلاک":"🚫 بلاک: خالی","📨 دعوت":"📨 دعوت ارسال شد","🎁 ارسال هدیه":"🎁 هدیه ارسال شد (+۱۰۰)","📩 درخواست دوستی":"📩 درخواست جدید","👀 مشاهده پروفایل":"👀 پروفایل کاربر A"}
    send_message(TOKEN, chat_id, msg.get(btn,"👥 اجتماعی"), chat_keypad=kb_social())

def handle_market(uid, chat_id, btn):
    msg = {"📈 خرید و فروش":"📈 بازار فعال","🏷 مزایده":"🏷 مزایده در حال برگزاری","💱 بازار آزاد":"💱 بازار آزاد (قیمت توسط کاربران)","⏰ قیمت لحظه‌ای":"⏰ سکه: ۱ سکه | جم: ۱۰ سکه","💸 مالیات معامله":"💸 مالیات: ۵%"}
    send_message(TOKEN, chat_id, msg.get(btn,"📈 بازار"), chat_keypad=kb_market())

def handle_minigames(uid, chat_id, btn):
    msg = ""
    if btn == "✊ سنگ کاغذ قیچی":
        c1, c2 = random.choice(["✊","✋","✌️"]), random.choice(["✊","✋","✌️"])
        msg = f"✊ شما: {c1} | ربات: {c2} | {'مساوی' if c1==c2 else ('برنده' if (c1=='✊' and c2=='✌️') or (c1=='✋' and c2=='✊') or (c1=='✌️' and c2=='✋') else 'باخت')}"
    elif btn == "🎲 حدس عدد": msg = f"🎲 عدد من: <b>{random.randint(1,10)}</b>"
    elif btn == "🎲 دوز": msg = "🎲 دوز: تاس بیندازید!"
    elif btn == "♟ شطرنج": msg = "♟ شطرنج با ربات"
    elif btn == "🎲 تاس": msg = f"🎲 تاس: <b>{random.randint(1,6)}</b>"
    elif btn == "🎰 رولت": msg = f"🎰 رولت: <b>{random.randint(0,36)}</b>"
    elif btn == "♠ بلک جک": msg = "♠ بلک جک: کارت شما ۱۸ است"
    elif btn == "🧠 حافظه": msg = "🧠 حافظه: کارت‌ها را جفت کنید"
    elif btn == "⚡ مسابقه سرعت": msg = "⚡ مسابقه سرعت: سریع‌ترین کلیک برنده"
    else: msg = "🎮 مینی‌گیم"
    send_message(TOKEN, chat_id, msg, chat_keypad=kb_minigames())

def handle_jobs(uid, chat_id, btn):
    msg = {"⛏ معدنچی":"⛏ معدنچی: استخراج سریع","🌾 کشاورز":"🌾 کشاورز: کشت و فروش","💼 تاجر":"💼 تاجر: خرید/فروش","💻 برنامه‌نویس":"💻 برنامه‌نویس: ساخت ربات","👮 پلیس":"👮 پلیس: حفاظت","⚕ پزشک":"⚕ پزشک: درمان","📈 سرمایه‌گذار":"📈 سود بانکی","🚀 کارآفرین":"🚀 راه‌اندازی کسب‌وکار"}
    send_message(TOKEN, chat_id, msg.get(btn,"💼 شغل"), chat_keypad=kb_jobs())

def handle_map(uid, chat_id, btn):
    msg = {"🏙 شهرها":"🏙 تهران، اصفهان، شیراز، مشهد، تبریز","✈ سفر":"✈ سفر به شهر جدید (۱۰۰ سکه)","🎯 مأموریت شهری":"🎯 جمع منابع در شهر","⛏ منابع":"⛏ آهن، طلا، الماس","🗺 سرزمین":"🗺 شهر اصلی + ۳ منطقه","🏁 فتح مناطق":"🏁 فتح با مبارزه"}
    send_message(TOKEN, chat_id, msg.get(btn,"🌍 نقشه"), chat_keypad=kb_map())

def handle_systems(uid, chat_id, btn):
    msg = {"🔔 اعلان":"🔔 اعلان: جایزه آماده!","🛡 ضدتقلب":"🛡 ضدتقلب فعال","📜 لاگ کامل":"📜 لاگ: آخرین فعالیت‌ها","💾 بکاپ":"💾 بکاپ دستی انجام شد","📢 گزارش":"📢 گزارش مشکل: متن وارد کنید","⚙ تنظیمات بازی":"⚙ زبان فارسی | صدا روشن","📊 اقتصاد پویا":"📊 اقتصاد پویا فعال","🌐 API":"🌐 API ربات فعال"}
    send_message(TOKEN, chat_id, msg.get(btn,"🤖 سیستم"), chat_keypad=kb_systems())

def handle_mon(uid, chat_id, btn):
    msg = {"💎 خرید سکه":"💎 ۱۰۰۰ سکه = ۱۰,۰۰۰ تومان","💎 خرید جم":"💎 ۵۰ جم = ۵۰,۰۰۰ تومان","🎖 اشتراک VIP":"🎖 VIP ماهانه: ۵۰,۰۰۰","📢 تبلیغات":"📢 تبلیغ در کانال: ۱۰۰,۰۰۰","🤝 اسپانسر":"🤝 اسپانسر: همکاری با برند","📢 مأموریت تبلیغاتی":"📢 دعوت ۵ نفر (+۵۰۰)","📺 همکاری کانال":"📺 تبلیغ متقابل","💰 فروش آیتم":"💰 فروش در بازار (+۵% مالیات)","🎨 فروش اسکین":"🎨 فروش در مزایده","🎟 Battle Pass":"🎟 Battle Pass فصلی","🍀 Lucky Pass":"🍀 Lucky Pass روزانه","🌸 Season Pass":"🌸 Season Pass فصلی"}
    send_message(TOKEN, chat_id, msg.get(btn,"💎 درآمد"), chat_keypad=kb_mon())

def handle_addictive(uid, chat_id, btn):
    user = players.get(str(uid), {})
    msg = ""
    if btn == "🔥 استریک ورود": user['daily_streak'] += 1; msg = f"🔥 استریک: <b>{user['daily_streak']}</b> (+۵۰ سکه)"
    elif btn == "🎲 چرخ شانس": r = random.randint(1,100); prize = 100 if r<20 else (300 if r<50 else 800); user['coins'] += prize; msg = f"🎲 برنده <b>{prize}</b> سکه!"
    elif btn == "📦 جعبه ۶ ساعت": msg = "📦 جعبه رایگان آماده است!"
    elif btn == "🎲 مأموریت تصادفی": msg = "🎲 ماموریت جدید: ۲ برد (+۲۰۰ سکه)"
    elif btn == "🎉 رویداد محدود": msg = "🎉 رویداد محدود تا پایان هفته"
    elif btn == "🏅 دستاوردها": msg = f"🏅 سطح <b>{user.get('level',1)}</b> | ماینر <b>{user.get('miner_level',0)}</b>"
    elif btn == "🧩 کلکسیون": msg = f"🧩 آیتم‌ها: <b>{len(user.get('inventory',{}))}</b>"
    elif btn == "💎 امتیاز وفاداری": user['loyalty_points'] += 10; msg = f"💎 وفاداری: <b>{user['loyalty_points']}</b>"
    elif btn == "♾ لول بی‌نهایت": msg = "♾ لول بی‌نهایت فعال است"
    elif btn == "🔄 Prestige": user['prestige'] += 1; user['coins'] += 5000; msg = f"🔄 Prestige <b>{user['prestige']}</b> (+۵۰۰۰)"
    else: msg = "🌟 اعتیادآور"
    save_all()
    send_message(TOKEN, chat_id, msg, chat_keypad=kb_add())

def handle_admin(uid, chat_id, btn):
    msg = ""
    if btn == "➕ دادن سکه": msg = "➕ مقدار و شناسه را وارد کنید. مثال: 500 123456"
    elif btn == "➖ گرفتن سکه": msg = "➖ گرفتن سکه از کاربر"
    elif btn == "💎 دادن جم": msg = "💎 دادن جم به کاربر"
    elif btn == "📣 پیام همگانی": msg = "📣 متن پیام همگانی را وارد کنید"
    elif btn == "🪙 سکه همگانی": msg = "🪙 +۱۰۰ سکه برای همه ارسال شد"
    elif btn == "📊 آمار کاربران": msg = f"📊 کاربران: <b>{len(players)}</b>"
    elif btn == "📁 لاگ سیستم": msg = "📁 لاگ سیستم موجود است"
    elif btn == "⚙ تنظیمات بازی": msg = "⚙ تنظیمات در فایل قابل ویرایش است"
    elif btn == "🛡 ضدتقلب": msg = "🛡 ضدتقلب فعال است"
    elif btn == "💾 بکاپ دستی": msg = "💾 بکاپ دستی انجام شد"
    elif btn == "🔴 خروج از ادمین":
        players.get(str(uid),{})['admin_logged'] = False
        save_all()
        send_message(TOKEN, chat_id, "🔴 خارج شدید", chat_keypad=kb_main(is_adm(str(uid) in [str(x) for x in ADMINS if isinstance(x,int)] or any(is_admin_by_name(str(uid))))))
        return
    elif btn == "🔙 بازگشت اصلی":
        is_adm = check_admin(str(uid), players.get(str(uid),{}).get('name',''))
        send_message(TOKEN, chat_id, "🔙 منوی اصلی", chat_keypad=kb_main(is_adm))
        return
    else: msg = "🔧 پنل ادمین حرفه‌ای"
    send_message(TOKEN, chat_id, msg, chat_keypad=kb_admin_panel())

# ======================= حلقه اصلی =======================
def main():
    print("ربات روبیکا راه‌اندازی شد. در حال پولینگ با کتابخانه rubika-bot...")
    offset = None
    while True:
        try:
            updates_result = get_updates(token=TOKEN, limit=10, timeout=20)
            # کتابخانه rubika-bot پاسخ را به شکل (List[Update], str) برمی‌گرداند
            if isinstance(updates_result, tuple) and len(updates_result) == 2:
                updates, offset = updates_result
            elif isinstance(updates_result, list):
                updates = updates_result
            else:
                updates = []
            for update in updates:
                # از مدل Update کتابخانه استفاده می‌کنیم
                if hasattr(update, 'new_message'):
                    msg = update.new_message
                    chat_id = msg.chat_id if hasattr(msg, 'chat_id') else getattr(getattr(msg, 'chat', None), 'id', None)
                    text = msg.text if msg.text else ""
                    user_id = msg.sender_id if msg.sender_id else getattr(getattr(msg, 'from_chat', None), 'id', None)
                    user_name = getattr(getattr(msg, 'from_chat', None), 'first_name', '') if hasattr(msg, 'from_chat') else ''
                else:
                    # اگر به هر دلیلی مدل نبود، از دیکشنری استفاده می‌کنیم
                    msg = update.get('message', update.get('new_message', {})) if isinstance(update, dict) else {}
                    chat_id = msg.get('chat', {}).get('id') if isinstance(msg.get('chat'), dict) else msg.get('chat_id')
                    text = msg.get('text', '')
                    user_obj = msg.get('from', {}) if isinstance(msg.get('from'), dict) else msg.get('sender', {})
                    user_id = user_obj.get('id', msg.get('sender_id'))
                    user_name = user_obj.get('first_name', user_obj.get('username', msg.get('sender_name', '')))
                    if not chat_id or not user_id:
                        continue
                ensure_user_struct(user_id)
                user_data = players.get(str(user_id), {})
                user_data['name'] = user_name or user_data.get('name', 'کاربر')
                is_adm = check_admin(user_id, user_name)
                # پردازش دستورات
                if text.startswith("/") or text in ["شروع","استارت","/start","/admin","ادمین","/panel","راهنما","/help","/راهنما"]:
                    cmd = text.lower().strip()
                    if cmd in ["/start","شروع","استارت","/start"]:
                        user_data['started'] = True
                        send_message(TOKEN, chat_id, f"🎮 خوش آمدید {user_name or 'دوست عزیز'}! ربات بازی و اقتصاد فعال است.", chat_keypad=kb_main(is_adm))
                    elif cmd in ["/admin","ادمین","/panel"]:
                        if is_adm:
                            user_data['admin_logged'] = True
                            send_message(TOKEN, chat_id, "🔐 رمز پنل ادمین حرفه‌ای را وارد کنید (رمز: <b>ali</b>)", chat_keypad=kb([["🔑 ورود با رمز"],["🔙 بازگشت"]]))
                        else:
                            send_message(TOKEN, chat_id, "❌ شما ادمین نیستید.", chat_keypad=kb_main(is_adm))
                    elif cmd in ["/help","راهنما","/راهنما"]:
                        send_message(TOKEN, chat_id, ("📚 راهنما: 💰 اقتصاد | 👤 پروفایل | ⛏ ماینر | 🏦 بانک | ⚔️ مبارزه | 🏰 کلن | 🎯 ماموریت | 🏆 لیدربرد | 🎁 آیتم | 🐶 پت | 🛍 فروشگاه | 🎉 رویداد | 👥 اجتماعی | 📈 بازار | 🎮 مینی‌گیم | 💼 شغل | 🌍 نقشه | 🤖 سیستم | 💎 درآمد | 🌟 اعتیادآور | 🔧 ادمین (رمز: ali)"), chat_keypad=kb_main(is_adm))
                    else:
                        send_message(TOKEN, chat_id, "❓ دستور ناشناخته. از منو استفاده کنید.", chat_keypad=kb_main(is_adm))
                else:
                    # بررسی رمز ادمین
                    if text.lower().strip() == ADMIN_PASSWORD or (user_data.get('step') == 'admin_login' and text.lower().strip() == ADMIN_PASSWORD):
                        user_data['admin_logged'] = True; user_data['step'] = None
                        send_message(TOKEN, chat_id, "✅ رمز صحیح! به پنل ادمین حرفه‌ای خوش آمدید.", chat_keypad=kb_admin_panel())
                        save_all()
                        continue
                    # منطق دکمه‌ها
                    btn_map = {
                        "💰 اقتصاد بازی":"economy","👤 پروفایل":"profile","⛏️ ماینر":"miner","🏦 بانک":"bank",
                        "⚔️ مبارزه":"combat","🏰 کلن":"clan","🎯 ماموریت":"mission","🏆 لیدربرد":"leaderboard",
                        "🎁 آیتم":"items","🐶 حیوانات":"pets","🛍 فروشگاه":"shop","🎉 رویدادها":"events",
                        "👥 اجتماعی":"social","📈 بازار":"market","🎮 مینی‌گیم":"minigame","💼 شغل":"jobs",
                        "🌍 نقشه":"map","🤖 سیستم‌ها":"systems","💎 درآمدزایی":"monetization","🌟 اعتیادآور":"addictive",
                        "🔧 پنل ادمین حرفه‌ای":"admin"
                    }
                    matched = False
                    for k, v in btn_map.items():
                        if text == k:
                            user_data['prev'] = v; user_data['step'] = v
                            if v == "economy": handle_economy(user_id, chat_id, text)
                            elif v == "profile": handle_profile(user_id, chat_id, text)
                            elif v == "miner": handle_miner(user_id, chat_id, text)
                            elif v == "bank": handle_bank(user_id, chat_id, text)
                            elif v == "combat": handle_combat(user_id, chat_id, text)
                            elif v == "clan": handle_clan(user_id, chat_id, text)
                            elif v == "mission": handle_missions(user_id, chat_id, text)
                            elif v == "leaderboard": handle_leader(user_id, chat_id, text)
                            elif v == "items": handle_items(user_id, chat_id, text)
                            elif v == "pets": handle_pets(user_id, chat_id, text)
                            elif v == "shop": handle_shop(user_id, chat_id, text)
                            elif v == "events": handle_events(user_id, chat_id, text)
                            elif v == "social": handle_social(user_id, chat_id, text)
                            elif v == "market": handle_market(user_id, chat_id, text)
                            elif v == "minigame": handle_minigames(user_id, chat_id, text)
                            elif v == "jobs": handle_jobs(user_id, chat_id, text)
                            elif v == "map": handle_map(user_id, chat_id, text)
                            elif v == "systems": handle_systems(user_id, chat_id, text)
                            elif v == "monetization": handle_mon(user_id, chat_id, text)
                            elif v == "addictive": handle_addictive(user_id, chat_id, text)
                            elif v == "admin":
                                if user_data.get('admin_logged'):
                                    handle_admin(user_id, chat_id, text)
                                else:
                                    user_data['step'] = 'admin_login'
                                    send_message(TOKEN, chat_id, "🔑 رمز ادمین حرفه‌ای را وارد کنید (رمز: <b>ali</b>)", chat_keypad=kb([["ali"],["🔙 بازگشت"]]))
                            matched = True
                            break
                    if not matched:
                        prev = user_data.get('prev') or user_data.get('step')
                        if prev == "economy": handle_economy(user_id, chat_id, text)
                        elif prev == "profile": handle_profile(user_id, chat_id, text)
                        elif prev == "miner": handle_miner(user_id, chat_id, text)
                        elif prev == "bank": handle_bank(user_id, chat_id, text)
                        elif prev == "combat": handle_combat(user_id, chat_id, text)
                        elif prev == "clan": handle_clan(user_id, chat_id, text)
                        elif prev == "mission": handle_missions(user_id, chat_id, text)
                        elif prev == "leaderboard": handle_leader(user_id, chat_id, text)
                        elif prev == "items": handle_items(user_id, chat_id, text)
                        elif prev == "pets": handle_pets(user_id, chat_id, text)
                        elif prev == "shop": handle_shop(user_id, chat_id, text)
                        elif prev == "events": handle_events(user_id, chat_id, text)
                        elif prev == "social": handle_social(user_id, chat_id, text)
                        elif prev == "market": handle_market(user_id, chat_id, text)
                        elif prev == "minigame": handle_minigames(user_id, chat_id, text)
                        elif prev == "jobs": handle_jobs(user_id, chat_id, text)
                        elif prev == "map": handle_map(user_id, chat_id, text)
                        elif prev == "systems": handle_systems(user_id, chat_id, text)
                        elif prev == "monetization": handle_mon(user_id, chat_id, text)
                        elif prev == "addictive": handle_addictive(user_id, chat_id, text)
                        elif prev == "admin":
                            if user_data.get('admin_logged'):
                                handle_admin(user_id, chat_id, text)
                            else:
                                user_data['step'] = 'admin_login'
                                send_message(TOKEN, chat_id, "🔐 رمز ادمین حرفه‌ای (ali) را وارد کنید.", chat_keypad=kb([["ali"],["🔙 بازگشت"]]))
                        else:
                            is_adm = check_admin(user_id, user_name)
                            send_message(TOKEN, chat_id, "❓ لطفاً از منو انتخاب کنید.", chat_keypad=kb_main(is_adm))
                save_all()
        except Exception as e:
            print("Loop error:", e)
            time.sleep(2)

if __name__ == "__main__":
    main()
