from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QTableView, QHeaderView
from pandas import DataFrame

from query_rewriter.io.csv.csv_parser import CSVParser
from query_rewriter.ui.PandasTableModel import PandasTableModel


class DataTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setLayout(QVBoxLayout())

    def display(self, path: str):
        self.csv_parser: CSVParser = CSVParser(path)
        self.data_frame: DataFrame = self.csv_parser.data_frame

        table = QTableView()
        pandas_model: QAbstractTableModel = PandasTableModel(self.data_frame, self)
        table.setModel(pandas_model)
        table.setSortingEnabled(True)
        table.resizeRowsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # full width table

        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().deleteLater()

        self.layout().addWidget(table)
