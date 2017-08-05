import sys
import os
import csv
from attributed_graph_profiler.rfd_extractor import RFDExtractor


def main():
	print("CSV Test")
	csv_path = "../resources/dataset_string.csv"

	with open(csv_path, 'r') as csv_file:
		sniffer = csv.Sniffer()
		dialect = sniffer.sniff(csv_file.read(), delimiters=",;|")

		csv_file.seek(0)
		reader = csv.DictReader(csv_file, dialect=dialect)
		if sniffer.has_header(csv_path):
			print("Header")
			print(reader.fieldnames)

		for row in reader:
			print(row.values())

		csv_file.seek(0)
		sortedlist = sorted(reader, key=lambda row: (row["age"], row["name"]), reverse=False)

		print("\n<Sorted List>")
		for row in sortedlist:
			print(row.values())
		print("</Sorted List>\n")

	args = ["-c", "../resources/dataset_string.csv", "--human"]
	rfd_extractor = RFDExtractor(args, False)
	rfd_dictionary_list = rfd_extractor.get_rfd_dictionary_list()

	for dictionary in rfd_dictionary_list:
		print("RFD_Dictionary:", dictionary)


if __name__ == "__main__":
	main()
