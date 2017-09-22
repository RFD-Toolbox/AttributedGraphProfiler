import pandas as pd
import csv


class CSVParser:
    '''
    CSVParser allows to get the data and the info of a CSV file, given only the path.
    '''
    path: str = None
    '''
    The path of the CSV file.
    '''
    delimiter = None
    '''
    The fields separator of the CSV file.
    '''
    data_frame: pd.DataFrame = None
    '''
    The data_frame representing the data within the CSV file.
    '''
    rows_count: int = None
    '''
    The number of rows containing data within the CSV file.
    '''
    columns_count: int = None
    '''
    The number of columns of the CSV file.
    '''
    header: list = None
    '''
    The header labels.
    '''

    def __init__(self, csv_path: str):
        self.path = csv_path
        self.delimiter = self.__guess_delimiter()
        self.data_frame = pd.read_csv(self.path, delimiter=self.delimiter)
        self.rows_count, self.columns_count = self.data_frame.shape
        self.header = list(self.data_frame)

    def __guess_delimiter(self):
        '''
        Method to guess the CSV file delimiter by reading the first line.
        :return: the CSV file delimiter.
        :rtype:
        '''
        with open(self.path) as csv_file:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(csv_file.readline())
            delimiter = dialect.delimiter
        return delimiter
