import sys
import argparse
import logging
import ast
from query_rewriter.io.csv.io import CSVInputOutput
from query_rewriter.query.relaxer import QueryRelaxer
from query_rewriter.io.rfd import store_load_rfds
import pandas as pd
import numpy as np


def main(args):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    logging.basicConfig(filemode='w', level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="path of dataset", required=True)
    parser.add_argument("-r", "--rfds", help="optional path of rfds")
    parser.add_argument("-q", "--query", help="query", required=True)
    parser.add_argument("-n", "--numb_test", help="number of tests", default=1, type=int)
    arguments = parser.parse_args()
    start_process(arguments)


def start_process(arguments):
    csv_io = CSVInputOutput()
    dataset_path = arguments.path
    rfds_path = arguments.rfds
    if rfds_path is None:
        rfds_path = dataset_path.replace(".csv", "_rfds.csv")
        rfds_path = rfds_path.replace("dataset/", "dataset/rfds/")
        print(rfds_path)
        store_load_rfds.search_rfds(dataset_path, rfds_path)
    query = ast.literal_eval(arguments.query)
    data_set_df = csv_io.load(dataset_path)
    # print("Dataset:\n", data_set_df)

    print("Query is : ", query)

    rfds_df = csv_io.load(rfds_path)
    # print("RFDs:\n", rfds_df)

    rfds: pd.DataFrame = QueryRelaxer.drop_query_na(rfds_df, query)
    # print("Dropped query N/A:\n", rfds)

    rfds = QueryRelaxer.drop_query_rhs(rfds, query)
    # print("Dropped query RHS:\n", rfds)

    rfds = QueryRelaxer.sort_by_decresing_nan_incresing_threshold(rfds, query)
    # print("Sorted by decreasing NaNs & increasing query threshold attributes:\n", rfds)

    rfds_dict_list = rfds.to_dict(orient="records")

    #############################################################################################
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@RELAX@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #############################################################################################

    ################################################
    # @@@@@@@@@@@@__ORIGINAL QUERY__@@@@@@@@@@@@@@@#
    ################################################
    print("#" * 200)
    print("@" * 90 + " __ORIGINAL QUERY__ " + "@" * 90)
    print("#" * 200)
    print("OriginalQuery: ", query)
    query_expr = QueryRelaxer.query_dict_to_expr(query)
    print("OriginalQuery expr: ", query_expr)
    query_res_set = data_set_df.query(query_expr)
    print("Original Query Result Set:\n", query_res_set)

    ORIGINAL_QUERY_DATA_SET = query_res_set
    ORIGINAL_QUERY_DATA_SET_SIZE = query_res_set.shape[0]

    BEST_RFD = None
    BEST_RFD_DATA_SET_SIZE = np.inf
    BEST_RFD_DATA_SET = None
    BEST_RELAXED_QUERY = None

    for i in range(0, abs(min(len(rfds_dict_list), arguments.numb_test))):
        # print("#" * 200)
        # print("@" * 90 + " RELAX " + str(i) + "@" * 90)
        # print("#" * 200)
        choosen_rfd = rfds_dict_list[i]
        # print("\nChoosen RFD:\n", choosen_rfd)
        # print("\nRFD:\n", QueryRelaxer.rfd_to_string(choosen_rfd))

        rhs_column = choosen_rfd["RHS"]
        # print("\nRHS column: ", rhs_column)

        ################################################
        # @@@@@@@@@@@@__EXTENDED QUERY__@@@@@@@@@@@@@@@#
        ################################################
        # print("#" * 200)
        # print("@" * 90 + " __EXTENDED QUERY__ " + "@" * 90)
        # print("#" * 200)
        query_extended: dict = QueryRelaxer.extend_query_ranges(query, choosen_rfd, data_set_df)
        # print("Query extended: ", query_extended)
        query_extended_expr = QueryRelaxer.query_dict_to_expr(query_extended)
        # print("Query Extended Expr: ", query_extended_expr)

        query_extended_res_set = data_set_df.query(query_extended_expr)
        # print("Query Extended Result Set:\n ", query_extended_res_set)
        ################################################
        # @@@@@@@@@@@@__RELAXED QUERY__@@@@@@@@@@@@@@@#
        ################################################
        # print("#" * 200)
        # print("@" * 90 + " __RELAXED QUERY__ " + "@" * 90)
        # print("#" * 200)

        # start extracting values
        # print("#start extracting values")
        # print("\nChoosen RFD:\n", choosen_rfd)
        # print("\nRFD:\n", QueryRelaxer.rfd_to_string(choosen_rfd))
        relaxing_attributes = [col for col in list(data_set_df)
                               if col not in query.keys() and not np.isnan(choosen_rfd[col])]
        # print("RELAXING ATTRIBUTES:\n", relaxing_attributes)

        relaxing_values_list = extract_value_lists(query_extended_res_set, relaxing_attributes)

        # print("\nRelaxing values list: ", relaxing_values_list)

        # print("\nRFD:\n", QueryRelaxer.rfd_to_string(choosen_rfd))

        relaxing_values_extended = {}
        for attr, lst in relaxing_values_list.items():
            relaxing_values_extended[attr] = []
            threshold = choosen_rfd[attr]

            for val in lst:
                if isinstance(val, int) or isinstance(val, float):
                    for item in range(int(val - threshold), int(val + threshold + 1)):
                        relaxing_values_extended[attr].append(item)
                elif isinstance(val, str):
                    simil_strings = QueryRelaxer.similar_strings(val, data_set_df, attr, threshold)

                    for string in simil_strings:
                        relaxing_values_extended[attr].append(string)

            relaxing_values_extended[attr] = list(set(relaxing_values_extended[attr]))
            relaxing_values_extended[attr].sort()

        # print("Relaxing values extended dict: ", relaxing_values_extended)

        # RELAXED QUERY RHS ONLY
        relaxed_query = relaxing_values_extended

        # print("Relaxed Query: ", relaxed_query)
        relaxed_query_expr = QueryRelaxer.query_dict_to_expr(relaxed_query)
        # print("Relaxed Query expr: ", relaxed_query_expr)

        relaxed_result_set = data_set_df.query(relaxed_query_expr)
        # reset index
        relaxed_result_set.reset_index(inplace=True, level=0, drop=True)

        # print("\nRelaxed Result Set:\n", relaxed_result_set)

        original_query_result_set_size = query_res_set.shape[0]
        relaxed_query_result_set_size = relaxed_result_set.shape[0]
        full_data_set_size = data_set_df.shape[0]
        original_to_relaxed_ratio = relaxed_query_result_set_size / original_query_result_set_size
        original_to_relaxed_increment_rate = original_to_relaxed_ratio - 1
        relaxed_to_full_ratio = relaxed_query_result_set_size / full_data_set_size

        # print("original_query_result_set_size:", original_query_result_set_size)
        # print("relaxed_query_result_set_size:", relaxed_query_result_set_size)
        # print("full_data_set_size:", full_data_set_size)
        # print("original_to_relaxed_ratio:", original_to_relaxed_ratio)
        # print("original_to_relaxed_increment_rate:", original_to_relaxed_increment_rate, "%")
        # print("original_to_relaxed_increment_rate: +{:.0%}".format(original_to_relaxed_increment_rate))
        # print("relaxed_to_full_ratio: {:.0%}".format(relaxed_to_full_ratio))

        if ORIGINAL_QUERY_DATA_SET_SIZE < relaxed_query_result_set_size < BEST_RFD_DATA_SET_SIZE:
            BEST_RFD = choosen_rfd
            BEST_RFD_DATA_SET = relaxed_result_set
            BEST_RELAXED_QUERY = relaxed_query
            BEST_RFD_DATA_SET_SIZE = relaxed_query_result_set_size

    print("#" * 50 + "THE WINNER IS:" + "#" * 50)
    print("BEST_RFD:\n", QueryRelaxer.rfd_to_string(BEST_RFD))
    print("BEST_RELAXED_QUERY:\n", BEST_RELAXED_QUERY)
    print("BEST_RFD_DATA_SET:\n", BEST_RFD_DATA_SET)
    print("BEST_RFD_DATA_SET_SIZE:\n", BEST_RFD_DATA_SET_SIZE)


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


if __name__ == "__main__":
    main(sys.argv[1:])
