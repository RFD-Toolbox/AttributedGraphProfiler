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


def main(args):
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

    rfds: pd.DataFrame = QueryRelaxer.drop_query_nan(rfds_df, query)
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
        print("\nChoosen RFD:\n", choosen_rfd)
        print("\nRFD:\n", QueryRelaxer.rfd_to_string(choosen_rfd))

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
        print("Query Extended Result Set:\n ", query_extended_res_set)

        # ++++++++++++++++++++++++RELAXING ROW BY ROW+++++++++++++++++++++++++++
        rows_df_list = Slicer.slice(query_extended_res_set)

        relaxing_attributes = [col for col in list(data_set_df)
                               if col not in query.keys() and not np.isnan(choosen_rfd[col])]
        # print("RELAXING ATTRIBUTES:\n", relaxing_attributes)

        print("\n" + "+" * 35 + "Slices..." + "+" * 35)

        all_row_values_dict = {}

        current_row = 0
        for sl in rows_df_list:
            row_values = QueryRelaxer.extract_value_lists(sl, relaxing_attributes)

            relaxing_values_extended = {}
            for attr, lst in row_values.items():
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
                # print("RELAXING VALUES EXTENDED[{}]:".format(attr), relaxing_values_extended[attr])
                relaxing_values_extended[attr].sort()

            all_row_values_dict[current_row] = relaxing_values_extended

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

        # relaxing_values_list = QueryRelaxer.extract_value_lists(query_extended_res_set, relaxing_attributes)

        # print("\nRelaxing values list: ", relaxing_values_list)

        # print("\nRFD:\n", QueryRelaxer.rfd_to_string(choosen_rfd))



        # print("Relaxing values extended dict: ", relaxing_values_extended)
        final_expr = ""
        last_keys = list(all_row_values_dict.keys())[-1]
        for key, values in all_row_values_dict.items():
            # RELAXED QUERY RHS ONLY
            relaxed_query = values

            # print("Relaxed Query: ", relaxed_query)
            relaxed_query_expr = QueryRelaxer.query_dict_to_expr(relaxed_query)
            # print("Relaxed Query expr: ", relaxed_query_expr)
            final_expr += relaxed_query_expr
            if key is not last_keys:
                final_expr += " or "

        print("FINAL EXPRESSION:", final_expr)
        relaxed_result_set = data_set_df.query(final_expr)
        # reset index
        relaxed_result_set.reset_index(inplace=True, level=0, drop=True)

        print("\nRelaxed Result Set:\n", relaxed_result_set)

        original_query_result_set_size = query_res_set.shape[0]
        relaxed_query_result_set_size = relaxed_result_set.shape[0]
        full_data_set_size = data_set_df.shape[0]
        original_to_relaxed_ratio = None
        if original_query_result_set_size == 0:
            original_to_relaxed_ratio = 1.0
        else:
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

    ######JSON###########
    rel_query_json = json.dumps(BEST_RELAXED_QUERY)
    #print("REL_QUERY_JSON:", rel_query_json)

    loaded_rel_query_dict = json.loads(rel_query_json)
    #print("Loaded REL query JSON:", loaded_rel_query_dict)
    #print("Type of Loaded REL query JSON:", type(loaded_rel_query_dict))

    relaxed_query_path = arguments.out
    if relaxed_query_path is not None:
        with open(relaxed_query_path, 'w') as fp:
            json.dump(BEST_RELAXED_QUERY, fp)


if __name__ == "__main__":
    main(sys.argv[1:])
