from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.database import get_balance  # тільки з database!

router = Router()

@router.message(Command("balance"))
async def balance_handler(message: Message):
    balance = await get_balance(message.from_user.id)
    await message.answer(f"Ваш баланс: {balance} коінів 💰")
