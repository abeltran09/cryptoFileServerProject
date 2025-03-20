import json

DATA_FILE = "groupServerData.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        initial_data = {
            "users": {"admin": {"password": "admin"}},
            "groups": {"./ADMIN": {"owner": "admin", "members": ["admin"]}},
            "tokens": {}
        }
        with open(DATA_FILE, "w") as f:
            json.dump(initial_data, f, indent=4)
        return initial_data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

load_data()