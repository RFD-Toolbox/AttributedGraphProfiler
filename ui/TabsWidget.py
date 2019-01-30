import csv
import typing
from query_rewriter.io.csv.csv_parser import CSVParser

from PyQt5.QtWidgets import QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QFormLayout, QLineEdit, \
    QGroupBox, QLabel, QPushButton, QHBoxLayout, QGridLayout, QComboBox

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
        with open(path) as csv_file:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(csv_file.readline())
            csv_file.seek(0)
            has_header = sniffer.has_header(csv_file.readline())
            csv_file.seek(0)
            rows = sum(1 for line in csv_file)
            csv_file.seek(0)
            reader = csv.reader(csv_file, dialect)
            columns = len(next(reader))  # Read first line and count columns
            csv_file.seek(0)

            print("Delimiter: " + dialect.delimiter)
            print("Has Header: " + str(has_header))
            print("Rows: " + str(rows))
            print("Columns: " + str(columns))

            table = QTableWidget(rows, columns)
            table.setEnabled(True)
            table.setRowCount(rows - 1)  # excluding the header from the count
            table.setColumnCount(columns)

            header = next(reader)
            print("Header: ")
            print(header)

            # write the header
            for col in range(0, columns):
                table.setHorizontalHeaderItem(col, QTableWidgetItem(header[col]))

            # write the rows
            data_row = 0
            for row in reader:
                for col in range(0, columns):
                    table.setItem(data_row, col, QTableWidgetItem(row[col]))
                data_row += 1

            table.setSortingEnabled(True)

            layout = QVBoxLayout()
            table.setLayout(layout)

            tab_layout = self.dataset_tab.layout()

            for i in reversed(range(tab_layout.count())):
                tab_layout.itemAt(i).widget().deleteLater()

            tab_layout.addWidget(table)

    def init_query_tab(self, path: str):
        self.csv_parser = CSVParser(path)
        self.header = self.csv_parser.header

        groupBox = QGroupBox()
        gridLayout = QGridLayout()
        groupBox.setLayout(gridLayout)

        self.line_labels: dict[str, QLabel] = {}
        self.line_combos: dict[str, QComboBox] = {}
        self.line_edits: dict[str, QLineEdit] = {}

        rows = self.header.__len__()
        columns = 3

        for row in range(0, rows):
            h = self.header[row]

            self.line_labels[h] = QLabel(h)

            combo = QComboBox()
            combo.addItem("=")
            combo.addItem("~")
            combo.addItem("∈")
            combo.addItem(">")
            combo.addItem(">=")
            combo.addItem("<")
            combo.addItem("<=")
            combo.addItem("!=")

            self.line_combos[h] = combo
            self.line_edits[h] = QLineEdit()

            combo.currentTextChanged.connect(lambda ix, key=h, select=combo: self.combo_changed(select, key))
            combo.setCurrentIndex(1)
            combo.setCurrentIndex(0)

            gridLayout.addWidget(self.line_labels[h], row, 0)
            gridLayout.addWidget(self.line_combos[h], row, 1)
            gridLayout.addWidget(self.line_edits[h], row, 2)

        tab_layout = self.query_tab.layout();
        for i in reversed(range(tab_layout.count())):
            tab_layout.itemAt(i).widget().deleteLater()

        tab_layout.addWidget(groupBox)

        box2 = QGroupBox()
        box_layout = QVBoxLayout()
        box2.setLayout(box_layout)

        query_button = QPushButton("Query", box2)
        query_button.clicked.connect(self.query_click)

        tab_layout.addWidget(box2)

    def query_click(self):
        print("Clicked")
        operators: dict[str, str] = {}
        values: dict[str, str] = {}

        for header, line in self.line_edits.items():
            operators[header] = self.line_combos[header]
            values[header] = line.text()
            print(header + " " + self.line_combos[header].currentText() + " " + line.text())

        print("OriginalQuery: ", values)
        original_query_expression = QueryRelaxer.query_dict_to_expr(values)
        print("OriginalQuery expr: ", original_query_expression)
        original_query_result_set = self.csv_parser.data_frame.query(original_query_expression)
        print("Original Query Result Set:\n", original_query_result_set)

    def combo_changed(self, combo: QComboBox, key: str):
        print("Combo Changed: " + key)
        print("Combo Changed: " + combo.currentText())

        if combo.currentText() == "=":
            self.line_edits[key].setPlaceholderText("The exact value of this property")
        elif combo.currentText() == "~":
            self.line_edits[key].setPlaceholderText("A substring of this property")
        elif combo.currentText() == "∈":
            self.line_edits[key].setPlaceholderText("A set of values for this property. e.g. {Value_1, Value_2, Value_3} or [Value_min, Value_MAX]")
        elif combo.currentText() == ">":
            self.line_edits[key].setPlaceholderText("A minimum value of this property (value excluded)")
        elif combo.currentText() == ">=":
            self.line_edits[key].setPlaceholderText("A minimum value of this property (value included)")
        elif combo.currentText() == "<":
            self.line_edits[key].setPlaceholderText("A maximum value of this property (value excluded)")
        elif combo.currentText() == "<=":
            self.line_edits[key].setPlaceholderText("A maximum value of this property (value included)")
        elif combo.currentText() == "!=":
            self.line_edits[key].setPlaceholderText("A value not admitted for this property")
