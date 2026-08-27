from datetime import datetime
from pathlib import Path
import uuid

import cv2

from app.database.detection_repository import (
    DetectionRepository
)

from app.services.cooldown_service import (
    CooldownService
)

from app.telegram.notifier import (
    TelegramNotifier
)


DETECTIONS_DIR = Path(
    "data/detections"
)


class MonitoringService:
    def __init__(
        self,
        bot_token: str = "",
        chat_id: str = "",
        cooldown_seconds: int = 300,
    ):
        DETECTIONS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        self.cooldown = CooldownService(
            cooldown_seconds=cooldown_seconds
        )

        self.detection_repository = (
            DetectionRepository()
        )

        self.telegram = TelegramNotifier(
            bot_token=bot_token,
            chat_id=chat_id,
        )

    def update_telegram(
        self,
        bot_token: str,
        chat_id: str,
    ):
        self.telegram = TelegramNotifier(
            bot_token=bot_token,
            chat_id=chat_id,
        )

    def handle_recognition(
        self,
        person_id: int,
        name: str,
        similarity: float,
        frame,
    ):
        if not self.cooldown.can_trigger(
            person_id
        ):
            return {
                "triggered": False,
                "reason": "cooldown",
            }

        screenshot_path = (
            self.save_detection_frame(
                frame=frame,
                person_id=person_id,
            )
        )

        self.detection_repository.add_detection(
            person_id=person_id,
            confidence=similarity,
            screenshot_path=str(
                screenshot_path
            ),
        )

        self.cooldown.trigger(
            person_id
        )

        telegram_sent = False
        telegram_error = None

        if self.telegram.enabled:
            try:
                timestamp = datetime.now().strftime(
                    "%d.%m.%Y %H:%M:%S"
                )

                caption = (
                    "🚨 Обнаружен человек из базы\n\n"
                    f"Имя: {name}\n"
                    f"Время: {timestamp}\n"
                    f"Совпадение: {similarity:.2f}"
                )

                self.telegram.send_photo(
                    photo_path=screenshot_path,
                    caption=caption,
                )

                telegram_sent = True

            except Exception as exc:
                telegram_error = str(exc)

        return {
            "triggered": True,
            "screenshot_path": str(
                screenshot_path
            ),
            "telegram_sent": telegram_sent,
            "telegram_error": telegram_error,
        }

    def save_detection_frame(
        self,
        frame,
        person_id: int,
    ) -> Path:
        now = datetime.now()

        date_dir = (
            DETECTIONS_DIR
            / now.strftime("%Y-%m-%d")
        )

        date_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        filename = (
            f"{now.strftime('%H-%M-%S')}"
            f"_person_{person_id}_"
            f"{uuid.uuid4().hex[:8]}.jpg"
        )

        destination = (
            date_dir
            / filename
        )

        success = cv2.imwrite(
            str(destination),
            frame
        )

        if not success:
            raise RuntimeError(
                "Не удалось сохранить кадр обнаружения."
            )

        return destination