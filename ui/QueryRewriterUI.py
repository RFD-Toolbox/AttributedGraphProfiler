import sys
import os
import csv

from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QFileDialog, QTableWidget, QTableWidgetItem, \
    QDesktopWidget, QVBoxLayout

from ui.TabsWidget import TabsWidget


class QueryRewriterUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Window's title
        self.setWindowTitle("RFD Query Rewriter")

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

        self.setGeometry(0, 0, 900, 500)

        # geometry of the main window
        qr = self.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()

        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())

        self.tabs = TabsWidget(self)
        self.setCentralWidget(self.tabs)

        self.show()

    def open_file(self):
        open_file_dialog = QFileDialog(self)
        csv_path, _filter = open_file_dialog.getOpenFileName(parent=self,
                                                             directory=os.getenv("HOME"),
                                                             filter="CSV(*.csv)")
        print("File Name: " + csv_path)

        if csv_path != "":
            self.tabs.init_dataset_tab(csv_path)
            self.tabs.init_query_tab(csv_path)
            self.tabs.init_rfds_tab(csv_path)
            self.tabs.init_rewrite_tab()
            '''with open(file_name) as csv_file:
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(csv_file.readline())
                csv_file.seek(0)
                has_header = sniffer.has_header(csv_file.readline())
                csv_file.seek(0)
                rows = sum(1 for line in csv_file)
                csv_file.seek(0)
                reader = csv.reader(csv_file, dialect)
                columns = len(next(reader))  # Read first line and count columns
                csv_file.seek(0)

                print("Delimiter: " + dialect.delimiter)
                print("Has Header: " + str(has_header))
                print("Rows: " + str(rows))
                print("Columns: " + str(columns))

                table = QTableWidget(rows, columns)
                table.setEnabled(True)
                table.setRowCount(rows - 1)  # excluding the header from the count
                table.setColumnCount(columns)

                header = next(reader)
                print("Header: ")
                print(header)

                # write the header
                for col in range(0, columns):
                    table.setHorizontalHeaderItem(col, QTableWidgetItem(header[col]))

                # write the rows
                data_row = 0
                for row in reader:
                    for col in range(0, columns):
                        table.setItem(data_row, col, QTableWidgetItem(row[col]))
                    data_row += 1

                table.setSortingEnabled(True)
                self.setCentralWidget(table)
                layout = QVBoxLayout()
                table.setLayout(layout)'''


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QueryRewriterUI()
    sys.exit(app.exec_())
