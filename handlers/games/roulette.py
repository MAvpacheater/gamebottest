import random
import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from utils.game_utils import (
    parse_bet,
    update_balance,
    check_referral_events,
    add_game_stat,
    get_user_name,
)

router = Router()

RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

@router.message(Command("рулетка"))
async def roulette_game(message: Message):
    user_id = str(message.from_user.id)
    args = message.text.split()

    if len(args) < 3:
        await message.answer("❗ Використання: /рулетка {ставка} {колір(b/r)/число/і те і те}")
        return

    bet_str = args[1]
    bet, error = await parse_bet(user_id, bet_str)
    if error:
        await message.answer(f"❗ {error}")
        return

    color = None
    number = None
    for arg in args[2:]:
        arg = arg.lower()
        if arg in ["r", "червоне"]:
            if color:
                await message.answer("❗ Можна вибрати лише один колір.")
                return
            color = "red"
        elif arg in ["b", "чорне"]:
            if color:
                await message.answer("❗ Можна вибрати лише один колір.")
                return
            color = "black"
        elif arg.isdigit():
            num = int(arg)
            if 1 <= num <= 36:
                number = num
            else:
                await message.answer("❗ Число має бути від 1 до 36.")
                return

    if not color and number is None:
        await message.answer("❗ Вкажи колір (r або b) або число від 1 до 36, або і те і те.")
        return

    await update_balance(user_id, -bet)

    # await message.answer_animation("https://media.giphy.com/media/3ohs4C2yYXHXX8tCuk/giphy.gif")
    # await asyncio.sleep(2)

    result = random.randint(1, 36)
    result_color = "red" if result in RED_NUMBERS else "black"

    win_color = (color == result_color)
    win_number = (number == result)

    multiplier = 0
    if win_color and win_number:
        multiplier = 5
    elif win_color:
        multiplier = 1.5
    elif win_number:
        multiplier = 2

    name = get_user_name(message.from_user)

    text = f"🎲 Випало число: <b>{result}</b> ({'🔴 Червоне' if result_color == 'red' else '⚫ Чорне'})\n"

    if multiplier > 0:
        win_amount = int(bet * multiplier)
        await update_balance(user_id, win_amount)
        await add_game_stat(user_id, True, "рулетка")
        await check_referral_events(user_id=user_id, change=win_amount, is_win=True)


        reasons = []
        if win_color: reasons.append("колір")
        if win_number: reasons.append("число")

        text += (
            f"🎉 <b>{name}</b>, ти вгадав(ла) {', '.join(reasons)}! x{multiplier} 🥳\n"
            f"💸 Ставка: <b>{bet}</b>\n"
            f"🏆 Виграш: <b>{win_amount}</b>"
        )
    else:
        await add_game_stat(user_id, False, "рулетка")
        await check_referral_events(user_id=user_id, change=-bet, is_win=False)
        text += f"💀 <b>{name}</b>, ти програв(ла) ставку! 😢\n💸 Ставка: <b>{bet}</b>"

    await message.answer(text, parse_mode="HTML")
