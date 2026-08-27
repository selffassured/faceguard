from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis


class FaceEngine:
    def __init__(
        self,
        model_name: str = "buffalo_l",
        det_size: tuple[int, int] = (640, 640),
    ):
        self.model_name = model_name
        self.det_size = det_size

        print("[FACE] Loading InsightFace...")

        self.app = FaceAnalysis(
            name=self.model_name,
            providers=[
                "CPUExecutionProvider",
            ],
        )

        self.app.prepare(
            ctx_id=0,
            det_size=self.det_size,
        )

        print("[FACE] InsightFace ready")

    def read_image(self, image_path: str | Path):
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Файл не найден: {image_path}"
            )

        image = cv2.imread(
            str(image_path)
        )

        if image is None:
            raise ValueError(
                f"Не удалось открыть изображение: {image_path}"
            )

        return image

    def detect_faces(self, image):
        """
        Возвращает все найденные лица.
        """

        if image is None:
            return []

        faces = self.app.get(image)

        return faces

    def get_embedding_from_image(
        self,
        image,
        require_single_face: bool = True,
    ):
        """
        Находит лицо и возвращает нормализованный embedding.

        Если require_single_face=True:
        на изображении должно быть ровно одно лицо.
        """

        faces = self.detect_faces(
            image
        )

        if not faces:
            raise ValueError(
                "На фотографии не найдено лицо."
            )

        if (
            require_single_face
            and len(faces) > 1
        ):
            raise ValueError(
                f"На фотографии найдено несколько лиц: {len(faces)}."
            )

        # Если лиц несколько и single_face выключен,
        # берём самое крупное.
        face = max(
            faces,
            key=self._face_area,
        )

        embedding = face.embedding

        if embedding is None:
            raise ValueError(
                "InsightFace не вернул embedding лица."
            )

        return self.normalize_embedding(
            embedding
        )

    def get_embedding_from_file(
        self,
        image_path: str | Path,
        require_single_face: bool = True,
    ):
        image = self.read_image(
            image_path
        )

        return self.get_embedding_from_image(
            image,
            require_single_face=require_single_face,
        )

    @staticmethod
    def normalize_embedding(
        embedding: np.ndarray,
    ) -> np.ndarray:
        embedding = np.asarray(
            embedding,
            dtype=np.float32,
        )

        norm = np.linalg.norm(
            embedding
        )

        if norm == 0:
            raise ValueError(
                "Получен пустой embedding."
            )

        return embedding / norm

    @staticmethod
    def similarity(
        embedding_a: np.ndarray,
        embedding_b: np.ndarray,
    ) -> float:
        """
        Cosine similarity.

        Чем ближе значение к 1.0,
        тем больше лица похожи.
        """

        embedding_a = FaceEngine.normalize_embedding(
            embedding_a
        )

        embedding_b = FaceEngine.normalize_embedding(
            embedding_b
        )

        return float(
            np.dot(
                embedding_a,
                embedding_b,
            )
        )

    @staticmethod
    def _face_area(face):
        bbox = face.bbox

        x1, y1, x2, y2 = bbox

        width = max(
            0,
            x2 - x1,
        )

        height = max(
            0,
            y2 - y1,
        )

        return width * height