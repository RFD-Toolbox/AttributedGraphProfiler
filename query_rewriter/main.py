import sys
import argparse
import logging
import ast
from query_rewriter.io.csv.io import CSVInputOutput
from query_rewriter.query.relaxer import QueryRelaxer
from query_rewriter.io.rfd import store_load_rfds
import pandas as pd
import numpy as np
import json
from query_rewriter.query.slicer import Slicer
import copy
import time


def main(args):
    '''
    This is the main method, the core of our program
    :param args: some params read by command line
    :return: None
    '''
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    logging.basicConfig(filemode='w', level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="path of dataset", required=True)
    parser.add_argument("-r", "--rfds", help="optional path of rfds")
    parser.add_argument("-q", "--query", help="query", required=True)
    parser.add_argument("-n", "--numb_test", help="number of tests", default=1, type=int)
    parser.add_argument("-o", "--out", help="query output path", type=str)
    arguments = parser.parse_args()

    start_process(arguments)


def start_process(arguments):
    '''
    In this method we encapsulated all process of Query Relaxing
    :param arguments: arguments passed by command line
    :return: some control sentence and create some file
    '''
    #############################################################################################
    # __________________________________________DATA SET________________________________________#
    #############################################################################################
    csv_io = CSVInputOutput()
    data_set_path = arguments.path
    data_set_df = csv_io.load(data_set_path)
    # print("Dataset:\n", data_set_df)

    #############################################################################################
    # ____________________________________________QUERY_________________________________________#
    #############################################################################################
    original_query: dict = ast.literal_eval(arguments.query)
    print("Query is : ", original_query)
    print(type(original_query))

    #############################################################################################
    # ____________________________________________RFDs__________________________________________#
    #############################################################################################
    rfds_path = arguments.rfds
    if rfds_path is None:
        rfds_path = data_set_path.replace(".csv", "_rfds.csv")
        rfds_path = rfds_path.replace("dataset/", "dataset/rfds/")
        rfds_search_start_time = time.time()
        store_load_rfds.discover_rfds(data_set_path, rfds_path)
        rfds_search_end_time = time.time()
        print("RFDs search executed in ", int((rfds_search_end_time - rfds_search_start_time) * 1000))
    init_time = time.time()
    rfds_df = csv_io.load(rfds_path)
    # print("RFDs:\n", rfds_df)

    rfds: pd.DataFrame = QueryRelaxer.drop_query_nan(rfds_df, original_query)
    # print("Dropped query N/A:\n", rfds)

    rfds = QueryRelaxer.drop_query_rhs(rfds, original_query)
    # print("Dropped query RHS:\n", rfds)

    rfds = QueryRelaxer.sort_by_decresing_nan_incresing_threshold(rfds, original_query)
    # print("Sorted by decreasing NaNs & increasing query threshold attributes:\n", rfds)

    rfds_dict_list = rfds.to_dict(orient="records")

    #############################################################################################
    # __________________________________________RELAX___________________________________________#
    #############################################################################################

    #############################################################################################
    # ______________________________________ORIGINAL QUERY______________________________________#
    #############################################################################################
    print("#" * 200)
    print("@" * 90 + " __ORIGINAL QUERY__ " + "@" * 90)
    print("#" * 200)
    print("OriginalQuery: ", original_query)
    original_query_expression = QueryRelaxer.query_dict_to_expr(original_query)
    print("OriginalQuery expr: ", original_query_expression)
    original_query_result_set = data_set_df.query(original_query_expression)
    print("Original Query Result Set:\n", original_query_result_set)

    ORIGINAL_QUERY_DATA_SET = original_query_result_set
    ORIGINAL_QUERY_DATA_SET_ROWS \
        = original_query_result_set.shape[0]

    BEST_RFD = None
    BEST_RFD_DATA_SET_SIZE = np.inf
    BEST_RFD_DATA_SET = None
    BEST_RELAXED_QUERY = None
    number_of_rfds_to_test: int = np.clip(a=arguments.numb_test, a_min=1, a_max=len(rfds_dict_list))

    for i in range(0, number_of_rfds_to_test):
        # print("#" * 200)
        # print("@" * 90 + " RELAX " + str(i) + " @" * 90)
        # print("#" * 200)
        chosen_rfd = rfds_dict_list[i]
        # print("\nChosen RFD:\n", chosen_rfd)
        # print("\nRFD:\n", QueryRelaxer.rfd_to_string(chosen_rfd))

        ################################################
        # @@@@@@@@@@@@__EXTENDED QUERY__@@@@@@@@@@@@@@@#
        ################################################
        print("#" * 200)
        print("@" * 90 + " __EXTENDED QUERY__ " + "@" * 90)
        print("#" * 200)
        extended_query: dict = QueryRelaxer.extend_query_ranges(copy.deepcopy(original_query),
                                                                copy.deepcopy(chosen_rfd),
                                                                data_set_df)
        print("Query extended: ", extended_query)
        extended_query_expression = QueryRelaxer.query_dict_to_expr(extended_query)
        print("Query Extended Expr: ", extended_query_expression)

        query_extended_res_set = data_set_df.query(extended_query_expression)
        print("Query Extended Result Set:\n ", query_extended_res_set)

        # ++++++++++++++++++++++++RELAXING ROW BY ROW+++++++++++++++++++++++++++
        rows_df_list = Slicer.slice(query_extended_res_set)

        relaxing_attributes = [col for col in list(data_set_df)
                               if col not in original_query.keys() and not np.isnan(chosen_rfd[col])]
        print("RELAXING ATTRIBUTES:\n", relaxing_attributes)

        print("\n" + "+" * 35 + "Slices..." + "+" * 35)

        all_row_values_dict = {}

        current_row = 0
        for row in rows_df_list:
            row_values = QueryRelaxer.extract_value_lists(row, relaxing_attributes)

            relaxing_values_extended = {}
            for attr, lst in row_values.items():
                relaxing_values_extended[attr] = []
                threshold = chosen_rfd[attr]

                for val in lst:
                    if isinstance(val, int) or isinstance(val, float):
                        for item in range(int(val - threshold), int(val + threshold + 1)):
                            relaxing_values_extended[attr].append(item)
                    elif isinstance(val, str):
                        simil_strings = QueryRelaxer.similar_strings(val, data_set_df, attr, threshold)

                        for string in simil_strings:
                            relaxing_values_extended[attr].append(string)

                relaxing_values_extended[attr] = list(set(relaxing_values_extended[attr]))
                # print("RELAXING VALUES EXTENDED[{}]:".format(attr), relaxing_values_extended[attr])
                relaxing_values_extended[attr].sort()

            all_row_values_dict[current_row] = relaxing_values_extended

        ################################################
        # @@@@@@@@@@@@__RELAXED QUERY__@@@@@@@@@@@@@@@#
        ################################################
        print("#" * 200)
        print("@" * 90 + " __RELAXED QUERY__ " + "@" * 90)
        print("#" * 200)

        # print("Relaxing values extended dict: ", relaxing_values_extended)
        final_expr = ""
        last_key = None

        if bool(all_row_values_dict):
            last_key = list(all_row_values_dict.keys())[-1]

            for key, values in all_row_values_dict.items():
                # RELAXED QUERY RHS ONLY
                relaxed_query = values

                # print("Relaxed Query: ", relaxed_query)
                relaxed_query_expr = QueryRelaxer.query_dict_to_expr(relaxed_query)
                # print("Relaxed Query expr: ", relaxed_query_expr)
                final_expr += relaxed_query_expr
                if key is not last_key:
                    final_expr += " or "

            # print("FINAL EXPRESSION:", final_expr)
            relaxed_result_set = data_set_df.query(final_expr)
            # reset index
            relaxed_result_set.reset_index(inplace=True, level=0, drop=True)

            # print("\nRelaxed Result Set:\n", relaxed_result_set)

            relaxed_query_result_set_size = relaxed_result_set.shape[0]

            if ORIGINAL_QUERY_DATA_SET_ROWS < relaxed_query_result_set_size < BEST_RFD_DATA_SET_SIZE:
                BEST_RFD = chosen_rfd
                BEST_RFD_DATA_SET = relaxed_result_set
                BEST_RELAXED_QUERY = final_expr  # relaxed_query
                BEST_RFD_DATA_SET_SIZE = relaxed_query_result_set_size

    end_time = time.time()
    print("#" * 50 + "THE WINNER IS:" + "#" * 50)
    print("BEST_RFD:\n", BEST_RFD)
    print("BEST_RFD:\n", QueryRelaxer.rfd_to_string(BEST_RFD))
    print("BEST_RELAXED_QUERY:\n", BEST_RELAXED_QUERY)
    print("BEST_RFD_DATA_SET:\n", BEST_RFD_DATA_SET)
    print("BEST_RFD_DATA_SET_SIZE:\n", BEST_RFD_DATA_SET_SIZE)
    timing = int((end_time - init_time) * 1000)
    print("Query Relaxation executed in ", timing, "ms")
    ######JSON###########
    rel_query_json = json.dumps(BEST_RELAXED_QUERY)
    # print("REL_QUERY_JSON:", rel_query_json)

    loaded_rel_query_dict = json.loads(rel_query_json)

    relaxed_query_path = arguments.out
    if relaxed_query_path is not None:
        with open(relaxed_query_path, 'w') as fp:
            json.dump(BEST_RELAXED_QUERY, fp)
    with open("test.txt", "a") as fp:
        fp.write(
            arguments.path + "    " + arguments.query + "    " + str(arguments.numb_test) + "    " + str(
                timing) + "ms\n")
        fp.close()


if __name__ == "__main__":
    main(sys.argv[1:])
