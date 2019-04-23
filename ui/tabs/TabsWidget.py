import typing

from PyQt5.QtWidgets import QTabWidget, QWidget
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
