from PyQt5.QtCore import QRegExp


class RegularExpression:
    ANYTHING = QRegExp(".*")
    ANYTHING_LIST = QRegExp("^\\[(.*,?)+\\]$")
    INTEGER = QRegExp("^0$|^(-)?[1-9]+[0-9]*$")
    INTEGER_LIST = QRegExp("^\\[(-?\\d+,?)+\\]$")
    DECIMAL = QRegExp("^(0|[1-9]+[0-9]*)(\\.\\d+)?$")
    DECIMAL_LIST = QRegExp("^\\[(((0|([1-9]+[0-9]*))(\\.\\d+)?),?)+\\]$")
    STRING = QRegExp("^[\\w-\\s\\.\\(\\)]*$")
    STRING_LIST = QRegExp("^\\[((\\w|\\s|-|\\(|\\)),*)+\\]$")
