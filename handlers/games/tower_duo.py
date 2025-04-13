import string
import random
from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from utils.database import get_balance, update_balance

router = Router()
tower_duo_games = {}

def generate_game_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def generate_tower_board():
    board = []
    for _ in range(10):
        row = ["💣"] * 2
        crystal_index = random.randint(0, 1)
        row[crystal_index] = "💎"
        board.append(row)
    return board

def generate_markup(rows, game_id, disabled=False, include_collect=True, include_cancel=False, revealed_cells=None):
    keyboard = []
    for row_index, row in enumerate(rows[::-1]):
        actual_level = len(rows) - 1 - row_index
        buttons = []
        for i, cell in enumerate(row):
            if revealed_cells and (actual_level, i) in revealed_cells:
                text = cell
            else:
                text = cell if disabled else "❓"
            callback_data = "none" if disabled else f"towerduo:{game_id}:{actual_level}:{i}"
            buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        keyboard.append(buttons)

    control_row = []
    if include_collect and not disabled and len(rows) > 1:
        control_row.append(InlineKeyboardButton(text="💰 Забрати", callback_data=f"towerduo_collect:{game_id}"))
    if include_cancel and not disabled and len(rows) == 1:
        control_row.append(InlineKeyboardButton(text="❌ Скасувати", callback_data=f"towerduo_cancel:{game_id}"))
    if control_row:
        keyboard.append(control_row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def calculate_towerduo_multiplier(level):
    return 2 ** level

@router.message(Command("тавер"))
async def cmd_towerduo(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return await message.answer("Вкажи ставку. Наприклад: /тавер 100")

    bet = int(args[1])
    balance = await get_balance(user_id)
    if balance < bet:
        return await message.answer("Недостатньо коінів 💸")

    game_id = generate_game_id()
    board = generate_tower_board()

    tower_duo_games[game_id] = {
        "user_id": user_id,
        "bet": bet,
        "board": board,
        "level": 0,
        "active": True,
        "revealed": [],
        "message_id": None
    }

    await update_balance(user_id, -bet)

    markup = generate_markup([board[0]], game_id, include_cancel=True)
    sent = await message.answer(f"🗼 Тавер - Рівень 1\nСтавка: {bet} коінів", reply_markup=markup)
    tower_duo_games[game_id]["message_id"] = sent.message_id

@router.callback_query(lambda c: c.data.startswith("towerduo:"))
async def handle_towerduo_click(callback: CallbackQuery):
    _, game_id, level_str, index_str = callback.data.split(":")
    level = int(level_str)
    index = int(index_str)

    game = tower_duo_games.get(game_id)
    if not game or not game["active"]:
        return await callback.answer("Гра завершена або не знайдена")

    user_id = callback.from_user.id
    if game["user_id"] != user_id:
        return await callback.answer("Це не твоя гра")

    if level != game["level"]:
        return await callback.answer("Цей рівень вже пройдений")

    cell = game["board"][level][index]

    if cell == "💣":
        game["board"][level][index] = "💥"
        game["active"] = False
        game["revealed"].append((level, index))
        visible = game["board"][:level + 1]
        markup = generate_markup(visible, game_id, disabled=True, revealed_cells=game["revealed"])
        return await callback.message.edit_text(
            f"💥 Ти натрапив на міну на рівні {level+1}! Програш {game['bet']} 💸",
            reply_markup=markup
        )

    game["board"][level][index] = "💎"
    game["revealed"].append((level, index))
    game["level"] += 1

    if game["level"] == 10:
        game["active"] = False
        win = game["bet"] * 1024
        await update_balance(user_id, win)
        markup = generate_markup(game["board"], game_id, disabled=True, revealed_cells=game["revealed"])
        return await callback.message.edit_text(
            f"🎉 Ти пройшов всю Тавер! Виграш {win} 💰",
            reply_markup=markup
        )

    visible = game["board"][:game["level"] + 1]
    multiplier = calculate_towerduo_multiplier(game["level"])
    potential_win = game["bet"] * multiplier
    markup = generate_markup(visible, game_id, revealed_cells=game["revealed"])
    await callback.message.edit_text(
        f"🗼 Тавер - Рівень {game['level'] + 1}\nСтавка: {game['bet']} коінів\nПоточний множник: x{multiplier}\nМожливий виграш: {potential_win} 💰",
        reply_markup=markup
    )

@router.callback_query(lambda c: c.data.startswith("towerduo_collect:"))
async def handle_towerduo_collect(callback: CallbackQuery):
    _, game_id = callback.data.split(":")
    game = tower_duo_games.get(game_id)

    if not game or not game["active"]:
        return await callback.answer("Гра завершена або не знайдена")

    user_id = callback.from_user.id
    if game["user_id"] != user_id:
        return await callback.answer("Це не твоя гра")

    game["active"] = False
    multiplier = calculate_towerduo_multiplier(game["level"])
    win = game["bet"] * multiplier
    await update_balance(user_id, win)

    visible = game["board"][:game["level"]]
    markup = generate_markup(visible, game_id, disabled=True, revealed_cells=game["revealed"])
    await callback.message.edit_text(
        f"💰 Ти забрав {win} коінів з множником x{multiplier}",
        reply_markup=markup
    )

@router.callback_query(lambda c: c.data.startswith("towerduo_cancel:"))
async def handle_towerduo_cancel(callback: CallbackQuery):
    _, game_id = callback.data.split(":")
    game = tower_duo_games.get(game_id)

    if not game or not game["active"]:
        return await callback.answer("Гру вже завершено або не знайдено")

    user_id = callback.from_user.id
    if game["user_id"] != user_id:
        return await callback.answer("Це не твоя гра")

    game["active"] = False
    await update_balance(user_id, game["bet"])
    await callback.message.edit_text("❌ Гру скасовано. Ставку повернено.")
