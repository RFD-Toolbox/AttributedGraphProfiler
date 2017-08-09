import pandas as pandas
import numpy as np
from loader.distance_mtr import DiffMatrix
from attributed_graph_profiler.rfd_extractor import RFDExtractor


def main():
    print("Clustering TEST")
    csv_path = "../../resources/dataset_string.csv"
    csv_data_frame = pandas.read_csv(csv_path, delimiter=";")
    csv_headers = list(csv_data_frame)

    print("\nOriginal Values:")
    print(csv_data_frame)
    rows_count, columns_count = csv_data_frame.shape
    print("\nRowsCount:", rows_count)
    print("\nColumnsCount:", columns_count)
    print("\n")

    distance_matrix = DiffMatrix(csv_path,
                                 sep=";",
                                 semantic=False,
                                 missing="?",
                                 datetime=False).distance_df

    print("DistanceMatrix:\n", distance_matrix, end="\n\n")

    groups = {}
    group_begin_index = 0
    for row_num in range(0, rows_count - 1):
        print("Row{}".format(row_num))
        group_end_index = group_begin_index + (rows_count - 1 - row_num)
        groups[row_num] = distance_matrix[group_begin_index:group_end_index]
        group = groups[row_num]

        print("SIZE:", len(group))
        print(groups[row_num], end="\n\n")
        group_begin_index = group_end_index

    args = ["-c", "../../resources/dataset_string.csv"]
    rfd_extractor = RFDExtractor(args, False)
    rfds = rfd_extractor.get_rfd_dictionary_list()

    print("RFDs...")
    for rfd_dic in rfds:
        print("RFD:", rfd_dic)

        # =============================
        diff = lambda l1, l2: [x for x in l1 if x not in l2]
        keys = rfd_dic.keys()
        print("Keys:", keys)
        rhs_header_value = diff(list(group), keys)
        length = len(rhs_header_value)
        print("RHS_Header:", rhs_header_value[0])

        rfd_dic[rhs_header_value[0]] = rfd_dic.pop("RHS")
        print("RFD after POP:", rfd_dic)

        if length == 0:
            print("Lenght:", length)
            print("Group:", group)
            print("RFD_dic:", rfd_dic)
        # =============================
        for key, group in groups.items():
            print("\nGroup{}\n".format(key), group)

            query = ' and '.join(['{} <= {}'.format(k, v) for k, v in rfd_dic.items() if not np.isnan(v)])
            my_set = group.query(query)

            print("SET{}\n".format(key), my_set)


if __name__ == "__main__":
    main()
