from query_rewriter.model.Query import Query


class RFDFilter:
    @staticmethod
    def query_not_in_rhs(rfds: list, query: Query) -> list:
        '''
        Returns the subset of the RFD where NO attribute of the query is in the RHS.
        :param rfds: the list of the RFDs to filter
        :param query: the query
        :return: the subset of the RFD where NO attribute of the query is in the RHS.
        '''

        return [rfd for rfd in rfds
                if all(attribute not in rfd.get_right_hand_side()
                       for attribute in query.get_fields())]
