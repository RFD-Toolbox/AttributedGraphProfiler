from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView
from pandas import DataFrame
from rx.subjects import Subject

from query_rewriter.io.csv.csv_parser import CSVParser
from query_rewriter.model.Query import Query
from query_rewriter.model.RFD import RFD
from query_rewriter.ui.PandasTableModel import PandasTableModel
from query_rewriter.utils.RFDExtent import RFDExtent


class DataTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setLayout(QVBoxLayout())

    def display(self, path: str):
        self.csv_parser: CSVParser = CSVParser(path)
        self.data_frame: DataFrame = self.csv_parser.data_frame

        self.table = QTableView()
        pandas_model: QAbstractTableModel = PandasTableModel(self.data_frame, self)
        self.table.setModel(pandas_model)
        self.table.setSortingEnabled(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # full width table
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)

        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().deleteLater()

        self.layout().addWidget(self.table)

    def set_initial_query_subject(self, query_subject: Subject):
        self.initial_query_subject: Subject = query_subject

        self.initial_query_subject.subscribe(
            on_next=lambda query:
            (
                self.__update_initial_query(query)
            )
        )

    def __update_initial_query(self, query: Query):
        print("Update initial query:")
        self.initial_query: Query = query

        print("InitialQuery:")
        print(self.initial_query.to_expression())

        print("Data Frame:")
        print(self.data_frame)

        result_set: DataFrame = self.data_frame.query(self.initial_query.to_expression())

        df_indexes = result_set.index.values.tolist()
        print("Indexes:")
        print(df_indexes)

        self.table.clearSelection()
        for index in df_indexes:
            print("Current index:")
            print(index)
            self.table.selectRow(index)

    def set_rfd_subject(self, rfd_subject: Subject):
        self.rfd_subject: Subject = rfd_subject
        self.rfd_subject.subscribe(
            on_next=lambda rfd: (
                self.update_selected_rfd(rfd)
            )
        )

    def update_selected_rfd(self, rfd: RFD):
        print("Update selected RFD...")
        self.rfd: RFD = rfd

        rfd_df_indexes = RFDExtent.extent_indexes(self.data_frame, rfd)

        self.table.clearSelection()
        for index in rfd_df_indexes:
            self.table.selectRow(index)
