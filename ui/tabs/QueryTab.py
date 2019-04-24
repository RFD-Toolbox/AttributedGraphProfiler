import copy

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QGroupBox, QGridLayout, QLabel, QLineEdit, QComboBox, \
    QPushButton, QTableView, QHeaderView
from pandas import DataFrame
import numpy as np
from rx.subjects import Subject

from query_rewriter.io.csv.csv_parser import CSVParser
from query_rewriter.model.Operator import Operator
from query_rewriter.model.Query import Query
from ui.PandasTableModel import PandasTableModel


class QueryTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.query_subject = Subject()

        self.content_widget = QWidget()
        self.setWidget(self.content_widget)
        self.setWidgetResizable(True)

        self.setLayout(QVBoxLayout(self.content_widget))

    def display(self, path: str):
        self.path = path
        self.csv_parser: CSVParser = CSVParser(path)
        self.data_frame: DataFrame = self.csv_parser.data_frame
        self.column_types: dict = self.data_frame.dtypes.to_dict()
        self.header = self.csv_parser.header
        self.separator = self.csv_parser.delimiter

        groupBox = QGroupBox()
        input_rows_layout = QGridLayout()
        groupBox.setLayout(input_rows_layout)

        self.line_labels: dict[str, QLabel] = {}
        self.query_operators: dict[str, QComboBox] = {}
        self.query_items: dict[str, QLineEdit] = {}

        rows = self.header.__len__()

        for row in range(0, rows):
            h: str = self.header[row]

            self.line_labels[h] = QLabel(h.title().replace("_", " "))

            operatorsComboBox = QComboBox()
            operatorsComboBox.addItem(Operator.EQUAL)
            operatorsComboBox.addItem(Operator.NOT_EQUAL)
            operatorsComboBox.addItem(Operator.BELONGING)
            operatorsComboBox.addItem(Operator.NOT_BELONGING)

            # TODO check for column type
            column_type = self.column_types[self.header[row]]
            print("Column " + self.header[row] + " is of Type:")
            print(column_type)

            if column_type == np.int64 or column_type == np.float64:
                operatorsComboBox.addItem(Operator.GREATER)
                operatorsComboBox.addItem(Operator.GREATER_EQUAL)
                operatorsComboBox.addItem(Operator.LESS)
                operatorsComboBox.addItem(Operator.LESS_EQUAL)

            self.query_operators[h] = operatorsComboBox
            self.query_items[h] = QLineEdit()
            self.query_items[h].returnPressed.connect(lambda: self.execute_query())

            operatorsComboBox.currentTextChanged.connect(
                lambda ix, key=h, select=operatorsComboBox: self.combo_changed(select, key))
            operatorsComboBox.setCurrentIndex(1)
            operatorsComboBox.setCurrentIndex(0)

            if row % 2 == 0:
                input_rows_layout.addWidget(self.line_labels[h], row, 0)
                input_rows_layout.addWidget(self.query_operators[h], row, 1)
                input_rows_layout.addWidget(self.query_items[h], row, 2)
            else:
                input_rows_layout.addWidget(self.line_labels[h], row - 1, 3)
                input_rows_layout.addWidget(self.query_operators[h], row - 1, 4)
                input_rows_layout.addWidget(self.query_items[h], row - 1, 5)

        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().deleteLater()

        self.layout().addWidget(groupBox)

        box2 = QGroupBox()
        grid_layout = QGridLayout()
        box2.setLayout(grid_layout)

        query_button = QPushButton("Query")
        width = query_button.fontMetrics().boundingRect(query_button.text()).width() + 20
        query_button.setMaximumWidth(width)
        query_button.setAutoDefault(True)
        grid_layout.addWidget(query_button, 0, 0, 1, 1)
        query_button.clicked.connect(lambda: self.execute_query())

        self.query_label = QLabel("", box2)
        grid_layout.addWidget(self.query_label, 0, 1, 1, 4)

        self.layout().addWidget(box2)

        self._query_data_frame = copy.deepcopy(self.data_frame)

        table = QTableView()
        self._query_data_model: PandasTableModel = PandasTableModel(self._query_data_frame, self)
        table.setModel(self._query_data_model)
        table.setSortingEnabled(True)
        table.resizeRowsToContents()
        table.setMinimumHeight(200)
        # ui->tableView->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # full width table

        layout = QVBoxLayout()
        table.setLayout(layout)

        self.layout().addWidget(table)

    def build_query(self) -> Query:
        query: Query = Query()

        for column, line in self.query_items.items():
            # print("Column: " + column)

            operator = self.query_operators[column].currentText()
            # print("Operator: " + operator)

            if operator == Operator.EQUAL \
                    or operator == Operator.NOT_EQUAL \
                    or operator == Operator.GREATER \
                    or operator == Operator.GREATER_EQUAL \
                    or operator == Operator.LESS \
                    or operator == Operator.LESS_EQUAL:
                try:
                    value = int(line.text())
                except ValueError:
                    try:
                        value = float(line.text())
                    except ValueError:
                        value = line.text()
            elif operator == Operator.BELONGING or operator == Operator.NOT_BELONGING:
                print("Line text list:")
                print(line.text())
                try:
                    value: list = [int(item) for item in line.text().replace('[', '').replace(']', '').split(',')]
                except ValueError:
                    try:
                        value: list = [float(item) for item in line.text().replace('[', '').replace(']', '').split(',')]
                    except ValueError:
                        value: list = [str(item) for item in line.text().replace('[', '').replace(']', '').split(',')]

            if operator and value:
                query.add_operator_value(column, operator, value)

        return query

    def execute_query(self):
        # print("Clicked")

        query: Query = self.build_query()
        self.query_subject.on_next(query)
        self.original_query_expression = query.to_expression()
        print("Original Query expression:")
        print(self.original_query_expression)

        # self.original_query_expression = QueryRelaxer.query_operator_values_to_expression(operator_values)
        self.query_label.setText(self.original_query_expression)
        # print("OriginalQuery expr: ", self.original_query_expression)
        original_query_result_set: DataFrame = self.csv_parser.data_frame.query(self.original_query_expression)
        # print("Original Query Result Set:\n", original_query_result_set)
        self._query_data_model.update_data(original_query_result_set)

    def combo_changed(self, combo: QComboBox, key: str):
        if combo.currentText() == Operator.EQUAL:
            self.query_items[key].setText("")
            self.query_items[key].setPlaceholderText("The exact value of this property")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)
        elif combo.currentText() == Operator.BELONGING:
            self.query_items[key].setText("")
            self.query_items[key].setPlaceholderText("A list of values for this property.")
            reg_ex = QRegExp("^\\[([a-zA-Z0-9_\\.-\\s]+(,)?)*\\]$")
            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)
        elif combo.currentText() == Operator.NOT_BELONGING:
            self.query_items[key].setText("")
            self.query_items[key].setPlaceholderText("A list of values to exclude for this property.")
            reg_ex = QRegExp("^\\[([a-zA-Z0-9_\\.-\\s]+(,)?)*\\]$")
            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)
        elif combo.currentText() == Operator.GREATER:
            self.query_items[key].setText("")
            self.query_items[key].setPlaceholderText("A minimum value of this property (value excluded)")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)
        elif combo.currentText() == Operator.GREATER_EQUAL:
            self.query_items[key].setText("")
            self.query_items[key].setPlaceholderText("A minimum value of this property (value included)")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)
        elif combo.currentText() == Operator.LESS:
            self.query_items[key].setText("")
            self.query_items[key].setPlaceholderText("A maximum value of this property (value excluded)")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)
        elif combo.currentText() == Operator.LESS_EQUAL:
            self.query_items[key].setText("")
            self.query_items[key].setPlaceholderText("A maximum value of this property (value included)")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)
        elif combo.currentText() == Operator.NOT_EQUAL:
            self.query_items[key].setText("")
            self.query_items[key].setPlaceholderText("A value not admitted for this property")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)

    def get_initial_query_subject(self):
        return self.query_subject
