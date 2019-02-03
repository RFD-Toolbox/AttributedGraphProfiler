class RFD(dict):
    def __init__(self, lhs: dict = {}, rhs: dict = {}) -> None:
        super().__init__()
        self["LHS"]: dict[str, float] = lhs
        self["RHS"]: dict[str, float] = rhs

    def get_left_hand_side(self) -> dict:
        return self["LHS"]

    def get_right_hand_side(self) -> dict:
        return self["RHS"]

    def __getitem__(self, k: str) -> dict:
        return super().__getitem__(k)

    def __str__(self) -> str:
        return str(self["LHS"]) + " ==> " + str(self["RHS"])


if __name__ == '__main__':
    lhs = {"name": 1, "age": 3}
    rhs = {"city": 0, "height": 5, "surname": 0}

    rfd = RFD(lhs, rhs)

    print(rfd)
