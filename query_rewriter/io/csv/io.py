import pandas as pd


class CSVInputOutput:
    '''
    CSVInputOutput allows to load/store a Pandas.DataFrame from/to a CSV file.
    '''

    sep = ";"
    '''
    CSV fields delimiter symbol.
    '''
    na_rep = "?"
    '''
    Missing data representation symbol.
    '''
    index = False
    '''
    Boolean to indicate if we want row indexes to be written to the CSV file.
    '''
    encoding = "utf-8"
    '''
    The encoding of the input/output file.
    '''
    date_format: str = None
    '''
    Format string for datetime objects.
    '''

    def store(self, df: pd.DataFrame, path: str):
        '''
        Stores the DataFrame to the given path as a CSV file.
        :param df: the DataFrame to be stored.
        :type df: pandas.DataFrame
        :param path: the path where to store the DataFrame.
        :type path: str
        :return:
        :rtype:
        '''
        df.to_csv(path, sep=self.sep, na_rep=self.na_rep, index=self.index, encoding=self.encoding,
                  date_format=self.date_format)

    def load(self, path: str) -> pd.DataFrame:
        '''
        Loads the DataFrame from the given CSV file path.
        :param path: the path where the CSV file is.
        :type path: str
        :return: the DataFrame loaded.
        :rtype:
        '''
        return pd.read_csv(path, sep=self.sep, na_values=self.na_rep, parse_dates=True, decimal=".")
