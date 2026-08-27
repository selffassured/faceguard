from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QLabel,
)

from app.config.settings import (
    Settings
)

from app.telegram.notifier import (
    TelegramNotifier
)


class SettingsWindow(
    QDialog
):
    def __init__(
        self,
        parent=None
    ):
        super().__init__(
            parent
        )

        self.setWindowTitle(
            "FaceGuard — Настройки"
        )

        self.resize(
            550,
            420
        )

        self.settings = (
            Settings()
        )

        self.build_ui()
        self.load_settings()

    def build_ui(
        self
    ):
        layout = (
            QVBoxLayout(
                self
            )
        )

        telegram_title = QLabel(
            "Telegram"
        )

        font = (
            telegram_title
            .font()
        )

        font.setPointSize(
            15
        )

        font.setBold(
            True
        )

        telegram_title.setFont(
            font
        )

        layout.addWidget(
            telegram_title
        )

        telegram_form = (
            QFormLayout()
        )

        self.bot_token_input = (
            QLineEdit()
        )

        self.bot_token_input.setEchoMode(
            QLineEdit.Password
        )

        self.chat_id_input = (
            QLineEdit()
        )

        telegram_form.addRow(
            "Bot Token:",
            self.bot_token_input
        )

        telegram_form.addRow(
            "Chat ID:",
            self.chat_id_input
        )

        layout.addLayout(
            telegram_form
        )

        self.test_telegram_button = (
            QPushButton(
                "Проверить Telegram"
            )
        )

        self.test_telegram_button.clicked.connect(
            self.test_telegram
        )

        layout.addWidget(
            self.test_telegram_button
        )

        recognition_title = QLabel(
            "Распознавание"
        )

        recognition_font = (
            recognition_title
            .font()
        )

        recognition_font.setPointSize(
            15
        )

        recognition_font.setBold(
            True
        )

        recognition_title.setFont(
            recognition_font
        )

        layout.addWidget(
            recognition_title
        )

        recognition_form = (
            QFormLayout()
        )

        self.threshold_input = (
            QDoubleSpinBox()
        )

        self.threshold_input.setRange(
            0.0,
            1.0
        )

        self.threshold_input.setDecimals(
            2
        )

        self.threshold_input.setSingleStep(
            0.05
        )

        self.cooldown_input = (
            QSpinBox()
        )

        self.cooldown_input.setRange(
            1,
            86400
        )

        self.process_fps_input = (
            QSpinBox()
        )

        self.process_fps_input.setRange(
            1,
            30
        )

        recognition_form.addRow(
            "Порог совпадения:",
            self.threshold_input
        )

        recognition_form.addRow(
            "Cooldown, сек:",
            self.cooldown_input
        )

        recognition_form.addRow(
            "AI FPS:",
            self.process_fps_input
        )

        layout.addLayout(
            recognition_form
        )

        buttons = (
            QHBoxLayout()
        )

        self.save_button = (
            QPushButton(
                "Сохранить"
            )
        )

        self.cancel_button = (
            QPushButton(
                "Отмена"
            )
        )

        self.save_button.clicked.connect(
            self.save_settings
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        buttons.addStretch()

        buttons.addWidget(
            self.save_button
        )

        buttons.addWidget(
            self.cancel_button
        )

        layout.addLayout(
            buttons
        )

    def load_settings(
        self
    ):
        telegram = (
            self.settings
            .telegram()
        )

        recognition = (
            self.settings
            .recognition()
        )

        self.bot_token_input.setText(
            telegram.get(
                "bot_token",
                ""
            )
        )

        self.chat_id_input.setText(
            telegram.get(
                "chat_id",
                ""
            )
        )

        self.threshold_input.setValue(
            float(
                recognition.get(
                    "threshold",
                    0.45
                )
            )
        )

        self.cooldown_input.setValue(
            int(
                recognition.get(
                    "cooldown",
                    300
                )
            )
        )

        self.process_fps_input.setValue(
            int(
                recognition.get(
                    "process_fps",
                    3
                )
            )
        )

    def save_settings(
        self
    ):
        telegram = (
            self.settings
            .telegram()
        )

        recognition = (
            self.settings
            .recognition()
        )

        telegram[
            "bot_token"
        ] = (
            self.bot_token_input
            .text()
            .strip()
        )

        telegram[
            "chat_id"
        ] = (
            self.chat_id_input
            .text()
            .strip()
        )

        recognition[
            "threshold"
        ] = (
            self.threshold_input
            .value()
        )

        recognition[
            "cooldown"
        ] = (
            self.cooldown_input
            .value()
        )

        recognition[
            "process_fps"
        ] = (
            self.process_fps_input
            .value()
        )

        self.settings.save()

        QMessageBox.information(
            self,
            "FaceGuard",
            "Настройки сохранены."
        )

        self.accept()

    def test_telegram(
        self
    ):
        token = (
            self.bot_token_input
            .text()
            .strip()
        )

        chat_id = (
            self.chat_id_input
            .text()
            .strip()
        )

        notifier = (
            TelegramNotifier(
                bot_token=token,
                chat_id=chat_id
            )
        )

        try:
            bot = (
                notifier
                .test_connection()
            )

            notifier.send_message(
                "✅ FaceGuard подключён к Telegram."
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Telegram",
                str(exc)
            )

            return

        QMessageBox.information(
            self,
            "Telegram",
            (
                "Telegram работает.\n\n"
                f"Bot: @{bot.get('username', '')}"
            )
        )