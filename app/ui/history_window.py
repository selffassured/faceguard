from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QLabel,
    QSplitter,
)

from app.database.detection_repository import DetectionRepository


class HistoryWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("FaceGuard — История обнаружений")
        self.resize(1100, 650)

        self.repository = DetectionRepository()

        self.build_ui()
        self.load_history()

    def build_ui(self):
        layout = QVBoxLayout(self)

        buttons = QHBoxLayout()

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_history)

        buttons.addWidget(self.refresh_button)
        buttons.addStretch()

        layout.addLayout(buttons)

        splitter = QSplitter(Qt.Horizontal)

        self.table = QTableWidget()
        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Человек",
                "Время",
                "Similarity",
                "Person ID",
                "Скриншот",
            ]
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.table.verticalHeader().setVisible(False)

        self.table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        self.table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.Stretch
        )

        self.table.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        self.table.horizontalHeader().setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents
        )

        self.table.horizontalHeader().setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

        self.table.horizontalHeader().setSectionResizeMode(
            5,
            QHeaderView.Stretch
        )

        self.table.itemSelectionChanged.connect(
            self.show_selected_screenshot
        )

        splitter.addWidget(self.table)

        self.preview_label = QLabel(
            "Выберите событие"
        )

        self.preview_label.setAlignment(
            Qt.AlignCenter
        )

        self.preview_label.setMinimumWidth(
            350
        )

        self.preview_label.setStyleSheet(
            """
            QLabel {
                background: #111;
                color: #aaa;
                border-radius: 8px;
            }
            """
        )

        splitter.addWidget(
            self.preview_label
        )

        splitter.setSizes(
            [
                750,
                350
            ]
        )

        layout.addWidget(splitter)

    def load_history(self):
        try:
            rows = (
                self.repository
                .get_recent(
                    limit=500
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "FaceGuard",
                f"Не удалось загрузить историю:\n\n{exc}"
            )
            return

        self.table.setRowCount(
            len(rows)
        )

        for row_index, detection in enumerate(rows):
            name = (
                detection["name"]
                if detection["name"]
                else "Неизвестный"
            )

            confidence = detection["confidence"]

            confidence_text = (
                f"{confidence:.4f}"
                if confidence is not None
                else ""
            )

            person_id = (
                detection["person_id"]
                if detection["person_id"] is not None
                else ""
            )

            screenshot_path = (
                detection["screenshot_path"]
                if detection["screenshot_path"]
                else ""
            )

            values = [
                detection["id"],
                name,
                detection["detected_at"],
                confidence_text,
                person_id,
                screenshot_path,
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(
                    str(value)
                )

                if column in (
                    0,
                    3,
                    4
                ):
                    item.setTextAlignment(
                        Qt.AlignCenter
                    )

                self.table.setItem(
                    row_index,
                    column,
                    item
                )

        self.preview_label.clear()
        self.preview_label.setText(
            "Выберите событие"
        )

    def show_selected_screenshot(self):
        row = self.table.currentRow()

        if row < 0:
            return

        item = self.table.item(
            row,
            5
        )

        if item is None:
            return

        path_text = item.text().strip()

        if not path_text:
            self.preview_label.clear()
            self.preview_label.setText(
                "Скриншот отсутствует"
            )
            return

        path = Path(path_text)

        if not path.exists():
            self.preview_label.clear()
            self.preview_label.setText(
                "Файл не найден"
            )
            return

        pixmap = QPixmap(
            str(path)
        )

        if pixmap.isNull():
            self.preview_label.clear()
            self.preview_label.setText(
                "Не удалось открыть изображение"
            )
            return

        pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.preview_label.setPixmap(
            pixmap
        )