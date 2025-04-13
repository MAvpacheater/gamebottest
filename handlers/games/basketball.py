import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.filters import Command

from utils.game_utils import (
    get_user_name,
    parse_bet,
    update_balance,
    add_game_stat,
    send_message_with_balance,
    get_balance,  # ✅ не забудь імпорт
)

router = Router()

@router.message(Command("баскетбол"))
@router.message(F.text.lower().startswith("баскетбол"))
async def basketball_handler(message: Message):
    user_id = message.from_user.id
    username = get_user_name(message.from_user)

    # Отримуємо ставку
    args = message.text.split()
    if len(args) < 2:
        await message.reply("❌ Вкажи ставку після команди. Приклад: /баскетбол 100")
        return

    amount, error = await parse_bet(user_id, args[1])
    if error:
        await message.reply(error)
        return

    # Кидаємо баскетбольний м'яч
    dice = await message.answer_dice(emoji=DiceEmoji.BASKETBALL)
    value = dice.dice.value

    # Чекаємо завершення анімації
    await asyncio.sleep(3.5)

    # Обробка результату
    if value <= 2:
        multiplier = 0
        result_text = f"{username}, ти промахнувся! x0 😧"
    elif value <= 4:
        multiplier = 1.5
        result_text = f"{username}, кидок був на межі фолу! x1.5 😳"
    else:
        multiplier = 2
        result_text = f"{username}, прямо в ціль, м'яч у кільці! x2 🏀"

    win = int(amount * multiplier)
    diff = win - amount

    await update_balance(user_id, diff)
    await add_game_stat(user_id, won=(win > amount), game="баскетбол")

    # Повідомлення з результатом
    text = result_text + f"\n·····················\n💸 Ставка: {amount} mCoin"
    if win > 0:
        text += f"\n🎉 Виграш: {win} mCoin"

    balance = await get_balance(user_id)  # ✅ виправлено
    await send_message_with_balance(message, text, balance)
