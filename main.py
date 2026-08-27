import sys

from app.database.db import init_db
from app.ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication


def main():
    init_db()

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "FaceGuard"
    )

    window = MainWindow()
    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()