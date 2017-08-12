from loader.distance_mtr import DiffMatrix
import pandas as pandas
from attributed_graph_profiler.clustering.splitter import Splitter
from attributed_graph_profiler.clustering.csv_parser import CSVParser


def main():
    csv_path = "../../resources/dataset_string.csv"
    parser = CSVParser(csv_path)

    distance_matrix: pandas.DataFrame = DiffMatrix(csv_path,
                                                   sep=parser.delimiter,
                                                   semantic=False,
                                                   missing="?",
                                                   datetime=False).distance_df

    print("DistanceMatrix:\n", distance_matrix, end="\n\n")
    groups = Splitter.split(distance_matrix, parser.rows_count)

    for group_id, group in groups.items():
        print("Group:", group_id)
        print(group, end="\n\n")


if __name__ == "__main__":
    main()
