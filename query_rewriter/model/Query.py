from typing import ItemsView, KeysView, ValuesView, MappingView

from query_rewriter.model.Operator import Operator

VALUES = "VALUES"
OPERATORS = "OPERATORS"


class Query(dict):
    def __init__(self, operators: dict = {}, values: dict = {}) -> None:
        super().__init__()
        self.set_operators_values(operators, values)

    def set_operators_values(self, operators: dict = {}, values: dict = {}):
        if not operators.keys() == values.keys():
            raise Exception("Keys of operators and values must be the same!!!")

        self[OPERATORS]: dict[str, str] = operators
        self[VALUES]: dict[str, int | float | str | list] = values

    def add_operator_value(self, key: str, operator: str, value):
        self.get_operators()[key] = operator
        self.get_values()[key] = value

    def to_expression(self) -> str:
        '''
                ' item[0]-->key or column
                ' item[1]-->tuple (operator, value)
                ' item[1][1]-->value
                ' Keep only the item having a value.
                '''
        operator_values = dict(filter(lambda item: item[1][1], self.items()))

        if not list(operator_values.keys()):
            return "ilevel_0 in ilevel_0"

        print("After filter")
        print("Keys:")
        print(operator_values.keys())
        print("Values:")
        print(operator_values.values())

        first_key = list(operator_values.keys())[0]
        expr = ""

        for key, (operator, value) in operator_values.items():
            if value:  # check if there is a value
                if key is not first_key:
                    expr += " and "

                if operator == "=":
                    if isinstance(value, (int, float)):
                        expr += " {} == {}".format(key, value)
                    elif isinstance(value, str):
                        expr += " {} == '{}'".format(key, value)
                elif operator == "~":
                    if isinstance(value, str):
                        expr += "{}.str.contains('{}') ".format(key, value)
                elif operator == "!=":
                    if isinstance(value, (int, float)):
                        expr += " {} != {}".format(key, value)
                    elif isinstance(value, str):
                        expr += " {} != '{}'".format(key, value)
                elif operator == "∈":
                    if isinstance(value, list):
                        expr += " {} in {}".format(key, value)
                elif operator == "∉":
                    if isinstance(value, list):
                        expr += " {} not in {}".format(key, value)
                elif operator == ">":
                    expr += " {} > '{}'".format(key, value)
                elif operator == ">=":
                    expr += " {} >= '{}'".format(key, value)
                elif operator == "<":
                    expr += " {} < '{}'".format(key, value)
                elif operator == "<=":
                    expr += " {} <= '{}'".format(key, value)

        return expr

    def get_fields(self) -> list:
        return self[OPERATORS].keys()

    def get_operators(self) -> dict:
        return self[OPERATORS]

    def get_values(self) -> dict:
        return self[VALUES]

    def __getitem__(self, k: str) -> dict or tuple:
        try:
            return super().__getitem__(k)
        except KeyError:
            operator = self.get_operators()[k]
            value = self.get_operators()[k]

            return operator, value

    def keys(self) -> KeysView[str]:
        return self[OPERATORS].keys()

    def values(self) -> ValuesView[tuple]:
        # TODO Fix this
        return ((self[OPERATORS][key], self[VALUES][key]) for key in self.keys())

    def items(self) -> ItemsView[str, tuple]:
        # TODO Fix this
        return ((key, (self[OPERATORS][key], self[VALUES][key])) for key in self.keys())


if __name__ == '__main__':
    operators = {"A": Operator.EQUAL, "B": Operator.GREATER}
    values = {"A": 0, "B": 5}

    query = Query(operators, values)

    print(query)

    for (key, value) in query.items():
        print("Key: " + key + " ===> " + "Value: " + str(value))
