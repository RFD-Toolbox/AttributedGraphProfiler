import pandas as pd


class CSVInputOutput:
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

    def store(self, rfd_df: pd.DataFrame, path: str):
        return rfd_df.to_csv(path, sep=self.sep, na_rep=self.na_rep, index=self.index, encoding=self.encoding,
                             date_format=self.date_format)

    def load(self, path: str) -> pd.DataFrame:
        return pd.read_csv(path, sep=self.sep, na_values=self.na_rep, parse_dates=True)
