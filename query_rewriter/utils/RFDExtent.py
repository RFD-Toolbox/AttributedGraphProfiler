from pandas import DataFrame

from query_rewriter.model.RFD import RFD
from numpy import ndarray, array, bitwise_and
import networkx as nx

from query_rewriter.utils.DiffDataFrame import DiffDataFrame
from pandas.compat import reduce


class RFDExtent:
    @staticmethod
    def extent_indexes(data_frame: DataFrame, rfd: RFD):
        '''
        Returns the extent's indexes of the RFD.
        :return:
        '''

        # https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression#26853961
        rfd_thresholds: dict = {**rfd.get_left_hand_side(), **rfd.get_right_hand_side()}

        lhs = rfd.get_left_hand_side()
        rhs = rfd.get_right_hand_side()

        lhs_keys = lhs.keys()
        rhs_keys = rhs.keys()

        # https://stackoverflow.com/questions/1720421/how-to-concatenate-two-lists-in-python#answer-35631185
        rfd_columns = [*lhs_keys, *rhs_keys]

        rfd_columns_index: dict = {value: position for (position, value) in enumerate(rfd_columns)}

        rows, columns = data_frame.shape

        # Calculate all possible differences.
        # This is an O(N^2) operation and may be costly in terms of time and memory.
        # dist: ndarray = np.abs(rfd_columns_data[:, None] - rfd_columns_data)

        full_dist = DiffDataFrame.full_diff(data_frame[rfd_columns])

        dist: ndarray = array(
            [[full_dist.iloc[row1 * rows + row2] for row2 in range(0, rows)] for row1 in range(0, rows)])

        # Identify the suitable pairs of rows:
        # im: ndarray = (dist[:, :, 0] <= 2) & (dist[:, :, 1] <= 0) & (dist[:, :, 2] <= 1)

        conditions_arrays: ndarray = [(dist[:, :, rfd_columns_index[column]] <= rfd_thresholds[column])
                                      for column in rfd_columns]

        adjacency_matrix: ndarray = array(reduce(lambda a, b: bitwise_and(a, b), conditions_arrays))

        # Use them as an adjacency matrix and construct a graph.
        # The graph nodes represent rows in the original dataframe.
        # The nodes are connected if the corresponding rows are in the RFD:

        graph = nx.from_numpy_matrix(adjacency_matrix)

        max_clique = max(nx.clique.find_cliques(graph), key=len)
        df: DataFrame = data_frame.loc[max_clique, :]

        # percentage = round((df.shape[0] / self.rows_count) * 100)
        # current.setText(self.EXTENT, str(percentage) + "%")

        df_indexes = df.index.values.tolist()

        # self.pandas_model.update_data(self.data_frame)

        '''self.rfd_data_set_table.clearSelection()
        for index in df_indexes:
            self.rfd_data_set_table.selectRow(index)'''

        return df_indexes
