from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel, QGroupBox
from pandas import DataFrame
from rx.subjects import Subject

from query_rewriter.io.csv.csv_parser import CSVParser
from query_rewriter.model.Query import Query
from query_rewriter.model.RFD import RFD


class ExtensionTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

    def display(self, path: str):
        self.extended_query_subject = Subject()

        self.container_vertical_layout = QVBoxLayout()
        container_group_box = QGroupBox()
        container_group_box.setLayout(self.container_vertical_layout)
        self.setWidget(container_group_box)
        self.setWidgetResizable(True)

        for i in reversed(range(self.container_vertical_layout.count())):
            self.container_vertical_layout.itemAt(i).widget().deleteLater()

        self.initial_query: Query = None
        self.rfd: RFD = None

        self.path = path
        self.csv_parser: CSVParser = CSVParser(path)
        self.data_frame: DataFrame = self.csv_parser.data_frame

        self.initial_query_title = QLabel("Initial Query")
        self.initial_query_title.setWordWrap(True)
        self.initial_query_title.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.container_vertical_layout.addWidget(self.initial_query_title)

        self.initial_query_value = QLabel("")
        self.initial_query_value.setWordWrap(True)
        self.initial_query_value.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Cursive))
        self.container_vertical_layout.addWidget(self.initial_query_value)

        self.rfd_title = QLabel("RFD")
        self.rfd_title.setWordWrap(True)
        self.rfd_title.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.container_vertical_layout.addWidget(self.rfd_title)

        self.rfd_value = QLabel("")
        self.rfd_value.setWordWrap(True)
        self.rfd_value.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Cursive))
        self.container_vertical_layout.addWidget(self.rfd_value)

        self.extended_query_title = QLabel("Extended Query")
        self.extended_query_title.setWordWrap(True)
        self.extended_query_title.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.container_vertical_layout.addWidget(self.extended_query_title)

        self.extended_query_value = QLabel("")
        self.extended_query_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.extended_query_value.setWordWrap(True)
        self.extended_query_value.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Cursive))
        self.container_vertical_layout.addWidget(self.extended_query_value)

    def set_initial_query_subject(self, query_subject: Subject):
        self.initial_query_subject: Subject = query_subject
        self.initial_query_subject.subscribe(
            on_next=lambda query:
            (
                self.update_initial_query(query),
                self.extend_query()
            )
        )

    def update_initial_query(self, query: Query):
        self.initial_query: Query = query
        self.initial_query_value.setText(self.initial_query.to_rich_text_expression())
        self.initial_query_value.setTextFormat(Qt.RichText)

    def set_rfd_subject(self, rfd_subject: Subject):
        self.rfd_subject: Subject = rfd_subject
        self.rfd_subject.subscribe(
            on_next=lambda rfd: (
                self.update_selected_rfd(rfd),
                self.extend_query()
            )
        )

    def update_selected_rfd(self, rfd: RFD):
        self.rfd: RFD = rfd
        self.rfd_value.setText(self.rfd.__str__())

    def extend_query(self):
        if self.initial_query and self.rfd:
            self.extended_query = self.initial_query.extend_ranges(self.rfd, self.data_frame)
            self.extended_query_subject.on_next(self.extended_query)

            self.extended_query_value.setText(self.extended_query.to_rich_text_expression())
            self.extended_query_value.setTextFormat(Qt.RichText)

    def get_extended_query_subject(self) -> Subject:
        return self.extended_query_subject
