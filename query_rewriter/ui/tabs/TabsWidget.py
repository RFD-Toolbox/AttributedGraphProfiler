import typing

from PyQt5.QtWidgets import QTabWidget, QWidget
from query_rewriter.ui.tabs.ExtensionTab import ExtensionTab
from query_rewriter.ui.tabs.QueryTab import QueryTab
from query_rewriter.ui.tabs.RFDsTab import RFDsTab
from query_rewriter.ui.tabs.RelaxTab import RelaxTab


class TabsWidget(QTabWidget):
    QUERY_TAB_INDEX, RFDS_TAB_INDEX, EXTENSION_TAB_INDEX, RELAX_TAB_INDEX = range(4)
    RFD, EXTENT, TIME = range(3)

    def __init__(self, parent: typing.Optional[QWidget] = ...) -> None:
        super().__init__(parent)

        # Query Tab
        self.query_tab: QueryTab = QueryTab()
        self.addTab(self.query_tab, "Query")

        # RFDs Tab
        self.rfds_tab: RFDsTab = RFDsTab()
        self.addTab(self.rfds_tab, "RFDs")

        # Extension Tab
        self.extension_tab: ExtensionTab = ExtensionTab()
        self.addTab(self.extension_tab, "Extension")

        # Relax Tab
        self.relax_tab: RelaxTab = RelaxTab()
        self.addTab(self.relax_tab, "Relax")

        self.rfds: list = []

    def init_data_tab(self, path: str):
        self.data_tab.display(path)

    def init_query_tab(self, path: str):
        self.query_tab.display(path)

    def init_rfds_tab(self, path: str):
        self.rfds_tab.display(path)

    def init_extension_tab(self, path: str):
        self.extension_tab.display(path)

    def init_relax_tab(self, path: str):
        self.relax_tab.display(path)
