import pandas as pandas


class Splitter:
    @staticmethod
    def split(distance_matrix: pandas.DataFrame, csv_rows: int) -> dict:
        '''
        Splits the given distance matrix into the groups it is composed of.
        Each group with id equals to G contains the portion of the distance
        matrix with the distances, for each column, between row G and all
        the subsequent rows.
        :param distance_matrix: the distance matrix to split into groups.
        :param csv_rows: the number of rows (header excluded) of the original
        CSV file to which tha distance matrix refers.
        :return: a dictionary of the form (id: int --> group: pandas.DataFrame).
        '''
        groups = {}
        group_begin_index = 0
        for row_num in range(0, csv_rows - 1):
            group_end_index = group_begin_index + (csv_rows - 1 - row_num)
            groups[row_num] = distance_matrix[group_begin_index:group_end_index]
            group_begin_index = group_end_index

        return groups
