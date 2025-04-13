import asyncio
import random
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from utils.game_utils import (
    check_referral_events,
    parse_bet,
    update_balance,
    add_game_stat,
    send_usage_hint,
    get_user_name,
)

router = Router()

@router.message(Command("вг"))
async def guess_number(message: Message):
    user_id = str(message.from_user.id)
    args = message.text.split()

    if len(args) < 3:
        await send_usage_hint(message, "вг")
        return

    bet_str = args[1]
    bet, error = await parse_bet(user_id, bet_str)
    if error:
        await message.answer(f"❗ {error}")
        return

    try:
        guess = int(args[2])
        max_range = int(args[3]) if len(args) >= 4 and args[3].isdigit() else 15
    except ValueError:
        await message.answer("❗ Введи правильне число та діапазон")
        return

    if max_range < 2 or max_range > 100:
        await message.answer("❗ Діапазон має бути від 2 до 100")
        return

    if guess < 1 or guess > max_range:
        await message.answer(f"❗ Введи число від 1 до {max_range}")
        return

    await update_balance(user_id, -bet)

    loading = await message.answer("🎯 Обираємо число...")
    await asyncio.sleep(2)

    number = random.randint(1, max_range)
    win = (number == guess)
    name = get_user_name(message.from_user)

    if win:
        multiplier = round(max_range / 10, 2)
        reward = int(bet * multiplier)
        await update_balance(user_id, reward)
        await add_game_stat(user_id, True, "вг")
        await check_referral_events(user_id=user_id, change=reward, is_win=True)


        text = (
            f"🎯 <b>{name}</b>, ти вгадав(ла) число! 🎉\n"
            f"🔢 Загадане число: <b>{number}</b>\n"
            f"📈 Множник: x{multiplier}\n"
            f"💰 Виграш: <b>{reward} mCoin</b>"
        )
    else:
        await add_game_stat(user_id, False, "вг")
        await check_referral_events(user_id=user_id, change=-bet, is_win=False)


        text = (
            f"🎯 <b>{name}</b>, не вгадав(ла) число 😢\n"
            f"🔢 Загадане число було: <b>{number}</b>\n"
            f"💸 Ставка згоріла: <b>{bet} mCoin</b>"
        )

    await loading.edit_text(text, parse_mode="HTML")
