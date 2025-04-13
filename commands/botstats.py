from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command

from utils.helpers import load_all_users_data

router = Router()

@router.message(Command(commands=["статботу", "botstats"]))
async def bot_stats(message: Message):
    users = await load_all_users_data()

    total_users = len(users)
    total_games = sum(user.get("games_played", 0) for user in users.values())
    total_wins = sum(user.get("games_won", 0) for user in users.values())
    total_losses = sum(user.get("games_lost", 0) for user in users.values())
    total_balance = sum(user.get("balance", 0) for user in users.values())

    richest_user = max(users.items(), key=lambda u: u[1].get("balance", 0), default=(None, {}))
    richest_uid = richest_user[0]
    richest_balance = richest_user[1].get("balance", 0)

    text = (
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Користувачів: <b>{total_users}</b>\n"
        f"🎮 Зіграно ігор: <b>{total_games}</b>\n"
        f"✅ Перемог: <b>{total_wins}</b>\n"
        f"❌ Поразок: <b>{total_losses}</b>\n"
        f"💰 Всього коінів в обігу: <b>{total_balance}</b>\n\n"
    )

    if richest_uid:
        username = users[richest_uid].get("username") or f"ID:{richest_uid}"
        text += f"🏆 Найбагатший гравець: <b>{username}</b> — <b>{richest_balance} коінів</b>"

    await message.answer(text)
