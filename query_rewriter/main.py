import sys
import argparse
import logging
import ast
from query_rewriter.io.csv.io import CSVInputOutput
from query_rewriter.query.relaxer import QueryRelaxer
from query_rewriter.io.rfd import store_load_rfds


def main(args):
    path_dataset = None
    path_rfds = None
    query_dict = {}
    numb_rfd_test = None
    logging.basicConfig(filemode='w', level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="path of dataset", required=True)
    parser.add_argument("-r", "--rfds", help="optional path of rfds")
    parser.add_argument("-q", "--query", help="query", required=True)
    parser.add_argument("-n", "--numb_test", help="number of tests", default=0)
    arguments = parser.parse_args()
    logging.info(arguments)
    start_process(arguments)


def start_process(arguments):
    csv_io = CSVInputOutput()
    dataset_path = arguments.path
    rfds_path = arguments.rfds
    if rfds_path is None:
        rfds_path = "dataset/rfds/now_in_use.csv"
        store_load_rfds.search_rfds(dataset_path, "dataset/rfds/now_in_use.csv")
        '''calculate rfd from file '''
    query = ast.literal_eval(arguments.query)
    data_set_df = csv_io.load(dataset_path)
    logging.info("Dataset: \n%s", data_set_df)

    logging.info("Query is : %s", query)
    insert_space(query)

    rfds_df = csv_io.load(rfds_path)
    logging.info("RFDs:\n%s", rfds_df)

    query_relaxer = QueryRelaxer(query=query, rfds_df=rfds_df, data_set_df=data_set_df)
    df = query_relaxer.drop_query_na()
    logging.info("Dropped query N/A:\n%s", df)

    df = query_relaxer.drop_query_rhs()
    logging.info("Dropped query RHS:\n%s", df)

    df = query_relaxer.sort_nan_query_attributes()
    logging.info("Sorted by NaNs and query attributes:\n%s", df)

    rfds_dict_list = df.to_dict(orient="records")
    logging.info("RFD dict list:")
    for dct in rfds_dict_list:
        logging.info(dct)

    #############################################################################################
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@RELAX@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #############################################################################################
    logging.info("#" * 200)
    logging.info("@" * 90 + " RELAX " + "@" * 90)
    logging.info("#" * 200)
    choosen_rfd = rfds_dict_list[0]
    logging.info("\nChoosen RFD:\n%s", choosen_rfd)
    logging.info("\nRFD:\n%s", QueryRelaxer.rfd_to_string(choosen_rfd))

    rhs_column = choosen_rfd["RHS"]
    logging.info("\nRHS column: %s", rhs_column)

    ################################################
    # @@@@@@@@@@@@__ORIGINAL QUERY__@@@@@@@@@@@@@@@#
    ################################################
    logging.info("#" * 200)
    logging.info("@" * 90 + " __ORIGINAL QUERY__ " + "@" * 90)
    logging.info("#" * 200)
    logging.info("OriginalQuery: %s", query)
    query_expr = QueryRelaxer.query_dict_to_expr(query)
    logging.info("OriginalQuery expr: %s", query_expr)
    query_res_set = data_set_df.query(query_expr)
    logging.info("Original Query Result Set:\n%s", query_res_set)
    ################################################
    # @@@@@@@@@@@@__EXTENDED QUERY__@@@@@@@@@@@@@@@#
    ################################################
    logging.info("#" * 200)
    logging.info("@" * 90 + " __EXTENDED QUERY__ " + "@" * 90)
    logging.info("#" * 200)
    query_extended = QueryRelaxer.extend_query_ranges(query, choosen_rfd, data_set_df)
    logging.info("Query extended: %s", query_extended)
    query_extended_expr = QueryRelaxer.query_dict_to_expr(query_extended)
    logging.info("Query Extended Expr: %s", query_extended_expr)
    query_extended_res_set = data_set_df.query(query_extended_expr)
    logging.info("Query Extended Result Set:\n %s", query_extended_res_set)
    ################################################
    # @@@@@@@@@@@@__RELAXED QUERY__@@@@@@@@@@@@@@@#
    ################################################
    logging.info("#" * 200)
    logging.info("@" * 90 + " __RELAXED QUERY__ " + "@" * 90)
    logging.info("#" * 200)

    rhs_values_list = query_extended_res_set[rhs_column].tolist()
    rhs_values_list.sort()
    logging.info("\nRHS values: %s", rhs_values_list)
    # removing duplicates
    rhs_values_list = list(set(rhs_values_list))
    # sorting
    rhs_values_list.sort()
    logging.info("\nRHS values no duplicates: %s", rhs_values_list)

    logging.info("\nRFD:\n%s", QueryRelaxer.rfd_to_string(choosen_rfd))
    rhs_threshold = choosen_rfd[choosen_rfd["RHS"]]
    logging.info("RHS threshold: %s", rhs_threshold)
    rhs_extended_values = []
    for x in rhs_values_list:
        if isinstance(x, int):
            for y in range(int(x - rhs_threshold), int(x + rhs_threshold + 1)):
                rhs_extended_values.append(y)
        else:
            simil_string = QueryRelaxer.similar_strings(x, data_set_df, rhs_column, rhs_threshold)
            for a in simil_string:
                rhs_extended_values.append(a)

    rhs_extended_values.sort()
    logging.info("RHS extended values: %s", rhs_extended_values)

    rhs_extended_values_no_duplicates = list(set(rhs_extended_values))
    rhs_extended_values_no_duplicates.sort()
    logging.info("RHS extended values no duplicates: %s", rhs_extended_values_no_duplicates)

    relaxed_query = {rhs_column: rhs_extended_values_no_duplicates}
    logging.info("Relaxed Query: %s", relaxed_query)
    relaxed_query_expr = QueryRelaxer.query_dict_to_expr(relaxed_query)
    logging.info("Relaxed Query expr: %s", relaxed_query_expr)

    relaxed_result_set = data_set_df.query(relaxed_query_expr)
    logging.info("\nRelaxed Result Set:\n%s", relaxed_result_set)


def insert_space(query):
    for key, value in query.items():
        query[key] = value.replace('$', ' ')
    logging.info("Query with space is : %s", query)
    return query


if __name__ == "__main__":
    main(sys.argv[1:])
