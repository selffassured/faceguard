from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.database.people_repository import PeopleRepository
from app.ui.add_person_dialog import AddPersonDialog


class PeopleWindow(QWidget):
    def __init__(
        self,
        parent=None
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "База людей"
        )

        self.resize(
            850,
            500
        )

        self.repository = (
            PeopleRepository()
        )

        self.build_ui()
        self.load_people()

    def build_ui(self):
        layout = QVBoxLayout(
            self
        )

        buttons = QHBoxLayout()

        self.add_button = (
            QPushButton(
                "Добавить человека"
            )
        )

        self.refresh_button = (
            QPushButton(
                "Обновить"
            )
        )

        self.delete_button = (
            QPushButton(
                "Удалить"
            )
        )

        self.add_button.clicked.connect(
            self.add_person
        )

        self.refresh_button.clicked.connect(
            self.load_people
        )

        self.delete_button.clicked.connect(
            self.delete_person
        )

        buttons.addWidget(
            self.add_button
        )

        buttons.addWidget(
            self.refresh_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.delete_button
        )

        layout.addLayout(
            buttons
        )

        self.table = (
            QTableWidget()
        )

        self.table.setColumnCount(
            5
        )

        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Имя",
                "Комментарий",
                "Фото",
                "Добавлен"
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

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(
            self.table
        )

    def load_people(self):
        people = (
            self.repository
            .get_all_people()
        )

        self.table.setRowCount(
            len(people)
        )

        for row_index, person in enumerate(
            people
        ):
            values = [
                person["id"],
                person["name"],
                person["comment"],
                person["photo_count"],
                person["created_at"],
            ]

            for (
                column_index,
                value
            ) in enumerate(values):

                item = QTableWidgetItem(
                    str(value)
                )

                if column_index in (
                    0,
                    3
                ):
                    item.setTextAlignment(
                        Qt.AlignCenter
                    )

                self.table.setItem(
                    row_index,
                    column_index,
                    item
                )

    def add_person(self):
        dialog = AddPersonDialog(
            self
        )

        if dialog.exec():
            self.load_people()

    def delete_person(self):
        row = (
            self.table.currentRow()
        )

        if row < 0:
            QMessageBox.warning(
                self,
                "FaceGuard",
                "Выберите человека."
            )
            return

        person_id_item = (
            self.table.item(
                row,
                0
            )
        )

        name_item = (
            self.table.item(
                row,
                1
            )
        )

        person_id = int(
            person_id_item.text()
        )

        name = (
            name_item.text()
        )

        result = QMessageBox.question(
            self,
            "Удаление",
            (
                f"Удалить человека "
                f"«{name}» из базы?"
            ),
            QMessageBox.Yes
            | QMessageBox.No
        )

        if result != QMessageBox.Yes:
            return

        self.repository.delete_person(
            person_id
        )

        self.load_people()