import json
import os

DATA_FILE = "data/users.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def create_user(user_id):
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "balance": 1000,
            "referrer": None,
            "games": 0,
            "wins": 0,
            "losses": 0,
            "used_promos": [],
            "game_stats": {}
        }
        save_data(data)

def get_referrer(user_id):
    return load_data().get(str(user_id), {}).get("referrer")

def set_referrer(user_id, referrer_id):
    data = load_data()
    uid = str(user_id)
    if uid in data:
        data[uid]["referrer"] = referrer_id
        save_data(data)

def add_balance(user_id, amount):
    data = load_data()
    uid = str(user_id)
    if uid in data:
        data[uid]["balance"] += amount
        save_data(data)
