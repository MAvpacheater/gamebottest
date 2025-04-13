import asyncio
import random
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from utils.game_utils import (
    get_user_name,
    get_balance,
    update_balance,
    parse_bet,
    add_game_stat,
    send_message_with_balance,
)
from handlers.general.referrals import handle_loss_referral, handle_win_referral

router = Router()

MULTIPLIERS = [
    0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2,
    2.25, 0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2,
    2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75, 4,
    4.25, 4.5, 4.75, 5, 5.25, 5.5, 5.75, 6, 6.5, 6.75, 7,
    7.25, 7.5, 7.75, 8, 8.25, 8.5, 8.75, 9, 9.25, 9.5, 9.75, 10
]

@router.message(Command("казино"))
async def play_casino(message: Message):
    user_id = message.from_user.id
    username = get_user_name(message.from_user)  # 🔧 без await

    args = message.text.split()
    if len(args) < 2:
        await message.reply(
            "🎰 Неправильний формат!\n\n"
            "Спробуй так:\n"
            "<code>/казино 100</code> або <code>/казино все</code>"
        )
        return

    amount, error = await parse_bet(user_id, args[1])
    if error:
        await message.reply(error)
        return

    await update_balance(user_id, -amount)

    loading_msg = await message.answer("🎰 Обертаємо слот...")
    await asyncio.sleep(2)

    multiplier = random.choice(MULTIPLIERS)
    win = int(amount * multiplier)
    diff = win - amount

    await update_balance(user_id, diff)
    await add_game_stat(user_id, won=(win > amount), game="казино")

    if win < amount:
        await handle_loss_referral(user_id, amount, message.bot)
    elif win - amount >= 10_000:
        await handle_win_referral(user_id, win - amount, message.bot)

    if win >= amount:
        text = (
            f"{username}, тобі випало x{multiplier} 🎰\n"
            f"🎉 Твій виграш: {win} mCoin!"
        )
    else:
        text = (
            f"{username}, тобі випало x{multiplier} 🎰\n"
            f"😢 Ти програв {amount - win} mCoin."
        )

    final_balance = await get_balance(user_id)
    await send_message_with_balance(loading_msg, text, final_balance)
