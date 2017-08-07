import sys
import os
import collections
import numpy as np
from attributed_graph_profiler.rfd_extractor import RFDExtractor


def main():
    print("[Test]")
    args = ["-c", "../resources/dataset_string.csv", "--human"]
    rfd_extractor = RFDExtractor(args, False)
    rfd_data_frames: list = rfd_extractor.rfd_data_frame_list

    print("[Test]")
    print("RFDs.Count:", len(rfd_data_frames))
    for rfd_data_frame in rfd_data_frames:
        print("RFD_DataFrame:\n", rfd_data_frame)
        print()
        print("Number of RFDs found:", len(rfd_data_frame))

        string = ""
        for _, row in rfd_data_frame.iterrows():
            string += "".join(
                ["" if np.isnan(row[col]) else "{}(<= {}), ".format(rfd_data_frame.columns[col],
                                                                    round(row[col], ndigits=2))
                 # it starts from 1 and not 0 'cause at position 0 there is the RHS
                 for col in range(1, len(row))
                 ]
            )

            string += "-> {}(<= {})".format(rfd_data_frame.columns[0], round(row[0], ndigits=2))
            string += "\n"
        print(string)

        for _, row in rfd_data_frame.iterrows():
            rfd_dictionary = {}
            for col in range(0, len(row)):
                rfd_dictionary[rfd_data_frame.columns[col]] = round(row[col], ndigits=2)

            print("RFD_Dictionary:", rfd_dictionary)

        print()


if __name__ == "__main__":
    main()
