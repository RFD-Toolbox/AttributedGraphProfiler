from attributed_graph_profiler.query.relaxer import QueryRelaxer
from attributed_graph_profiler.io.csv.io import CSVInputOutput


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


if __name__ == "__main__":
    main()
