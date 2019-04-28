from numpy import NaN

from query_rewriter.model.Operator import Operator

RHS = "RHS"
LHS = "LHS"


class RFD(dict):

    def __init__(self, lhs: dict = {}, rhs: dict = {}) -> None:
        super().__init__()
        self[LHS]: dict[str, float | NaN] = lhs
        self[RHS]: dict[str, float | NaN] = rhs

    def get_left_hand_side(self) -> dict:
        return self[LHS]

    def get_right_hand_side(self) -> dict:
        return self[RHS]

    def __getitem__(self, k: str) -> dict:
        try:
            return super().__getitem__(k)
        except KeyError:
            try:
                return self.get_left_hand_side()[k]
            except KeyError:
                return self.get_right_hand_side()[k]

    def __contains__(self, o: object) -> bool:
        return super().__contains__(o) \
               or \
               self.get_left_hand_side().__contains__(o) \
               or \
               self.get_right_hand_side().__contains__(o)

    def __str__(self) -> str:
        label = ""
        
        if self.get_left_hand_side() and self.get_right_hand_side():
            label = "("

            lhs_last_key: str = list(self.get_left_hand_side().keys())[-1]

            for key, value in self.get_left_hand_side().items():
                label += key.title().replace("_", " ")
                label += " " + Operator.LESS_EQUAL + " "
                label += str(value)

                if key is not lhs_last_key:
                    label += ", "

            label += ") → ("

            rhs_last_key: str = list(self.get_right_hand_side().keys())[-1]

            for key, value in self.get_right_hand_side().items():
                label += key.title().replace("_", " ")
                label += " " + Operator.LESS_EQUAL + " "
                label += str(value)

                if key is not rhs_last_key:
                    label += ", "

            label += ")"

        return label
