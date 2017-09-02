import csv

from query_rewriter.io.rfd.rfd_extractor import RFDExtractor


def main():
    print("CSV Test")
    csv_path = "../dataset/dataset_string.csv"

    with open(csv_path, 'r') as csv_file:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(csv_file.read(4096), delimiters=",;|")

        csv_file.seek(0)
        reader = csv.DictReader(csv_file, dialect=dialect)
        if sniffer.has_header(csv_path):
            print("<Header>")
            print("\t", end="")
            print(reader.fieldnames[0:])
            print("</Header>\n")
        else:
            print("Error 404: Header not found.")

        for row in reader:
            print(row.values())

        csv_file.seek(0)
        sortedlist = sorted(reader, key=lambda line: (line["age"], line["name"]), reverse=False)

        print("\n<Sorted List>")
        for row in sortedlist:
            print("\t", end="")
            for key in row.keys():
                print("%-20s" % (row[key]), end="")
            print()
        print("</Sorted List>\n")

    args = ["-c", "../dataset/dataset_string.csv", "--human"]
    rfd_extractor = RFDExtractor(args, False)
    rfd_dictionary_list = rfd_extractor.get_rfd_dictionary_list()

    for dictionary in rfd_dictionary_list:
        print("RFD_Dictionary:", dictionary)
        print(dictionary.keys())


if __name__ == "__main__":
    main()
