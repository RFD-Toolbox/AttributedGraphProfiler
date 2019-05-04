from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QStyledItemDelegate


class ItemDelegate(QStyledItemDelegate):
    def editorEvent(self, event, model, option, index):
        if event.type() in (
                QEvent.MouseButtonPress,
                QEvent.MouseButtonRelease,
                QEvent.MouseButtonDblClick,
                QEvent.MouseMove,
                QEvent.KeyPress
        ):
            return True
        else:
            res = super(ItemDelegate, self).editorEvent(event, model, option, index)
            return res
