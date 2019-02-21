import pandas as pd

from pandas import DataFrame, Series
import numpy as np
import loader.levenshtein_wrapper as lw
from nltk.corpus import wordnet as wn


class DiffDataFrame:
    sysnset_dict: dict = {}
    semantic_diff_dict = {}

    @staticmethod
    def full_diff(data_frame: DataFrame):
        rows, columns = data_frame.shape

        distance_df = DataFrame(columns=data_frame.columns.tolist(),
                                index=list(range(0, rows * rows)),
                                dtype=float)

        ops = DiffDataFrame.map_types_to_distance_function(data_frame)

        k = 0

        for i in range(0, rows):
            row_i: Series = data_frame.iloc[i]

            for j in range(0, rows):  # iterate on each pair of rows
                if i == j:
                    diff_ij = [0 for _ in range(0, columns)]
                    # distance_df.iloc[k] = diff_ij
                    # k += 1
                else:
                    row_j: Series = data_frame.iloc[j]
                    diff_ij = [np.absolute(diff_function(a, b)) for a, b, diff_function in
                               list(zip(*[np.array(row_i), np.array(row_j), ops]))]

                try:
                    distance_df.iloc[k] = diff_ij
                    k += 1
                except IndexError as iex:
                    print("Index ", k, " out of bound")
                    print(iex)

        return distance_df

    @staticmethod
    def map_types_to_distance_function(data_frame: DataFrame, semantic=True):
        """
        For each attribute, find a distance function according to its type. According to the value
        of the instance variable semantic, the function will use a appropriate mapping function.
        :returns: a list containing one distance function for each data frame's column
        :rtype: list
        """
        if semantic:
            # iterate over columns
            types = np.array([DiffDataFrame.semantic_diff_criteria(col)
                              for col_label, col in data_frame.iteritems()])
        else:
            types = np.array([DiffDataFrame.diff_criteria(col)
                              for col_label, col in data_frame.iteritems()])
        return types.tolist()

    @staticmethod
    def diff_criteria(col: Series):
        """
        Given an attribute's column, check its type and return the appropriate distance function.
        The difference between __semantic_diff_criteria__ and this method is that this method will use the
        edit distance for strings.
        If the type of a function is an object, it will use the edit distance for this attribute.
        If the type of an attribute is not valid, the method will raise an exception.
        :param col_label: the column's label
        :type col_label: str
        :param col: the attribute's values
        :type col: pandas.core.series.Series
        :return: a distance function
        :rtype: method
        :raise: Exception, when the attribute's type is not valid
        """
        numeric = {np.dtype('int'), np.dtype('int32'), np.dtype('int64'), np.dtype('float'), np.dtype('float64')}
        string = {np.dtype('string_'), np.dtype('object')}
        if col.dtype in numeric:
            return DiffDataFrame.number_diff
        elif col.dtype in string:
            return DiffDataFrame.edit_distance
        elif np.issubdtype(col.dtype, np.datetime64):
            return DiffDataFrame.date_diff
        else:
            raise Exception("Unrecognized dtype")

    @staticmethod
    def semantic_diff_criteria(column: Series):
        """
        Given an attribute's column, check its type and return the appropriate distance function.
        The difference between __diff_criteria__ and this method is that this method will use the
        semantic difference for strings and the edit distance as fallback when the Wordnet lookup fails.
        If the type of a function is an object, it will use the semantic difference for this attribute.
        If the type of an attribute is not valid, the method will raise an exception.
        :param column: the attribute's values
        :type column: pandas.core.series.Series
        :return: a distance function
        :rtype: method
        :raise: Exception, when the attribute's type is not valid
        """
        numeric = {np.dtype('int'), np.dtype('int32'), np.dtype('int64'), np.dtype('float'), np.dtype('float64')}
        string = {np.dtype('string_'), np.dtype('object')}
        if column.dtype in numeric:
            return DiffDataFrame.number_diff
        elif column.dtype in string:
            for val in column:
                if isinstance(val, float) and np.isnan(val):
                    continue
                if val not in DiffDataFrame.sysnset_dict:
                    s = wn.synsets(val)
                    if len(s) > 0:
                        DiffDataFrame.sysnset_dict[val] = s[
                            0]  # NOTE terms added from later dropped columns are kept in dict
                    else:
                        return DiffDataFrame.edit_distance
            return DiffDataFrame.semantic_diff
        elif np.issubdtype(column.dtype, np.datetime64):
            return DiffDataFrame.date_diff
        else:
            raise Exception("Unrecognized dtype")

    @staticmethod
    def number_diff(a: float, b: float):
        """
        Computes the aritmetic difference on given floats a and b.
        If one of the two parameter is NaN, the distance returned will be infinity.
        If both are NaN, the distance returned will be 0.
        :param a: first term
        :type a: float
        :param b: second term
        :type b: float
        :return: difference in float
        :rtype float
        """
        if (isinstance(a, float) and np.isnan(a)) and (isinstance(b, float) and np.isnan(b)):
            return 0
        if isinstance(a, float) and np.isnan(a):
            return np.inf
        if isinstance(b, float) and np.isnan(b):
            return np.inf
        return a - b

    @staticmethod
    def edit_distance(a: str, b: str):
        """
        Computes the Levenshtein distance between two strings a and b.
        If one of the two parameter is NaN, the distance returned will be infinity.
        If both are NaN, the distance returned will be 0.
        :param a: first term
        :type a: str or float for NaN value
        :param b: second term
        :type b: str or float for NaN value
        :return: the edit distance between a and b
        :rtype float
        """
        if (isinstance(a, float) and np.isnan(a)) and (isinstance(b, float) and np.isnan(b)):
            return 0
        if isinstance(a, float) and np.isnan(a):
            return np.inf
        if isinstance(b, float) and np.isnan(b):
            return np.inf
        if a == b:
            return 0
        return lw.lev_distance(str(a), str(b))

    @staticmethod
    def semantic_diff(a: object, b: object):
        """
        Computes the semantic difference, as 1 - path similarity, between two string.
        After calculated, the semantic difference will be stored in the dictionary semantic_diff_dic so when this distance is again requested it will
        not be calculated a second time.
        The path similarity is calculated by using WordNet.
        If one of the two parameter is NaN, the distance returned will be infinity.
        If both are NaN, the distance returned will be 0.
        :param a: first term
        :type a: str or float for NaN value
        :param b: second term
        :type b: str or float for NaN value
        :return: the semantic difference between a and b
        :rtype float
        """
        if (isinstance(a, float) and np.isnan(a)) and (isinstance(b, float) and np.isnan(b)):
            return 0
        if isinstance(a, float) and np.isnan(a):
            return np.inf
        if isinstance(b, float) and np.isnan(b):
            return np.inf
        if a == b:
            return 0
        if (a, b) in DiffDataFrame.semantic_diff_dict:
            return DiffDataFrame.semantic_diff_dict[(a, b)]
        elif (b, a) in DiffDataFrame.semantic_diff_dict:
            return DiffDataFrame.semantic_diff_dict[(b, a)]
        else:
            t = wn.path_similarity(DiffDataFrame.sysnset_dict[a], DiffDataFrame.sysnset_dict[b])
            DiffDataFrame.semantic_diff_dict[(a, b)] = 1 - t
            DiffDataFrame.semantic_diff_dict[(b, a)] = 1 - t
            return 1 - t

    @staticmethod
    def date_diff(a: pd.Timestamp, b: pd.Timestamp):
        """
        Computes the aritmetic difference on given dates a and b.
        If one of the two parameter is NaT, the distance returned will be infinity.
        If both are NaT, the distance returned will be 0.
        :param a: first date
        :type a: pandas.tslib.Timestamp or float for NaN value
        :param b: comparison date
        :type b: pandas.tslib.Timestamp or float for NaN value
        :return: difference in days
        :rtype float
        """
        if (a is pd.NaT) and (b is pd.NaT):
            return 0
        if a is pd.NaT:
            return np.inf
        if b is pd.NaT:
            return np.inf
        delta = a - b
        return int(delta / np.timedelta64(1, 'D'))
