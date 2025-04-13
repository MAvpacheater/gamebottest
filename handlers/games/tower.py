import random
import string
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from utils.database import get_balance, update_balance

router = Router()
tower_games = {}

def generate_game_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def generate_board(mines):
    board = []
    for _ in range(10):
        crystal_pos = random.sample(range(5), 5 - mines)
        row = ["💎" if i in crystal_pos else "💣" for i in range(5)]
        board.append(row)
    return board

def generate_markup(rows, game_id, disabled=False, include_collect=True, include_cancel=False, revealed_cells=None):
    keyboard = []
    revealed_cells = revealed_cells or set()

    for row_index, row in enumerate(reversed(rows)):
        actual_level = len(rows) - 1 - row_index
        buttons = []
        for i in range(5):
            cell = row[i]
            if disabled or (actual_level, i) in revealed_cells:
                text = cell
                if (actual_level, i) in revealed_cells and cell == "💣":
                    text = "💥"
            else:
                text = "⬜️"
            callback_data = "none" if disabled else f"tower:{game_id}:{actual_level}:{i}"
            buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        keyboard.append(buttons)

    control_row = []
    if include_collect and not disabled and len(rows) > 1:
        control_row.append(InlineKeyboardButton(text="💰 Забрати", callback_data=f"tower_collect:{game_id}"))
    if include_cancel and not disabled and len(rows) == 1:
        control_row.append(InlineKeyboardButton(text="❌ Скасувати", callback_data=f"tower_cancel:{game_id}"))
    if control_row:
        keyboard.append(control_row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def calculate_multiplier(mines, level):
    base = {1: 1.1, 2: 1.2, 3: 1.3, 4: 1.5}.get(mines, 1.1)
    return round(base ** level, 2)

@router.message(Command("вежа"))
async def cmd_tower(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("Вкажи ставку. Наприклад: /вежа 100 або /вежа 100 3")

    try:
        bet = int(args[1])
    except ValueError:
        return await message.answer("Ставка має бути цілим числом")

    try:
        mines = int(args[2]) if len(args) > 2 else 1
    except ValueError:
        return await message.answer("Кількість мін має бути цілим числом")

    mines = max(1, min(mines, 4))

    balance = await get_balance(user_id)
    if balance < bet:
        return await message.answer("Недостатньо коінів 💸")

    game_id = generate_game_id()
    board = generate_board(mines)

    tower_games[game_id] = {
        "user_id": user_id,
        "bet": bet,
        "mines": mines,
        "board": board,
        "level": 0,
        "active": True,
        "message_id": None,
        "revealed_cells": set()
    }

    await update_balance(user_id, -bet)

    markup = generate_markup([board[0]], game_id, include_cancel=True)
    sent = await message.answer("🛬 Вежа - Рівень 1", reply_markup=markup)
    tower_games[game_id]["message_id"] = sent.message_id

@router.callback_query(lambda c: c.data.startswith("tower:"))
async def handle_tower_click(callback: CallbackQuery):
    _, game_id, level_str, index_str = callback.data.split(":")
    level = int(level_str)
    index = int(index_str)

    game = tower_games.get(game_id)
    if not game or not game["active"]:
        return await callback.answer("Гра завершена або не знайдена")

    user_id = callback.from_user.id
    if game["user_id"] != user_id:
        return await callback.answer("Це не твоя гра")

    current_level = game.get("level", 0)
    if level != current_level:
        return await callback.answer("Цей рівень вже пройдений")

    cell = game["board"][level][index]

    if cell == "💣":
        game["board"][level][index] = "💥"
        game["active"] = False

        visible_board = game["board"][:level + 1]
        markup = generate_markup(visible_board, game_id, disabled=True, revealed_cells=game["revealed_cells"])
        return await callback.message.edit_text(
            f"💥 Ти натрапив на міну на рівні {level + 1}! Програш {game['bet']} 💸",
            reply_markup=markup
        )

    game["revealed_cells"].add((level, index))
    game["level"] = current_level + 1

    if game["level"] == 10:
        game["active"] = False
        win = game["bet"] * 10
        await update_balance(user_id, win)
        markup = generate_markup(game["board"], game_id, disabled=True, revealed_cells=game["revealed_cells"])
        return await callback.message.edit_text(
            f"🎉 Ти пройшов всю вежу! Виграш {win} 💰",
            reply_markup=markup
        )

    next_level = game["level"]
    visible_board = game["board"][:next_level + 1]
    markup = generate_markup(visible_board, game_id, revealed_cells=game["revealed_cells"])

    from_user = callback.from_user
    username = from_user.username or from_user.full_name or "Гравець"
    multiplier = calculate_multiplier(game["mines"], next_level)
    potential_win = round(game["bet"] * multiplier)

    await callback.message.edit_text(
        f"🧗 {username}\n"
        f"📶 Рівень: {next_level}\n"
        f"✖️ Множник: x{multiplier}\n"
        f"💰 Прибуток: {potential_win}\n"
        f"🎯 Ставка: {game['bet']}\n\n"
        f"⬆️ Обери клітинку наступного рівня ({next_level + 1})",
        reply_markup=markup
    )


@router.callback_query(lambda c: c.data.startswith("tower_collect:"))
async def handle_tower_collect(callback: CallbackQuery):
    _, game_id = callback.data.split(":")
    game = tower_games.get(game_id)

    if not game or not game["active"]:
        return await callback.answer("Гра завершена або не знайдена")

    user_id = callback.from_user.id
    if game["user_id"] != user_id:
        return await callback.answer("Це не твоя гра")

    game["active"] = False
    level = game.get("level", 0)
    multiplier = calculate_multiplier(game["mines"], level)
    win = round(game["bet"] * multiplier)
    await update_balance(user_id, win)

    visible_board = game["board"][:level]
    markup = generate_markup(visible_board, game_id, disabled=True, revealed_cells=game["revealed_cells"])
    await callback.message.edit_text(
        f"💰 Ти забрав {win} коінів з множником x{multiplier}",
        reply_markup=markup
    )

@router.callback_query(lambda c: c.data.startswith("tower_cancel:"))
async def handle_tower_cancel(callback: CallbackQuery):
    _, game_id = callback.data.split(":")
    game = tower_games.get(game_id)

    if not game or not game["active"]:
        return await callback.answer("Гру вже завершено або не знайдено")

    user_id = callback.from_user.id
    if game["user_id"] != user_id:
        return await callback.answer("Це не твоя гра")

    game["active"] = False
    await update_balance(user_id, game["bet"])
    await callback.message.edit_text("❌ Гру скасовано. Ставку повернено.")
