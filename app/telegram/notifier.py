from pathlib import Path

import requests


class TelegramNotifier:
    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        timeout: int = 10,
    ):
        self.bot_token = bot_token.strip()
        self.chat_id = str(chat_id).strip()
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(
            self.bot_token
            and self.chat_id
        )

    @property
    def api_url(self) -> str:
        return (
            f"https://api.telegram.org/"
            f"bot{self.bot_token}"
        )

    def test_connection(self):
        if not self.bot_token:
            raise ValueError(
                "Не указан Bot Token."
            )

        response = requests.get(
            f"{self.api_url}/getMe",
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            raise RuntimeError(
                "Telegram вернул ошибку."
            )

        return data["result"]

    def send_message(
        self,
        text: str,
    ):
        if not self.enabled:
            raise ValueError(
                "Telegram не настроен."
            )

        response = requests.post(
            f"{self.api_url}/sendMessage",
            data={
                "chat_id": self.chat_id,
                "text": text,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("ok"):
            raise RuntimeError(
                result.get(
                    "description",
                    "Ошибка Telegram API"
                )
            )

        return result

    def send_photo(
        self,
        photo_path: str | Path,
        caption: str = "",
    ):
        if not self.enabled:
            raise ValueError(
                "Telegram не настроен."
            )

        photo_path = Path(
            photo_path
        )

        if not photo_path.exists():
            raise FileNotFoundError(
                f"Файл не найден: {photo_path}"
            )

        with photo_path.open("rb") as photo:
            response = requests.post(
                f"{self.api_url}/sendPhoto",
                data={
                    "chat_id": self.chat_id,
                    "caption": caption,
                },
                files={
                    "photo": photo,
                },
                timeout=self.timeout,
            )

        response.raise_for_status()

        result = response.json()

        if not result.get("ok"):
            raise RuntimeError(
                result.get(
                    "description",
                    "Ошибка Telegram API"
                )
            )

        return result