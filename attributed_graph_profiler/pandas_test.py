import pandas as pandas
import numpy as numpy


def main():
    csv_path = "../resources/dataset_string.csv"
    csv_data_frame = pandas.read_csv(csv_path, delimiter=";")
    print("\nOriginal Values:")
    print(csv_data_frame)

    sorted_df = csv_data_frame.sort_values(by=["age", "name"], kind="mergesort")
    print("\nSorted Values by AGE & NAME:")
    print(sorted_df)

    min_age = int(numpy.min(sorted_df["age"]))
    print("\nMin_Age:", min_age)
    max_age = int(numpy.max(sorted_df["age"]))
    print("\nMax_Age:", max_age)

    threshold = 3
    bins = numpy.arange(min_age, max_age, threshold)
    print("Bins:", bins)
    ind = numpy.digitize(sorted_df["age"], bins)
    print(ind)

    print("\n\nClustering by hand:\n")
    current_min = min_age
    for cluster in range(min_age, max_age, threshold):
        next_min = current_min + threshold
        print("<Cluster({})>".format(cluster))
        print(sorted_df[(current_min <= sorted_df["age"]) & (sorted_df["age"] <= next_min)])
        print("</Cluster({})>\n".format(cluster + threshold))
        current_min = next_min


if __name__ == "__main__":
    main()
