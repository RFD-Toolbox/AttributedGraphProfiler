import pandas as pd

from query_rewriter.io.csv.io import CSVInputOutput
from query_rewriter.io.rfd.rfd_extractor import RFDExtractor


def diff(list1: list, list2: list):
    '''
    Returns a list of the elements present in list1 but not in list2.
    :param list1: the 1st list to which apply the difference function.
    :param list2: the 2nd list to which apply the difference function.
    :return: a list of the elements present in list1 but not in list2.
    '''
    return [item for item in list1 if item not in list2]


def search_rfds(csvPath,name_rfds_file):
    print("Store&Load RFDs")
    args = ["-c", csvPath, "--human"]
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
    path = name_rfds_file
    csv_io.store(df=ad_hoc_all_rfds_df, path=path)

    loaded_rfds_df = csv_io.load(path=path)
    print("\n\nLoaded rfds df\n")
    print(loaded_rfds_df)


def main():
    print("Store&Load RFDs")
    args = ["-c", "../../dataset/cora.csv", "--human"]
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
    path = "cora_rfds.csv"
    csv_io.store(df=ad_hoc_all_rfds_df, path=path)

    loaded_rfds_df = csv_io.load(path=path)
    print("\n\nLoaded rfds df\n")
    print(loaded_rfds_df)

    # ##############################################START QUERY##########################################
    # print("#" * 50 + " QUERY " + "#" * 50)
    # query = 'height==175'
    # print("Query:", query)
    # query_dict = {"height": 175}
    # print("Query dict:", query_dict)
    # my_set = rfd_extractor.data_frame
    # my_set = my_set.query(query)
    # print("Query Result SET:")
    # print(my_set, end="\n\n")
    #
    # loaded_rfds_df.sort_values(by=['height', 'age', 'shoe_size', 'weight'], inplace=True)
    # print("Ordered rfds df by height, age, shoe_size, weight:")
    # print(loaded_rfds_df, end="\n\n")
    #
    # nan_count = "NaNs"
    # kwargs = {nan_count: lambda x: x.isnull().sum(axis=1)}
    # loaded_rfds_df = loaded_rfds_df.assign(**kwargs)
    #
    # diff_sum = "diff_sum"
    # kwargs2 = {diff_sum: lambda x: x.drop(nan_count, axis=1).sum(axis=1)}
    # loaded_rfds_df = loaded_rfds_df.assign(**kwargs2)
    #
    # sorting_keys = [nan_count, diff_sum]
    # print("Sorting Keys:", sorting_keys)
    # ascending = [False, True]
    #
    # query_dict_keys = list(query_dict.keys())
    # print("Query Dict Keys:", query_dict_keys)
    # loaded_rfds_df = loaded_rfds_df.dropna(subset=query_dict_keys)
    #
    # print("Dropped DF Nans on query attributes:", end="\n\n")
    # print(loaded_rfds_df)
    #
    # # drop RFDs containing an attribute of the Query as the RHS.
    # loaded_rfds_df = loaded_rfds_df.drop(
    #     loaded_rfds_df[loaded_rfds_df["RHS"].isin(query_dict_keys)].index).reset_index(
    #     drop=True)
    #
    # print("Dropped DF RHS query attributes:", end="\n\n")
    # print(loaded_rfds_df)
    #
    # sorting_keys.extend(query_dict_keys)
    # print("Extended keys:", sorting_keys)
    # ascending.extend([True for _ in query_dict_keys])
    #
    # print("Acending mask:", ascending)
    # # drop RFDs that doesn't contain attributes of the original Query.
    # loaded_rfds_df.drop = loaded_rfds_df.dropna(subset=query_dict_keys)
    #
    # loaded_rfds_df = loaded_rfds_df.sort_values(by=sorting_keys,
    #                                             ascending=ascending,
    #                                             na_position="first").reset_index(drop=True)
    #
    # print("Sorted...")
    # print(loaded_rfds_df)
    '''
    print("Group by")
    df_grouped_by_height = loaded_rfds_df.groupby(by='height')

    for name, group in df_grouped_by_height:
        print("#" * 100)
        print("Height =", name)
        df = group.drop(group[group["RHS"] == 'height'].index).reset_index(drop=True)
        print(df, end="\n\n")

        nan_count = "NaNs"
        kwargs = {nan_count: lambda x: x.isnull().sum(axis=1)}
        df = df.assign(**kwargs)

        diff_sum = "diff_sum"
        kwargs2 = {diff_sum: lambda x: x.drop(nan_count, axis=1).sum(axis=1)}
        df = df.assign(**kwargs2)

        df = df.sort_values([nan_count, diff_sum, "age", "shoe_size", "weight"],
                            ascending=[False, True, True, True, True], na_position="first").reset_index(drop=True)

        df = df.drop(nan_count, axis=1)
        df = df.drop(diff_sum, axis=1)

        print("Sorted RFDs DF + reset_index:")
        print(df, end="\n\n")

        print("Best RFD:")
        best_rfd_df = df.ix[[0]]
        print(best_rfd_df)

        for index, row in best_rfd_df.iterrows():
            string = ""
            string += "".join(["" if col == "RHS" or col == row["RHS"] or np.isnan(row[col]) else col + " <= " + str(
                row[col]) + ", " for col in best_rfd_df])
            string += "---> {} <= {}".format(row["RHS"], row[row["RHS"]])
            print("RFD:\n", string)

        print("=" * 100, end="\n\n")
    '''


if __name__ == "__main__":
    main()
