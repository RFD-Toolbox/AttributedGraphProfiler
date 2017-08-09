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

    print("Type of distance_df is:", type(distance_matrix.distance_df), end="\n\n")

    '''
    Will be printed ((rows) * (rows - 1))/2 distance tuples.
    First will be printed distances from the row i to all the remaining (rows -i) rows.
    Each column has distances on the corresponding attribute.
    For example, if there are 7 rows in the data-set, (7 * 6)/2 = 21 rows will be printed out:
    The first 6 printed rows will contain the distances from the 1st row to the remaining 6 rows.
    The next 5 printed rows will contain the distances from the 2nd row to the remaining 5 rows.
    The next 4 printed rows will contain the distances from the 2nd row to the remaining 4 rows.
    ....................................................................................
    ....................................................................................
    ....................................................................................
    The last 1 printed row will contain the distances from the penultimate row to the last one.
    '''
    print(distance_matrix.distance_df)


if __name__ == "__main__":
    main()
