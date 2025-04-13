from aiogram.types import Message
from aiogram import types
from utils.database import (
    get_balance,
    set_balance,
    update_balance,
    get_user_data,
    save_user_data,
)

# Тексти підказок
HINT_TEXT = (
    "❗ Неправильна команда. Приклад використання:\n"
    "/казино 100\n"
    "/рулетка 200 3\n"
    "/кубики 150 4\n"
    "/вг 50 7 20\n"
    "/міни 100 2\n"
    "/баскетбол 100"
)

START_COMMANDS = (
    "/start - початок\n"
    "/help - Показати підказки\n"
    "/profile - Профіль\n"
    "/мійстат - Статистика\n"
    "/завдання - Перевірити завдання\n"
    "/топ - Топ гравців\n"
    "/передати - Передати коіни іншому\n"
    "/промокод - Ввести промокод\n"
    "/реферал - Моя реферальна система\n"
    "\n🎮 Ігри:\n"
    "/казино {ставка}\n"
    "/рулетка {ставка} {чорне/червоне} {число}\n"
    "/кубики {ставка} {більше/менше} {число}\n"
    "/вг {ставка} {число} {діапазон}\n"
    "/міни {ставка} {кількість мін}\n"
    "/баскетбол {ставка}"
)

HELP_COMMANDS = (
    "📝 Підказки для команд:\n"
    "/казино {ставка} — випадковий множник від 0x до 10x\n"
    "/рулетка {ставка} {чорне/червоне} {число (1-36)} — рулетка\n"
    "/кубики {ставка} {більше/менше} {число} — вгадай результат кубика (1–6)\n"
    "/вг {ставка} {число} {діапазон} — вгадай число в діапазоні\n"
    "/міни {ставка} {кількість мін (1–10)} — відкривай поле, уникаючи мін\n"
    "\n"
    "/profile — показати профіль\n"
    "/мійстат — статистика ігор\n"
    "/завдання — переглянути активні завдання\n"
    "/топ — топ гравців за різними критеріями\n"
    "/передати {нік} {сума} — передати коіни іншому гравцю\n"
    "/промокод {код} — активувати промокод\n"
    "/реферал — твоя реферальна система"
)


async def add_balance(user_id: int, amount: int):
    user_data = await get_user_data(user_id)
    user_data["balance"] = user_data.get("balance", 0) + amount
    await save_user_data(user_id, user_data)

async def remove_balance(user_id: int, amount: int) -> bool:
    user_data = await get_user_data(user_id)
    if user_data.get("balance", 0) < amount:
        return False
    user_data["balance"] -= amount
    await save_user_data(user_id, user_data)
    return True

async def update_stats(user_id: int, game: str, win: bool):
    await add_game_stat(user_id, win, game)

def get_user_name(user) -> str:
    return user.first_name if not user.username else f"@{user.username}"


def send_usage_hint(message: Message):
    return message.answer(HINT_TEXT)


async def parse_bet(user_id: int, bet_input):
    balance = await get_balance(user_id)

    if str(bet_input).lower() == "все":
        bet = balance
    else:
        try:
            bet = int(bet_input)
        except ValueError:
            return None, "❌ Введіть коректну ставку."

    if bet <= 0 or bet > balance:
        return None, "❌ Недостатньо коінів або некоректна ставка."

    return bet, None




def get_bet_amount(user_id: str, arg: str) -> int | None:
    user_data = get_user_data(user_id)
    balance = user_data.get("balance", 0)
    if arg.lower() == "все":
        return balance
    try:
        bet = int(arg)
        if bet > balance or bet <= 0:
            return None
        return bet
    except:
        return None


async def add_game_stat(user_id: int, won: bool | None, game: str):
    user_data = await get_user_data(user_id)

    user_data["games_played"] = user_data.get("games_played", 0) + 1
    if won is True:
        user_data["games_won"] = user_data.get("games_won", 0) + 1
    elif won is False:
        user_data["games_lost"] = user_data.get("games_lost", 0) + 1

    # Перевіряємо, що games_stat — словник
    if not isinstance(user_data.get("games"), dict):
        user_data["games"] = {}

    game_stats = user_data["games"]
    game_stats[game] = game_stats.get(game, 0) + 1

    await save_user_data(user_id, user_data)


async def add_referral_bonus(referer_id: int, bonus: int, reason: str = ""):
    await update_balance(referer_id, bonus)
    # optionally log reason or send notification


async def check_referral_events(user_id: int, change: int, is_win: bool):
    user_data = await get_user_data(user_id)
    referer_id = user_data.get("referer_id")
    if not referer_id:
        return

    if not is_win and change < 0:
        bonus = int(abs(change) * 0.05)
        await add_referral_bonus(referer_id, bonus, "5% з програшу реферала")
    elif is_win and change > 10_000:
        bonus = int(change * 0.03)
        await add_referral_bonus(referer_id, bonus, "3% з виграшу >10к")

async def send_message_with_balance(message: Message, text: str, balance: int):
    await message.answer(f"{text}\n💰 Баланс: {balance}")

async def db_get_balance(user_id: int) -> int:
    user_data = await get_balance(user_id)
    return user_data or 0

async def db_add_balance(user_id: int, amount: int):
    await update_balance(user_id, amount)

def get_user_name(user: types.User) -> str:
    if user.username:
        return f"@{user.username}"
    return user.full_name

async def update_user_stats(user_id: str, game: str, is_win: bool):
    # Реалізація оновлення статистики перемог/поразок, наприклад:
    stats = await get_user_stats(user_id)
    stats["games"] += 1
    stats["wins"] += int(is_win)
    stats["losses"] += int(not is_win)
    stats["by_game"].setdefault(game, {"wins": 0, "losses": 0})
    if is_win:
        stats["by_game"][game]["wins"] += 1
    else:
        stats["by_game"][game]["losses"] += 1
    await save_user_stats(user_id, stats)
