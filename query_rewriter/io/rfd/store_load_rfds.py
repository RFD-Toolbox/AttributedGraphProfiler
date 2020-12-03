import pandas as pd
from pandas import DataFrame

from query_rewriter.io.csv.csv_io import CSVInputOutput
from query_rewriter.io.rfd.rfd_extractor import RFDExtractor


def diff(list1: list, list2: list):
    '''
    Returns a list of the elements present in list1 but not in list2.
    :param list1: the 1st list to which apply the difference function.
    :param list2: the 2nd list to which apply the difference function.
    :return: a list of the elements present in list1 but not in list2.
    '''
    return [item for item in list1 if item not in list2]


def discover_rfds(csvPath, name_rfds_file):
    '''
    This method calls algorithm of RFDs Discovery and create a file containing list of RFDs and returning its path
    :param csvPath: path of Dataset on which call algorithm of RFDD
    :param name_rfds_file: name of new file containing RFDs list
    :return: None
    '''
    print("Store&Load RFDs")
    args = ["-c", csvPath, "--human"]
    rfd_extractor = RFDExtractor(args, False)
    rfds_df_list: list[DataFrame] = rfd_extractor.rfd_data_frame_list
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

    ad_hoc_all_rfds_df: DataFrame = pd.concat([rfd_df for rfd_df in ad_hoc_rfds_df_list], axis=0, ignore_index=True)
    # ad_hoc_all_rfds_df.reset_index(drop=True, inplace=True)
    ad_hoc_all_rfds_df = ad_hoc_all_rfds_df.round(decimals=2)
    print("Ad hoc all rfds df")
    print(ad_hoc_all_rfds_df)

    csv_io = CSVInputOutput()
    path = name_rfds_file
    csv_io.store(df=ad_hoc_all_rfds_df, path=path)

    loaded_rfds_df = csv_io.load(path=path)
    print("\n\nLoaded rfds df\n")
    print(loaded_rfds_df)


def main():
    print("Store&Load RFDs")
    args = ["-c", "../../dataset/dataset.csv", "--human"]
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

    ad_hoc_all_rfds_df: DataFrame = pd.concat([rfd_df for rfd_df in ad_hoc_rfds_df_list], axis=0, ignore_index=True, sort=True)
    # ad_hoc_all_rfds_df.reset_index(drop=True, inplace=True)
    ad_hoc_all_rfds_df = ad_hoc_all_rfds_df.round(decimals=2)
    print("Ad hoc all rfds df")
    print(ad_hoc_all_rfds_df)

    csv_io = CSVInputOutput()
    path = "cora_rfds.csv"
    csv_io.store(df=ad_hoc_all_rfds_df, path=path)

    loaded_rfds_df = csv_io.load(path=path)
    print("\n\nLoaded rfds df\n")
    print(loaded_rfds_df)


if __name__ == "__main__":
    main()
