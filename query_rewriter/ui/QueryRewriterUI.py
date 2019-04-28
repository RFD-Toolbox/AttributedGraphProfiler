import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QFileDialog, QDesktopWidget, QSplitter, QLabel

from query_rewriter.ui.tabs.DataTab import DataTab
from query_rewriter.ui.tabs.TabsWidget import TabsWidget
from pkg_resources import resource_filename


class QueryRewriterUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Window's title
        self.setWindowTitle("RFD Query Rewriter")

        # Window's icon
        icon_path = resource_filename("query_rewriter", "assets/images/growth.png")
        icon: QIcon = QIcon(icon_path)
        self.setWindowIcon(icon)

        # Menu
        menu_bar = self.menuBar()
        # File
        file_menu = menu_bar.addMenu('&File')
        # Open
        open_file_button = QAction('Open', self)
        open_file_button.setShortcut("Ctrl+O")
        open_file_button.triggered.connect(self.open_file)
        file_menu.addAction(open_file_button)
        # Exit
        exit_button = QAction("Exit", self)
        exit_button.setShortcut("Ctrl+X")
        exit_button.triggered.connect(self.close)
        file_menu.addAction(exit_button)

        self.setGeometry(0, 0, 1200, 700)

        # geometry of the main window
        qr = self.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()

        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())

        splitter: QSplitter = QSplitter(Qt.Vertical)

        self.tabs = TabsWidget(self)
        # self.tabs.blockSignals(True) #just for not showing the initial message
        self.tabs.currentChanged.connect(self.onTabChange)  # changed!
        # self.setCentralWidget(self.tabs)

        splitter.addWidget(self.tabs)

        self.data_tab: DataTab = DataTab()
        splitter.addWidget(self.data_tab)

        splitter.setSizes([500, 500])
        self.setCentralWidget(splitter)

        self.show()

    def onTabChange(self, index):
        print("On Tab Change...")
        print("Index: " + str(index))
        self.data_tab.onTabChange(index)

    def open_file(self):
        open_file_dialog = QFileDialog(self)
        csv_path, _filter = open_file_dialog.getOpenFileName(parent=self,
                                                             directory=os.getenv("HOME"),
                                                             filter="CSV(*.csv)")
        print("DataSet: " + csv_path)

        if csv_path != "":
            # self.tabs.init_data_tab(csv_path)
            self.data_tab.display(csv_path)
            self.tabs.init_query_tab(csv_path)
            self.tabs.init_rfds_tab(csv_path)
            self.tabs.init_extension_tab(csv_path)
            self.tabs.init_relax_tab(csv_path)

            self.data_tab.set_initial_query_subject(self.tabs.query_tab.get_initial_query_subject())
            self.data_tab.set_rfd_subject(self.tabs.rfds_tab.get_rfd_subject())
            self.data_tab.set_extended_query_subject(self.tabs.extension_tab.get_extended_query_subject())
            self.data_tab.set_relaxed_query_subject(self.tabs.relax_tab.get_relaxed_query_subject())

            self.tabs.rfds_tab.set_initial_query_subject(self.tabs.query_tab.get_initial_query_subject())

            self.tabs.extension_tab.set_initial_query_subject(self.tabs.query_tab.get_initial_query_subject())
            self.tabs.extension_tab.set_rfd_subject(self.tabs.rfds_tab.get_rfd_subject())

            self.tabs.relax_tab.set_initial_query_subject(self.tabs.query_tab.get_initial_query_subject())
            self.tabs.relax_tab.set_rfd_subject(self.tabs.rfds_tab.get_rfd_subject())
            self.tabs.relax_tab.set_extended_query_subject(self.tabs.extension_tab.get_extended_query_subject())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QueryRewriterUI()
    sys.exit(app.exec_())
