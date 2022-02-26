from __future__ import annotations
import json
from PyQt5 import QtCore, QtWidgets, QtGui

# fmt: off

class CustomQTableWidget(QtWidgets.QTableWidget):
    column_visibility_changed = QtCore.pyqtSignal(int, bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header_context_menu = self.set_header_context_menu()

        self.mouse_over_column = (-1)  # -1 means no column is currently being hovered over

        self.setShowGrid(True)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self.show_header_context_menu)
        self.horizontalHeader().setDefaultSectionSize(75)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().sortIndicatorChanged.connect(self.sortItems)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setStretchLastSection(False)
        self.setWordWrap(False)

        font = QtGui.QFont()
        font.setBold(True)
        self.horizontalHeader().setFont(font)

    def insert_row_data(self, data: list[str], user_data=None):
        column_count = self.columnCount()
        assert len(data) == column_count

        row_count = self.rowCount()
        self.insertRow(row_count)
        for column, text in enumerate(data):
            item = QtWidgets.QTableWidgetItem(text)
            if user_data:
                item.setData(QtCore.Qt.UserRole, user_data)
            self.setItem(row_count, column, item)

    def setHorizontalHeaderLabels(self, headers: list[str]):
        """Sets the horizontal header labels. Also updates the heder context menu."""
        self.setColumnCount(len(headers))
        super().setHorizontalHeaderLabels(headers)
        self.header_context_menu = self.set_header_context_menu()

    def toggle_column(self, checked: bool):
        action = self.sender()
        header_text = action.text()

        for column in range(self.columnCount()):
            header = self.horizontalHeaderItem(column)
            if header.text() != header_text:
                continue

            self.setColumnHidden(column, not checked)
            # emit a signal on the column visibility change
            self.column_visibility_changed.emit(column, checked)

    def set_header_context_menu(self) -> QtWidgets.QMenu:
        menu = QtWidgets.QMenu()

        menu.addAction("Hide This Column.", self.toggle_column)
        menu.addSeparator()

        menu.addSeparator()

        for column in range(self.columnCount()):
            action = menu.addAction(self.horizontalHeaderItem(column).text())
            action.setCheckable(True)
            action.setChecked(not self.isColumnHidden(column))
            action.toggled.connect(self.toggle_column)

        menu.addSeparator()

        menu.addAction("Auto Resize This Column", self.resize_current_column)
        menu.addAction("Auto Resize All Columns", self.resize_all_columns)
        return menu

    def show_header_context_menu(self, pos):
        header = self.horizontalHeader()
        self.mouse_over_column = header.logicalIndexAt(pos)
        point = header.mapToGlobal(pos)
        self.header_context_menu.exec_(point)

    def resize_current_column(self):
        current_column = self.mouse_over_column
        self.resizeColumnToContents(current_column)

    def resize_all_columns(self):
        for column in range(self.columnCount()):
            self.resizeColumnToContents(column)

    def get_selected_rows(self) -> list[int]:
        """Returns a list of integers representing the selected rows."""
        selected_items = self.selectedItems()
        selected_rows = []
        for item in selected_items:
            index = item.row()
            if index in selected_rows:
                continue
            selected_rows.append(index)
        return selected_rows

    def copy_selected_rows(self):
        rows = self.selectionModel().selectedRows()
        if not rows:
            return
        rows = sorted(rows)
        row_count = len(rows)
        column_headers = [self.horizontalHeaderItem(i).text() for i in range(self.columnCount())]
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.clear()

        row_data = []  # type: list[list[dict[str, str]]]
        for row in rows:
            data = []  # type: list[dict[str, str]]
            for index, column_header in enumerate(column_headers):
                item = self.item(row.row(), index)
                if item is None:
                    data.append({column_header: ""})
                else:
                    data.append({column_header: item.text()})
            row_data.append(data)

        json_data = json.dumps(row_data, indent=4, sort_keys=True)
        clipboard.setText(json_data)

# fmt: on
