import threading

import cv2

from PySide6.QtCore import (
    QThread,
    Signal,
)

from PySide6.QtGui import (
    QImage,
)


class CameraWorker(QThread):
    frame_ready = Signal(QImage)
    connected = Signal()
    disconnected = Signal()
    error = Signal(str)

    def __init__(
        self,
        rtsp_url: str
    ):
        super().__init__()

        self.rtsp_url = (
            rtsp_url
        )

        self.running = False
        self.cap = None

        self.latest_frame = None

        self.frame_lock = (
            threading.Lock()
        )

    def run(self):
        self.running = True

        try:
            while self.running:
                self.cap = (
                    cv2.VideoCapture(
                        self.rtsp_url,
                        cv2.CAP_FFMPEG,
                        [
                            cv2.CAP_PROP_OPEN_TIMEOUT_MSEC,
                            5000,

                            cv2.CAP_PROP_READ_TIMEOUT_MSEC,
                            5000,
                        ],
                    )
                )

                if not self.running:
                    self._release()
                    break

                if not self.cap.isOpened():
                    self.error.emit(
                        "Не удалось подключиться "
                        "к RTSP-потоку"
                    )

                    self._release()

                    for _ in range(
                        30
                    ):
                        if not self.running:
                            break

                        self.msleep(
                            100
                        )

                    continue

                self.cap.set(
                    cv2.CAP_PROP_BUFFERSIZE,
                    1
                )

                self.connected.emit()

                failed_frames = 0

                while self.running:
                    ret, frame = (
                        self.cap.read()
                    )

                    if not self.running:
                        break

                    if not ret:
                        failed_frames += 1

                        if (
                            failed_frames
                            >= 5
                        ):
                            break

                        self.msleep(
                            50
                        )

                        continue

                    failed_frames = 0

                    with self.frame_lock:
                        self.latest_frame = (
                            frame.copy()
                        )

                    image = (
                        self.frame_to_qimage(
                            frame
                        )
                    )

                    self.frame_ready.emit(
                        image
                    )

                self._release()

                if self.running:
                    self.disconnected.emit()

                    for _ in range(
                        20
                    ):
                        if not self.running:
                            break

                        self.msleep(
                            100
                        )

        except Exception as exc:
            self.error.emit(
                str(exc)
            )

        finally:
            self._release()

            with self.frame_lock:
                self.latest_frame = None

            self.running = False

    def get_latest_frame(
        self
    ):
        with self.frame_lock:
            if (
                self.latest_frame
                is None
            ):
                return None

            return (
                self.latest_frame
                .copy()
            )

    def stop(self):
        self.running = False

    def _release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    @staticmethod
    def frame_to_qimage(
        frame
    ):
        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        height, width, channels = (
            rgb.shape
        )

        bytes_per_line = (
            channels * width
        )

        return QImage(
            rgb.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888
        ).copy()