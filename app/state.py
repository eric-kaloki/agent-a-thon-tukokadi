import json
import os
from datetime import datetime

STATE_FILE = "app/data/user_state.json"

class StateManager:
    def __init__(self):
        if not os.path.exists(STATE_FILE):
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            with open(STATE_FILE, "w") as f:
                json.dump({}, f)
        
    def get_user(self, phone_hash: str):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
        
        if phone_hash not in data:
            data[phone_hash] = {
                "xp": 0,
                "level": 1,
                "badges": [],
                "streak": 1,
                "last_active": datetime.now().isoformat()
            }
            self._save(data)
        
        return data[phone_hash]

    def update_user(self, phone_hash: str, updates: dict):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
        
        if phone_hash in data:
            data[phone_hash].update(updates)
            self._save(data)

    def _save(self, data):
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)

state_manager = StateManager()
