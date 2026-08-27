from app.database.people_repository import (
    PeopleRepository
)

from app.database.face_embedding_repository import (
    FaceEmbeddingRepository
)

from app.recognition.face_engine import (
    FaceEngine
)


class PersonService:
    def __init__(
        self,
        face_engine: FaceEngine | None = None
    ):
        self.people_repository = (
            PeopleRepository()
        )

        self.embedding_repository = (
            FaceEmbeddingRepository()
        )

        # Можно передать уже загруженный FaceEngine,
        # чтобы потом не грузить модель несколько раз.
        self.face_engine = (
            face_engine
            if face_engine is not None
            else FaceEngine()
        )

    def add_person(
        self,
        name: str,
        photo_paths: list[str],
        comment: str = ""
    ):
        """
        1. Сохраняет человека и фотографии.
        2. Находит лицо на каждой фотографии.
        3. Создаёт embedding.
        4. Сохраняет embeddings в SQLite.

        Если ни одна фотография не подходит,
        человек удаляется обратно.
        """

        person_id = (
            self.people_repository
            .add_person(
                name=name,
                photo_paths=photo_paths,
                comment=comment
            )
        )

        stored_photos = (
            self.people_repository
            .get_person_photos(
                person_id
            )
        )

        successful = []
        failed = []

        for photo in stored_photos:
            photo_id = photo["id"]
            photo_path = photo["photo_path"]

            try:
                embedding = (
                    self.face_engine
                    .get_embedding_from_file(
                        photo_path,
                        require_single_face=True
                    )
                )

                self.embedding_repository.save_embedding(
                    person_id=person_id,
                    photo_id=photo_id,
                    embedding=embedding
                )

                successful.append(
                    photo_path
                )

            except Exception as exc:
                failed.append(
                    {
                        "photo_path": photo_path,
                        "error": str(exc),
                    }
                )

        if not successful:
            self.people_repository.delete_person(
                person_id
            )

            raise ValueError(
                "Ни на одной фотографии "
                "не удалось корректно определить лицо."
            )

        return {
            "person_id": person_id,
            "successful": successful,
            "failed": failed,
            "embedding_count": len(successful),
        }