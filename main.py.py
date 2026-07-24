..# -- coding: utf-8 --
"""

"""

import urllib.request
import urllib.parse
import json
import os
import time
import random
from typing import Dict, Any

# ---------------- تنظیمات ---------------- #
TOKEN = "2012882271:Njz5XlWS6LLYTiT5arMZ2TZNOifXOjiol1g"   # ← توکن رباتت را اینجا بگذار
BOT_URL = f"https://tapi.bale.ir/bot{TOKEN}/"
CHANNEL = "@coin_war"
DATA_FILE = "players.json"
PENDING_GAMES_FILE = "pending_games.json"

ADMINS = [1570690274]

DEFAULT_COINS = 1000
ROBOT_POWER = 100
BANK_INTEREST_RATE = 0.05
MINER_BASE_PER_LEVEL = 100
MINER_MAX_LEVEL = 100

BAD_NAME_KEYWORDS = [
    "بد", "مسخره", "fuck", "shit", "کور", "فروش", "دزد", "حرومزاده"
]

# ---------------- توابع API ---------------- #
def api_request(method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    درخواست به API بله.
    اگر params داده شود آن‌ها را به query-string تبدیل می‌کنیم (GET).
    reply_markup اگر باشد به JSON تبدیل می‌شود (ensure_ascii=False).
    تابع همیشه دیکشنری برگشت می‌دهد.
    """
    url = BOT_URL + method
    safe = {}
    if params:
        for k, v in params.items():
            if k == "reply_markup":
                # reply_markup را به رشتهٔ JSON تبدیل کن (utf-8 safe)
                safe[k] = json.dumps(v, ensure_ascii=False)
            else:
                safe[k] = v
    try:
        if safe:
            query = urllib.parse.urlencode(safe, doseq=True)
            full_url = url + "?" + query
            req = urllib.request.Request(full_url)
            with urllib.request.urlopen(req, timeout=30) as res:
                text = res.read()
        else:
            # هیچ پارامتری نیست -> مستقیم GET
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as res:
                text = res.read()
        try:
            return json.loads(text)
        except Exception:
            # اگر JSON نبود، خطا چاپ کن ولی برنامه ادامه میده
            print("api_request: failed to decode JSON response")
            return {}
    except Exception as e:
        print("API request error:", e)
        return {}

def get_updates(offset=None, timeout=20):
    params = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset
    return api_request("getUpdates", params)

def send_message(chat_id, text, reply_markup=None):
    params = {"chat_id": chat_id, "text": text}
    if reply_markup is not None:
        params["reply_markup"] = reply_markup
    return api_request("sendMessage", params)

# ---------------- ذخیره/بارگذاری ---------------- #
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
pending_games = load_json(PENDING_GAMES_FILE, [])

def save_all():
    save_json(DATA_FILE, players)
    save_json(PENDING_GAMES_FILE, pending_games)

# ---------------- کیبوردها ---------------- #
def keyboard_main(is_admin_user=False):
    kb = [
        ["🎮 بازی", "🏦 بانک"],
        ["⛏️ ماینر", "✏️ تغییر نام"],
        ["🏆 بهترین‌ها", "💸 انتقال سکه"],
        ["👤 وضعیت من"]
    ]
    if is_admin_user:
        kb.append(["🔧 پنل ادمین"])
    return {"keyboard": kb, "resize_keyboard": True}

def keyboard_yesno(back=True):
    kb = {"keyboard": [["✅ بله", "❌ خیر"]], "resize_keyboard": True, "one_time_keyboard": True}
    if back:
        kb["keyboard"].append(["🔙 بازگشت"])
    return kb

def keyboard_game_choice():
    return {"keyboard": [["🎯 بازی با ربات", "👥 بازی با بازیکن"], ["➕ ساخت یک بازی"], ["🔙 بازگشت"]], "resize_keyboard": True}

def keyboard_admin_panel():
    return {"keyboard": [["➕ دادن سکه", "➖ گرفتن سکه"], ["📣 پیام همگانی", "🪙 سکه همگانی"], ["🔙 بازگشت"]], "resize_keyboard": True}

def keyboard_miner():
    return {"keyboard": [["📥 جمع‌آوری پاداش", "🔼 ارتقا ماینر"], ["🔙 بازگشت"]], "resize_keyboard": True}

def keyboard_bank_has_money():
    return {"keyboard":[["🏦 برداشت","🔙 بازگشت"]],"resize_keyboard":True}

def kb_single_back():
    return {"keyboard":[["🔙 بازگشت"]],"resize_keyboard":True}

def kb_pending_view(game_id):
    if game_id is None:
        return {"keyboard": [["🔙 بازگشت"]], "resize_keyboard": True}
    return {"keyboard": [["بعد"], [f"✅ قبول {game_id}", f"❌ رد {game_id}"], ["🔙 بازگشت"]], "resize_keyboard": True}

# ---------------- کمک‌ها ---------------- #
def ensure_user_struct(user_id: int):
    uid = str(user_id)
    if uid not in players:
        players[uid] = {
            "name": None,
            "coins": DEFAULT_COINS,
            "miner_level": 0,
            "miner_last_collect": 0,
            "bank_amount": 0,
            "bank_time": 0,
            "step": None,
            "admin_step": None,
            "started": False,
            "view_pending_index": None
        }
        save_all()

def is_admin(user_id):
    try:
        return int(user_id) in ADMINS
    except:
        return False

def name_is_bad(name: str) -> bool:
    if not name:
        return True
    lowered = name.lower()
    for bad in BAD_NAME_KEYWORDS:
        if bad in lowered:
            return True
    return False

# ---------------- بانک و ماینر ---------------- #
def miner_accumulated(user: Dict[str, Any]) -> int:
    level = user.get("miner_level", 0)
    if level <= 0:
        return 0
    last = user.get("miner_last_collect", 0)
    now = time.time()
    if last <= 0:
        return 0
    hours = int((now - last) // 3600)
    return hours * (MINER_BASE_PER_LEVEL * level)

def collect_miner(user_id, chat_id):
    uid = str(user_id)
    user = players[uid]
    amt = miner_accumulated(user)
    if amt <= 0:
        send_message(chat_id, "⛏️ هنوز چیزی برای جمع‌آوری نیست. ساعتی تولید می‌شود؛ بعداً امتحان کن.", reply_markup=kb_single_back())
        return
    user["coins"] += amt
    user["miner_last_collect"] = int(time.time())
    save_all()
    send_message(chat_id, f"⛏️ پاداش ماینر جمع‌آوری شد: +{amt} سکه ✅", reply_markup=keyboard_main(is_admin(user_id)))

def check_bank_payout(user: Dict[str, Any]):
    if user.get("bank_amount",0) > 0 and user.get("bank_time",0) > 0:
        if time.time() - user["bank_time"] >= 24*3600:
            deposit = user["bank_amount"]
            interest = int(deposit * BANK_INTEREST_RATE)
            user["coins"] += deposit + interest
            user["bank_amount"] = 0
            user["bank_time"] = 0
            save_all()
            return deposit + interest, interest
    return 0, 0

# ---------------- بازی با ربات و بازیکن (بدون تغییر منطقی اصلی) ---------------- #
def play_with_robot(user_id, chat_id):
    uid = str(user_id)
    user = players[uid]
    stake = ROBOT_POWER
    if user.get("coins",0) < stake:
        send_message(chat_id, "💸 سکهٔ کافی برای بازی با ربات نداری. حداقل 100 سکه لازم است.", reply_markup=keyboard_main(is_admin(user_id)))
        return
    text = (
        f"🤖 قدرت ربات : {ROBOT_POWER} سکه\n"
        "___________________________________________\n\n"
        f"💪 قدرت تو : {user.get('coins',0)} سکه\n\n"
        "آیا بازی میکنی؟\n\n"
        "اگر ببری تمام سکه ربات برا تو می‌شود، اگر ببازی سکه های تو برای ربات می‌شود"
    )
    send_message(chat_id, text, reply_markup=keybo_
