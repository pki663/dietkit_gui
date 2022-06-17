from PyQt5.QtWidgets import QItemDelegate, QComboBox, QCompleter
from PyQt5.QtCore import Qt

class ComboDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(ComboDelegate, self).__init__(parent)
    def setItems(self, items):
        self.items = items
    def createEditor(self, widget, option, index):
        editor = QComboBox(widget)
        editor.addItems(self.items)
        editor.setEditable(True)
        completer = QCompleter(self.items)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setFilterMode(Qt.MatchContains)
        editor.setCompleter(completer)
        return editor