import sqlite3
from pathlib import Path


DB_PATH = Path("data/faceguard.db")


def get_connection():
    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    # SQLite требует включать foreign_keys
    # для каждого соединения отдельно.
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def init_db():
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                comment TEXT DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS person_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (person_id)
                    REFERENCES people(id)
                    ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS face_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                photo_id INTEGER,
                embedding BLOB NOT NULL,
                dimension INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (person_id)
                    REFERENCES people(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (photo_id)
                    REFERENCES person_photos(id)
                    ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_embeddings_person_id
            ON face_embeddings(person_id)
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER,
                detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                confidence REAL,
                screenshot_path TEXT,

                FOREIGN KEY (person_id)
                    REFERENCES people(id)
                    ON DELETE SET NULL
            )
            """
        )

        connection.commit()