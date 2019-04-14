import copy

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QGroupBox, QGridLayout, QLabel, QLineEdit, QComboBox, \
    QPushButton, QTableView, QHeaderView
from pandas import DataFrame
from rx.subjects import Subject

from query_rewriter.io.csv.csv_parser import CSVParser
from query_rewriter.model.Operator import Operator
from query_rewriter.query.relaxer import QueryRelaxer
from ui.PandasTableModel import PandasTableModel


class QueryTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.content_widget = QWidget()
        self.setWidget(self.content_widget)
        self.setWidgetResizable(True)

        self.setLayout(QVBoxLayout(self.content_widget))

    def display(self, path: str):
        self.path = path
        self.csv_parser: CSVParser = CSVParser(path)
        self.data_frame: DataFrame = self.csv_parser.data_frame
        self.header = self.csv_parser.header
        self.separator = self.csv_parser.delimiter
        self.query_subject = Subject()

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

            operatorsComboBox = QComboBox()
            operatorsComboBox.addItem(Operator.EQUAL)
            operatorsComboBox.addItem(Operator.NOT_EQUAL)
            operatorsComboBox.addItem(Operator.BELONGING)
            operatorsComboBox.addItem(Operator.NOT_BELONGING)
            operatorsComboBox.addItem(Operator.GREATER)
            operatorsComboBox.addItem(Operator.GREATER_EQUAL)
            operatorsComboBox.addItem(Operator.LESS)
            operatorsComboBox.addItem(Operator.LESS_EQUAL)

            self.line_combos[h] = operatorsComboBox
            self.line_edits[h] = QLineEdit()
            self.line_edits[h].returnPressed.connect(lambda: self.execute_query())

            operatorsComboBox.currentTextChanged.connect(
                lambda ix, key=h, select=operatorsComboBox: self.combo_changed(select, key))
            operatorsComboBox.setCurrentIndex(1)
            operatorsComboBox.setCurrentIndex(0)

            if row % 2 == 0:
                input_rows_layout.addWidget(self.line_labels[h], row, 0)
                input_rows_layout.addWidget(self.line_combos[h], row, 1)
                input_rows_layout.addWidget(self.line_edits[h], row, 2)
            else:
                input_rows_layout.addWidget(self.line_labels[h], row - 1, 3)
                input_rows_layout.addWidget(self.line_combos[h], row - 1, 4)
                input_rows_layout.addWidget(self.line_edits[h], row - 1, 5)

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

    def execute_query(self):
        print("Clicked")
        operators: dict[str, str] = {}
        values: dict[str, object] = {}
        operator_values: dict[str, (str, object)] = {}

        for header, line in self.line_edits.items():
            print("Header: " + header)
            operators[header] = self.line_combos[header].currentText()
            print("Operator: " + operators[header])

            if operators[header] == Operator.EQUAL \
                    or operators[header] == Operator.NOT_EQUAL \
                    or operators[header] == Operator.GREATER \
                    or operators[header] == Operator.GREATER_EQUAL \
                    or operators[header] == Operator.LESS \
                    or operators[header] == Operator.LESS_EQUAL:
                try:
                    values[header] = int(line.text())
                except ValueError:
                    try:
                        values[header] = float(line.text())
                    except ValueError:
                        values[header] = line.text()
            elif operators[header] == Operator.BELONGING or operators[header] == Operator.NOT_BELONGING:
                values[header] = line.text().replace("[", "").replace("]", "").split(",")

            if header in operators and header in values and values[header]:
                operator_values[header] = (operators[header], values[header])
                print(header + " " + self.line_combos[header].currentText() + " " + line.text())

        print("OriginalQuery: ", operator_values)
        self.query_subject.on_next(operator_values)

        self.original_query_expression = QueryRelaxer.query_operator_values_to_expression(operator_values)
        self.query_label.setText(self.original_query_expression)
        print("OriginalQuery expr: ", self.original_query_expression)
        original_query_result_set: DataFrame = self.csv_parser.data_frame.query(self.original_query_expression)
        print("Original Query Result Set:\n", original_query_result_set)
        self._query_data_model.update_data(original_query_result_set)

    def combo_changed(self, combo: QComboBox, key: str):
        if combo.currentText() == Operator.EQUAL:
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("The exact value of this property")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == Operator.BELONGING:
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A list of values for this property.")
            reg_ex = QRegExp("^\\[([a-zA-Z0-9_\\.-\\s]+(,)?)*\\]$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == Operator.NOT_BELONGING:
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A list of values to exclude for this property.")
            reg_ex = QRegExp("^\\[([a-zA-Z0-9_\\.-\\s]+(,)?)*\\]$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == Operator.GREATER:
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A minimum value of this property (value excluded)")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == Operator.GREATER_EQUAL:
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A minimum value of this property (value included)")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == Operator.LESS:
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A maximum value of this property (value excluded)")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == Operator.LESS_EQUAL:
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A maximum value of this property (value included)")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
        elif combo.currentText() == Operator.NOT_EQUAL:
            self.line_edits[key].setText("")
            self.line_edits[key].setPlaceholderText("A value not admitted for this property")
            reg_ex = QRegExp("^[a-zA-Z0-9_\\.-\\s]+$")
            input_validator = QRegExpValidator(reg_ex, self.line_edits[key])
            self.line_edits[key].setValidator(input_validator)
