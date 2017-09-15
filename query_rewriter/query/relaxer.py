import pandas as pd
import numpy as np
import editdistance
from random import shuffle


class QueryRelaxer:
    '''
    Auxiliary class to relax a certain Query by means of a Relaxed Functional Dependency.
    '''

    @staticmethod
    def drop_query_na(rfds_df: pd.DataFrame, query: dict) -> pd.DataFrame:
        '''
        Drops the RFDs where an attribute of the query is NaN.
        :param rfds_df: the Relaxed Functional Dependencies DataFrame to drop.
        :param query: the query containing the attributes for dropping.
        :return: the dropped RFDs DataFrame.
        '''
        query_attributes = list(query.keys())
        rfds = rfds_df.dropna(subset=query_attributes).reset_index(drop=True)
        return rfds

    @staticmethod
    def drop_query_rhs(rfds_df: pd.DataFrame, query: dict) -> pd.DataFrame:
        '''
        Drops the RFDs where the RHS attribute is part of the query.
        :param rfds_df: the Relaxed Functional Dependencies DataFrame to drop.
        :param query: the query containing the attributes for dropping.
        :return: the dropped RFDs DataFrame.
        '''
        query_attributes = list(query.keys())
        rfds = rfds_df.drop(rfds_df[rfds_df["RHS"].isin(query_attributes)].index).reset_index(drop=True)
        return rfds

    @staticmethod
    def sort_by_decresing_nan_incresing_threshold(rfds_df: pd.DataFrame, query: dict) -> pd.DataFrame:
        '''
        Sorts the RFDs DataFrame by decreasing number of NaNs and increasing threshold values of query attributes.
        :param rfds_df: the Relaxed Functional Dependencies DataFrame to sort.
        :param query: the query containing the attributes for sorting.
        :return: the sorted RFDs DataFrame.
        '''
        query_attributes = list(query.keys())

        nan_count = "NaNs"
        kwargs = {nan_count: lambda x: x.isnull().sum(axis=1)}
        rfds = rfds_df.assign(**kwargs)

        sorting_cols = [nan_count]
        ascending = [False]

        sorting_cols.extend(query_attributes)
        ascending.extend([True for _ in query_attributes])
        rfds = rfds.sort_values(by=sorting_cols,
                                ascending=ascending,
                                na_position="first").reset_index(drop=True).drop(nan_count, axis=1)

        return rfds

    @staticmethod
    def sort_by_increasing_threshold(rfds_df: pd.DataFrame, data_set: pd.DataFrame, query: dict) -> pd.DataFrame:
        '''
        Sorts the Relaxed Functional Dependencies DataFrame
        by increasing threshold value of the query and non-query attributes.
        :param rfds_df: the Relaxed Functional Dependencies DataFrame to sort.
        :param data_set: the data set which the RFDs refers to.
        :param query: the query containing the attributes for sorting.
        :return: the sorted Relaxed Functional Dependencies DataFrame.
        '''
        query_attributes = list(query.keys())
        sorting_attributes = [attr for attr in query_attributes]
        ascending = [True for _ in query_attributes]

        data_set_attributes = list(data_set)

        non_query_attributes = [attr for attr in data_set_attributes if attr not in query_attributes]
        shuffle(non_query_attributes)

        for attr in non_query_attributes:
            sorting_attributes.append(attr)
            ascending.append(True)

        return rfds_df.sort_values(by=sorting_attributes,
                                   ascending=ascending,
                                   na_position="last").reset_index(drop=True)

    @staticmethod
    def rfd_to_string(rfd: dict) -> str:
        '''
        Converts the Relaxed Functional Dependency to a human readable string representation.
        :param rfd: the Relaxed Functional Dependency to convert.
        :return: a human readable string representation of the Relaxed Functional Dependency.
        '''
        string = ""
        string += "".join(["" if key == "RHS" or key == rfd["RHS"] or np.isnan(val) else "(" + key + " <= " + str(
            val) + ") " for key, val in rfd.items()])
        string += "---> ({} <= {})".format(rfd["RHS"], rfd[rfd["RHS"]])
        return string

    @staticmethod
    def query_dict_to_expr(query: dict) -> str:
        '''
        Converts the query dictionary to the string format required by Pandas.DataFrame.Query() method.
        :param query: the Query dictionary to convert.
        :return: the string format corresponding to the query dictionary.
        '''
        expr = " and ".join(
            ["{} == {}".format(k, v) if not isinstance(v, str) else "{} == '{}'".format(k, v) for k, v in
             query.items()])
        return expr

    @staticmethod
    def extend_query_ranges(query: dict, rfd: dict, data_set: pd.DataFrame = None) -> dict:
        '''
        Given a query and an RFD, extends the query attributes range
        by the corresponding threshold contained in the RFD.
        If some of the query attributes are of type string, the full DataFrame
        is needed to calculate the list of strings similar to the attribute value.
        :param query: The query to be extended.
        :param rfd: The RFD containing the thresholds to apply.
        :param data_set: The full DataFrame to query.
        :return: the extended query.
        '''

        for key, val in query.items():
            if key in rfd:
                threshold = rfd[key]

                if threshold > 0.0:
                    if isinstance(val, int) or isinstance(val, float):
                        val_range = range(int(val - threshold), int(val + threshold + 1))
                        query[key] = list(val_range)
                    elif isinstance(val, str):
                        source = val
                        simil_string = QueryRelaxer.similar_strings(source=source, data=data_set, col=key,
                                                                    threshold=threshold)
                        query[key] = simil_string

        return query

    @staticmethod
    def similar_strings(source: str, data: pd.DataFrame, col: str, threshold: int) -> list:
        '''
        Returns a list of strings, from the column col of data DataFrame,
        that are similar to the source string with an edit distance of at most threshold.
        :param source: the string against which to compute the edit distances.
        :param data: the DataFrame containing the string values.
        :param col: the DataFrame column containing the string values.
        :param threshold: the maximum edit distance between source and another string.
        :return: the list of strings similar to source.
        '''

        return data[data[col].apply(lambda word: int(editdistance.eval(source, word)) <= threshold)][
            col].tolist()

    @staticmethod
    def extract_value_lists(df: pd.DataFrame, columns: list):
        '''
        Extracts values of given columns from thd DataFrane and returns them as a
        Dictionary of value lists.
        :param df: The DataFrame from which to extract values.
        :param columns: The columns we are interested in extracting values.
        :return: A Dictionary of lists containing the values for the corresponding columns.
        '''
        dictionary = {}
        for col in columns:
            # duplicates removed too.
            dictionary[col] = list(set(df[col].tolist()))
            dictionary[col].sort()

        return dictionary
