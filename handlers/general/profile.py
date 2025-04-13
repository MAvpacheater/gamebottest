from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import get_user_data

router = Router()

@router.message(F.text.lower() == "/profile")
async def profile_handler(message: Message):
    user_id = message.from_user.id
    data = await get_user_data(user_id)

    if "balance" not in data:
        await message.answer("❗ Тебе не знайдено. Використай /start.")
        return

    username = message.from_user.username or message.from_user.full_name
    balance = data.get("balance", 0)
    games_played = data.get("games_played", 0)
    games_won = data.get("games_won", 0)
    games_lost = data.get("games_lost", 0)
    promo_used = data.get("promo_used", 0)
    game_stats = data.get("games", {})

    text = (
        f"👤 <b>Профіль:</b> {username}\n"
        f"💰 <b>Баланс:</b> {balance} mCoin\n"
        f"🎮 <b>Всього ігор:</b> {games_played}\n"
        f"🏆 <b>Перемог:</b> {games_won}\n"
        f"💥 <b>Програшів:</b> {games_lost}\n"
        f"🎁 <b>Використаних промокодів:</b> {promo_used}\n"
    )

    if game_stats:
        text += f"\n🎯 <b>Статистика по іграх:</b>\n"
        for game_name, count in game_stats.items():
            text += f"• {game_name}: {count}\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Мої транзакції", callback_data="my_transactions")]
    ])

    await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data == "my_transactions")
async def show_transaction_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="profile")],
        [
            InlineKeyboardButton(text="📥 Отримані", callback_data="transactions_received"),
            InlineKeyboardButton(text="📤 Надіслані", callback_data="transactions_sent"),
        ],
    ])
    await callback.message.edit_text("💸 Оберіть тип транзакцій:", reply_markup=keyboard)

@router.callback_query(F.data == "transactions_received")
async def show_received_transactions(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = await get_user_data(user_id)
    received = data.get("received_transactions", [])

    if not received:
        text = "📥 У вас ще немає отриманих транзакцій."
    else:
        lines = []
        for tx in reversed(received[-10:]):
            lines.append(f"🔹 {tx['amount']} коінів від @{tx['from_username']}")
        text = "📥 Останні отримані транзакції:\n" + "\n".join(lines)

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="my_transactions")]
    ]))

@router.callback_query(F.data == "transactions_sent")
async def show_sent_transactions(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = await get_user_data(user_id)
    sent = data.get("sent_transactions", [])

    if not sent:
        text = "📤 У вас ще немає надісланих транзакцій."
    else:
        lines = []
        for tx in reversed(sent[-10:]):
            lines.append(f"🔸 {tx['amount']} коінів для @{tx['to_username']}")
        text = "📤 Останні надіслані транзакції:\n" + "\n".join(lines)

    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="my_transactions")]
    ]))

@router.callback_query(F.data == "profile")
async def return_to_profile(callback: CallbackQuery):
    message = callback.message
    await profile_handler(message)
