import time
import cv2

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from app.recognition.face_engine import FaceEngine
from app.recognition.face_matcher import FaceMatcher


class RecognitionWorker(QThread):
    frame_ready = Signal(QImage)
    status = Signal(str)
    recognized = Signal(dict)

    def __init__(
        self,
        camera_worker,
        threshold: float = 0.45,
        process_fps: int = 3,
    ):
        super().__init__()

        self.camera_worker = camera_worker

        self.threshold = threshold
        self.process_fps = max(1, process_fps)

        self.running = False

        self.face_engine = None
        self.matcher = None

    def run(self):
        self.running = True

        try:
            self.status.emit(
                "Загрузка InsightFace..."
            )

            self.face_engine = FaceEngine()

            self.matcher = FaceMatcher(
                threshold=self.threshold
            )

            self.status.emit(
                f"Распознавание запущено. "
                f"Embeddings: {len(self.matcher.database)}"
            )

            delay = (
                1.0 / self.process_fps
            )

            while self.running:
                started_at = time.time()

                frame = (
                    self.camera_worker
                    .get_latest_frame()
                )

                if frame is None:
                    self.msleep(50)
                    continue

                processed_frame = (
                    self.process_frame(
                        frame
                    )
                )

                image = (
                    self.frame_to_qimage(
                        processed_frame
                    )
                )

                self.frame_ready.emit(
                    image
                )

                elapsed = (
                    time.time()
                    - started_at
                )

                remaining = (
                    delay - elapsed
                )

                if remaining > 0:
                    self.msleep(
                        int(
                            remaining * 1000
                        )
                    )

        except Exception as exc:
            self.status.emit(
                f"Ошибка распознавания: {exc}"
            )

            print(
                "[RECOGNITION ERROR]",
                exc
            )

        finally:
            self.running = False

            self.status.emit(
                "Распознавание остановлено"
            )

    def process_frame(
        self,
        frame
    ):
        output = frame.copy()

        faces = (
            self.face_engine
            .detect_faces(
                frame
            )
        )

        for face in faces:
            bbox = (
                face.bbox
                .astype(int)
            )

            x1, y1, x2, y2 = bbox

            embedding = (
                face.embedding
            )

            if embedding is None:
                continue

            result = (
                self.matcher
                .match(
                    embedding
                )
            )

            similarity = (
                result[
                    "similarity"
                ]
            )

            if result["matched"]:
                name = (
                    result["name"]
                )

                label = (
                    f"{name} "
                    f"{similarity:.2f}"
                )

                box_color = (
                    0,
                    255,
                    0
                )

                self.recognized.emit(
                    {
                        "person_id": (
                            result[
                                "person_id"
                            ]
                        ),
                        "name": name,
                        "similarity": (
                            similarity
                        ),
                    }
                )

            else:
                label = (
                    f"UNKNOWN "
                    f"{similarity:.2f}"
                )

                box_color = (
                    0,
                    0,
                    255
                )

            cv2.rectangle(
                output,
                (
                    x1,
                    y1
                ),
                (
                    x2,
                    y2
                ),
                box_color,
                2
            )

            text_y = max(
                25,
                y1 - 10
            )

            cv2.putText(
                output,
                label,
                (
                    x1,
                    text_y
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                box_color,
                2,
                cv2.LINE_AA
            )

        return output

    def reload_database(self):
        if self.matcher is not None:
            self.matcher.reload()

    def stop(self):
        self.running = False

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