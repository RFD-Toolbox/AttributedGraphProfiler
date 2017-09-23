import pandas as pd
from query_rewriter.io.csv.io import CSVInputOutput


class RFDInputOutput:
    '''
    This class is addicted to load file containing a list of rfd
    '''
    csv_io = CSVInputOutput()

    def load(self, path: str) -> pd.DataFrame:
        '''
        This method load file from a path and return a Dataframe containing a list of RFDs
        :param path: Path of file containing list of RFDs
        :return: Pandas Dataframe containing list of RFDs
        '''
        return self.csv_io.load(path=path)

