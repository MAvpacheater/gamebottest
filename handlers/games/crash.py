import random
import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command

from utils.game_utils import (
    parse_bet,
    update_balance,
    add_game_stat,
    check_referral_events,
    get_user_name
)

router = Router()

@router.message(Command(commands=["краш"]))
async def play_crash(message: Message):
    user_id = str(message.from_user.id)

    try:
        parts = message.text.split()
        bet_str = parts[1]
        chosen = int(float(parts[2]))
        if not (1 <= chosen <= 10):
            raise ValueError
    except (IndexError, ValueError):
        await message.answer(
            "❗ Використання: <b>/краш {ставка} {число 1–10}</b>\n"
            "Наприклад: <code>/краш 100 3</code>",
            parse_mode="HTML"
        )
        return

    bet, error = await parse_bet(user_id, bet_str)
    if error:
        await message.answer(f"❗ {error}")
        return

    await update_balance(user_id, -bet)
    await add_game_stat(user_id, None, "краш")  # Результат визначимо згодом

    await message.answer_animation(
        "https://media.giphy.com/media/l0MYEqEzwMWFCg8rm/giphy.gif",
        caption="🚀 Запуск ракети..."
    )
    await asyncio.sleep(2)

    rocket = random.randint(1, 10)
    win = 0
    name = get_user_name(message.from_user)

    if chosen <= rocket:
        win = bet * chosen
        await update_balance(user_id, win)
        await add_game_stat(user_id, True, "краш")
        await check_referral_events(user_id, change=win - bet, is_win=True)

        caption = (
            f"🚀 <b>{name}</b>, ракета злетіла до <b>{rocket}</b>!\n"
            f"🎯 Твоє число: <b>{chosen}</b>\n"
            f"✅ Ти виграв <b>{win} mCoin</b>"
        )
    else:
        await add_game_stat(user_id, False, "краш")
        await check_referral_events(user_id, change=-bet, is_win=False)

        caption = (
            f"💥 <b>{name}</b>, ракета впала на висоті <b>{rocket}</b>!\n"
            f"❌ Твоє число: <b>{chosen}</b>\n"
            f"😢 Ти програв <b>{bet} mCoin</b>"
        )

    from utils.helpers import load_users
    users = load_users()
    caption += f"\n\n💰 Баланс: <b>{users[user_id]['balance']} mCoin</b>"

    await message.answer(caption, parse_mode="HTML")
