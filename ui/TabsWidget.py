import typing
import copy
from PyQt5.QtCore import QAbstractTableModel, Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from pandas import DataFrame

from query_rewriter.io.csv.csv_parser import CSVParser
from ui.PandasTableModel import PandasTableModel

from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLineEdit, \
    QGroupBox, QLabel, QPushButton, QGridLayout, QComboBox, QTableView, QScrollArea, QHBoxLayout

from query_rewriter.query.relaxer import QueryRelaxer


class TabsWidget(QTabWidget):
    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        self.dataset_tab = QWidget()
        self.dataset_tab.setLayout(QVBoxLayout())

        self.query_tab = QWidget()
        self.query_tab.setLayout(QVBoxLayout())

        self.relax_tab = QWidget()
        self.relax_tab.setLayout(QVBoxLayout())

        self.addTab(self.dataset_tab, "Dataset")
        self.addTab(self.query_tab, "Query")
        self.addTab(self.relax_tab, "RFDs")

    def init_dataset_tab(self, path: str):
        csv_parser: CSVParser = CSVParser(path)
        self.data_frame: DataFrame = csv_parser.data_frame
        table = QTableView()
        pandas_model: QAbstractTableModel = PandasTableModel(self.data_frame, self.dataset_tab)
        table.setModel(pandas_model)
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        print("DTypes:")
        print(self.data_frame.dtypes)

        layout = QVBoxLayout()
        table.setLayout(layout)

        tab_layout = self.dataset_tab.layout()

        for i in reversed(range(tab_layout.count())):
            tab_layout.itemAt(i).widget().deleteLater()

        tab_layout.addWidget(table)

    def init_query_tab(self, path: str):
        self.csv_parser: CSVParser = CSVParser(path)
        self.header = self.csv_parser.header

        groupBox = QGroupBox()
        input_rows_layout = QGridLayout()
        groupBox.setLayout(input_rows_layout)

        self.line_labels: dict[str, QLabel] = {}
        self.line_combos: dict[str, QComboBox] = {}
        self.line_edits: dict[str, QLineEdit] = {}

        rows = self.header.__len__()

        for row in range(0, rows):
            h = self.header[row]

            self.line_labels[h] = QLabel(h)

            combo = QComboBox()
            combo.addItem("=")
            combo.addItem("~")
            combo.addItem("!=")
            combo.addItem("∈")
            combo.addItem("∉")
            combo.addItem(">")
            combo.addItem(">=")
            combo.addItem("<")
            combo.addItem("<=")

            self.line_combos[h] = combo
            self.line_edits[h] = QLineEdit()

            combo.currentTextChanged.connect(lambda ix, key=h, select=combo: self.combo_changed(select, key))
            combo.setCurrentIndex(1)
            combo.setCurrentIndex(0)

            if row % 2 == 0:
                input_rows_layout.addWidget(self.line_labels[h], row, 0)
                input_rows_layout.addWidget(self.line_combos[h], row, 1)
                input_rows_layout.addWidget(self.line_edits[h], row, 2)
            else:
                input_rows_layout.addWidget(self.line_labels[h], row - 1, 3)
                input_rows_layout.addWidget(self.line_combos[h], row - 1, 4)
                input_rows_layout.addWidget(self.line_edits[h], row - 1, 5)

        tab_layout = self.query_tab.layout()
        for i in reversed(range(tab_layout.count())):
            tab_layout.itemAt(i).widget().deleteLater()

        tab_layout.addWidget(groupBox)

        box2 = QGroupBox()
        grid_layout = QGridLayout()
        box2.setLayout(grid_layout)

        query_button = QPushButton("Query")
        grid_layout.addWidget(query_button, 0, 0, 1, 1)
        query_button.clicked.connect(lambda checked: self.query_click())

        self.query_label = QLabel("", box2)
        grid_layout.addWidget(self.query_label, 0, 1, 1, 4)

        tab_layout.addWidget(box2)

        self._query_data_frame = copy.deepcopy(self.data_frame)

        table = QTableView()
        self._query_data_model: PandasTableModel = PandasTableModel(self._query_data_frame, self.query_tab)
        table.setModel(self._query_data_model)
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        layout = QVBoxLayout()
        table.setLayout(layout)

        tab_layout = self.query_tab.layout()

        tab_layout.addWidget(table)

    def query_click(self):
        print("Clicked")
        operators: dict[str, str] = {}
        values: dict[str, object] = {}
        operator_values: dict[str, (str, object)] = {}

        for header, line in self.line_edits.items():
            print("Header: " + header)
            operators[header] = self.line_combos[header].currentText()
            print("Operator: " + operators[header])

            if operators[header] == "=" or operators[header] == "!=" or operators[header] == ">" \
                    or operators[header] == ">=" or operators[header] == "<" or operators[header] == "<=":
                try:
                    values[header] = int(line.text())
                except ValueError:
                    try:
                        values[header] = float(line.text())
                    except ValueError:
                        values[header] = line.text()
            elif operators[header] == "~":
                values[header] = line.text()
            elif operators[header] == "∈" or operators[header] == "∉":
                values[header] = line.text().replace("[", "").replace("]", "").split(",")

            if header in operators and header in values and values[header]:
                operator_values[header] = (operators[header], values[header])
                print(header + " " + self.line_combos[header].currentText() + " " + line.text())

        print("OriginalQuery: ", operator_values)
        original_query_expression = QueryRelaxer.query_operator_values_to_expression(operator_values)
        self.query_label.setText(original_query_expression)
        print("OriginalQuery expr: ", original_query_expression)
        original_query_result_set: DataFrame = self.csv_parser.data_frame.query(original_query_expression)
        print("Original Query Result Set:\n", original_query_result_set)
        self._query_data_model.update_data(original_query_result_set)

    def combo_changed(self, combo: QComboBox, key: str):
        if combo.currentText() == "=":
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("The exact value of this property")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == "~":
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A substring of this property")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == "∈":
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A list of values for this property.")
            reg_ex = QRegExp("^\\[([a-zA-Z0-9_\\.-\\s]+(,)?)*\\]$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == "∉":
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A list of values to exclude for this property.")
            reg_ex = QRegExp("^\\[([a-zA-Z0-9_\\.-\\s]+(,)?)*\\]$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == ">":
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A minimum value of this property (value excluded)")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == ">=":
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A minimum value of this property (value included)")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == "<":
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A maximum value of this property (value excluded)")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == "<=":
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A maximum value of this property (value included)")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == "!=":
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A value not admitted for this property")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
