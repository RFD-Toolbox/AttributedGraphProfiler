import pandas as pd
import numpy as np


class QueryRelaxer:
    query: dict = None
    '''
    Dictionary of key-value pairs representing the original query.
    Each key is an attribute of the DataSet.
    The corresponding value can be a single value or a list of values for which the equality has to be true.
    '''
    rfds_df: pd.DataFrame = None
    '''
    DataFrame containing all the RFDs in the following format:
    RHS | Attributes
    RHS column is the RHS attribute label of the RFD for each row.
    Attributes columns contains the corresponding threshold for the RFD attribute.
    '''
    data_set_df: pd.DataFrame = None
    '''
    DataFrame containing the data to query.
    '''
    query_attributes: list = None
    '''
    List of the attributes involved in the query.
    '''

    def __init__(self, query: dict, rfds_df: pd.DataFrame, data_set_df: pd.DataFrame) -> None:
        super().__init__()
        self.query = query
        self.rfds_df = rfds_df
        self.data_set_df = data_set_df
        # ===============================================
        self.query_attributes = list(self.query.keys())

    def dropna(self):
        '''
        Drops the RFDs where an attribute of the query is NaN.
        :return:
        '''
        return self.rfds_df.dropna(subset=self.query_attributes).reset_index(drop=True)

    def droprhs(self):
        '''
        Drops the RFDs where the RHS attribute is part of the query.
        :return:
        '''
        return self.rfds_df.drop(self.rfds_df[self.rfds_df["RHS"].isin(self.query_attributes)]
                                 .index).reset_index(drop=True)

    def sort_nan_query_attributes(self):
        nan_count = "NaNs"
        kwargs = {nan_count: lambda x: x.isnull().sum(axis=1)}
        self.rfds_df = self.rfds_df.assign(**kwargs)

        sorting_cols = [nan_count]
        print("Sorting Keys:", sorting_cols)
        ascending = [False]

        sorting_cols.extend(self.query_attributes)
        ascending.extend([True for _ in self.query_attributes])

        return self.rfds_df.sort_values(by=sorting_cols,
                                        ascending=ascending,
                                        na_position="first").reset_index(drop=True)
