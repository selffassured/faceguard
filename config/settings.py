import json
from pathlib import Path

CONFIG_PATH = Path("config/settings.json")

DEFAULT_SETTINGS = {
    "camera": {
        "host": "192.168.10.69",
        "port": 554,
        "path": "/onvif1",
        "username": "",
        "password": ""
    },
    "telegram": {
        "bot_token": "",
        "chat_id": ""
    },
    "recognition": {
        "threshold": 0.45,
        "cooldown": 300,
        "process_fps": 3
    }
}


class Settings:
    def __init__(self):
        self.data = {}
        self.load()

    def load(self):
        if not CONFIG_PATH.exists():
            self.data = DEFAULT_SETTINGS.copy()
            self.save()
            return

        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except (json.JSONDecodeError, OSError):
            self.data = DEFAULT_SETTINGS.copy()

    def save(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(CONFIG_PATH, "w", encoding="utf-8") as file:
            json.dump(
                self.data,
                file,
                indent=4,
                ensure_ascii=False
            )

    def camera(self):
        return self.data["camera"]

    def telegram(self):
        return self.data["telegram"]

    def recognition(self):
        return self.data["recognition"]