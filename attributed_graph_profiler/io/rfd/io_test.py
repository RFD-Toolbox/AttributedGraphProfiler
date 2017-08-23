from attributed_graph_profiler.io.rfd.io import RFDInputOutput
import pandas as pd


def main():
    rfd_io = RFDInputOutput()
    age_rfd_df = rfd_io.load("../../age.csv")
    print(age_rfd_df)

    zipped = list(zip(age_rfd_df.columns, ["RHS", "height", "weight", "shoe_size"]))

    age_rfd_df.columns = pd.MultiIndex.from_tuples(zipped)
    print("MultiIndexDF:", end="\n\n")
    print(age_rfd_df)

    print(age_rfd_df[("age", "RHS")])
    print(age_rfd_df.sort_index(1).loc[:, (slice(None), 'RHS')])
    print(age_rfd_df.sort_index(1).loc[:, pd.IndexSlice[:, 'RHS']])
    age_rfd_df.to_csv(path_or_buf="age2.csv", sep=";", na_rep="?", index=False)

    age2_rfd_df = pd.read_csv(filepath_or_buffer="age2.csv", sep=";", na_values="?", header=[0, 1])
    print(age2_rfd_df)


if __name__ == "__main__":
    main()
