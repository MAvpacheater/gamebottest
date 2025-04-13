from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
import random

from utils.game_utils import db_add_balance, get_user_data, save_user_data

router = Router()

BONUSES = {
    "hourly": {
        "label": "🎯 Щогодинний",
        "cooldown": timedelta(hours=1),
        "range": (50, 150),
    },
    "daily": {
        "label": "☀️ Щоденний",
        "cooldown": timedelta(hours=24),
        "range": (300, 1000),
    },
    "weekly": {
        "label": "🏆 Щотижневий",
        "cooldown": timedelta(days=7),
        "range": (1500, 3000),
    }
}

@router.message(Command("bonus"))
async def choose_bonus_type(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=b["label"], callback_data=f"bonus:{key}")]
        for key, b in BONUSES.items()
    ])
    await message.answer("🎁 Оберіть тип бонусу:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("bonus:"))
async def handle_bonus(callback: CallbackQuery):
    user_id = callback.from_user.id
    bonus_type = callback.data.split(":")[1]

    user = await get_user_data(user_id)
    if user is None:
        await callback.answer("❗ Спочатку зареєструйтесь за допомогою /start", show_alert=True)
        return

    now = datetime.utcnow()
    key = f"last_{bonus_type}_bonus"
    last_claim_str = user.get(key)

    cooldown = BONUSES[bonus_type]["cooldown"]
    reward_range = BONUSES[bonus_type]["range"]

    if last_claim_str:
        try:
            last_claim = datetime.fromisoformat(last_claim_str)
            if now - last_claim < cooldown:
                time_left = cooldown - (now - last_claim)
                hours, remainder = divmod(int(time_left.total_seconds()), 3600)
                minutes = (remainder // 60) % 60
                await callback.answer(
                    f"⏳ Спробуйте ще через {hours} год {minutes} хв.", show_alert=True
                )
                return
        except Exception:
            pass  # У випадку неправильного формату — ігноруємо

    bonus_amount = random.randint(*reward_range)
    await db_add_balance(user_id, bonus_amount)

    # оновлюємо час останнього бонусу
    user[key] = now.isoformat()
    await save_user_data(user_id, user)

    await callback.message.answer(
        f"✅ Ви отримали {BONUSES[bonus_type]['label']} бонус: <b>{bonus_amount}</b> коінів!"
    )
    await callback.answer()
