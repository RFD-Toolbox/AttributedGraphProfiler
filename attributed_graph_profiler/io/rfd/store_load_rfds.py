from attributed_graph_profiler.rfd_extractor import RFDExtractor
from attributed_graph_profiler.io.csv.io import CSVInputOutput
import pandas as pd

diff = lambda l1, l2: [x for x in l1 if x not in l2]


def diff(list1: list, list2: list):
    '''
    Returns a list of the elements present in list1 but not in list2.
    :param list1: the 1st list to which apply the difference function.
    :param list2: the 2nd list to which apply the difference function.
    :return: a list of the elements present in list1 but not in list2.
    '''
    return [item for item in list1 if item not in list2]


def main():
    print("Store&Load RFDs")
    args = ["-c", "../../../resources/dataset_string.csv", "--human"]
    rfd_extractor = RFDExtractor(args, False)
    rfds_df_list = rfd_extractor.rfd_data_frame_list
    csv_main_header = rfd_extractor.header
    print("CSV Main Header:", csv_main_header, end="\n\n")
    ad_hoc_rfds_df_list = list()

    for rfd_df in rfds_df_list:
        print("#" * 50 + "BEGIN" + "#" * 50)
        print(rfd_df)
        rfd_df_header = list(rfd_df)
        print("RFD_df header:", rfd_df_header)
        rhs_column = diff(csv_main_header, rfd_df_header)
        print("RHS_column:", rhs_column)
        rfd_df.rename(columns={"RHS": rhs_column[0]}, inplace=True)
        print("Renamed...")
        print(rfd_df, end="\n\n")
        rows = rfd_df.shape[0]
        print("Rows:", rows)

        new_column_key = "RHS"
        kwargs = {new_column_key: [rhs_column[0] for _ in range(rows)]}

        rfd_df = rfd_df.assign(**kwargs)
        print("With RHS column")
        print(rfd_df)
        ad_hoc_rfds_df_list.append(rfd_df)
        print("#" * 50 + "END" + "#" * 50)

    print("\n\nAfter rename & add RHS column\n\n")
    for rfd_df in ad_hoc_rfds_df_list:
        print(rfd_df, end="\n\n")

    ad_hoc_all_rfds_df: pd.DataFrame = pd.concat([rfd_df for rfd_df in ad_hoc_rfds_df_list], axis=0, ignore_index=True)
    # ad_hoc_all_rfds_df.reset_index(drop=True, inplace=True)
    ad_hoc_all_rfds_df = ad_hoc_all_rfds_df.round(decimals=2)
    print("Ad hoc all rfds df")
    print(ad_hoc_all_rfds_df)

    csv_io = CSVInputOutput()
    path = "ad_hoc_all_rfds_df.csv"
    csv_io.store(df=ad_hoc_all_rfds_df, path=path)

    loaded_rfds_df = csv_io.load(path=path)
    print("\n\nLoaded rfds df\n")
    print(loaded_rfds_df)


if __name__ == "__main__":
    main()
