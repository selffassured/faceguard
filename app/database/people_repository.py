import shutil
import uuid
from pathlib import Path

from app.database.db import get_connection


FACES_DIR = Path("data/faces")


class PeopleRepository:
    def __init__(self):
        FACES_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

    def add_person(
        self,
        name: str,
        photo_paths: list[str],
        comment: str = ""
    ) -> int:
        name = name.strip()
        comment = comment.strip()

        if not name:
            raise ValueError(
                "Имя человека не может быть пустым"
            )

        if not photo_paths:
            raise ValueError(
                "Нужно добавить хотя бы одну фотографию"
            )

        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO people (
                    name,
                    comment
                )
                VALUES (?, ?)
                """,
                (
                    name,
                    comment
                )
            )

            person_id = cursor.lastrowid

            person_dir = (
                FACES_DIR
                / str(person_id)
            )

            person_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            for source_path in photo_paths:
                source = Path(
                    source_path
                )

                if not source.exists():
                    continue

                extension = (
                    source.suffix.lower()
                    or ".jpg"
                )

                filename = (
                    f"{uuid.uuid4().hex}"
                    f"{extension}"
                )

                destination = (
                    person_dir
                    / filename
                )

                shutil.copy2(
                    source,
                    destination
                )

                cursor.execute(
                    """
                    INSERT INTO person_photos (
                        person_id,
                        photo_path
                    )
                    VALUES (?, ?)
                    """,
                    (
                        person_id,
                        str(destination)
                    )
                )

            connection.commit()

            return person_id

    def get_all_people(self):
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    p.id,
                    p.name,
                    p.comment,
                    p.created_at,
                    COUNT(pp.id) AS photo_count
                FROM people p

                LEFT JOIN person_photos pp
                    ON pp.person_id = p.id

                GROUP BY
                    p.id,
                    p.name,
                    p.comment,
                    p.created_at

                ORDER BY p.id DESC
                """
            )

            return cursor.fetchall()

    def get_person(self, person_id: int):
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT *
                FROM people
                WHERE id = ?
                """,
                (person_id,)
            )

            return cursor.fetchone()

    def get_person_photos(
        self,
        person_id: int
    ):
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT *
                FROM person_photos
                WHERE person_id = ?
                ORDER BY id ASC
                """,
                (person_id,)
            )

            return cursor.fetchall()

    def delete_person(
        self,
        person_id: int
    ):
        person_dir = (
            FACES_DIR
            / str(person_id)
        )

        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM person_photos
                WHERE person_id = ?
                """,
                (person_id,)
            )

            cursor.execute(
                """
                DELETE FROM people
                WHERE id = ?
                """,
                (person_id,)
            )

            connection.commit()

        if person_dir.exists():
            shutil.rmtree(
                person_dir,
                ignore_errors=True
            )