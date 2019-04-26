from numpy import diff, NaN, isnan
from pandas import DataFrame
from query_rewriter.io.rfd.store_load_rfds import diff

from query_rewriter.model.RFD import RFD


class Transformer:
    @staticmethod
    def rfd_data_frame_to_rfd_list(rfd_df: DataFrame, header: list) -> list:
        rfds: list[RFD] = list()

        rfd_df_header = list(rfd_df)
        rhs_column = diff(header, rfd_df_header)[0]

        lhs_columns = diff(header, rhs_column)

        rfd_df.rename(columns={"RHS": rhs_column}, inplace=True)

        for index, row in rfd_df.iterrows():

            lhs: list[dict] = {key: row[key] for key in lhs_columns if not isnan(row[key])}
            rhs: list[dict] = {rhs_column: row[rhs_column]}

            rfd = RFD(lhs, rhs)

            rfds.append(rfd)

        return rfds
