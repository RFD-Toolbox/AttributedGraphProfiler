import pandas as pd


class Slicer:
    '''
    Auxiliary class to divide a DataFrame in a list of one-row DataFrames.
    '''

    @staticmethod
    def slice(df: pd.DataFrame) -> list:
        '''
        Slices the input DataFrame in a list of DataFrames, each one composed of a single row.
        :param df: the DataFrame to slice.
        :type df: pandas.DataFrame
        :return: a list of DataFrames, each one composed of a single row of the input DataFrame.
        :rtype: list[pandas.DataFrame]
        '''
        rows = df.shape[0]
        return [df[i:i + 1] for i in range(0, rows)]
