from PyQt5.QtWidgets import QItemDelegate, QComboBox, QCompleter, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

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

class NumericDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(NumericDelegate, self).__init__(parent)
    def createEditor(self, widget, option, index):
        editor = QLineEdit(widget)
        editor.setValidator(QDoubleValidator(bottom = 0.0))
        return editor