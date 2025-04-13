from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.database import (
    get_user_data,
    update_balance,
    create_user_if_needed,
    save_user_data
)
import os, json

router = Router()

@router.message(Command("give"))
async def handle_give(message: Message):
    args = message.text.split()

    if len(args) < 3:
        return await message.answer("❗ Використання: /give {сума} {username без @}")

    try:
        amount = int(args[1])
        if amount <= 0:
            return await message.answer("❗ Сума має бути більшою за 0.")
    except ValueError:
        return await message.answer("❗ Невірна сума.")

    sender_id = message.from_user.id
    sender_data = await get_user_data(sender_id)
    if sender_data.get("balance", 0) < amount:
        return await message.answer("❗ Недостатньо коінів для переказу.")

    username = args[2].lstrip("@").lower()
    recipient_id = None

    for file in os.listdir("data/users"):
        path = os.path.join("data/users", file)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if str(data.get("username", "")).lower() == username:
                recipient_id = int(file.replace(".json", ""))
                break

    if recipient_id is None:
        return await message.answer("❗ Користувача з таким юзернеймом не знайдено.")

    if recipient_id == sender_id:
        return await message.answer("❗ Ви не можете передати коіни самі собі.")

    await update_balance(sender_id, -amount)
    await create_user_if_needed(recipient_id)
    await update_balance(recipient_id, amount)

    # Оновлення даних після зміни балансу
    sender_data = await get_user_data(sender_id)
    recipient_data = await get_user_data(recipient_id)

    # Логування транзакцій
    sender_data.setdefault("sent_transactions", [])
    recipient_data.setdefault("received_transactions", [])

    sender_data["sent_transactions"].append({
        "to_id": recipient_id,
        "to_username": username,
        "amount": amount
    })

    recipient_data["received_transactions"].append({
        "from_id": sender_id,
        "from_username": message.from_user.username or "невідомо",
        "amount": amount
    })

    await save_user_data(sender_id, sender_data)
    await save_user_data(recipient_id, recipient_data)

    await message.answer(f"✅ Ви успішно передали <b>{amount}</b> коінів гравцю @{username}!")

    try:
        await message.bot.send_message(
            recipient_id,
            f"🎉 Вам надіслав(ла) @{message.from_user.username or 'гравець'} <b>{amount}</b> коінів!"
        )
    except:
        pass
