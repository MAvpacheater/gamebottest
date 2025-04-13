from datetime import datetime
from utils.database import (
    get_user_data,
    save_user_data,
    create_user_if_needed
)

async def get_balance(user_id: int) -> int:
    data = await get_user_data(user_id)
    return data.get("balance", 0)

async def update_balance(user_id: int, amount: int):
    data = await get_user_data(user_id)
    data["balance"] = data.get("balance", 0) + amount
    await save_user_data(user_id, data)

async def set_bonus_time(user_id: int, bonus_type: str):
    data = await get_user_data(user_id)
    data.setdefault("bonuses", {})
    data["bonuses"][bonus_type] = datetime.now().isoformat()
    await save_user_data(user_id, data)

async def get_bonus_time(user_id: int, bonus_type: str) -> str:
    data = await get_user_data(user_id)
    return data.get("bonuses", {}).get(bonus_type)

async def get_referrer(user_id: int):
    data = await get_user_data(user_id)
    return data.get("referrer")

async def update_stats(user_id: int, result: str, game_type: str):
    data = await get_user_data(user_id)
    data.setdefault('stats', {})
    data['stats']['total_games'] = data['stats'].get('total_games', 0) + 1
    data['stats'].setdefault('games_per_type', {})
    data['stats']['games_per_type'][game_type] = data['stats']['games_per_type'].get(game_type, 0) + 1

    if result == 'win':
        data['stats']['wins'] = data['stats'].get('wins', 0) + 1
    elif result == 'loss':
        data['stats']['losses'] = data['stats'].get('losses', 0) + 1

    await save_user_data(user_id, data)

async def ensure_user(user_id: int):
    await create_user_if_needed(user_id)

async def load_all_users_data() -> dict:
    users = {}
    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".json"):
            user_id = filename.replace(".json", "")
            with open(os.path.join(DATA_PATH, filename), "r", encoding="utf-8") as f:
                try:
                    users[user_id] = json.load(f)
                except json.JSONDecodeError:
                    continue
    return users


def get_help_text():
    return (
        "ℹ️ Доступні команди:\n\n"
        "🎁 /bonus — Отримати щоденний бонус\n"
        "🧑‍💼 /profile — Ваш профіль\n"
        "👥 /ref — Ваше реферальне посилання\n"
        "🏆 /топ — Лідерборд гравців\n"
        "🎫 /промо {код} — Активувати промокод\n\n"
        "🎰 /казино {ставка} — Грати в казино\n"
        "🎲 /кубик {ставка} {&lt;, &gt;, число} — Грати в кубики\n"
        "💣 /міни {ставка} {кількість_мін} — Гра «Міни»\n"
        "🎡 /рулетка {ставка} {червоне/чорне/число} — Грати в рулетку\n"
        "🔢 /вг {ставка} {число} {діапазон} — Вгадати число\n"
        "📉 /краш {ставка} — Гра «Краш»\n"
        "🏀 /баскетбол {ставка} — Гра «Баскетбол»\n"
        "🗼 /тавер {ставка} — Гра «Тавер»\n"
        "🏯 /вежа {ставка} {кількість_мін} — Гра «Вежа»\n\n"
    )

def get_command_list():
    return (
        "👋 <b>Привіт!</b> Бот готовий до гри!\n\n"
        "🔸 <b>Команди для гри та бонусів:</b>\n"
        "/start - почати 🚀\n"
        "/bonus - бонус 🎁\n"
        "/profile - профіль 👤\n"
        "/ref - реферальне посилання 🔗\n"
        "/мійстат - моя статистика 📊\n"
        "/топ - топ гравців 💎\n"
        "/промо - промокоди 🎟\n\n"
        "🎮 <b>Ігри:</b>\n"
        "/казино - гра казино 🎰\n"
        "/кубик - кидок кубика 🎲\n"
        "/міни - гра в міни 💣\n"
        "/рулетка - рулетка 🎯\n"
        "/вг - вгадай число 💥\n"
        "/краш - краш гра 📉\n"
        "/баскетбол - баскетбол 🏀\n"
        "/тавер - тавер 🗼\n"
        "/вежа - вежа 🏯\n\n"
        "ℹ️ Напиши <b>/help</b>, щоб побачити опис кожної команди! 📋"
    )

def get_usage_hint(username: str) -> str:
    return f"🥶 {username}, ти ввів щось неправильно!\n" \
           "❌ Неправильна команда.\n" \
           "Скористайся /help, щоб дізнатись, як правильно її використовувати."
