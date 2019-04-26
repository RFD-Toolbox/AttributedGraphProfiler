from typing import ItemsView, KeysView, ValuesView
from string import Template

from pandas import DataFrame, np

from query_rewriter.model.Operator import Operator
from query_rewriter.model.RFD import RFD
from query_rewriter.query.relaxer import QueryRelaxer

VALUES = "VALUES"
OPERATORS = "OPERATORS"
COLUMN_CLASS = "column"
OPERATOR_CLASS = "operator"
VALUE_CLASS = "value"
CONNECTOR_CLASS = "connector"

STYLE_TEMPLATE: Template = Template(
    """
    <style>
    .$column_class{color:$column_color}
    .$operator_class{color:$operator_color}
    .$value_class{color:$value_color}
    .$connector_class{color:$connector_color}
    </style>
    """
)


class Query(dict):
    def __init__(self, operators: dict = {}, values: dict = {}) -> None:
        super().__init__()
        operators = operators or {}
        values = values or {}
        self.set_operators_values(operators, values)
        self.set_colors()

    def set_colors(self, column: str = "Blue", operator: str = "Green", value: str = "Black",
                   connector: str = "DarkMagenta"):
        self.column_color: str = column
        self.operator_color: str = operator
        self.value_color: str = value
        self.connector_color: str = connector

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

        # print("After filter")
        # print("Keys:")
        # print(operator_values.keys())
        # print("Values:")
        # print(operator_values.values())

        first_key = list(operator_values.keys())[0]
        expr = ""

        for key, (operator, value) in operator_values.items():
            if value:  # check if there is a value
                if key is not first_key:
                    expr += " and "

                if operator == Operator.EQUAL:
                    if isinstance(value, (int, float)):
                        expr += " {} == {}".format(key, value)
                    elif isinstance(value, str):
                        expr += " {} == '{}'".format(key, value)
                elif operator == Operator.NOT_EQUAL:
                    if isinstance(value, (int, float)):
                        expr += " {} != {}".format(key, value)
                    elif isinstance(value, str):
                        expr += " {} != '{}'".format(key, value)
                elif operator == Operator.BELONGING:
                    if isinstance(value, list):
                        if all(isinstance(item, (int, float)) for item in value):
                            expr += " {} in {}".format(key, value)
                        elif all(isinstance(item, str) for item in value):
                            expr += " {} in {}".format(key, value)
                elif operator == Operator.NOT_BELONGING:
                    if isinstance(value, list):
                        if all(isinstance(item, (int, float)) for item in value):
                            expr += " {} not in {}".format(key, value)
                        elif all(isinstance(item, str) for item in value):
                            expr += " {} not in {}".format(key, value)
                elif operator == Operator.GREATER:
                    if isinstance(value, (int, float)):
                        expr += " {} > {}".format(key, value)
                elif operator == Operator.GREATER_EQUAL:
                    if isinstance(value, (int, float)):
                        expr += " {} >= {}".format(key, value)
                elif operator == Operator.LESS:
                    if isinstance(value, (int, float)):
                        expr += " {} < {}".format(key, value)
                elif operator == Operator.LESS_EQUAL:
                    if isinstance(value, (int, float)):
                        expr += " {} <= {}".format(key, value)

        return expr

    def to_pretty_expression(self) -> str:
        operator_values = dict(filter(lambda item: item[1][1], self.items()))

        if not list(operator_values.keys()):
            return "All"

        first_key = list(operator_values.keys())[0]
        pretty_expr = ""

        for key, (operator, value) in operator_values.items():
            if value:  # check if there is a value
                if key is not first_key:
                    pretty_expr += " AND "

                pretty_expr += "{} {} {}".format(str(key).title().replace("_", " "), operator, value)

        return pretty_expr

    def to_rich_text_expression(self) -> str:
        style = STYLE_TEMPLATE.safe_substitute(column_class=COLUMN_CLASS, column_color=self.column_color,
                                               operator_class=OPERATOR_CLASS, operator_color=self.operator_color,
                                               value_class=VALUE_CLASS, value_color=self.value_color,
                                               connector_class=CONNECTOR_CLASS, connector_color=self.connector_color)

        body = ""
        operator_values = dict(filter(lambda item: item[1][1], self.items()))

        if not list(operator_values.keys()):
            body = "<span class=\"{}\">{}</span>".format(VALUE_CLASS, "All")
        else:
            first_key = list(operator_values.keys())[0]

            for key, (operator, value) in operator_values.items():
                if value:  # check if there is a value
                    if key is not first_key:
                        body += "<span class=\"{}\"> AND <span/>".format(CONNECTOR_CLASS)

                    body += "<span class=\"{}\">{}</span>".format(COLUMN_CLASS, str(key).title().replace("_", " "))
                    body += "<span class=\"{}\"> {} </span>".format(OPERATOR_CLASS, operator)
                    body += "<span class=\"{}\">{}</span>".format(VALUE_CLASS, value)

        return style + body

    def extend_ranges(self, rfd: RFD, data_set: DataFrame):
        column_types: dict = data_set.dtypes.to_dict()
        extended_query = Query()

        for item_key, (item_operator, item_value) in self.items():
            if item_value:  # check if there is a value
                if rfd.__contains__(item_key):  # extend its range
                    threshold: float = rfd[item_key]

                    column_type = column_types.get(item_key)  # get the type of this column of the DataFrame

                    if item_operator == Operator.EQUAL:
                        if column_type == np.int64 or column_type == np.float64:
                            if threshold > 0:  # once extended it will turn into a belonging
                                extended_value = list(
                                    range(int(item_value - threshold), int(item_value + threshold + 1)))
                                extended_value.sort()
                                extended_query.add_operator_value(item_key, Operator.BELONGING, extended_value)
                            elif threshold == 0:  # nothing to extend
                                extended_value = item_value
                                extended_query.add_operator_value(item_key, Operator.EQUAL, extended_value)
                        elif column_type == np.object:
                            if threshold > 0:
                                similar_strings: list[str] = list(set(QueryRelaxer.similar_strings(source=item_value,
                                                                                                   data=data_set,
                                                                                                   col=item_key,
                                                                                                   threshold=threshold)))
                                similar_strings.sort()
                                extended_query.add_operator_value(item_key, Operator.BELONGING, similar_strings)
                            elif threshold == 0:
                                extended_query.add_operator_value(item_key, Operator.EQUAL, item_value)
                    elif item_operator == Operator.NOT_EQUAL:
                        #  TODO think for improvements
                        extended_query.add_operator_value(item_key, Operator.NOT_EQUAL, item_value)
                    elif item_operator == Operator.BELONGING:
                        if threshold > 0:
                            if isinstance(item_value, list) \
                                    and all(isinstance(element, str) for element in item_value):

                                extended_value: list = []

                                for item in item_value:
                                    extended_value.extend(list(set(QueryRelaxer.similar_strings(source=item,
                                                                                                data=data_set,
                                                                                                col=item_key,
                                                                                                threshold=threshold))))
                                extended_value = list(set(extended_value))
                                extended_value.sort()
                                extended_query.add_operator_value(item_key, Operator.BELONGING, extended_value)

                            elif isinstance(item_value, list) and all(
                                    isinstance(element, (int, float)) for element in item_value):

                                extended_value: list = []

                                for item in item_value:
                                    extended_value.extend(list(range(int(item - threshold), int(item + threshold + 1))))

                                extended_value = list(set(extended_value))
                                extended_value.sort()
                                extended_query.add_operator_value(item_key, Operator.BELONGING, extended_value)
                        elif threshold == 0:
                            extended_query.add_operator_value(item_key, Operator.BELONGING, item_value)
                    elif item_operator == Operator.NOT_BELONGING:
                        #  TODO think for improvements
                        extended_query.add_operator_value(item_key, Operator.NOT_BELONGING, item_value)
                    elif item_operator == Operator.GREATER:
                        # reduce the lower bound
                        if isinstance(item_value, (int, float)):
                            extended_value = item_value - threshold
                        else:
                            extended_value = item_value

                        extended_query.add_operator_value(item_key, Operator.GREATER, extended_value)
                    elif item_operator == Operator.GREATER_EQUAL:
                        # reduce the lower bound
                        if isinstance(item_value, (int, float)):
                            extended_value = item_value - threshold
                        else:
                            extended_value = item_value

                        extended_query.add_operator_value(item_key, Operator.GREATER_EQUAL, extended_value)
                    elif item_operator == Operator.LESS:
                        # increase the upper bound
                        if isinstance(item_value, (int, float)):
                            extended_value = item_value + threshold
                        else:
                            extended_value = item_value

                        extended_query.add_operator_value(item_key, Operator.LESS, extended_value)
                    elif item_operator == Operator.LESS_EQUAL:
                        # increase the upper bound
                        if isinstance(item_value, (int, float)):
                            extended_value = item_value + threshold
                        else:
                            extended_value = item_value

                        extended_query.add_operator_value(item_key, Operator.LESS_EQUAL, extended_value)
                else:  # use the initial range
                    extended_query.add_operator_value(item_key, item_operator, item_value)

        if extended_query.__len__() == 0:
            return self
        else:
            return extended_query

    def relax_constraints(self, rfd: RFD, data_set: DataFrame):
        '''
        Relaxes this Query
        :param rfd: The RFD to use for relaxing this Query
        :param data_set: The full data set
        :return: the Relaxed Query
        '''

        extended_result_set: DataFrame = data_set.query(self.to_expression())

        # List containing only the columns/attributes that will be in the Relaxed Query
        # In order to do this we look for columns not in the original query
        relaxing_columns: list = [col for col in list(extended_result_set)
                                  if col not in self.keys() and col in rfd]

        # Check if the list is empty
        if not relaxing_columns:
            # Use only columns in the RHS
            relaxing_columns = [col for col in rfd.get_right_hand_side().keys()]

        relaxed_query: Query = Query()

        # These columns are not part of the query, hence we can use a simple belonging operator
        for col in relaxing_columns:
            extended_column_values: list = extended_result_set[col].tolist()
            threshold: float = rfd[col]

            relaxed_column_values: list = []

            if threshold > 0:
                for colulmn_value in extended_column_values:
                    # relax the values
                    if isinstance(colulmn_value, (int, float)):
                        relaxed_column_values.extend(
                            list(range(int(colulmn_value - threshold), int(colulmn_value + threshold + 1))))
                    elif isinstance(colulmn_value, str):
                        similar_strings: list[str] = list(set(QueryRelaxer.similar_strings(source=colulmn_value,
                                                                                           data=data_set,
                                                                                           col=col,
                                                                                           threshold=threshold)))
                        relaxed_column_values.extend(similar_strings)
            else:
                # keep the extended values
                relaxed_column_values.extend(extended_column_values)

            # Remove duplicates
            relaxed_column_values = list(set(relaxed_column_values))
            # Sort values
            relaxed_column_values.sort()

            relaxed_query.add_operator_value(col, Operator.BELONGING, relaxed_column_values)

        return relaxed_query

    def get_fields(self) -> list:
        return self[OPERATORS].keys()

    def get_operators(self) -> dict:
        return self[OPERATORS]

    def get_values(self) -> dict:
        return self[VALUES]

    def __len__(self) -> int:
        return self.get_operators().__len__()

    def __getitem__(self, k: str) -> dict or tuple:
        try:
            return super().__getitem__(k)
        except KeyError:
            item_operator = self.get_operators()[k]
            item_value = self.get_operators()[k]

            return item_operator, item_value

    def keys(self) -> KeysView[str]:
        return self[OPERATORS].keys()

    def values(self) -> ValuesView[tuple]:
        # TODO Fix this
        return ((self[OPERATORS][key], self[VALUES][key]) for key in self.keys())

    def items(self) -> ItemsView[str, tuple]:
        # TODO Fix this
        return ((key, (self[OPERATORS][key], self[VALUES][key])) for key in self.keys())
