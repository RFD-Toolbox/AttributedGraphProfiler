from query_rewriter.utils.QueryRelaxer import QueryRelaxer
from query_rewriter.io.csv.csv_io import CSVInputOutput
import numpy as np
import pandas as pd
import editdistance


def rfd_to_string(rfd: dict) -> str:
    string = ""
    string += "".join(["" if key == "RHS" or key == rfd["RHS"] or np.isnan(val) else "(" + key + " <= " + str(
        val) + ") " for key, val in rfd.items()])
    string += "---> ({} <= {})".format(rfd["RHS"], rfd[rfd["RHS"]])
    return string


def query_dict_to_expr(query: dict) -> str:
    # expr = " and ".join(
    #     ["{} == {}".format(k, v) if not isinstance(v, str) else "{} == '{}'".format(k, v) for k, v in query.items()])
    last_keys = query.keys()[-1]
    print(last_keys)
    expr = ""
    for k, v in query.items():
        print(type(v))
        if isinstance(v, dict):
            expr + " {} >= v['{}'] and {} <= v['{}']".format(k, v['min'], k, v['max'])
        elif isinstance(v, [int, float]):
            expr + " {} == {}".format(k, v)
        elif isinstance(v, str):
            needle = k + ".str.contains('{}')".format(v)
            print("Like instance " + needle)
            expr + " {} == '{}'".format(k, needle)
        if k is not last_keys:
            expr + " and "
    print("FIXED expression")
    return expr


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
        print("{} : {}".format(key, val))
        if key in rfd:
            print(key + " in RFD")
            threshold = rfd[key]
            print("Threshold:", threshold)

            if threshold > 0.0:
                print("Threshold is positive:", threshold)
                if isinstance(val, int):
                    print(val, " is int...")
                    val_range = range(int(val - threshold), int(val + threshold + 1))
                    print("Range: ", list(val_range))
                    query[key] = list(val_range)
                elif isinstance(val, str):
                    print(val, " is string...")
                    source = val
                    simil_string = similar_strings(source=source, data=data_set, col=key, threshold=threshold)
                    print("Similar strings: ", simil_string)
                    query[key] = simil_string
            else:
                print("Threshold is not positive:", threshold)
    return query


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


# def query_rhs_rewrite(result_set: pd.DataFrame, rfd: dict)

def relax_query(csv_path: str, query: {}, rfds_path, numb_test):
    csv_io = CSVInputOutput()
    data_set_df = csv_io.load(csv_path)
    print("DataSet:\n", data_set_df, end="\n\n")

    print("Query:", query, end="\n\n")

    rfds_df = csv_io.load(rfds_path)
    print("RFDs:\n", rfds_df, end="\n\n")

    query_relaxer = QueryRelaxer(query=query, rfds_df=rfds_df, data_set_df=data_set_df)
    df = query_relaxer.drop_query_nan()
    print("Dropped query N/A:\n", df, end="\n\n")

    df = query_relaxer.drop_query_rhs()
    print("Dropped query RHS:\n", df, end="\n\n")

    df = query_relaxer.sort_by_decresing_nan_incresing_threshold()
    print("Sorted by NaNs and query attributes:\n", df, end="\n\n")

    rfds_dict_list = df.to_dict(orient="records")
    print("RFD dict list:")
    for dct in rfds_dict_list:
        print(dct)

    #############################################################################################
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@RELAX@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #############################################################################################
    print("#" * 200)
    print("@" * 90 + " RELAX " + "@" * 90)
    print("#" * 200)
    choosen_rfd = rfds_dict_list[0]
    print("\nChoosen RFD:\n", choosen_rfd)
    print("\nRFD:\n", rfd_to_string(choosen_rfd))

    rhs_column = choosen_rfd["RHS"]
    print("\nRHS column:", rhs_column)

    ################################################
    # @@@@@@@@@@@@__ORIGINAL QUERY__@@@@@@@@@@@@@@@#
    ################################################
    print("#" * 200)
    print("@" * 90 + " __ORIGINAL QUERY__ " + "@" * 90)
    print("#" * 200)
    print("OriginalQuery:", query)
    query_expr = query_dict_to_expr(query)
    print("OriginalQuery expr:", query_expr)
    query_res_set = data_set_df.query(query_expr)
    print("Original Query Result Set:\n", query_res_set)

    ################################################
    # @@@@@@@@@@@@__EXTENDED QUERY__@@@@@@@@@@@@@@@#
    ################################################
    print("#" * 200)
    print("@" * 90 + " __EXTENDED QUERY__ " + "@" * 90)
    print("#" * 200)
    query_extended = extend_query_ranges(query, choosen_rfd, data_set_df)
    print("Query extended: ", query_extended)
    query_extended_expr = query_dict_to_expr(query_extended)
    print("Query Extended Expr:", query_extended_expr)
    query_extended_res_set = data_set_df.query(query_extended_expr)
    print("Query Extended Result Set:\n", query_extended_res_set)

    ################################################
    # @@@@@@@@@@@@__RELAXED QUERY__@@@@@@@@@@@@@@@#
    ################################################
    print("#" * 200)
    print("@" * 90 + " __RELAXED QUERY__ " + "@" * 90)
    print("#" * 200)

    rhs_values_list = query_extended_res_set[rhs_column].tolist()
    rhs_values_list.sort()
    print("\nRHS values:", rhs_values_list)
    # removing duplicates
    rhs_values_list = list(set(rhs_values_list))
    # sorting
    rhs_values_list.sort()
    print("\nRHS values no duplicates:", rhs_values_list)

    print("\nRFD:\n", rfd_to_string(choosen_rfd))
    rhs_threshold = choosen_rfd[choosen_rfd["RHS"]]
    print("RHS threshold:", rhs_threshold)
    rhs_extended_values = []
    for x in rhs_values_list:
        if isinstance(x, int):
            for y in range(int(x - rhs_threshold), int(x + rhs_threshold + 1)):
                rhs_extended_values.append(y)
        else:
            simil_string = similar_strings(x, data_set_df, rhs_column, rhs_threshold)
            for a in simil_string:
                rhs_extended_values.append(a)
    print("List comprehesion alternative : \n", rhs_extended_values)
    '''rhs_extended_values = [y for x in rhs_values_list if (isinstance(x, int)) for y in
                           range(int(x - rhs_threshold), int(x + rhs_threshold + 1))]'''

    rhs_extended_values.sort()

    print("RHS extended values:", rhs_extended_values)

    rhs_extended_values_no_duplicates = list(set(rhs_extended_values))
    rhs_extended_values_no_duplicates.sort()
    print("RHS extended values no duplicates:", rhs_extended_values_no_duplicates)

    relaxed_query = {rhs_column: rhs_extended_values_no_duplicates}
    print("Relaxed Query:", relaxed_query)
    relaxed_query_expr = query_dict_to_expr(relaxed_query)
    print("Relaxed Query expr:", relaxed_query_expr)

    relaxed_result_set = data_set_df.query(relaxed_query_expr)
    print("\nRelaxed Result Set:\n", relaxed_result_set)


def main():
    csv_io = CSVInputOutput()
    csv_path = "../dataset/dataset_string.csv"
    data_set_df = csv_io.load(csv_path)
    print("DataSet:\n", data_set_df, end="\n\n")

    query = {"name": "joh"}
    print("Query:", query, end="\n\n")

    rfds_path = "../dataset/rfds/dataset_string_rfds.csv"
    rfds_df = csv_io.load(rfds_path)
    print("RFDs:\n", rfds_df, end="\n\n")

    query_relaxer = QueryRelaxer(query=query, rfds_df=rfds_df, data_set_df=data_set_df)
    df = query_relaxer.drop_query_nan()
    print("Dropped query N/A:\n", df, end="\n\n")

    df = query_relaxer.drop_query_rhs()
    print("Dropped query RHS:\n", df, end="\n\n")

    df = query_relaxer.sort_by_decresing_nan_incresing_threshold()
    print("Sorted by NaNs and query attributes:\n", df, end="\n\n")

    rfds_dict_list = df.to_dict(orient="records")
    print("RFD dict list:")
    for dct in rfds_dict_list:
        print(dct)

    #############################################################################################
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@RELAX@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #############################################################################################
    print("#" * 200)
    print("@" * 90 + " RELAX " + "@" * 90)
    print("#" * 200)
    choosen_rfd = rfds_dict_list[0]
    print("\nChoosen RFD:\n", choosen_rfd)
    print("\nRFD:\n", rfd_to_string(choosen_rfd))

    rhs_column = choosen_rfd["RHS"]
    print("\nRHS column:", rhs_column)

    ################################################
    # @@@@@@@@@@@@__ORIGINAL QUERY__@@@@@@@@@@@@@@@#
    ################################################
    print("#" * 200)
    print("@" * 90 + " __ORIGINAL QUERY__ " + "@" * 90)
    print("#" * 200)
    print("OriginalQuery:", query)
    query_expr = query_dict_to_expr(query)
    print("OriginalQuery expr:", query_expr)
    query_res_set = data_set_df.query(query_expr)
    print("Original Query Result Set:\n", query_res_set)

    ################################################
    # @@@@@@@@@@@@__EXTENDED QUERY__@@@@@@@@@@@@@@@#
    ################################################
    print("#" * 200)
    print("@" * 90 + " __EXTENDED QUERY__ " + "@" * 90)
    print("#" * 200)
    query_extended = extend_query_ranges(query, choosen_rfd, data_set_df)
    print("Query extended: ", query_extended)
    query_extended_expr = query_dict_to_expr(query_extended)
    print("Query Extended Expr:", query_extended_expr)
    query_extended_res_set = data_set_df.query(query_extended_expr)
    print("Query Extended Result Set:\n", query_extended_res_set)

    ################################################
    # @@@@@@@@@@@@__RELAXED QUERY__@@@@@@@@@@@@@@@#
    ################################################
    print("#" * 200)
    print("@" * 90 + " __RELAXED QUERY__ " + "@" * 90)
    print("#" * 200)

    rhs_values_list = query_extended_res_set[rhs_column].tolist()
    rhs_values_list.sort()
    print("\nRHS values:", rhs_values_list)
    # removing duplicates
    rhs_values_list = list(set(rhs_values_list))
    # sorting
    rhs_values_list.sort()
    print("\nRHS values no duplicates:", rhs_values_list)

    print("\nRFD:\n", rfd_to_string(choosen_rfd))
    rhs_threshold = choosen_rfd[choosen_rfd["RHS"]]
    print("RHS threshold:", rhs_threshold)
    rhs_extended_values = []
    for x in rhs_values_list:
        if isinstance(x, int):
            for y in range(int(x - rhs_threshold), int(x + rhs_threshold + 1)):
                rhs_extended_values.append(y)
        else:
            simil_string = similar_strings(x, data_set_df, rhs_column, rhs_threshold)
            for a in simil_string:
                rhs_extended_values.append(a)
    print("List comprehesion alternative : \n", rhs_extended_values)
    '''rhs_extended_values = [y for x in rhs_values_list if (isinstance(x, int)) for y in
                           range(int(x - rhs_threshold), int(x + rhs_threshold + 1))]'''

    rhs_extended_values.sort()

    print("RHS extended values:", rhs_extended_values)

    rhs_extended_values_no_duplicates = list(set(rhs_extended_values))
    rhs_extended_values_no_duplicates.sort()
    print("RHS extended values no duplicates:", rhs_extended_values_no_duplicates)

    relaxed_query = {rhs_column: rhs_extended_values_no_duplicates}
    print("Relaxed Query:", relaxed_query)
    relaxed_query_expr = query_dict_to_expr(relaxed_query)
    print("Relaxed Query expr:", relaxed_query_expr)

    relaxed_result_set = data_set_df.query(relaxed_query_expr)
    print("\nRelaxed Result Set:\n", relaxed_result_set)


if __name__ == "__main__":
    main()
