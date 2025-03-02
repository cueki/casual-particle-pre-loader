import json
from pathlib import Path
import webbrowser
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidget, QHeaderView, QCheckBox, QHBoxLayout, QWidget, QPushButton


def load_mod_urls():
    # load saved URLs from a file
    urls_file = Path("mod_urls.json")
    if urls_file.exists():
        try:
            with open(urls_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading mod URLs: {e}")
    return {}


class ConflictMatrix(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QTableWidget { border: 1px solid #ccc; }")
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.selections_file = Path("matrix_selections.json")
        self.saved_selections = self.load_selections()
        self.mod_urls = {}
        self.verticalHeader().sectionClicked.connect(self.on_mod_name_clicked)

    def on_mod_name_clicked(self, index):
        mod_name = self.verticalHeaderItem(index).text()
        if mod_name in self.mod_urls and self.mod_urls[mod_name]:
            self.open_mod_url(mod_name)

    def open_mod_url(self, mod_name):
        # open the URL for the mod in the default web browser
        if mod_name in self.mod_urls and self.mod_urls[mod_name]:
            try:
                webbrowser.open(self.mod_urls[mod_name])
            except Exception as e:
                print(f"Error opening URL for {mod_name}: {e}")

    def load_selections(self):
        try:
            if self.selections_file.exists():
                with open(self.selections_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading selections: {e}")
            return {}

    def save_selections(self):
        try:
            selections = {}
            for col in range(1, self.columnCount()):
                particle_file = self.horizontalHeaderItem(col).text()
                for row in range(self.rowCount()):
                    cell_widget = self.cellWidget(row, col)
                    if cell_widget:
                        checkbox = cell_widget.layout().itemAt(0).widget()
                        if checkbox and checkbox.isChecked():
                            mod_name = self.verticalHeaderItem(row).text()
                            selections[particle_file] = mod_name

            with open(self.selections_file, "w") as f:
                json.dump(selections, f)
        except Exception as e:
            print(f"Error saving selections: {e}")

    def update_matrix(self, mods, pcf_files):
        # load mod URLs
        self.mod_urls = load_mod_urls()

        # add one extra column for the Select All button
        self.setColumnCount(len(pcf_files) + 1)
        self.setRowCount(len(mods))

        # headers
        headers = ["Select All"] + pcf_files
        self.setHorizontalHeaderLabels(headers)
        self.setVerticalHeaderLabels(mods)

        # make vertical header interactive
        self.verticalHeader().setStyleSheet("""
            QHeaderView::section { 
                background-color: lightgray; 
                border-style: outset; 
                border-width: 2px; 
                border-color: gray;
                color: black;
            }
            QHeaderView::section:hover { 
                color: blue; 
                text-decoration: underline;
                background-color: #e0e0e0;
            }
        """)

        for row, mod in enumerate(mods):
            # Select All button
            select_all_widget = QWidget()
            select_all_layout = QHBoxLayout(select_all_widget)
            select_all_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            select_all_layout.setContentsMargins(0, 0, 0, 0)

            select_all_button = QPushButton("Select All")
            select_all_button.setFixedWidth(70)
            select_all_layout.addWidget(select_all_button)
            self.setCellWidget(row, 0, select_all_widget)

            # checkboxes for each particle file
            for col, pcf_file in enumerate(pcf_files):
                cell_widget = QWidget()
                layout = QHBoxLayout(cell_widget)
                layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)

                checkbox = self.create_checkbox(row, col + 1)

                # restore saved selection
                if pcf_file in self.saved_selections and self.saved_selections[pcf_file] == mod:
                    checkbox.setChecked(True)

                layout.addWidget(checkbox)
                self.setCellWidget(row, col + 1, cell_widget)

            # connect Select All button
            select_all_button.clicked.connect(lambda checked, r=row: self.select_all_row(r))

    def select_all_row(self, row):
        any_checked = False
        for col in range(1, self.columnCount()):
            cell_widget = self.cellWidget(row, col)
            if cell_widget:
                checkbox = cell_widget.layout().itemAt(0).widget()
                if checkbox and checkbox.isChecked():
                    any_checked = True
                    break

        for col in range(1, self.columnCount()):
            cell_widget = self.cellWidget(row, col)
            if cell_widget:
                checkbox = cell_widget.layout().itemAt(0).widget()
                if checkbox:
                    if not any_checked and checkbox.isEnabled():
                        # only check if no others in this column are checked
                        self.uncheck_column_except(col, row)
                        checkbox.setChecked(True)
                    else:
                        checkbox.setChecked(False)

        self.save_selections()

    def uncheck_column_except(self, col, target_row):
        for row in range(self.rowCount()):
            if row != target_row:
                cell_widget = self.cellWidget(row, col)
                if cell_widget:
                    checkbox = cell_widget.layout().itemAt(0).widget()
                    if checkbox and checkbox.isChecked():
                        checkbox.setChecked(False)
        self.save_selections()

    def create_checkbox(self, row, col):
        checkbox = QCheckBox()

        def on_state_changed(state):
            if state == Qt.CheckState.Checked.value:
                # uncheck all other boxes in this column
                for other_row in range(self.rowCount()):
                    if other_row != row:
                        other_cell = self.cellWidget(other_row, col)
                        if other_cell:
                            other_checkbox = other_cell.layout().itemAt(0).widget()
                            if other_checkbox and other_checkbox.isEnabled():
                                other_checkbox.setChecked(False)
            self.save_selections()

        checkbox.stateChanged.connect(on_state_changed)
        return checkbox

    def get_selected_particles(self):
        selections = {}
        for col in range(1, self.columnCount()):
            particle_file = self.horizontalHeaderItem(col).text()
            for row in range(self.rowCount()):
                cell_widget = self.cellWidget(row, col)
                if cell_widget:
                    checkbox = cell_widget.layout().itemAt(0).widget()
                    if checkbox and checkbox.isChecked():
                        mod_name = self.verticalHeaderItem(row).text()
                        selections[particle_file] = mod_name
                        break
        return selections