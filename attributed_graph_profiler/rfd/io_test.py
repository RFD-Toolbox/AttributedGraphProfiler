import os
import sys
from attributed_graph_profiler.rfd.input_output import RFDInputOutput

def main():
    rfd_io = RFDInputOutput()
    age_rfd_df = rfd_io.load_rfd_df("../age.csv")
    print(age_rfd_df)

if __name__ == "__main__":
    main()
