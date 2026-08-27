import numpy as np

from app.database.db import (
    get_connection
)


class FaceEmbeddingRepository:
    def save_embedding(
        self,
        person_id: int,
        embedding: np.ndarray,
        photo_id: int | None = None
    ) -> int:
        embedding = np.asarray(
            embedding,
            dtype=np.float32
        )

        if embedding.ndim != 1:
            raise ValueError(
                "Embedding должен быть одномерным массивом."
            )

        blob = embedding.tobytes()

        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO face_embeddings (
                    person_id,
                    photo_id,
                    embedding,
                    dimension
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    person_id,
                    photo_id,
                    blob,
                    embedding.shape[0]
                )
            )

            connection.commit()

            return cursor.lastrowid

    def get_all_embeddings(self):
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    fe.id,
                    fe.person_id,
                    fe.photo_id,
                    fe.embedding,
                    fe.dimension,
                    p.name,
                    p.comment,
                    pp.photo_path

                FROM face_embeddings fe

                JOIN people p
                    ON p.id = fe.person_id

                LEFT JOIN person_photos pp
                    ON pp.id = fe.photo_id

                ORDER BY
                    fe.person_id ASC,
                    fe.id ASC
                """
            )

            rows = cursor.fetchall()

        result = []

        for row in rows:
            embedding = np.frombuffer(
                row["embedding"],
                dtype=np.float32
            ).copy()

            expected_dimension = (
                row["dimension"]
            )

            if (
                embedding.shape[0]
                != expected_dimension
            ):
                continue

            result.append(
                {
                    "id": row["id"],
                    "person_id": row["person_id"],
                    "photo_id": row["photo_id"],
                    "name": row["name"],
                    "comment": row["comment"],
                    "photo_path": row["photo_path"],
                    "embedding": embedding,
                }
            )

        return result

    def get_person_embeddings(
        self,
        person_id: int
    ):
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    person_id,
                    photo_id,
                    embedding,
                    dimension

                FROM face_embeddings

                WHERE person_id = ?

                ORDER BY id ASC
                """,
                (
                    person_id,
                )
            )

            rows = cursor.fetchall()

        result = []

        for row in rows:
            embedding = np.frombuffer(
                row["embedding"],
                dtype=np.float32
            ).copy()

            result.append(
                {
                    "id": row["id"],
                    "person_id": row["person_id"],
                    "photo_id": row["photo_id"],
                    "embedding": embedding,
                }
            )

        return result

    def delete_person_embeddings(
        self,
        person_id: int
    ):
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM face_embeddings
                WHERE person_id = ?
                """,
                (
                    person_id,
                )
            )

            connection.commit()

    def count_embeddings(self) -> int:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT COUNT(*) AS count
                FROM face_embeddings
                """
            )

            row = cursor.fetchone()

            return row["count"]