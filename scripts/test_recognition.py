from app.database.db import (
    init_db
)

from app.database.face_embedding_repository import (
    FaceEmbeddingRepository
)

from app.recognition.face_engine import (
    FaceEngine
)

from app.recognition.face_matcher import (
    FaceMatcher
)


MATCH_THRESHOLD = 0.45


def main():
    print()
    print(
        "================================"
    )

    print(
        " FaceGuard SQLite Recognition"
    )

    print(
        "================================"
    )

    init_db()

    embedding_repository = (
        FaceEmbeddingRepository()
    )

    embedding_count = (
        embedding_repository
        .count_embeddings()
    )

    print()
    print(
        f"Embeddings в SQLite: "
        f"{embedding_count}"
    )

    if embedding_count == 0:
        print()
        print(
            "В базе пока нет embeddings."
        )

        print(
            "Удалите старого тестового человека "
            "и добавьте его заново через FaceGuard."
        )

        return

    engine = FaceEngine()

    matcher = FaceMatcher(
        threshold=MATCH_THRESHOLD
    )

    print()

    query_path = input(
        "Путь к тестовой фотографии: "
    ).strip().strip('"')

    if not query_path:
        print(
            "Путь не указан."
        )

        return

    try:
        query_embedding = (
            engine
            .get_embedding_from_file(
                query_path,
                require_single_face=True
            )
        )

    except Exception as exc:
        print()
        print(
            f"[ERROR] {exc}"
        )

        return

    result = matcher.match(
        query_embedding
    )

    print()
    print(
        "================================"
    )

    print(
        "           РЕЗУЛЬТАТ"
    )

    print(
        "================================"
    )

    print(
        f"Similarity: "
        f"{result['similarity']:.4f}"
    )

    if result["matched"]:
        print(
            f"РАСПОЗНАН: "
            f"{result['name']}"
        )

        print(
            f"Person ID: "
            f"{result['person_id']}"
        )

        print(
            f"Фото базы: "
            f"{result['photo_path']}"
        )

    else:
        print(
            "НЕИЗВЕСТНЫЙ ЧЕЛОВЕК"
        )


if __name__ == "__main__":
    main()