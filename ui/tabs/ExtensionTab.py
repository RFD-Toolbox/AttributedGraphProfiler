from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel, QLayout
from rx.subjects import Subject

from query_rewriter.model.Query import Query
from query_rewriter.model.RFD import RFD


class ExtensionTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.content_widget = QWidget()
        self.setWidget(self.content_widget)
        self.setWidgetResizable(True)
        self.setLayout(QVBoxLayout(self.content_widget))
        self.layout().setAlignment(Qt.AlignTop)

    def display(self, path: str):
        self.path = path

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

    def set_query_subject(self, query_subject: Subject):
        self.query_subject: Subject = query_subject
        self.query_subject.subscribe(
            on_next=lambda ov: self.update_initial_query(ov)
        )

    def update_initial_query(self, query: Query):
        self.query: Query = query
        self.initial_query_value.setText(self.query.to_expression())

    def set_rfd_subject(self, rfd_subject: Subject):
        self.rfd_subject: Subject = rfd_subject
        self.rfd_subject.subscribe(
            on_next=lambda rfd: self.update_rfd_label(rfd)
        )

    def update_rfd_label(self, rfd: RFD):
        self.rfd: RFD = rfd
        self.rfd_value.setText(self.rfd.__str__())
