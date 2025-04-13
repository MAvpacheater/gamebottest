from aiogram import Router, F
from aiogram.types import Message
from utils.helpers import create_user_if_needed
from handlers.general import db

router = Router()

@router.message(F.text.startswith("/ref"))
async def ref_link_handler(message: Message):
    user_id = message.from_user.id
    bot_username = (await message.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={user_id}"
    await message.answer(f"👥 Ваше реферальне посилання:\n{link}")

@router.message(F.text.startswith("/start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    create_user_if_needed(str(user_id))

    args = message.text.strip().split()

    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != user_id and db.get_referrer(user_id) is None:
            db.set_referrer(user_id, referrer_id)
            db.add_balance(referrer_id, 500)
            await message.bot.send_message(
                referrer_id,
                "🎉 Ви отримали 500 коінів за нового реферала!"
            )

    await message.answer("👋 Привіт! Напиши /help для перегляду команд.")

async def handle_loss_referral(user_id: int, bet: int, bot):
    referrer_id = db.get_referrer(user_id)
    if referrer_id:
        bonus = int(bet * 0.05)
        db.add_balance(referrer_id, bonus)
        await bot.send_message(referrer_id, f"💸 Ви отримали {bonus} коінів (5% від програшу вашого реферала)")

async def handle_win_referral(user_id: int, win_amount: int, bot):
    if win_amount <= 10_000:
        return
    referrer_id = db.get_referrer(user_id)
    if referrer_id:
        bonus = int(win_amount * 0.03)
        db.add_balance(referrer_id, bonus)
        await bot.send_message(referrer_id, f"💰 Ви отримали {bonus} коінів (3% від великого виграшу вашого реферала)")
