from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from utils.helpers import (
    get_command_list,
    get_help_text,
    get_balance,
    ensure_user
)
from utils.database import create_user_if_needed, get_user_data

router = Router()

# /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""

    user_data = await get_user_data(user_id)

    if not user_data:
        await create_user_if_needed(user_id, username=username)
        await message.answer("🎉 Вас зареєстровано!\nСтартовий баланс: <b>1000</b> коінів.")
    else:
        await message.answer("👋 Ви вже зареєстровані.")

    await message.answer(get_command_list())


# /balance
@router.message(Command("balance"))
async def cmd_balance(message: Message):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.answer("❗ Спочатку зареєструйтесь за допомогою /start")
        return

    balance = await get_balance(user_id)
    await message.answer(f"💰 Ваш баланс: <b>{balance}</b> коінів")


# /help
@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(get_help_text())
