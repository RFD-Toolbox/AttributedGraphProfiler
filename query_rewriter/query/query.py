class Query(dict):
    '''
    Class representing a query for the dataset.
    Each condition is represented using a key:value pair,
    in which the key indicates the column/attribute and
    the value indicates the corresponding value we are looking for.
    '''

    def to_expression(self) -> str:
        '''
        Converts the query dictionary to the string format required by Pandas.DataFrame.Query() method.
        :param query: the Query dictionary to convert.
        :return: the string format corresponding to the query dictionary.
        :rtype:
        '''
        # expr = " and ".join(
        #     ["{} == {}".format(k, v) if not isinstance(v, str) else "{} == '{}'".format(k, v) for k, v in
        #      query.items()])
        last_key = list(self.keys())[-1]
        expr = ""
        for k, v in self.items():
            if isinstance(v, dict):
                expr += " {} >= {} and {} <= {}".format(k, v['min'], k, v['max'])
            elif isinstance(v, (int, float, list)):
                expr += " {} == {}".format(k, v)
            elif isinstance(v, str):
                expr += k + ".str.contains('{}') ".format(v)
            if k is not last_key:
                expr += " and "

        return expr


q: Query = Query({"A": "1", "B": "2", "C": "3"})
q.to_expression()
