import numpy as np

from app.database.face_embedding_repository import (
    FaceEmbeddingRepository
)

from app.recognition.face_engine import (
    FaceEngine
)


class FaceMatcher:
    def __init__(
        self,
        threshold: float = 0.45
    ):
        self.threshold = threshold

        self.embedding_repository = (
            FaceEmbeddingRepository()
        )

        self.database = []

        self.reload()

    def reload(self):
        self.database = (
            self.embedding_repository
            .get_all_embeddings()
        )

        print(
            f"[MATCHER] Loaded embeddings: "
            f"{len(self.database)}"
        )

    def match(
        self,
        query_embedding: np.ndarray
    ):
        if not self.database:
            return {
                "matched": False,
                "person_id": None,
                "name": None,
                "similarity": 0.0,
                "photo_path": None,
            }

        best_record = None
        best_similarity = -1.0

        for record in self.database:
            similarity = FaceEngine.similarity(
                query_embedding,
                record["embedding"]
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_record = record

        if best_record is None:
            return {
                "matched": False,
                "person_id": None,
                "name": None,
                "similarity": 0.0,
                "photo_path": None,
            }

        matched = (
            best_similarity
            >= self.threshold
        )

        return {
            "matched": matched,
            "person_id": (
                best_record["person_id"]
                if matched
                else None
            ),
            "name": (
                best_record["name"]
                if matched
                else None
            ),
            "similarity": best_similarity,
            "photo_path": (
                best_record["photo_path"]
            ),
        }