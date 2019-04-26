from numpy import NaN


class RFD(dict):
    def __init__(self, lhs: dict = {}, rhs: dict = {}) -> None:
        super().__init__()
        self["LHS"]: dict[str, float | NaN] = lhs
        self["RHS"]: dict[str, float | NaN] = rhs

    def get_left_hand_side(self) -> dict:
        return self["LHS"]

    def get_right_hand_side(self) -> dict:
        return self["RHS"]

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
        return str(self["LHS"]) + " → " + str(self["RHS"])


if __name__ == '__main__':
    lhs = {"name": 1, "age": 3}
    rhs = {"city": 0, "height": 5, "surname": 0}

    rfd = RFD(lhs, rhs)

    print(rfd)
