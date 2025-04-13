from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

import os
import json

router = Router()

USERS_PATH = "data/users"


@router.message(Command("топ"))
async def top_command(message: Message):
    if not os.path.exists(USERS_PATH):
        await message.answer("📊 Ще немає гравців у топі.")
        return

    args = message.text.strip().split()
    if len(args) < 2:
        await message.answer(
            "❗ Використання: /топ [коін|він|луз|реф]\n"
            "🔹 /топ коін — топ за балансом\n"
            "🔹 /топ він — топ за перемогами\n"
            "🔹 /топ луз — топ за програшами\n"
            "🔹 /топ реф — топ за кількістю рефералів"
        )
        return

    param = args[1].lower()
    sort_key = None
    title = ""

    if param == "коін":
        sort_key = "balance"
        title = "🏆 Топ 10 за балансом:"
    elif param == "він":
        sort_key = "games_won"
        title = "🥊 Топ 10 за перемогами:"
    elif param == "луз":
        sort_key = "games_lost"
        title = "💀 Топ 10 за програшами:"
    elif param == "реф":
        sort_key = "referrals"
        title = "👥 Топ 10 за рефералами:"
    else:
        await message.answer("❌ Невідомий параметр. Спробуйте: коін, він, луз, реф.")
        return

    users_data = []
    for filename in os.listdir(USERS_PATH):
        if filename.endswith(".json"):
            user_id = filename.replace(".json", "")
            with open(os.path.join(USERS_PATH, filename), "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    users_data.append((user_id, data))
                except Exception as e:
                    print(f"Помилка читання {filename}: {e}")

    if not users_data:
        await message.answer("📊 Немає доступних даних користувачів.")
        return

    sorted_users = sorted(users_data, key=lambda x: x[1].get(sort_key, 0), reverse=True)

    def format_entry(i, user_id, data):
        username = data.get("username")
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        if username:
            name = f"@{username}"
        elif first_name:
            name = f"{first_name} {last_name}" if last_name else first_name
        else:
            name = f"ID:{user_id}"

        value = data.get(sort_key, 0)
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
        return f"{medal} {name} — {value}"

    result = "\n".join([format_entry(i, uid, data) for i, (uid, data) in enumerate(sorted_users[:10])])
    await message.answer(f"{title}\n{result}")
