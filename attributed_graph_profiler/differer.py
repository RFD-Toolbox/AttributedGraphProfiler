import sys
import os
import csv
import numpy


class differer:
    csv_path = ""
    separator = ";"
    start_decoration = "====================START===================="
    end_decoration = "====================END===================="
    has_header = True
    column_key = 0
    number_of_columns = 4
    line_count = 0
    dictionary = {"null": "null"}
    matrix = 0

    def __init__(self):
        print(self.start_decoration)
        self.csv_path = "../resources/dataset.csv"
        matrix = self.load_csv()
        print(matrix)
        self.testDiff(matrix)

    def load_csv(self):
        np = numpy.loadtxt(open(self.csv_path), delimiter=";", skiprows=1)
        return np

    def testDiff(self, np):
        a = np[1, :] - np[2, :]
        print(a);


def main():
    hey = differer()


if __name__ == "__main__":
    main()
