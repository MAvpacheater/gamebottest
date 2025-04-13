import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.game_utils import (
    parse_bet, update_balance, add_game_stat,
    check_referral_events, get_user_name, send_usage_hint
)

router = Router()
games = {}

def create_board(mines_count: int):
    positions = [(x, y) for x in range(5) for y in range(5)]
    mine_positions = random.sample(positions, mines_count)
    board = [["💎" for _ in range(5)] for _ in range(5)]
    for x, y in mine_positions:
        board[x][y] = "💣"
    return board

def calculate_multiplier(collected: int):
    return round(1.1 * (1.3 ** max(collected - 1, 0)), 2)

def generate_markup(board, revealed, game_id, finished=False, show_collect=False, multiplier=1.0):
    kb = InlineKeyboardBuilder()
    boom_cell = games.get(game_id, {}).get("boom_cell")

    for i in range(5):
        row = []
        for j in range(5):
            if finished:
                if (i, j) == boom_cell:
                    cell = "💥"
                elif board[i][j] == "💣":
                    cell = "💣"
                elif revealed[i][j]:
                    cell = "💎"
                else:
                    cell = "⬜"
            elif revealed[i][j]:
                cell = "💎"
            else:
                cell = "⬜"

            row.append(
                InlineKeyboardButton(
                    text=cell,
                    callback_data=f"mines:{game_id}:{i}:{j}" if not finished else "none"
                )
            )
        kb.row(*row)

    if not finished:
        if show_collect:
            kb.row(
                InlineKeyboardButton(
                    text=f"💎 Забрати виграш (x{round(multiplier, 2)})",
                    callback_data=f"mines_collect:{game_id}"
                )
            )
        else:
            kb.row(
                InlineKeyboardButton(
                    text="❌ Скасувати",
                    callback_data=f"mines_cancel:{game_id}"
                )
            )
    return kb.as_markup()

@router.message(Command("міни"))
async def cmd_mines(message: Message):
    user_id = str(message.from_user.id)
    args = message.text.split()

    if len(args) < 2:
        await send_usage_hint(message, "міни")
        return

    bet_str = args[1]
    bet, error = await parse_bet(user_id, bet_str)
    if error:
        await message.answer(f"❗ {error}")
        return

    try:
        mines = int(args[2]) if len(args) > 2 else 1
        if not (1 <= mines <= 10):
            raise ValueError
    except:
        await message.answer("❗ Кількість мін має бути від 1 до 10.")
        return

    await update_balance(user_id, -bet)
    await add_game_stat(user_id, None, "міни")

    board = create_board(mines)
    revealed = [[False]*5 for _ in range(5)]
    game_id = str(random.randint(100000, 999999))

    games[game_id] = {
        "user_id": user_id,
        "board": board,
        "revealed": revealed,
        "bet": bet,
        "mines": mines,
        "collected": 0,
        "finished": False,
        "boom_cell": None
    }

    markup = generate_markup(board, revealed, game_id)
    await message.answer(
        f"🎮 Гру розпочато!\n💰 Ставка: {bet}\n💣 Мін: {mines}",
        reply_markup=markup
    )

@router.callback_query(F.data.startswith("mines:"))
async def on_click(callback: CallbackQuery):
    data = callback.data.split(":")
    game_id, x, y = data[1], int(data[2]), int(data[3])
    user_id = str(callback.from_user.id)
    name = get_user_name(callback.from_user)

    game = games.get(game_id)
    if not game or game["user_id"] != user_id:
        await callback.answer("Це не твоя гра.")
        return

    if game["finished"]:
        await callback.answer("Гру завершено.")
        return

    if game["revealed"][x][y]:
        await callback.answer("Вже відкрито.")
        return

    if game["board"][x][y] == "💣":
        game["finished"] = True
        game["boom_cell"] = (x, y)
        markup = generate_markup(game["board"], game["revealed"], game_id, finished=True)

        await add_game_stat(user_id, False, "міни")
        await check_referral_events(user_id, -game["bet"], is_win=False)


        await callback.message.edit_text(
            f"💥 {name}, ти програв(ла)!\nНаступного разу пощастить!",
            reply_markup=markup
        )
        await update_user_stats(user_id, "міни", is_win=False)
        return

    game["revealed"][x][y] = True
    game["collected"] += 1
    total_safe = 25 - game["mines"]
    multiplier = calculate_multiplier(game["collected"])

    if game["collected"] == total_safe:
        game["finished"] = True
        await update_user_stats(user_id, "міни", is_win=True) 
        reward = int(game["bet"] * multiplier)
        await update_balance(user_id, reward)
        await add_game_stat(user_id, True, "міни")
        await check_referral_events(user_id, win=reward - game["bet"])

        markup = generate_markup(game["board"], game["revealed"], game_id, finished=True)
        await callback.message.edit_text(
            f"🏆 {name}, ти зібрав(ла) усі кристали!\n💰 Виграш: {reward}",
            reply_markup=markup
        )
        return

    markup = generate_markup(game["board"], game["revealed"], game_id, show_collect=True, multiplier=multiplier)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer()

@router.callback_query(F.data.startswith("mines_collect:"))
async def on_collect(callback: CallbackQuery):
    game_id = callback.data.split(":")[1]
    user_id = str(callback.from_user.id)
    name = get_user_name(callback.from_user)
    game = games.get(game_id)

    if not game or game["user_id"] != user_id:
        await callback.answer("Це не твоя гра.")
        return

    if game["finished"]:
        await callback.answer("Ти вже забрав(ла) приз.")
        return

    game["finished"] = True
    multiplier = calculate_multiplier(game["collected"])
    reward = int(game["bet"] * multiplier)

    await update_balance(user_id, reward)
    await add_game_stat(user_id, True, "міни")
    await check_referral_events(user_id, reward - game["bet"], is_win=True)


    markup = generate_markup(game["board"], game["revealed"], game_id, finished=True)
    await callback.message.edit_text(
        f"💎 {name}, ти успішно забрав(ла) приз!\n📈 Множник: x{multiplier}\n💰 Виграш: {reward}",
        reply_markup=markup
    )

@router.callback_query(F.data.startswith("mines_cancel:"))
async def on_cancel(callback: CallbackQuery):
    game_id = callback.data.split(":")[1]
    user_id = str(callback.from_user.id)
    game = games.get(game_id)

    if not game or game["user_id"] != user_id:
        await callback.answer("Це не твоя гра.")
        return

    if game["finished"] or game["collected"] > 0:
        await callback.answer("Не можна скасувати після початку гри.")
        return

    await update_balance(user_id, game["bet"])
    game["finished"] = True

    markup = generate_markup(game["board"], game["revealed"], game_id, finished=True)
    await callback.message.edit_text(
        f"❌ Гру скасовано. Ставку повернуто.",
        reply_markup=markup
    )
