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
    QLabel,
    QApplication
)

from app.services.person_service import (
    PersonService
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
            620,
            520
        )

        self.photo_paths = []

        self.person_service = None

        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "Добавление человека"
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

        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText(
            "Например: Иван Иванов"
        )

        self.comment_input = QTextEdit()

        self.comment_input.setPlaceholderText(
            "Необязательный комментарий"
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
            "Фотографии человека"
        )

        layout.addWidget(
            photos_label
        )

        self.photos_list = QListWidget()

        layout.addWidget(
            self.photos_list
        )

        photo_buttons = QHBoxLayout()

        self.add_photo_button = QPushButton(
            "Добавить фотографии"
        )

        self.remove_photo_button = QPushButton(
            "Удалить выбранную"
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

        info_label = QLabel(
            "Рекомендуется 3–5 фотографий. "
            "На каждой фотографии должен быть "
            "один хорошо видимый человек."
        )

        info_label.setWordWrap(
            True
        )

        layout.addWidget(
            info_label
        )

        self.status_label = QLabel(
            ""
        )

        layout.addWidget(
            self.status_label
        )

        buttons = QHBoxLayout()

        self.save_button = QPushButton(
            "Сохранить"
        )

        self.cancel_button = QPushButton(
            "Отмена"
        )

        self.save_button.clicked.connect(
            self.save_person
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        buttons.addStretch()

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
                "Изображения "
                "(*.jpg *.jpeg *.png *.bmp *.webp)"
            )
        )

        for file_path in files:
            if file_path not in self.photo_paths:
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

        del self.photo_paths[row]

    def set_processing(
        self,
        processing: bool
    ):
        self.save_button.setEnabled(
            not processing
        )

        self.cancel_button.setEnabled(
            not processing
        )

        self.add_photo_button.setEnabled(
            not processing
        )

        self.remove_photo_button.setEnabled(
            not processing
        )

        self.name_input.setEnabled(
            not processing
        )

        self.comment_input.setEnabled(
            not processing
        )

        if processing:
            self.status_label.setText(
                "Загрузка InsightFace и обработка фотографий..."
            )
        else:
            self.status_label.setText(
                ""
            )

        QApplication.processEvents()

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
                "Добавьте хотя бы одну фотографию."
            )

            return

        self.set_processing(
            True
        )

        try:
            if self.person_service is None:
                self.person_service = (
                    PersonService()
                )

            result = (
                self.person_service
                .add_person(
                    name=name,
                    photo_paths=self.photo_paths,
                    comment=comment
                )
            )

        except Exception as exc:
            self.set_processing(
                False
            )

            QMessageBox.critical(
                self,
                "FaceGuard",
                (
                    "Не удалось добавить человека:\n\n"
                    f"{exc}"
                )
            )

            return

        self.set_processing(
            False
        )

        successful_count = len(
            result["successful"]
        )

        failed_count = len(
            result["failed"]
        )

        message = (
            f"Человек добавлен.\n\n"
            f"Embeddings сохранено: {successful_count}"
        )

        if failed_count:
            message += (
                f"\nФотографий пропущено: {failed_count}"
            )

        QMessageBox.information(
            self,
            "FaceGuard",
            message
        )

        self.accept()