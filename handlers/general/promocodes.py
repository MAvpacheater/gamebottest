from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from utils.database import get_user_data, save_user_data, update_balance

import json
import os

router = Router()

PROMO_PATH = "data/promocodes.json"

# Ініціалізація промокодів, якщо файлу немає
os.makedirs("data", exist_ok=True)

if not os.path.exists(PROMO_PATH):
    default_promos = {
        "#newbot": {"reward": 1000, "uses_left": 100},
        "#newadmin": {"reward": 5000, "uses_left": 100},
        "#newgame": {"reward": 2000, "uses_left": 100}
    }
    with open(PROMO_PATH, "w") as f:
        json.dump(default_promos, f, indent=4)


@router.message(Command(commands=["промо", "промокод"]))
async def promo_command(message: Message):
    args = message.text.strip().split()

    if len(args) < 2:
        await message.answer("❗ Використання: /промокод #код")
        return

    code = args[1].strip().lower()
    if not code.startswith("#"):
        await message.answer("❌ Промокод має починатися з `#`, наприклад: /промокод #newgame")
        return

    user_id = str(message.from_user.id)

    user_data = await get_user_data(user_id)

    with open(PROMO_PATH, "r", encoding="utf-8") as f:
        promocodes = json.load(f)

    if code not in promocodes:
        await message.answer("❌ Промокод не знайдено")
        return

    if code in user_data.get("used_promocodes", []):
        await message.answer("⚠️ Ви вже використали цей промокод")
        return

    promo = promocodes[code]
    if promo["uses_left"] <= 0:
        await message.answer("⚠️ Цей промокод вже вичерпано")
        return

    reward = promo["reward"]
    await update_balance(user_id, reward)

    user_data.setdefault("used_promocodes", []).append(code)
    await save_user_data(user_id, user_data)

    promocodes[code]["uses_left"] -= 1
    with open(PROMO_PATH, "w", encoding="utf-8") as f:
        json.dump(promocodes, f, indent=4, ensure_ascii=False)

    new_balance = user_data.get("balance", 0) + reward

    await message.answer(
        f"✅ <b>Промокод активовано:</b> {code}\n"
        f"➕ Отримано: {reward} коінів\n"
        f"💰 Новий баланс: {new_balance} коінів"
    )
