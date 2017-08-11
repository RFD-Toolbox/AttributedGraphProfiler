import pandas as pandas
import csv


class CSVParser:
    path = None
    delimiter = None
    data_frame = None
    rows_count = None
    columns_count = None
    header = None

    def __init__(self, csv_path):
        self.path = csv_path
        self.delimiter = self.__guess_delimiter()
        self.data_frame = pandas.read_csv(self.path, delimiter=self.delimiter)
        self.rows_count, self.columns_count = self.data_frame.shape
        self.header = list(self.data_frame)

    def __guess_delimiter(self):
        with open(self.path) as csv_file:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(csv_file.read(2048))
            delimiter = dialect.delimiter
        return delimiter
