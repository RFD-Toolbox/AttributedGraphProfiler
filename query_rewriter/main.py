import sys
import os
import argparse


def main(args):
    path_dataset = None
    path_rfds = None
    query_dict = {}
    numb_rfd_test = None
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="path of dataset", required=True)
    parser.add_argument("-r", "--rfds", help="optional path of rfds")
    parser.add_argument("-q", "--query", help="query", required=True)
    parser.add_argument("-n", "--numb_test", help="number of tests")
    arguments = parser.parse_args()
    print(arguments)


def parsequery(str):
    print("Wee")


if __name__ == "__main__":
    main(sys.argv[1:])
