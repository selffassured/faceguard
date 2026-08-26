import cv2

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage


class CameraWorker(QThread):
    frame_ready = Signal(QImage)
    connected = Signal()
    disconnected = Signal()
    error = Signal(str)

    def __init__(self, rtsp_url: str):
        super().__init__()

        self.rtsp_url = rtsp_url
        self.running = False
        self.cap = None

    def run(self):
        self.running = True

        try:
            while self.running:
                self.cap = cv2.VideoCapture(
                    self.rtsp_url,
                    cv2.CAP_FFMPEG,
                    [
                        cv2.CAP_PROP_OPEN_TIMEOUT_MSEC,
                        5000,
                        cv2.CAP_PROP_READ_TIMEOUT_MSEC,
                        5000,
                    ],
                )

                if not self.running:
                    self._release()
                    break

                if not self.cap.isOpened():
                    self.error.emit(
                        "Не удалось подключиться к RTSP-потоку"
                    )

                    self._release()

                    # Ждём 3 секунды перед следующей попыткой,
                    # но можем остановиться в любой момент.
                    for _ in range(30):
                        if not self.running:
                            break

                        self.msleep(100)

                    continue

                self.cap.set(
                    cv2.CAP_PROP_BUFFERSIZE,
                    1,
                )

                self.connected.emit()

                failed_frames = 0

                while self.running:
                    ret, frame = self.cap.read()

                    if not self.running:
                        break

                    if not ret:
                        failed_frames += 1

                        if failed_frames >= 5:
                            break

                        self.msleep(50)
                        continue

                    failed_frames = 0

                    rgb = cv2.cvtColor(
                        frame,
                        cv2.COLOR_BGR2RGB,
                    )

                    height, width, channels = rgb.shape
                    bytes_per_line = channels * width

                    image = QImage(
                        rgb.data,
                        width,
                        height,
                        bytes_per_line,
                        QImage.Format_RGB888,
                    ).copy()

                    self.frame_ready.emit(image)

                self._release()

                if self.running:
                    self.disconnected.emit()

                    # Небольшая пауза перед переподключением.
                    for _ in range(20):
                        if not self.running:
                            break

                        self.msleep(100)

        except Exception as exc:
            self.error.emit(str(exc))

        finally:
            self._release()
            self.running = False

    def stop(self):
        """
        Не release'им VideoCapture из GUI-потока.

        Просто сообщаем worker'у,
        что он должен завершиться.
        """
        self.running = False

    def _release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None