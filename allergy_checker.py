from PyQt5.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QCheckBox, QDialogButtonBox
from PyQt5 import QtCore
from math import sqrt, ceil

class AllergyWindow(QDialog):
    checklist = []
    def __init__(self, header):
        super().__init__()
        self.initUI(header)

    def initUI(self, header):
        self.setWindowTitle('알러지 검사')
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        col_count = ceil(sqrt(len(header)))
        row_count = ceil(len(header) / col_count)

        self.cboxes = [QCheckBox(label) for label in header]
        
        vbox = QVBoxLayout()
        grid = QGridLayout()
        
        for row in range(row_count):
            for col in range(col_count):
                try:
                    grid.addWidget(self.cboxes[row * col_count + col], row, col)
                except IndexError:
                    break
        
        vbox.addLayout(grid)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        vbox.addWidget(self.buttonBox, 0, QtCore.Qt.AlignHCenter)
        self.buttonBox.accepted.connect(self.getChecklist)
        self.buttonBox.rejected.connect(self.close)
        self.setLayout(vbox)
        self.show()
        self.exec_()
    
    def getChecklist(self):
        checked = []
        for checkbox in self.cboxes:
            if checkbox.isChecked():
                checked.append(checkbox.text())
        self.checklist = checked
        self.close()