from app.database.db import (
    get_connection
)


class DetectionRepository:
    def add_detection(
        self,
        person_id: int | None,
        confidence: float,
        screenshot_path: str | None = None,
    ) -> int:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO detections (
                    person_id,
                    confidence,
                    screenshot_path
                )
                VALUES (?, ?, ?)
                """,
                (
                    person_id,
                    confidence,
                    screenshot_path,
                )
            )

            connection.commit()

            return cursor.lastrowid

    def get_recent(
        self,
        limit: int = 100,
    ):
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    d.id,
                    d.person_id,
                    d.detected_at,
                    d.confidence,
                    d.screenshot_path,
                    p.name

                FROM detections d

                LEFT JOIN people p
                    ON p.id = d.person_id

                ORDER BY
                    d.detected_at DESC

                LIMIT ?
                """,
                (
                    limit,
                )
            )

            return cursor.fetchall()