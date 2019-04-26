from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel, QTableView, QHeaderView, QAbstractItemView
from pandas import DataFrame
from rx.subjects import Subject

from query_rewriter.io.csv.csv_parser import CSVParser
from query_rewriter.model.Query import Query
from query_rewriter.model.RFD import RFD
from ui.PandasTableModel import PandasTableModel


class RelaxTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.content_widget = QWidget()
        self.setWidget(self.content_widget)
        self.setWidgetResizable(True)
        self.setLayout(QVBoxLayout(self.content_widget))
        self.layout().setAlignment(Qt.AlignTop)

        self.initial_query: Query = None
        self.rfd: RFD = None
        self.extended_query: Query = None

    def display(self, path: str):
        self.path = path
        self.csv_parser: CSVParser = CSVParser(path)
        self.data_frame: DataFrame = self.csv_parser.data_frame

        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().deleteLater()

        self.relaxed_query_title = QLabel("Relaxed Query")
        self.relaxed_query_title.setWordWrap(True)
        self.relaxed_query_title.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.layout().addWidget(self.relaxed_query_title)

        self.relaxed_query_value = QLabel("")
        self.relaxed_query_value.setWordWrap(True)
        self.relaxed_query_value.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Cursive))
        self.layout().addWidget(self.relaxed_query_value)

        self.data_set_table = QTableView()
        self.pandas_model: PandasTableModel = PandasTableModel(self.data_frame, self.layout())
        self.data_set_table.setModel(self.pandas_model)
        self.data_set_table.setSortingEnabled(False)
        self.data_set_table.resizeRowsToContents()
        self.data_set_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # full width table
        self.data_set_table.setSelectionMode(QAbstractItemView.MultiSelection)

        self.layout().addWidget(self.data_set_table)

    def set_initial_query_subject(self, query_subject: Subject):
        self.query_subject: Subject = query_subject
        self.query_subject.subscribe(
            on_next=lambda query:
            (
                self.update_initial_query(query),
                self.relax_query()
            )
        )

    def update_initial_query(self, query: Query):
        self.initial_query: Query = query

    def set_extended_query_subject(self, query_subject: Subject):
        self.extended_query_subject: Subject = query_subject
        self.extended_query_subject.subscribe(
            on_next=lambda query:
            (
                self.update_extended_query(query),
                self.relax_query()
            )
        )

    def update_extended_query(self, query: Query):
        self.extended_query: Query = query
        self.extended_result_set: DataFrame = self.data_frame.query(self.extended_query.to_expression())

    def set_rfd_subject(self, rfd_subject: Subject):
        self.rfd_subject: Subject = rfd_subject
        self.rfd_subject.subscribe(
            on_next=lambda rfd: (
                self.update_selected_rfd(rfd),
                self.relax_query()
            )
        )

    def update_selected_rfd(self, rfd: RFD):
        self.rfd: RFD = rfd

    def relax_query(self):
        if self.initial_query and self.extended_query and self.extended_result_set is not None and self.rfd:
            self.relaxed_query: Query = self.extended_query.relax_constraints(self.rfd, self.data_frame)

            self.relaxed_query_value.setText(self.relaxed_query.to_rich_text_expression())
            self.relaxed_query_value.setTextFormat(Qt.RichText)

            relaxed_result_set: DataFrame = self.data_frame.query(self.relaxed_query.to_expression())

            df_indexes = relaxed_result_set.index.values.tolist()

            self.data_set_table.clearSelection()
            for index in df_indexes:
                self.data_set_table.selectRow(index)
