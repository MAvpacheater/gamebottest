import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums.dice_emoji import DiceEmoji

from utils.game_utils import (
    parse_bet,
    update_balance,
    get_user_name,
    add_game_stat,
    check_referral_events,  # ✅ новий імпорт
)

router = Router()

@router.message(F.text.startswith("/кубики"))
async def play_dice(message: Message):
    args = message.text.split()
    user_id = str(message.from_user.id)

    if len(args) != 3:
        await message.answer(
            "🎲 Введи команду у форматі:\n"
            "<code>/кубики 100 >3</code> або <code>/кубики все 4</code>",
            parse_mode="HTML"
        )
        return

    bet_str, condition = args[1], args[2]
    bet, error = await parse_bet(user_id, bet_str)
    if error:
        await message.answer(f"❗ {error}")
        return

    # Обробка умови
    operator = None
    number = None
    if condition[0] in [">", "<", "="] and len(condition) > 1:
        operator = condition[0]
        try:
            number = int(condition[1:])
        except ValueError:
            await message.answer("❗ Умова має бути у форматі >3, <4, =6 або просто 4.")
            return
    else:
        try:
            number = int(condition)
            operator = "="
        except ValueError:
            await message.answer("❗ Умова має бути у форматі >3, <4, =6 або просто 4.")
            return

    if not 1 <= number <= 6:
        await message.answer("❗ Можна вгадувати числа лише від 1 до 6.")
        return

    # Кидаємо кубик
    dice_msg = await message.answer_dice(emoji=DiceEmoji.DICE)
    await asyncio.sleep(3)  # зачекаємо завершення анімації

    dice_value = dice_msg.dice.value
    success = False
    multiplier = 0
    win = 0
    name = get_user_name(message.from_user)

    if operator == "=" and dice_value == number:
        success = True
        multiplier = 2
    elif operator == ">" and dice_value > number:
        success = True
        multiplier = 1.5
    elif operator == "<" and dice_value < number:
        success = True
        multiplier = 1.5

    if success:
        win = int(bet * multiplier)
        await update_balance(user_id, win - bet)
        await add_game_stat(user_id, True, "кубики")
        await check_referral_events(user_id, win, is_win=True)  # ✅ бонус за виграш
        result = (
            f"🎉 <b>{name}</b>, ти вгадав число! x{multiplier} 🥳\n"
            f"💸 Ставка: <b>{bet}</b>\n"
            f"🏆 Виграш: <b>{win}</b>"
        )
    else:
        await update_balance(user_id, -bet)
        await add_game_stat(user_id, False, "кубики")
        await check_referral_events(user_id, -bet, is_win=False)  # ✅ бонус за програш
        result = (
            f"🛑 <b>{name}</b>, ти не вгадав! 😣\n"
            f"💸 Ставка: <b>{bet}</b>"
        )

    await message.answer(f"🎲 Випало число: <b>{dice_value}</b>\n\n{result}", parse_mode="HTML")
