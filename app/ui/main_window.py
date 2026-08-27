from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QLabel,
    QMessageBox,
    QGroupBox,
)

from app.camera.rtsp_client import RTSPClient
from app.camera.camera_worker import CameraWorker
from app.recognition.recognition_worker import RecognitionWorker
from app.config.settings import Settings
from app.services.monitoring_service import MonitoringService
from app.ui.people_window import PeopleWindow
from app.ui.settings_window import SettingsWindow
from app.ui.history_window import HistoryWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FaceGuard")
        self.resize(1200, 820)

        self.settings = Settings()

        self.camera_worker = None
        self.recognition_worker = None

        self.people_window = None
        self.history_window = None

        self.manual_disconnect = False
        self.recognition_enabled = False

        self.monitoring_service = None

        self.build_ui()
        self.load_settings()
        self.create_monitoring_service()

    def create_monitoring_service(self):
        telegram = self.settings.telegram()
        recognition = self.settings.recognition()

        self.monitoring_service = MonitoringService(
            bot_token=telegram.get(
                "bot_token",
                ""
            ),
            chat_id=telegram.get(
                "chat_id",
                ""
            ),
            cooldown_seconds=int(
                recognition.get(
                    "cooldown",
                    300
                )
            ),
        )

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)

        title = QLabel("FaceGuard")
        title.setAlignment(Qt.AlignCenter)

        font = title.font()
        font.setPointSize(22)
        font.setBold(True)

        title.setFont(font)

        main_layout.addWidget(title)

        camera_group = QGroupBox("Камера")
        camera_form = QFormLayout(camera_group)

        self.ip_input = QLineEdit()

        self.port_input = QSpinBox()
        self.port_input.setRange(
            1,
            65535
        )

        self.path_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()

        self.password_input.setEchoMode(
            QLineEdit.Password
        )

        camera_form.addRow(
            "IP:",
            self.ip_input
        )

        camera_form.addRow(
            "Порт:",
            self.port_input
        )

        camera_form.addRow(
            "RTSP path:",
            self.path_input
        )

        camera_form.addRow(
            "Логин:",
            self.username_input
        )

        camera_form.addRow(
            "Пароль:",
            self.password_input
        )

        main_layout.addWidget(
            camera_group
        )

        camera_buttons = QHBoxLayout()

        self.connect_button = QPushButton(
            "Подключить камеру"
        )

        self.disconnect_button = QPushButton(
            "Отключить"
        )

        self.disconnect_button.setEnabled(
            False
        )

        self.connect_button.clicked.connect(
            self.connect_camera
        )

        self.disconnect_button.clicked.connect(
            self.disconnect_camera
        )

        camera_buttons.addWidget(
            self.connect_button
        )

        camera_buttons.addWidget(
            self.disconnect_button
        )

        main_layout.addLayout(
            camera_buttons
        )

        action_buttons = QHBoxLayout()

        self.people_button = QPushButton(
            "База людей"
        )

        self.history_button = QPushButton(
            "История"
        )

        self.settings_button = QPushButton(
            "Настройки"
        )

        self.recognition_button = QPushButton(
            "Запустить распознавание"
        )

        self.recognition_button.setEnabled(
            False
        )

        self.people_button.clicked.connect(
            self.open_people_window
        )

        self.history_button.clicked.connect(
            self.open_history_window
        )

        self.settings_button.clicked.connect(
            self.open_settings_window
        )

        self.recognition_button.clicked.connect(
            self.toggle_recognition
        )

        action_buttons.addWidget(
            self.people_button
        )

        action_buttons.addWidget(
            self.history_button
        )

        action_buttons.addWidget(
            self.settings_button
        )

        action_buttons.addWidget(
            self.recognition_button
        )

        action_buttons.addStretch()

        main_layout.addLayout(
            action_buttons
        )

        self.status_label = QLabel(
            "● Камера не подключена"
        )

        main_layout.addWidget(
            self.status_label
        )

        self.recognition_status_label = QLabel(
            "AI: выключен"
        )

        main_layout.addWidget(
            self.recognition_status_label
        )

        self.last_person_label = QLabel(
            "Последнее распознавание: —"
        )

        main_layout.addWidget(
            self.last_person_label
        )

        self.telegram_status_label = QLabel(
            "Telegram: ожидание"
        )

        main_layout.addWidget(
            self.telegram_status_label
        )

        self.video_label = QLabel(
            "Нет видеопотока"
        )

        self.video_label.setAlignment(
            Qt.AlignCenter
        )

        self.video_label.setMinimumSize(
            900,
            500
        )

        self.video_label.setStyleSheet(
            """
            QLabel {
                background: #111;
                color: #aaa;
                border-radius: 8px;
            }
            """
        )

        main_layout.addWidget(
            self.video_label,
            stretch=1
        )

    def load_settings(self):
        camera = self.settings.camera()

        self.ip_input.setText(
            camera.get(
                "host",
                ""
            )
        )

        self.port_input.setValue(
            camera.get(
                "port",
                554
            )
        )

        self.path_input.setText(
            camera.get(
                "path",
                "/onvif1"
            )
        )

        self.username_input.setText(
            camera.get(
                "username",
                ""
            )
        )

        self.password_input.setText(
            camera.get(
                "password",
                ""
            )
        )

    def save_camera_settings(self):
        camera = self.settings.camera()

        camera["host"] = (
            self.ip_input
            .text()
            .strip()
        )

        camera["port"] = (
            self.port_input
            .value()
        )

        camera["path"] = (
            self.path_input
            .text()
            .strip()
        )

        camera["username"] = (
            self.username_input
            .text()
            .strip()
        )

        camera["password"] = (
            self.password_input
            .text()
        )

        self.settings.save()

    def connect_camera(self):
        if (
            self.camera_worker is not None
            and self.camera_worker.isRunning()
        ):
            return

        self.save_camera_settings()

        camera = self.settings.camera()

        if not camera["host"]:
            QMessageBox.warning(
                self,
                "FaceGuard",
                "Введите IP камеры."
            )
            return

        client = RTSPClient(
            host=camera["host"],
            username=camera["username"],
            password=camera["password"],
            port=camera["port"],
            path=camera["path"],
        )

        self.status_label.setText(
            "● Подключение..."
        )

        self.connect_button.setEnabled(
            False
        )

        self.disconnect_button.setEnabled(
            True
        )

        self.camera_worker = CameraWorker(
            client.url
        )

        self.camera_worker.frame_ready.connect(
            self.update_camera_frame
        )

        self.camera_worker.connected.connect(
            self.on_camera_connected
        )

        self.camera_worker.disconnected.connect(
            self.on_camera_disconnected
        )

        self.camera_worker.error.connect(
            self.on_camera_error
        )

        self.camera_worker.finished.connect(
            self.on_camera_worker_finished
        )

        self.camera_worker.start()

    def disconnect_camera(self):
        self.stop_recognition()

        if self.camera_worker is not None:
            self.camera_worker.stop()

    def update_camera_frame(
        self,
        image
    ):
        if self.recognition_enabled:
            return

        self.show_image(
            image
        )

    def update_recognition_frame(
        self,
        image
    ):
        if not self.recognition_enabled:
            return

        self.show_image(
            image
        )

    def show_image(
        self,
        image
    ):
        pixmap = QPixmap.fromImage(
            image
        )

        pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.video_label.setPixmap(
            pixmap
        )

    def on_camera_connected(self):
        self.status_label.setText(
            "● Камера подключена"
        )

        self.recognition_button.setEnabled(
            True
        )

    def on_camera_disconnected(self):
        self.status_label.setText(
            "● Камера переподключается..."
        )

        self.stop_recognition()

    def on_camera_error(
        self,
        message
    ):
        self.status_label.setText(
            "● Ошибка камеры"
        )

        print(
            "[CAMERA ERROR]",
            message
        )

    def on_camera_worker_finished(self):
        worker = self.sender()

        if worker is self.camera_worker:
            self.camera_worker = None

        if worker is not None:
            worker.deleteLater()

        self.reset_camera_ui()

    def toggle_recognition(self):
        if self.recognition_enabled:
            self.stop_recognition()
        else:
            self.start_recognition()

    def start_recognition(self):
        if (
            self.camera_worker is None
            or not self.camera_worker.isRunning()
        ):
            QMessageBox.warning(
                self,
                "FaceGuard",
                "Сначала подключите камеру."
            )
            return

        recognition = (
            self.settings
            .recognition()
        )

        self.create_monitoring_service()

        self.recognition_enabled = True

        self.recognition_button.setText(
            "Остановить распознавание"
        )

        self.recognition_worker = RecognitionWorker(
            camera_worker=self.camera_worker,
            threshold=float(
                recognition.get(
                    "threshold",
                    0.45
                )
            ),
            process_fps=int(
                recognition.get(
                    "process_fps",
                    3
                )
            ),
        )

        self.recognition_worker.frame_ready.connect(
            self.update_recognition_frame
        )

        self.recognition_worker.status.connect(
            self.on_recognition_status
        )

        self.recognition_worker.recognized.connect(
            self.on_person_recognized
        )

        self.recognition_worker.finished.connect(
            self.on_recognition_worker_finished
        )

        self.recognition_worker.start()

    def stop_recognition(self):
        self.recognition_enabled = False

        self.recognition_button.setText(
            "Запустить распознавание"
        )

        self.recognition_status_label.setText(
            "AI: выключен"
        )

        if self.recognition_worker is not None:
            self.recognition_worker.stop()

    def on_recognition_status(
        self,
        message
    ):
        if self.recognition_enabled:
            self.recognition_status_label.setText(
                f"AI: {message}"
            )

    def on_person_recognized(
        self,
        data
    ):
        name = data["name"]
        similarity = data["similarity"]

        self.last_person_label.setText(
            (
                "Последнее распознавание: "
                f"{name} ({similarity:.2f})"
            )
        )

        try:
            result = (
                self.monitoring_service
                .handle_recognition(
                    person_id=data["person_id"],
                    name=name,
                    similarity=similarity,
                    frame=data["frame"],
                )
            )

        except Exception as exc:
            print(
                "[MONITORING ERROR]",
                exc
            )
            return

        if not result["triggered"]:
            return

        if result["telegram_sent"]:
            self.telegram_status_label.setText(
                f"Telegram: отправлено — {name}"
            )

        elif result["telegram_error"]:
            self.telegram_status_label.setText(
                "Telegram: ошибка"
            )

            print(
                "[TELEGRAM ERROR]",
                result["telegram_error"]
            )

        else:
            self.telegram_status_label.setText(
                "Telegram: не настроен"
            )

    def on_recognition_worker_finished(self):
        worker = self.sender()

        if worker is self.recognition_worker:
            self.recognition_worker = None

        if worker is not None:
            worker.deleteLater()

        self.recognition_enabled = False

        self.recognition_button.setText(
            "Запустить распознавание"
        )

    def open_people_window(self):
        if (
            self.people_window is None
            or not self.people_window.isVisible()
        ):
            self.people_window = PeopleWindow()
            self.people_window.show()
            return

        self.people_window.raise_()
        self.people_window.activateWindow()

    def open_history_window(self):
        if (
            self.history_window is None
            or not self.history_window.isVisible()
        ):
            self.history_window = HistoryWindow()
            self.history_window.show()
            return

        self.history_window.load_history()
        self.history_window.raise_()
        self.history_window.activateWindow()

    def open_settings_window(self):
        dialog = SettingsWindow(
            self
        )

        if dialog.exec():
            self.settings = Settings()
            self.create_monitoring_service()

    def reset_camera_ui(self):
        self.stop_recognition()

        self.status_label.setText(
            "● Камера не подключена"
        )

        self.video_label.clear()

        self.video_label.setText(
            "Нет видеопотока"
        )

        self.connect_button.setEnabled(
            True
        )

        self.disconnect_button.setEnabled(
            False
        )

        self.recognition_button.setEnabled(
            False
        )

    def closeEvent(
        self,
        event
    ):
        if (
            self.recognition_worker is not None
            and self.recognition_worker.isRunning()
        ):
            self.recognition_worker.stop()

            self.recognition_worker.wait(
                10000
            )

        if (
            self.camera_worker is not None
            and self.camera_worker.isRunning()
        ):
            self.camera_worker.stop()

            self.camera_worker.wait(
                7000
            )

            if self.camera_worker.isRunning():
                event.ignore()
                return

        event.accept()