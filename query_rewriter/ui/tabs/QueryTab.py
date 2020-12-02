from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QGroupBox, QGridLayout, QLabel, QLineEdit, QComboBox, \
    QPushButton
from pandas import DataFrame
import numpy as np
from numpy import dtype
from rx.subjects import Subject

from query_rewriter.io.csv.csv_parser import CSVParser
from query_rewriter.model.Operator import Operator
from query_rewriter.model.Query import Query
from query_rewriter.model.RegularExpression import RegularExpression


class QueryTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

    def display(self, path: str):
        self.query_subject = Subject()

        self.path = path
        self.csv_parser: CSVParser = CSVParser(self.path)
        self.data_frame: DataFrame = self.csv_parser.data_frame
        self.column_types: dict = self.data_frame.dtypes.to_dict()
        self.header = self.csv_parser.header
        self.separator = self.csv_parser.delimiter

        container_vertical_layout = QVBoxLayout()
        container_group_box = QGroupBox()
        container_group_box.setLayout(container_vertical_layout)
        self.setWidget(container_group_box)
        self.setWidgetResizable(True)

        input_grid_layout = QGridLayout()
        input_group_box = QGroupBox()
        input_group_box.setLayout(input_grid_layout)

        container_vertical_layout.addWidget(input_group_box)

        self.line_labels: dict[str, QLabel] = {}
        self.query_operators: dict[str, QComboBox] = {}
        self.query_items: dict[str, QLineEdit] = {}

        rows = self.header.__len__()

        for i in reversed(range(input_group_box.layout().count())):
            input_group_box.layout().itemAt(i).widget().deleteLater()

        for row in range(0, rows):
            h: str = self.header[row]

            self.line_labels[h] = QLabel(h.title().replace("_", " "))
            self.line_labels[h].setMinimumHeight(30)

            operatorsComboBox = QComboBox()
            operatorsComboBox.addItem(Operator.EQUAL)
            operatorsComboBox.addItem(Operator.NOT_EQUAL)
            operatorsComboBox.addItem(Operator.BELONGING)
            operatorsComboBox.addItem(Operator.NOT_BELONGING)

            column_type: dtype = self.column_types[self.header[row]]

            if column_type == np.int64 or column_type == np.float64:
                operatorsComboBox.addItem(Operator.GREATER)
                operatorsComboBox.addItem(Operator.GREATER_EQUAL)
                operatorsComboBox.addItem(Operator.LESS)
                operatorsComboBox.addItem(Operator.LESS_EQUAL)

            self.query_operators[h] = operatorsComboBox
            self.query_operators[h].setMinimumHeight(30)
            self.query_items[h] = QLineEdit()
            self.query_items[h].setMinimumHeight(30)
            self.query_items[h].returnPressed.connect(lambda: self.execute_query())

            operatorsComboBox.currentTextChanged.connect(
                lambda ix, key=h, select=operatorsComboBox: self.combo_changed(select, key, column_type))
            operatorsComboBox.setCurrentIndex(1)
            operatorsComboBox.setCurrentIndex(0)

            if row % 2 == 0:
                input_grid_layout.addWidget(self.line_labels[h], row, 0)
                input_grid_layout.addWidget(self.query_operators[h], row, 1)
                input_grid_layout.addWidget(self.query_items[h], row, 2)
            else:
                input_grid_layout.addWidget(self.line_labels[h], row - 1, 3)
                input_grid_layout.addWidget(self.query_operators[h], row - 1, 4)
                input_grid_layout.addWidget(self.query_items[h], row - 1, 5)

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
        self.query_label.setWordWrap(True)
        self.query_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.query_label.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Cursive))
        grid_layout.addWidget(self.query_label, 0, 1, 1, 4)

        container_vertical_layout.addWidget(box2)

    def build_query(self) -> Query:
        query: Query = Query()

        for column, line in self.query_items.items():
            operator = self.query_operators[column].currentText()

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
                try:
                    value: list = [int(item) for item in line.text().replace('[', '').replace(']', '').split(',')]
                except ValueError:
                    try:
                        value: list = [float(item) for item in line.text().replace('[', '').replace(']', '').split(',')]
                    except ValueError:
                        value: list = [str(item) for item in line.text().replace('[', '').replace(']', '').split(',')]

            valid_input: bool = line.hasAcceptableInput()

            if valid_input and operator and value:
                query.add_operator_value(column, operator, value)

        return query

    def execute_query(self):
        query: Query = self.build_query()
        self.query_subject.on_next(query)
        self.original_query_expression = query.to_expression()

        self.query_label.setText(query.to_rich_text_expression())
        self.query_label.setTextFormat(Qt.RichText)

    def combo_changed(self, combo: QComboBox, key: str, column_type: dtype):
        if combo.currentText() == Operator.EQUAL:
            self.query_items[key].setPlaceholderText("The exact value of this property ({})".format(column_type))

            if column_type == np.int64:
                reg_ex = RegularExpression.INTEGER
            elif column_type == np.float64:
                reg_ex = RegularExpression.DECIMAL
            elif column_type == np.object or column_type == np.unicode:
                reg_ex = RegularExpression.STRING
            else:
                reg_ex = RegularExpression.ANYTHING

            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)

            if not self.query_items[key].hasAcceptableInput():
                self.query_items[key].setText("")

        elif combo.currentText() == Operator.BELONGING:
            self.query_items[key].setPlaceholderText("A list of values for this property ({})".format(column_type))

            if column_type == np.int64:
                reg_ex = RegularExpression.INTEGER_LIST
            elif column_type == np.float64:
                reg_ex = RegularExpression.DECIMAL_LIST
            elif column_type == np.object or column_type == np.unicode:
                reg_ex = RegularExpression.STRING_LIST
            else:
                reg_ex = RegularExpression.ANYTHING_LIST

            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)

            if not self.query_items[key].hasAcceptableInput():
                self.query_items[key].setText("")
        elif combo.currentText() == Operator.NOT_BELONGING:
            self.query_items[key].setPlaceholderText(
                "A list of values to exclude for this property ({})".format(column_type))

            if column_type == np.int64:
                reg_ex = RegularExpression.INTEGER_LIST
            elif column_type == np.float64:
                reg_ex = RegularExpression.DECIMAL_LIST
            elif column_type == np.object or column_type == np.unicode:
                reg_ex = RegularExpression.STRING_LIST
            else:
                reg_ex = RegularExpression.ANYTHING_LIST

            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)

            if not self.query_items[key].hasAcceptableInput():
                self.query_items[key].setText("")
        elif combo.currentText() == Operator.GREATER:
            self.query_items[key].setPlaceholderText(
                "A minimum value of this property (value excluded) ({})".format(column_type))

            if column_type == np.int64:
                reg_ex = RegularExpression.INTEGER
            elif column_type == np.float64:
                reg_ex = RegularExpression.DECIMAL
            else:
                reg_ex = RegularExpression.ANYTHING

            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)

            if not self.query_items[key].hasAcceptableInput():
                self.query_items[key].setText("")
        elif combo.currentText() == Operator.GREATER_EQUAL:
            self.query_items[key].setPlaceholderText(
                "A minimum value of this property (value included) ({})".format(column_type))

            if column_type == np.int64:
                reg_ex = RegularExpression.INTEGER
            elif column_type == np.float64:
                reg_ex = RegularExpression.DECIMAL
            else:
                reg_ex = RegularExpression.ANYTHING

            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)

            if not self.query_items[key].hasAcceptableInput():
                self.query_items[key].setText("")
        elif combo.currentText() == Operator.LESS:
            self.query_items[key].setPlaceholderText(
                "A maximum value of this property (value excluded) ({})".format(column_type))

            if column_type == np.int64:
                reg_ex = RegularExpression.INTEGER
            elif column_type == np.float64:
                reg_ex = RegularExpression.DECIMAL
            else:
                reg_ex = RegularExpression.ANYTHING

            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)

            if not self.query_items[key].hasAcceptableInput():
                self.query_items[key].setText("")
        elif combo.currentText() == Operator.LESS_EQUAL:
            self.query_items[key].setPlaceholderText(
                "A maximum value of this property (value included) ({})".format(column_type))

            if column_type == np.int64:
                reg_ex = RegularExpression.INTEGER
            elif column_type == np.float64:
                reg_ex = RegularExpression.DECIMAL
            else:
                reg_ex = RegularExpression.ANYTHING

            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)

            if not self.query_items[key].hasAcceptableInput():
                self.query_items[key].setText("")
        elif combo.currentText() == Operator.NOT_EQUAL:
            self.query_items[key].setPlaceholderText("A value not admitted for this property ({})".format(column_type))

            if column_type == np.int64:
                reg_ex = RegularExpression.INTEGER
            elif column_type == np.float64:
                reg_ex = RegularExpression.DECIMAL
            else:
                reg_ex = RegularExpression.ANYTHING

            input_validator = QRegExpValidator(reg_ex, self.query_items[key])
            self.query_items[key].setValidator(input_validator)

            if not self.query_items[key].hasAcceptableInput():
                self.query_items[key].setText("")

    def get_initial_query_subject(self):
        return self.query_subject
