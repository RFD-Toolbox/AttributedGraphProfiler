import sys
import os
import pandas as pd
import numpy as np
from attributed_graph_profiler.rfd_extractor import RFDExtractor


def main():
    args = ["-c", "../../resources/dataset.csv"]
    rfd_extractor = RFDExtractor(args, False)
    rfds = rfd_extractor.get_sort_rfd_dictionary_list(True, ["RHS"])

    if __name__ == "__main__":
        main()
