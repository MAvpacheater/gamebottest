from aiogram import Router, F
from aiogram.types import Message
from utils.database import get_user_data, save_user_data

router = Router()

@router.message(F.text.lower() == "/start")
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    data = await get_user_data(user_id)
    data["username"] = message.from_user.username
    data["first_name"] = message.from_user.first_name
    data["last_name"] = message.from_user.last_name


    # завжди ініціалізуємо потрібні поля
    data.setdefault("balance", 1000)
    data.setdefault("promo_used", 0)
    data.setdefault("games_played", 0)
    data.setdefault("games_won", 0)
    data.setdefault("games_lost", 0)
    data.setdefault("referrals", 0)
    data.setdefault("used_promocodes", [])
    data.setdefault("games", {
        "казино": 0,
        "кубики": 0,
        "міни": 0,
        "рулетка": 0,
        "вг": 0,
        "краш": 0,
        "баскетбол": 0,
        "Вежа": 0,
        "Тавер": 0
    })
    data["username"] = username

    await save_user_data(user_id, data)

    await message.answer(
        f"👋 Ласкаво просимо! Ваш баланс: {data['balance']} коінів 💰\n"
        "Напиши /help для перегляду команд."
    )
