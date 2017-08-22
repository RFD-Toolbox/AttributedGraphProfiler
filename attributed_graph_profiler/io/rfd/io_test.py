from attributed_graph_profiler.io.rfd.io import RFDInputOutput


def main():
    rfd_io = RFDInputOutput()
    age_rfd_df = rfd_io.load("../../age.csv")
    print(age_rfd_df)


if __name__ == "__main__":
    main()
