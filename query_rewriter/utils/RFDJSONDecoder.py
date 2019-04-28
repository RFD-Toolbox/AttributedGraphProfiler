from typing import Union

from query_rewriter.model.RFD import RFD

RHS = "RHS"
LHS = "LHS"


class RFDJSONDecoder:
    @staticmethod
    def as_rfd(dictionary: dict) -> Union[RFD, dict]:
        if LHS in dictionary and RHS in dictionary:
            return RFD(dictionary[LHS], dictionary[RHS])
        else:
            return dictionary
