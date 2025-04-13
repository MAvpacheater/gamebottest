import json
import os

DB_PATH = "data/users"
os.makedirs(DB_PATH, exist_ok=True)
CHECKS_PATH = "data/checks"
os.makedirs(CHECKS_PATH, exist_ok=True)

def _get_check_file(code: str) -> str:
    return os.path.join(CHECKS_PATH, f"{code.upper()}.json")


def _get_user_file(user_id: int | str) -> str:
    return os.path.join(DB_PATH, f"{user_id}.json")


def _load_user_data(user_id: int | str) -> dict:
    file_path = _get_user_file(user_id)
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_user_data(user_id: int | str, data: dict):
    file_path = _get_user_file(user_id)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def get_user_data(user_id: int | str) -> dict:
    data = _load_user_data(user_id)
    data.setdefault("balance", 1000)
    data.setdefault("promo_used", 0)
    data.setdefault("games_played", 0)
    data.setdefault("games_won", 0)
    data.setdefault("games_lost", 0)
    data.setdefault("used_promocodes", [])
    data.setdefault("games", {
        "казино": 0,
        "кубики": 0,
        "міни": 0,
        "рулетка": 0,
        "вг": 0,
        "краш": 0
    })
    data.setdefault("username", None)
    data.setdefault("referrals", 0)
    data.setdefault("first_name", None)
    data.setdefault("last_name", None)
    data.setdefault("sent_transactions", [])
    data.setdefault("received_transactions", [])
    _save_user_data(user_id, data)
    return data



async def save_user_data(user_id: int | str, data: dict):
    _save_user_data(user_id, data)


async def get_balance(user_id: int | str) -> int:
    data = await get_user_data(user_id)
    return data.get("balance", 0)


async def set_balance(user_id: int | str, amount: int):
    data = await get_user_data(user_id)
    data["balance"] = amount
    await save_user_data(user_id, data)


async def update_balance(user_id: int | str, amount: int):
    data = await get_user_data(user_id)
    data["balance"] = max(0, data.get("balance", 0) + amount)
    await save_user_data(user_id, data)

async def create_user_if_needed(user_id: int | str, username: str = None):
    data = _load_user_data(user_id)
    if not data:
        data = {
            "balance": 1000,
            "promo_used": 0,
            "games_played": 0,
            "games_won": 0,
            "games_lost": 0,
            "used_promocodes": [],
            "games": {
                "казино": 0,
                "кубики": 0,
                "міни": 0,
                "рулетка": 0,
                "вг": 0,
                "краш": 0
            },
            "username": username,
            "referrals": 0
        }
        _save_user_data(user_id, data)

async def create_check(code: str, amount: int):
    file_path = _get_check_file(code)
    data = {
        "code": code.upper(),
        "amount": amount
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def get_check(code: str) -> tuple | None:
    file_path = _get_check_file(code)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["code"], data["amount"]

async def delete_check(code: str):
    file_path = _get_check_file(code)
    if os.path.exists(file_path):
        os.remove(file_path)
