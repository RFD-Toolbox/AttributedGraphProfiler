import sys
import getopt
import pandas as pd
import numpy as np
import utils.utils as ut
from loader.distance_mtr import DiffMatrix
from dominance.dominance_tools import RFDDiscovery


def main():
    print("MainTest")
    distance_matrix = DiffMatrix("../resources/dataset_string.csv",
                                 sep=";",
                                 index_col=0,
                                 semantic=False,
                                 missing="?",
                                 datetime=False)

    print(distance_matrix.distance_df)


if __name__ == "__main__":
    main()
