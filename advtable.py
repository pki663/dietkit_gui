from PyQt5.QtWidgets import QItemDelegate, QComboBox

class ComboDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(ComboDelegate, self).__init__(parent)
    def setItems(self, items):
        self.items = items
    def createEditor(self, widget, option, index):
        editor = QComboBox(widget)
        editor.addItems(self.items)
        editor.setEditable(True)
        return editor