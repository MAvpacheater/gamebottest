from aiogram import Router, F
from aiogram.types import Message

from utils.game_utils import db_add_balance, db_get_balance
from config import ADMIN_IDS

router = Router()

@router.message(F.text.startswith("/поповнити"))
async def admin_topup_handler(message: Message):
    user_id = message.from_user.id

    if user_id not in ADMIN_IDS:
        await message.answer("⛔ Ти не адмін 😎")
        return

    try:
        parts = message.text.split()
        if len(parts) == 2 and parts[1].isdigit():
            target_id = user_id
            amount = int(parts[1])
        elif len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
            target_id = int(parts[1])
            amount = int(parts[2])
        else:
            await message.answer("❌ Приклад:\n/поповнити 1000 — собі\n/поповнити 123456789 1000 — іншому")
            return

        await db_add_balance(target_id, amount)
        new_balance = await db_get_balance(target_id)

        await message.answer(f"✅ Користувачу {target_id} поповнено на {amount} коінів.\n💰 Новий баланс: {new_balance}")
    except Exception as e:
        await message.answer(f"❌ Сталася помилка: {e}")

@router.message(F.text.startswith("/баланс"))
async def admin_check_balance_handler(message: Message):
    user_id = message.from_user.id

    if user_id not in ADMIN_IDS:
        await message.answer("⛔ Ти не адмін 😎")
        return

    try:
        parts = message.text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            await message.answer("❌ Приклад: /баланс 123456789")
            return

        target_id = int(parts[1])
        balance = await db_get_balance(target_id)

        await message.answer(f"💰 Баланс користувача {target_id}: {balance}")
    except Exception as e:
        await message.answer(f"❌ Сталася помилка: {e}")
