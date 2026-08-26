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
from app.config.settings import Settings


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FaceGuard")
        self.resize(1100, 750)

        self.settings = Settings()

        self.camera_worker = None

        # Нужен, чтобы понимать,
        # пользователь сам нажал "Отключить"
        # или камера реально отвалилась.
        self.manual_disconnect = False

        self.build_ui()
        self.load_settings()

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)

        # -------------------------
        # TITLE
        # -------------------------

        title = QLabel("FaceGuard")
        title.setAlignment(Qt.AlignCenter)

        font = title.font()
        font.setPointSize(22)
        font.setBold(True)

        title.setFont(font)

        main_layout.addWidget(title)

        # -------------------------
        # CAMERA SETTINGS
        # -------------------------

        camera_group = QGroupBox("Камера")
        camera_form = QFormLayout(camera_group)

        self.ip_input = QLineEdit()

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(554)

        self.path_input = QLineEdit()

        self.username_input = QLineEdit()

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(
            QLineEdit.Password
        )

        camera_form.addRow(
            "IP:",
            self.ip_input,
        )

        camera_form.addRow(
            "Порт:",
            self.port_input,
        )

        camera_form.addRow(
            "RTSP path:",
            self.path_input,
        )

        camera_form.addRow(
            "Логин:",
            self.username_input,
        )

        camera_form.addRow(
            "Пароль:",
            self.password_input,
        )

        main_layout.addWidget(camera_group)

        # -------------------------
        # BUTTONS
        # -------------------------

        buttons_layout = QHBoxLayout()

        self.connect_button = QPushButton(
            "Подключить камеру"
        )

        self.disconnect_button = QPushButton(
            "Отключить"
        )

        self.disconnect_button.setEnabled(False)

        self.connect_button.clicked.connect(
            self.connect_camera
        )

        self.disconnect_button.clicked.connect(
            self.disconnect_camera
        )

        buttons_layout.addWidget(
            self.connect_button
        )

        buttons_layout.addWidget(
            self.disconnect_button
        )

        main_layout.addLayout(
            buttons_layout
        )

        # -------------------------
        # STATUS
        # -------------------------

        self.status_label = QLabel(
            "● Камера не подключена"
        )

        main_layout.addWidget(
            self.status_label
        )

        # -------------------------
        # VIDEO
        # -------------------------

        self.video_label = QLabel(
            "Нет видеопотока"
        )

        self.video_label.setAlignment(
            Qt.AlignCenter
        )

        self.video_label.setMinimumSize(
            800,
            450
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
            stretch=1,
        )

    def load_settings(self):
        camera = self.settings.camera()

        self.ip_input.setText(
            camera.get(
                "host",
                "",
            )
        )

        self.port_input.setValue(
            camera.get(
                "port",
                554,
            )
        )

        self.path_input.setText(
            camera.get(
                "path",
                "/onvif1",
            )
        )

        self.username_input.setText(
            camera.get(
                "username",
                "",
            )
        )

        self.password_input.setText(
            camera.get(
                "password",
                "",
            )
        )

    def save_camera_settings(self):
        camera = self.settings.camera()

        camera["host"] = (
            self.ip_input.text().strip()
        )

        camera["port"] = (
            self.port_input.value()
        )

        camera["path"] = (
            self.path_input.text().strip()
        )

        camera["username"] = (
            self.username_input.text().strip()
        )

        camera["password"] = (
            self.password_input.text()
        )

        self.settings.save()

    def connect_camera(self):
        # Если старый worker ещё не закончил,
        # новый не создаём.
        if (
            self.camera_worker is not None
            and self.camera_worker.isRunning()
        ):
            QMessageBox.information(
                self,
                "FaceGuard",
                "Камера уже подключается или работает.",
            )
            return

        self.manual_disconnect = False

        self.save_camera_settings()

        camera_settings = (
            self.settings.camera()
        )

        host = camera_settings["host"]
        username = camera_settings["username"]
        password = camera_settings["password"]
        port = camera_settings["port"]
        path = camera_settings["path"]

        if not host:
            QMessageBox.warning(
                self,
                "FaceGuard",
                "Введите IP камеры.",
            )
            return

        client = RTSPClient(
            host=host,
            username=username,
            password=password,
            port=port,
            path=path,
        )

        self.status_label.setText(
            "● Подключение..."
        )

        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)

        self.camera_worker = CameraWorker(
            client.url
        )

        self.camera_worker.frame_ready.connect(
            self.update_frame
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

        # Критически важная строка:
        # объект удаляем только после
        # фактического завершения QThread.
        self.camera_worker.finished.connect(
            self.on_worker_finished
        )

        self.camera_worker.start()

    def disconnect_camera(self):
        if self.camera_worker is None:
            self.reset_camera_ui()
            return

        if not self.camera_worker.isRunning():
            self.reset_camera_ui()
            return

        self.manual_disconnect = True

        self.status_label.setText(
            "● Отключение..."
        )

        self.disconnect_button.setEnabled(False)

        # Только просим worker завершиться.
        # НЕ уничтожаем объект.
        self.camera_worker.stop()

    def update_frame(self, image):
        pixmap = QPixmap.fromImage(
            image
        )

        pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.video_label.setPixmap(
            pixmap
        )

    def on_camera_connected(self):
        if self.manual_disconnect:
            return

        self.status_label.setText(
            "● Камера подключена"
        )

    def on_camera_disconnected(self):
        if self.manual_disconnect:
            return

        self.status_label.setText(
            "● Соединение потеряно. Переподключение..."
        )

    def on_camera_error(self, message):
        if self.manual_disconnect:
            return

        self.status_label.setText(
            "● Ошибка подключения"
        )

        print(
            "[CAMERA ERROR]",
            message,
        )

    def on_worker_finished(self):
        worker = self.sender()

        # Если завершился именно текущий worker,
        # только теперь убираем ссылку на него.
        if worker is self.camera_worker:
            self.camera_worker = None

        if worker is not None:
            worker.deleteLater()

        self.reset_camera_ui()

    def reset_camera_ui(self):
        self.status_label.setText(
            "● Камера не подключена"
        )

        self.video_label.clear()

        self.video_label.setText(
            "Нет видеопотока"
        )

        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)

    def closeEvent(self, event):
        """
        При закрытии окна ждём завершения worker,
        чтобы Qt не уничтожил работающий QThread.
        """

        worker = self.camera_worker

        if (
            worker is not None
            and worker.isRunning()
        ):
            worker.stop()

            # У нас open/read timeout = 5 секунд.
            # Даём немного запаса.
            worker.wait(7000)

            if worker.isRunning():
                print(
                    "[CAMERA] Worker did not stop in time"
                )

                # Не даём приложению закрыться,
                # пока поток реально жив.
                event.ignore()
                return

        event.accept()