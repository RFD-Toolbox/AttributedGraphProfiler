from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel
from pandas import DataFrame
from rx.subjects import Subject

from query_rewriter.io.csv.csv_parser import CSVParser
from query_rewriter.model.Query import Query
from query_rewriter.model.RFD import RFD


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

        self.initial_query_title = QLabel("Initial Query")
        self.initial_query_title.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.layout().addWidget(self.initial_query_title)

        self.initial_query_value = QLabel("")
        self.initial_query_value.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Cursive))
        self.layout().addWidget(self.initial_query_value)

        self.rfd_title = QLabel("RFD")
        self.rfd_title.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.layout().addWidget(self.rfd_title)

        self.rfd_value = QLabel("")
        self.rfd_value.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Cursive))
        self.layout().addWidget(self.rfd_value)

        self.extended_query_title = QLabel("Extended Query")
        self.extended_query_title.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.layout().addWidget(self.extended_query_title)

        self.extended_query_value = QLabel("")
        self.extended_query_value.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Cursive))
        self.layout().addWidget(self.extended_query_value)

    def set_initial_query_subject(self, query_subject: Subject):
        self.query_subject: Subject = query_subject
        self.query_subject.subscribe(
            on_next=lambda query:
            (
                self.update_initial_query(query)
            )
        )

    def update_initial_query(self, query: Query):
        self.initial_query: Query = query
        print("Initial Query changed...")
        print(self.initial_query)
        self.initial_query_value.setText(self.initial_query.to_expression())

    def set_extended_query_subject(self, query_subject: Subject):
        self.extended_query_subject: Subject = query_subject
        self.extended_query_subject.subscribe(
            on_next=lambda query:
            (
                self.update_extended_query(query)
            )
        )

    def update_extended_query(self, query: Query):
        self.extended_query: Query = query
        print("Extended Query changed...")
        print(self.extended_query)
        self.extended_query_value.setText(self.extended_query.to_expression())

    def set_rfd_subject(self, rfd_subject: Subject):
        self.rfd_subject: Subject = rfd_subject
        self.rfd_subject.subscribe(
            on_next=lambda rfd: (
                self.update_selected_rfd(rfd)
            )
        )

    def update_selected_rfd(self, rfd: RFD):
        self.rfd: RFD = rfd
        print("RFD changed...")
        print(self.rfd)
        self.rfd_value.setText(self.rfd.__str__())

