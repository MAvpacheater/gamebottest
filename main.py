import asyncio
import logging
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, BotCommandScopeDefault
from handlers.general.checks import router as checks_router

from config import TOKEN

# Імпорт бота та диспетчера
from loader import bot, dispatcher

# 🧩 Імпорт усіх роутерів
from handlers.general import (
    commands,
    bonus,
    profile,
    top,
    promocodes,
    referrals,
    group_handler,
    no_slash_commands,
    checks,
    transfer,
)

from handlers.games import (
    casino,
    dice,
    mines,
    roulette,
    guess,
    crash,
    basketball,
    tower,
    tower_duo,
)

from handlers.general.start import router as start_router
from handlers.general.balance import router as balance_router
from handlers import admin
from commands import botstats

# 🛠 Встановлення команд у меню Telegram
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Почати гру"),
        BotCommand(command="profile", description="Профіль"),
        BotCommand(command="balance", description="Баланс"),
        BotCommand(command="mycheck", description="Мої чеки"),
        BotCommand(command="createcheck", description="Створити чек"),
        BotCommand(command="ref", description="Реферальне посилання"),
        BotCommand(command="help", description="ℹ️ Список команд"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

# 🚀 Основна функція запуску бота
async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        commands.router,
        bonus.router,
        profile.router,
        top.router,
        promocodes.router,
        referrals.router,
        admin.router,
        transfer.router,

        casino.router,
        dice.router,
        mines.router,
        roulette.router,
        guess.router,
        crash.router,
        basketball.router,
        tower.router,
        tower_duo.router,

        group_handler.router,
        botstats.router,

        start_router,
        balance_router,
        checks_router,

        no_slash_commands.router  # ❗️ОБОВʼЯЗКОВО останнім!
    )

    await set_bot_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
