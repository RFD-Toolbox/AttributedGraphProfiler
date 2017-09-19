import pandas as pd
import numpy as np


def main():
    rows = 5
    cols = 3
    df = pd.DataFrame(np.random.randint(1, 6, (rows, cols)), columns=['A', 'B', 'C'])
    print(df, end="\n\n")

    '''
    Slicing using the [] operator selects a set of rows and/or columns from a DataFrame.
    To slice out a set of rows, you use the following syntax: data[start:stop].
    When slicing in pandas the start bound is included in the output.
    The stop bound is one step BEYOND the row you want to select.
    '''
    for i in range(0, rows):
        curr_row_df = df[i:i + 1]
        print("Row{}".format(i))
        print(curr_row_df, end="\n\n")

    slices = [df[i:i + 1] for i in range(0, rows)]
    print("Slices of DF...")
    for slice in slices:
        print(slice, end="\n\n")


if __name__ == '__main__':
    main()
