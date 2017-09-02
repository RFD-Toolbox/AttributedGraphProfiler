from query_rewriter.io.csv.csv_parser import CSVParser


def main():
    print("CSV_INFO_TEST")
    csv_path = "../../resources/dataset_string.csv"
    csv_parser = CSVParser(csv_path)

    print("csv_path:", csv_parser.path)
    print("csv_delimiter:", csv_parser.delimiter)
    print("csv_data_frame:\n", csv_parser.data_frame, end="\n\n")
    print("csv_rows_count:", csv_parser.rows_count)
    print("csv_columns_count:", csv_parser.columns_count)
    print("csv_header:", csv_parser.header)


if __name__ == "__main__":
    main()
