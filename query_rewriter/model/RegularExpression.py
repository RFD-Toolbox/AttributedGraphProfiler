from PyQt5.QtCore import QRegExp


class RegularExpression:
    ANYTHING = QRegExp(".*")
    INTEGERS = QRegExp("^0$|^(-)?[1-9]+[0-9]*$")
    DECIMALS = QRegExp("^(0|[1-9]+[0-9]*)(\\.\\d+)?$")
    STRINGS = QRegExp("^[\\w-\\s\\.\\(\\)]*$")
