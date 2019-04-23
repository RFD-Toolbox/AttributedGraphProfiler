import typing

from PyQt5.QtCore import Qt
from pandas import DataFrame

from query_rewriter.model.RFD import RFD

from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, \
    QGroupBox, QLabel, QScrollArea, \
    QTreeWidget, QTreeWidgetItem, QHeaderView

from query_rewriter.query.relaxer import QueryRelaxer
from ui.tabs.DataTab import DataTab
from ui.tabs.ExtensionTab import ExtensionTab
from ui.tabs.QueryTab import QueryTab
from ui.tabs.RFDsTab import RFDsTab


class TabsWidget(QTabWidget):
    RFD, EXTENT, TIME = range(3)

    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)

        # Data Tab
        self.data_tab: DataTab = DataTab()
        self.addTab(self.data_tab, "Data")

        # Query Tab
        self.query_tab: QueryTab = QueryTab()
        self.addTab(self.query_tab, "Query")

        # RFDs Tab
        self.rfds_tab: RFDsTab = RFDsTab()
        self.addTab(self.rfds_tab, "RFDs")

        # Extension Tab
        self.extension_tab: ExtensionTab = ExtensionTab()
        self.addTab(self.extension_tab, "Extension")

        self.rfds: list = []

    def init_data_tab(self, path: str):
        self.data_tab.display(path)

    def init_query_tab(self, path: str):
        self.query_tab.display(path)

    def init_rfds_tab(self, path: str):
        self.rfds_tab.display(path)

    def init_extension_tab(self, path: str):
        self.extension_tab.display(path)

    def rfd_selected_to_relaxed_query(self, current: QTreeWidgetItem, previous: QTreeWidgetItem):
        print("RFD selected to relaxed query...")
        current_rfd: RFD = current.data(self.RFD, Qt.UserRole)
        print("Current RFD: " + str(current_rfd))

        # TODO extend the Query
        extended_query = QueryRelaxer.extend_query_operator_values_ranges(self.original_query_operator_values,
                                                                          current_rfd, self.data_frame)
        print("Extended Query: ")
        print(extended_query)

        extended_expression = QueryRelaxer.query_operator_values_to_expression(extended_query)
        print("Extended expression: ")
        print(extended_expression)
        self.update_extended_query(extended_query)

        extended_result_set: DataFrame = self.data_frame.query(extended_expression)
        print("Extended result set:")
        print(extended_result_set)

    def update_extended_query(self, extended_operator_values: dict):
        self.extended_query_operator_values = extended_operator_values
        self.rewrite_extended_query_label.setText(
            QueryRelaxer.query_operator_values_to_expression(self.extended_query_operator_values))

    def show_rewrite_rfds(self, rfds: list):
        print("Show rewrite RFDs")
        print("Size: " + str(len(rfds)))

        self.rewrite_tree_header = QTreeWidgetItem()
        self.rewrite_tree_header.setText(self.RFD, "RFD")
        self.rewrite_tree_header.setText(self.EXTENT, "Extent")
        self.rewrite_tree_header.setText(self.TIME, "Time")

        self.rewrite_tree_widget = QTreeWidget()
        self.rewrite_tree_widget.setHeaderItem(self.rewrite_tree_header)
        self.rewrite_tree_wrapper = QGroupBox()
        self.rewrite_tree_wrapper_layout = QVBoxLayout(self.rewrite_tree_wrapper)

        self.rewrite_tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        print("Operator Values: ")
        print(self.original_query_operator_values)

        filteredRFDs = []

        for rfd in rfds:
            # https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression#26853961
            rfd_thresholds: dict = {**rfd.get_left_hand_side(), **rfd.get_right_hand_side()}

            # keep only the RFDs with all the fields of the Query
            if all(field in rfd_thresholds.keys() for field in self.original_query_operator_values.keys()):

                # remove the RFDs having a filed of the query in the RHS
                if not any(field in rfd.get_right_hand_side().keys() for field in
                           self.original_query_operator_values.keys()):
                    filteredRFDs.extend([rfd])

        # sort RFDs by non decreasing order of the Query's fields thresholds
        filteredRFDs = QueryRelaxer.sort_by_increasing_threshold(filteredRFDs,
                                                                 list(self.original_query_operator_values.keys()))

        print("Filtered RFDs:")
        print("Size: " + str(len(filteredRFDs)))

        print("*" * 100)
        for rfd in filteredRFDs:
            print(rfd)

            item = QTreeWidgetItem()
            item.setText(self.RFD, str(rfd).replace("{", "(").replace("}", ")"))
            item.setData(self.RFD, Qt.UserRole, rfd)
            item.setText(self.EXTENT, "")

            self.rewrite_tree_widget.addTopLevelItem(item)

        self.rewrite_tree_wrapper_layout.addWidget(self.rewrite_tree_widget)
        self.rewrite_tab_layout.addWidget(self.rewrite_tree_wrapper)

        self.rewrite_tree_widget.currentItemChanged.connect(self.rfd_selected_to_relaxed_query)
