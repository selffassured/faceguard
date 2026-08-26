from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QListWidget,
    QFileDialog,
    QMessageBox,
    QLabel
)

from app.database.people_repository import (
    PeopleRepository
)


class AddPersonDialog(QDialog):
    def __init__(
        self,
        parent=None
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "Добавить человека"
        )

        self.resize(
            600,
            500
        )

        self.repository = (
            PeopleRepository()
        )

        self.photo_paths = []

        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "Новый человек"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        font = title.font()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)

        layout.addWidget(
            title
        )

        form = QFormLayout()

        self.name_input = (
            QLineEdit()
        )

        self.comment_input = (
            QTextEdit()
        )

        self.comment_input.setFixedHeight(
            80
        )

        form.addRow(
            "Имя:",
            self.name_input
        )

        form.addRow(
            "Комментарий:",
            self.comment_input
        )

        layout.addLayout(
            form
        )

        photos_label = QLabel(
            "Фотографии:"
        )

        layout.addWidget(
            photos_label
        )

        self.photos_list = (
            QListWidget()
        )

        layout.addWidget(
            self.photos_list
        )

        photo_buttons = (
            QHBoxLayout()
        )

        self.add_photo_button = (
            QPushButton(
                "Добавить фотографии"
            )
        )

        self.remove_photo_button = (
            QPushButton(
                "Удалить выбранную"
            )
        )

        self.add_photo_button.clicked.connect(
            self.select_photos
        )

        self.remove_photo_button.clicked.connect(
            self.remove_selected_photo
        )

        photo_buttons.addWidget(
            self.add_photo_button
        )

        photo_buttons.addWidget(
            self.remove_photo_button
        )

        layout.addLayout(
            photo_buttons
        )

        buttons = QHBoxLayout()

        self.save_button = (
            QPushButton(
                "Сохранить"
            )
        )

        self.cancel_button = (
            QPushButton(
                "Отмена"
            )
        )

        self.save_button.clicked.connect(
            self.save_person
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        buttons.addWidget(
            self.save_button
        )

        buttons.addWidget(
            self.cancel_button
        )

        layout.addLayout(
            buttons
        )

    def select_photos(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите фотографии",
            "",
            (
                "Images "
                "(*.jpg *.jpeg *.png *.bmp *.webp)"
            )
        )

        for file_path in files:
            if (
                file_path
                not in self.photo_paths
            ):
                self.photo_paths.append(
                    file_path
                )

                self.photos_list.addItem(
                    Path(
                        file_path
                    ).name
                )

    def remove_selected_photo(self):
        row = (
            self.photos_list.currentRow()
        )

        if row < 0:
            return

        self.photos_list.takeItem(
            row
        )

        del self.photo_paths[
            row
        ]

    def save_person(self):
        name = (
            self.name_input
            .text()
            .strip()
        )

        comment = (
            self.comment_input
            .toPlainText()
            .strip()
        )

        if not name:
            QMessageBox.warning(
                self,
                "FaceGuard",
                "Введите имя человека."
            )
            return

        if not self.photo_paths:
            QMessageBox.warning(
                self,
                "FaceGuard",
                (
                    "Добавьте хотя бы "
                    "одну фотографию."
                )
            )
            return

        try:
            self.repository.add_person(
                name=name,
                photo_paths=(
                    self.photo_paths
                ),
                comment=comment
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "FaceGuard",
                str(exc)
            )
            return

        QMessageBox.information(
            self,
            "FaceGuard",
            "Человек добавлен в базу."
        )

        self.accept()