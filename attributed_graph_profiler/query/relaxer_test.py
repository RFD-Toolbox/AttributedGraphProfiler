from attributed_graph_profiler.query.relaxer import QueryRelaxer
from attributed_graph_profiler.io.csv.io import CSVInputOutput
import numpy as np


def rfd_to_string(rfd: dict) -> str:
    string = ""
    string += "".join(["" if key == "RHS" or key == rfd["RHS"] or np.isnan(val) else "(" + key + " <= " + str(
        val) + ") " for key, val in rfd.items()])
    string += "---> ({} <= {})".format(rfd["RHS"], rfd[rfd["RHS"]])
    return string


def query_dict_to_expr(query: dict) -> str:
    expr = " and ".join(["{} == {}".format(k, v) for k, v in query.items()])
    return expr


def extend_query_ranges(query: dict, rfd: dict) -> dict:
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
                    val_range = range(int(val - rfd[key]), int(val + rfd[key] + 1))
                    print("Range: ", list(val_range))
                    query[key] = list(val_range)
            else:
                print("Threshold is not positive:", threshold)
    return query


# def query_rhs_rewrite(result_set: pd.DataFrame, rfd: dict)


def main():
    csv_io = CSVInputOutput()
    csv_path = "../../resources/dataset.csv"
    data_set_df = csv_io.load(csv_path)
    print("DataSet:\n", data_set_df, end="\n\n")

    query = {"height": 175}
    print("Query:", query, end="\n\n")

    rfds_path = "../../resources/dataset_rfds.csv"
    rfds_df = csv_io.load(rfds_path)
    print("RFDs:\n", rfds_df, end="\n\n")

    query_relaxer = QueryRelaxer(query=query, rfds_df=rfds_df, data_set_df=data_set_df)
    df = query_relaxer.drop_query_na()
    print("Dropped query N/A:\n", df, end="\n\n")

    df = query_relaxer.drop_query_rhs()
    print("Dropped query RHS:\n", df, end="\n\n")

    df = query_relaxer.sort_nan_query_attributes()
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

    print("OriginalQuery:", query)
    query_expr = query_dict_to_expr(query)
    print("OriginalQuery expr:", query_expr)
    query_res_set = data_set_df.query(query_expr)
    print("Original Query Result Set:\n", query_res_set)

    query_extended = extend_query_ranges(query, choosen_rfd)
    print("Query extended: ", query_extended)
    query_extended_expr = query_dict_to_expr(query_extended)
    print("Query Extended Expr:", query_extended_expr)
    query_extended_res_set = data_set_df.query(query_extended_expr)
    print("Query Extended Result Set:\n", query_extended_res_set)
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

    rhs_extended_values = [y for x in rhs_values_list for y in
                           range(int(x - rhs_threshold), int(x + rhs_threshold + 1))]
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
