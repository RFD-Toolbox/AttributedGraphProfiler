import time
import typing
import copy

from PyQt5.QtCore import QAbstractTableModel, Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QStandardItemModel, QStandardItem
from pandas import DataFrame, Series
import networkx as nx
import numpy as np
from numpy import ndarray
from pandas.compat import reduce
from rx.subjects import Subject

from dominance.dominance_tools import RFDDiscovery
from loader.distance_mtr import DiffMatrix
from query_rewriter.io.csv.csv_parser import CSVParser
from query_rewriter.io.rfd.rfd_extractor import RFDExtractor
from query_rewriter.model.RFD import RFD
from query_rewriter.utils.DiffDataFrame import DiffDataFrame
from query_rewriter.utils.Transformer import Transformer
from ui.PandasTableModel import PandasTableModel

from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLineEdit, \
    QGroupBox, QLabel, QPushButton, QGridLayout, QComboBox, QTableView, QScrollArea, QHBoxLayout, QAbstractItemView, \
    QTreeWidget, QTreeWidgetItem, QHeaderView

from query_rewriter.query.relaxer import QueryRelaxer
from ui.tabs.DataTab import DataTab
from ui.tabs.QueryTab import QueryTab


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
        self.rfds_tab = QScrollArea()
        self.rfds_tab_content_widget = QWidget()
        self.rfds_tab.setWidget(self.rfds_tab_content_widget)
        self.rfds_tab.setWidgetResizable(True)
        self.rfds_tab_layout = QVBoxLayout(self.rfds_tab_content_widget)

        # Rewrite
        self.rewrite_tab = QScrollArea()
        self.rewrite_tab_content_widget = QWidget()
        self.rewrite_tab.setWidget(self.rewrite_tab_content_widget)
        self.rewrite_tab.setWidgetResizable(True)
        self.rewrite_tab_layout = QVBoxLayout(self.rewrite_tab_content_widget)

        # self.addTab(self.dataset_tab, "Dataset")
        # self.addTab(self.query_tab, "Query")
        # self.addTab(self.rfds_tab, "RFDs")
        # self.addTab(self.rewrite_tab, "Rewrite")

        self.rfds: list = []

    def init_data_tab(self, path: str):
        self.data_tab.display(path)

    def init_query_tab(self, path: str):
        self.query_tab.display(path)

    def init_rfds_tab(self, path: str):
        self.rfds_subject = Subject()

        for i in reversed(range(self.rfds_tab_layout.count())):
            self.rfds_tab_layout.itemAt(i).widget().deleteLater()

        self.rfds_tree_wrapper = QGroupBox()
        self.rfds_tree_wrapper_layout = QVBoxLayout(self.rfds_tree_wrapper)

        self.path = path
        main_group = QGroupBox()
        group_vertical_layout = QVBoxLayout()
        main_group.setLayout(group_vertical_layout)

        buttons_group_box = QGroupBox()
        buttons_horizontal_layout = QHBoxLayout()
        buttons_horizontal_layout.setAlignment(Qt.AlignLeft)
        buttons_horizontal_layout.setAlignment(Qt.AlignTop)
        buttons_group_box.setLayout(buttons_horizontal_layout)

        group_vertical_layout.addWidget(buttons_group_box)

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

        self.rfd_data_set_table = QTableView()
        self.pandas_model: PandasTableModel = PandasTableModel(self.data_frame, self.rfds_tab_layout)
        self.rfd_data_set_table.setModel(self.pandas_model)
        self.rfd_data_set_table.setSortingEnabled(False)
        self.rfd_data_set_table.resizeRowsToContents()
        self.rfd_data_set_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # full width table
        self.rfd_data_set_table.setSelectionMode(QAbstractItemView.MultiSelection)

        group_vertical_layout.addWidget(self.rfd_data_set_table)

        self.rfds_tab_layout.addWidget(main_group)

    def load_rfds(self):
        print("Loading RFDs")
        # Cleaning
        self.rfd_data_set_table.clearSelection()

    def discover_rfds(self):
        print("Discovering RFDs")
        # Cleaning
        self.rfd_data_set_table.clearSelection()

        for i in reversed(range(self.rfds_tree_wrapper_layout.count())):
            self.rfds_tree_wrapper_layout.itemAt(i).widget().deleteLater()

        self.rfds = []
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

        self.rfds_subject.on_next(self.rfds)

        self.tree_header = QTreeWidgetItem()
        self.tree_header.setText(self.RFD, "RFD")
        self.tree_header.setText(self.EXTENT, "Extent")
        self.tree_header.setText(self.TIME, "Time")

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderItem(self.tree_header)

        self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        print("\nRFDs list: ")
        for rfd in self.rfds:
            print(rfd)

            item = QTreeWidgetItem()
            item.setText(self.RFD, str(rfd).replace("{", "(").replace("}", ")"))
            item.setData(self.RFD, Qt.UserRole, rfd)
            item.setText(self.EXTENT, "")

            self.tree_widget.addTopLevelItem(item)

        self.rfds_tree_wrapper_layout.addWidget(self.tree_widget)
        self.rfds_tab_layout.addWidget(self.rfds_tree_wrapper)

        # combo.currentTextChanged.connect(lambda ix, key=h, select=combo: self.combo_changed(select, key))
        # self.tree_view.currentItemChanged.connect(self.rfd_selected)
        self.tree_widget.currentItemChanged.connect(self.rfd_selected_to_max_clique)

        self.addTab(self.rewrite_tab, "Rewrite")

    def rfd_selected_to_max_clique(self, current: QTreeWidgetItem, previous: QTreeWidgetItem):
        print("RFD selected")

        if current:
            t0 = time.time()

            print("Current:")
            print(current)
            rfd: RFD = current.data(self.RFD, Qt.UserRole)
            print("Current: " + str(rfd))

            # https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression#26853961
            rfd_thresholds: dict = {**rfd.get_left_hand_side(), **rfd.get_right_hand_side()}
            print("RFD thresholds:")
            print(rfd_thresholds)

            lhs = rfd.get_left_hand_side()
            rhs = rfd.get_right_hand_side()

            lhs_keys = lhs.keys()
            rhs_keys = rhs.keys()

            print("LHS Keys: " + str(lhs_keys))
            print("RHS Keys: " + str(rhs_keys))

            # https://stackoverflow.com/questions/1720421/how-to-concatenate-two-lists-in-python#answer-35631185
            rfd_columns = [*lhs_keys, *rhs_keys]
            print("RFD Columns:")
            print(rfd_columns)

            rfd_columns_index: dict = {value: position for (position, value) in enumerate(rfd_columns)}

            print("RFD Columns index:")
            print(rfd_columns_index)

            rows, columns = self.data_frame.shape

            # Calculate all possible differences.
            # This is an O(N^2) operation and may be costly in terms of time and memory.
            # dist: ndarray = np.abs(rfd_columns_data[:, None] - rfd_columns_data)

            full_dist = DiffDataFrame.full_diff(self.data_frame[rfd_columns])
            print("Full Dist:")
            print(full_dist)

            dist: ndarray = np.array(
                [[full_dist.iloc[row1 * rows + row2] for row2 in range(0, rows)] for row1 in range(0, rows)])
            print("Dist:")
            print(dist)

            # Identify the suitable pairs of rows:
            # im: ndarray = (dist[:, :, 0] <= 2) & (dist[:, :, 1] <= 0) & (dist[:, :, 2] <= 1)
            # print("IM:")
            # print(im)

            conditions_arrays: ndarray = [(dist[:, :, rfd_columns_index[column]] <= rfd_thresholds[column])
                                          for column in rfd_columns]

            print("Conditions Array:")
            print(conditions_arrays)

            adjacency_matrix: ndarray = np.array(reduce(lambda a, b: np.bitwise_and(a, b), conditions_arrays))
            print("Adjacency Matrix:")
            print(adjacency_matrix)

            # Use them as an adjacency matrix and construct a graph.
            # The graph nodes represent rows in the original dataframe.
            # The nodes are connected if the corresponding rows are in the RFD:

            graph = nx.from_numpy_matrix(adjacency_matrix)

            max_clique = max(nx.clique.find_cliques(graph), key=len)
            df: DataFrame = self.data_frame.loc[max_clique, :]
            t1 = time.time()

            seconds = t1 - t0
            current.setText(self.TIME, str(seconds) + "''")

            print("Time: " + str(seconds))

            print("DataFrame:")
            print(self.data_frame)

            print("RFD: " + str(rfd))
            print("RFD Subset:")
            print(df)

            percentage = round((df.shape[0] / self.rows_count) * 100)
            print("Percentage: " + str(percentage))
            current.setText(self.EXTENT, str(percentage) + "%")

            print("Indexes:")
            df_indexes = df.index.values.tolist()
            print(df_indexes)

            self.pandas_model.update_data(self.data_frame)

            self.rfd_data_set_table.clearSelection()
            for index in df_indexes:
                self.rfd_data_set_table.selectRow(index)

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

    def init_rewrite_tab(self):
        self.query_subject.subscribe(
            on_next=lambda ov: self.update_original_query(ov)
        )

        self.rfds_subject.subscribe(
            on_next=lambda rfds: self.show_rewrite_rfds(rfds)
        )

        self.rewrite_original_query_label = QLabel("")
        self.rewrite_tab_layout.addWidget(self.rewrite_original_query_label)

        self.rewrite_extended_query_label = QLabel("")
        self.rewrite_tab_layout.addWidget(self.rewrite_extended_query_label)

    def update_original_query(self, operator_values: dict):
        self.original_query_operator_values = operator_values
        self.rewrite_original_query_label.setText(
            QueryRelaxer.query_operator_values_to_expression(self.original_query_operator_values))

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