from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView
from pandas import DataFrame
from rx.subjects import Subject

from query_rewriter.io.csv.csv_parser import CSVParser
from query_rewriter.model.Query import Query
from query_rewriter.model.RFD import RFD
from query_rewriter.ui.PandasTableModel import PandasTableModel
from query_rewriter.ui.tabs.TabsWidget import TabsWidget
from query_rewriter.utils.RFDExtent import RFDExtent


class DataTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab = TabsWidget.QUERY_TAB_INDEX
        self.initial_query: Query = None
        self.initial_result_set: DataFrame = None
        self.rfd: RFD = None
        self.extended_query: Query = None
        self.extended_result_set: DataFrame = None
        self.relaxed_query: Query = None
        self.relaxed_result_set: DataFrame = None

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
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

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
        self.initial_result_set: DataFrame = self.data_frame.query(self.initial_query.to_expression())

        self.__highlight_initial_query()

    def __highlight_initial_query(self):
        if self.tab == TabsWidget.QUERY_TAB_INDEX:
            if self.table:
                self.table.clearSelection()

            if self.initial_result_set is not None:
                df_indexes = self.initial_result_set.index.values.tolist()

                for index in df_indexes:
                    self.table.selectRow(index)

    def set_rfd_subject(self, rfd_subject: Subject):
        self.rfd_subject: Subject = rfd_subject
        self.rfd_subject.subscribe(
            on_next=lambda rfd: (
                self.__update_selected_rfd(rfd)
            )
        )

    def __update_selected_rfd(self, rfd: RFD):
        print("Update selected RFD...")
        self.rfd: RFD = rfd

        self.__highlight_rfd()

    def __highlight_rfd(self):
        if self.tab == TabsWidget.RFDS_TAB_INDEX:
            if self.table:
                self.table.clearSelection()

            if self.data_frame is not None and self.rfd:
                rfd_df_indexes = RFDExtent.extent_indexes(self.data_frame, self.rfd)
                for index in rfd_df_indexes:
                    self.table.selectRow(index)

    def set_extended_query_subject(self, query_subject: Subject):
        self.extended_query_subject: Subject = query_subject

        self.extended_query_subject.subscribe(
            on_next=lambda query:
            (
                self.__update_extended_query(query)
            )
        )

    def __update_extended_query(self, query: Query):
        print("Update extended query...")
        self.extended_query: Query = query
        self.extended_result_set: DataFrame = self.data_frame.query(self.extended_query.to_expression())

        self.__highlight_extended_query()

    def __highlight_extended_query(self):
        if self.tab == TabsWidget.EXTENSION_TAB_INDEX:
            if self.table:
                self.table.clearSelection()

            if self.extended_result_set is not None:
                df_indexes = self.extended_result_set.index.values.tolist()

                for index in df_indexes:
                    self.table.selectRow(index)

    def set_relaxed_query_subject(self, query_subject: Subject):
        self.relaxed_query_subject: Subject = query_subject

        self.relaxed_query_subject.subscribe(
            on_next=lambda query:
            (
                self.__update_relaxed_query(query)
            )
        )

    def __update_relaxed_query(self, query: Query):
        print("Update relaxed query...")
        self.relaxed_query: Query = query
        self.relaxed_result_set: DataFrame = self.data_frame.query(self.relaxed_query.to_expression())

        self.__highlight_relaxed_query()

    def __highlight_relaxed_query(self):
        if self.tab == TabsWidget.RELAX_TAB_INDEX:
            if self.table:
                self.table.clearSelection()

            if self.relaxed_result_set is not None:
                df_indexes = self.relaxed_result_set.index.values.tolist()

                for index in df_indexes:
                    self.table.selectRow(index)

    def onTabChange(self, index):
        print("DataTab: On Tab Change...")
        if index == TabsWidget.QUERY_TAB_INDEX:
            print("Query TAB")
            self.tab = TabsWidget.QUERY_TAB_INDEX
            self.__highlight_initial_query()
        elif index == TabsWidget.RFDS_TAB_INDEX:
            print("RFD TAB")
            self.tab = TabsWidget.RFDS_TAB_INDEX
            self.__highlight_rfd()
        elif index == TabsWidget.EXTENSION_TAB_INDEX:
            print("Extension TAB")
            self.tab = TabsWidget.EXTENSION_TAB_INDEX
            self.__highlight_extended_query()
        elif index == TabsWidget.RELAX_TAB_INDEX:
            print("Relax TAB")
            self.tab = TabsWidget.RELAX_TAB_INDEX
            self.__highlight_relaxed_query()
