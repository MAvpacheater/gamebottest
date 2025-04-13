from utils.helpers import load_users, save_users, update_stats
from handlers.general.referrals import handle_loss_referral, handle_win_referral

async def finish_game(
    user_id: str,
    bet: int,
    won: bool,
    reward: int = 0,
    game_name: str = "",
):
    user_id = str(user_id)  # гарантія типу
    users = load_users()

    if user_id not in users:
        return

    if won:
        users[user_id]["balance"] += reward
        update_stats(users[user_id], "win", game_name)
        await handle_win_referral(user_id, reward)
    else:
        update_stats(users[user_id], "loss", game_name)
        await handle_loss_referral(user_id, bet)

    save_users(users)
