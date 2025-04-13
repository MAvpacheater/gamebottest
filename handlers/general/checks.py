import random
import string
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from utils.database import get_balance, update_balance, get_user_data, save_user_data, create_user_if_needed

router = Router()

def generate_check_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


@router.message(Command("createcheck"))
async def create_check(message: Message):
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        return await message.answer("❗ Використання: /createcheck {сума}")

    amount = int(args[1])
    user_id = message.from_user.id

    await create_user_if_needed(user_id)
    balance = await get_balance(user_id)
    if amount <= 0:
        return await message.answer("❗ Сума має бути більшою за 0.")
    if balance < amount:
        return await message.answer("❗ Недостатньо коінів.")

    code = generate_check_code()

    user_data = await get_user_data(user_id)
    checks = user_data.get("created_checks", [])
    checks.append({
        "code": code,
        "amount": amount,
        "claimed": False,
        "claimed_by": None
    })
    user_data["created_checks"] = checks
    await update_balance(user_id, -amount)
    await save_user_data(user_id, user_data)

    await message.answer(
        f"✅ Чек створено!\n🔒 Код: <code>{code}</code>\n🎁 Сума: <b>{amount}</b> коінів\n\n"
        f"👤 Перший, хто введе <code>/check {code}</code>, отримає нагороду!"
    )


@router.message(Command("check"))
async def redeem_check(message: Message):
    args = message.text.split()
    if len(args) != 2:
        return await message.answer("❗ Використання: /check {код}")

    code = args[1].strip().upper()
    user_id = message.from_user.id
    await create_user_if_needed(user_id)

    # Перевірка всіх користувачів (можна оптимізувати, якщо є індексовані файли)
    from os import listdir
    from utils.database import DB_PATH, _load_user_data, save_user_data

    for filename in listdir(DB_PATH):
        user_data = _load_user_data(filename.split(".")[0])
        checks = user_data.get("created_checks", [])
        for check in checks:
            if check["code"] == code:
                if check["claimed"]:
                    return await message.answer("❗ Цей чек вже активовано.")
                if int(filename.split(".")[0]) == user_id:
                    return await message.answer("❗ Ви не можете активувати власний чек.")

                # Активувати чек
                check["claimed"] = True
                check["claimed_by"] = user_id
                await update_balance(user_id, check["amount"])
                save_user_data(filename.split(".")[0], user_data)

                redeemer_data = await get_user_data(user_id)
                activated = redeemer_data.get("activated_checks", [])
                activated.append({
                    "code": code,
                    "amount": check["amount"]
                })
                redeemer_data["activated_checks"] = activated
                await save_user_data(user_id, redeemer_data)

                return await message.answer(f"🎉 Ви активували чек на <b>{check['amount']}</b> коінів!")

    return await message.answer("❗ Невірний або неіснуючий код чеку.")


@router.message(Command("mychecks"))
async def my_checks_menu(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Створені", callback_data="checks_created")],
        [InlineKeyboardButton(text="✅ Активовані", callback_data="checks_activated")]
    ])
    await message.answer("📋 Обери тип чеків:", reply_markup=kb)


@router.callback_query(F.data.startswith("checks_"))
async def handle_checks_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = await get_user_data(user_id)

    if callback.data == "checks_created":
        checks = data.get("created_checks", [])
        if not checks:
            return await callback.message.edit_text("📭 У вас немає створених чеків.")
        msg = "<b>📝 Створені чеки:</b>\n"
        for c in checks:
            status = "✅ активовано" if c["claimed"] else "🔒 неактивовано"
            msg += f"• <code>{c['code']}</code> — {c['amount']} коінів ({status})\n"
        await callback.message.edit_text(msg)

    elif callback.data == "checks_activated":
        checks = data.get("activated_checks", [])
        if not checks:
            return await callback.message.edit_text("📭 Ви ще не активували жодного чека.")
        msg = "<b>✅ Активовані чеки:</b>\n"
        for c in checks:
            msg += f"• <code>{c['code']}</code> — {c['amount']} коінів\n"
        await callback.message.edit_text(msg)
