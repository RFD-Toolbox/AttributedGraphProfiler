import typing
import copy
from PyQt5.QtCore import QAbstractTableModel, Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from pandas import DataFrame

from dominance.dominance_tools import RFDDiscovery
from loader.distance_mtr import DiffMatrix
from query_rewriter.io.csv.csv_parser import CSVParser
from query_rewriter.io.rfd.rfd_extractor import RFDExtractor
from query_rewriter.utils.Transformer import Transformer
from ui.PandasTableModel import PandasTableModel

from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLineEdit, \
    QGroupBox, QLabel, QPushButton, QGridLayout, QComboBox, QTableView, QScrollArea, QHBoxLayout, QListWidget

from query_rewriter.query.relaxer import QueryRelaxer


class TabsWidget(QTabWidget):
    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)

        # DataSet Tab
        self.dataset_tab = QScrollArea()
        self.dataset_tab_content_widget = QWidget()
        self.dataset_tab.setWidget(self.dataset_tab_content_widget)
        self.dataset_tab.setWidgetResizable(True)
        self.dataset_tab_layout = QVBoxLayout(self.dataset_tab_content_widget)

        # Query Tab
        self.query_tab = QScrollArea()
        self.query_tab_content_widget = QWidget()
        self.query_tab.setWidget(self.query_tab_content_widget)
        self.query_tab.setWidgetResizable(True)
        self.query_tab_layout = QVBoxLayout(self.query_tab_content_widget)

        # RFDs Tab
        self.rfds_tab = QScrollArea()
        self.rfds_tab_content_widget = QWidget()
        self.rfds_tab.setWidget(self.rfds_tab_content_widget)
        self.rfds_tab.setWidgetResizable(True)
        self.rfds_tab_layout = QVBoxLayout(self.rfds_tab_content_widget)

        self.addTab(self.dataset_tab, "Dataset")
        self.addTab(self.query_tab, "Query")
        self.addTab(self.rfds_tab, "RFDs")

        self.rfds: list = []

    def init_dataset_tab(self, path: str):
        self.path = path
        csv_parser: CSVParser = CSVParser(path)
        self.data_frame: DataFrame = csv_parser.data_frame
        (self.rows_count, self.columns_count) = self.data_frame.shape
        self.header = csv_parser.header
        table = QTableView()
        pandas_model: QAbstractTableModel = PandasTableModel(self.data_frame, self.dataset_tab)
        table.setModel(pandas_model)
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        print("DTypes:")
        print(self.data_frame.dtypes)

        for i in reversed(range(self.dataset_tab_layout.count())):
            self.dataset_tab_layout.itemAt(i).widget().deleteLater()

        self.dataset_tab_layout.addWidget(table)

    def init_query_tab(self, path: str):
        self.path = path
        self.csv_parser: CSVParser = CSVParser(path)
        self.header = self.csv_parser.header
        self.separator = self.csv_parser.delimiter

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
            self.line_edits[h].returnPressed.connect(lambda: self.query_click())

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

        for i in reversed(range(self.query_tab_layout.count())):
            self.query_tab_layout.itemAt(i).widget().deleteLater()

        self.query_tab_layout.addWidget(groupBox)

        box2 = QGroupBox()
        grid_layout = QGridLayout()
        box2.setLayout(grid_layout)

        query_button = QPushButton("Query")
        width = query_button.fontMetrics().boundingRect(query_button.text()).width() + 20
        query_button.setMaximumWidth(width)
        query_button.setAutoDefault(True)
        grid_layout.addWidget(query_button, 0, 0, 1, 1)
        query_button.clicked.connect(lambda: self.query_click())

        self.query_label = QLabel("", box2)
        grid_layout.addWidget(self.query_label, 0, 1, 1, 4)

        self.query_tab_layout.addWidget(box2)

        self._query_data_frame = copy.deepcopy(self.data_frame)

        table = QTableView()
        self._query_data_model: PandasTableModel = PandasTableModel(self._query_data_frame, self.query_tab)
        table.setModel(self._query_data_model)
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.setMinimumHeight(200)

        layout = QVBoxLayout()
        table.setLayout(layout)

        self.query_tab_layout.addWidget(table)

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
        self.original_query_expression = QueryRelaxer.query_operator_values_to_expression(operator_values)
        self.query_label.setText(self.original_query_expression)
        print("OriginalQuery expr: ", self.original_query_expression)
        original_query_result_set: DataFrame = self.csv_parser.data_frame.query(self.original_query_expression)
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

    def init_rfds_tab(self, path: str):
        for i in reversed(range(self.rfds_tab_layout.count())):
            self.rfds_tab_layout.itemAt(i).widget().deleteLater()

        self.rfds_list_wrapper = QGroupBox()
        self.rfds_list_wrapper_layout = QVBoxLayout(self.rfds_list_wrapper)

        self.path = path
        group = QGroupBox()
        buttons_horizontal_layout = QHBoxLayout()
        buttons_horizontal_layout.setAlignment(Qt.AlignLeft)
        buttons_horizontal_layout.setAlignment(Qt.AlignTop)
        group.setLayout(buttons_horizontal_layout)

        discover_rfds_button = QPushButton("Discover RFDs")
        width = discover_rfds_button.fontMetrics().boundingRect(discover_rfds_button.text()).width() + 20
        discover_rfds_button.setMaximumWidth(width)
        discover_rfds_button.clicked.connect(lambda: self.discover_rfds())

        load_rfds_button = QPushButton("Load RFDs")
        width = load_rfds_button.fontMetrics().boundingRect(load_rfds_button.text()).width() + 20
        load_rfds_button.setMaximumWidth(width)
        load_rfds_button.clicked.connect(lambda: self.load_rfds())

        buttons_horizontal_layout.addWidget(discover_rfds_button)
        buttons_horizontal_layout.addWidget(load_rfds_button)

        self.rfds_tab_layout.addWidget(group)

    def load_rfds(self):
        print("Loading RFDs")

    def discover_rfds(self):
        # Cleaning
        for i in reversed(range(self.rfds_list_wrapper_layout.count())):
            self.rfds_list_wrapper_layout.itemAt(i).widget().deleteLater()

        self.rfds = []
        print("Discovering RFDs")
        print("Header: " + str(self.header))

        columns_count = self.columns_count
        print("Columns count: " + str(self.columns_count))
        print("Rows count: " + str(self.rows_count))

        print("Separator: " + str(self.separator))

        hand_sides_specifications = RFDExtractor.extract_hss(columns_count)
        print("Hand Sides Specifications: ")
        print(hand_sides_specifications)

        self.distance_matrix = DiffMatrix(path=self.path, sep=self.separator)
        self.distance_df: DataFrame = self.distance_matrix.distance_df

        print("Distance Matrix: ")
        print(self.distance_df)

        self.rfd_data_frame_list: list[DataFrame] = list()

        for combination in hand_sides_specifications:
            '''
            combination is a dictionary containing rhs & lhs as keys,
            and a list of the corresponding indexes as valus.
            For example, given a set of 4 attributes, there will be 
            the following 4 combinations:
            Combination0: {'rhs': [0], 'lhs': [1, 2, 3]}
            Combination1: {'rhs': [1], 'lhs': [0, 2, 3]}
            Combination2: {'rhs': [2], 'lhs': [0, 1, 3]}
            Combination3: {'rhs': [3], 'lhs': [0, 1, 2]}
            '''
            combination_distance_matrix = self.distance_matrix.split_sides(combination)
            '''with ut.timeit_context("RFD Discover time for Combination {}".format(str(combination))):'''
            rfd_discovery = RFDDiscovery(combination_distance_matrix)

            self.rfd_data_frame_list.append(
                rfd_discovery.get_rfds(rfd_discovery.standard_algorithm, combination))

        for df in self.rfd_data_frame_list:
            # print("\n")
            # print(df)
            # print("\n")
            self.rfds.extend(Transformer.rfd_data_frame_to_rfd_list(df, self.header))

        list_widget = QListWidget()

        print("\nRFDs list: ")
        for rfd in self.rfds:
            print(rfd)
            list_widget.addItem(str(rfd).replace("{", "(").replace("}", ")"))

            self.rfds_list_wrapper_layout.addWidget(list_widget)
            self.rfds_tab_layout.addWidget(self.rfds_list_wrapper)
