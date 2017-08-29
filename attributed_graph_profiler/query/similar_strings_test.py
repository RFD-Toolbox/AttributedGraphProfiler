import pandas as pd
from io import StringIO
import editdistance


def main():
    print("Levenshtein similar strings...")
    data = StringIO("""name;sex;city;age
    john;male;newyork;20
    jack;male;newyork;21
    mary;female;losangeles;45
    maryanne;female;losangeles;48
    eric;male;san francisco;26
    jenny;female;boston2;30
    mattia;na;BostonDynamics;50""")

    df = pd.read_csv(data, sep=";", skipinitialspace=True)
    print(df)

    source = "john"
    max_dist = 3
    string_column = "name"

    string_list = df[string_column].tolist()
    print(end="\n\n")
    print(string_list)

    similar_strings = df[df[string_column].apply(lambda word: int(editdistance.eval(source, word)) <= max_dist)][
        string_column].tolist()
    print("{} Similar Strings {}:".format(source, max_dist), similar_strings)


if __name__ == "__main__":
    main()
