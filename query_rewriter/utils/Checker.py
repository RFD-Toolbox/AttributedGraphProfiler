class Checker:
    @staticmethod
    def check_consecutive_integers(values: list) -> bool:
        return sorted(values) == list(range(min(values), max(values) + 1))

if __name__ == '__main__':
    print(Checker.check_consecutive_integers([2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007]))
    print(Checker.check_consecutive_integers([2000, 2001, 2002, 2003, 2004, 2005, 2010, 2007]))