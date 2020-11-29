from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel, QGroupBox
from pandas import DataFrame
from rx.subjects import Subject

from query_rewriter.io.csv.csv_parser import CSVParser
from query_rewriter.model.Query import Query
from query_rewriter.model.RFD import RFD


class RelaxTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

    def display(self, path: str):
        self.relaxed_query_subject = Subject()

        self.initial_query: Query = None
        self.rfd: RFD = None
        self.extended_query: Query = None

        self.path = path
        self.csv_parser: CSVParser = CSVParser(path)
        self.data_frame: DataFrame = self.csv_parser.data_frame

        self.container_vertical_layout = QVBoxLayout()
        container_group_box = QGroupBox()
        container_group_box.setLayout(self.container_vertical_layout)
        self.setWidget(container_group_box)
        self.setWidgetResizable(True)

        for i in reversed(range(self.container_vertical_layout.count())):
            self.container_vertical_layout.itemAt(i).widget().deleteLater()

        self.relaxed_query_title = QLabel("Relaxed Query")
        self.relaxed_query_title.setWordWrap(True)
        self.relaxed_query_title.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.container_vertical_layout.addWidget(self.relaxed_query_title)

        self.relaxed_query_value = QLabel("")
        self.relaxed_query_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.relaxed_query_value.setWordWrap(True)
        self.relaxed_query_value.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Cursive))
        self.container_vertical_layout.addWidget(self.relaxed_query_value)

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
            self.relaxed_query_subject.on_next(self.relaxed_query)

            self.relaxed_query_value.setText(self.relaxed_query.to_rich_text_expression())
            self.relaxed_query_value.setTextFormat(Qt.RichText)

    def get_relaxed_query_subject(self) -> Subject:
        return self.relaxed_query_subject
