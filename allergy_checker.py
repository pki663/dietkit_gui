from PyQt5.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QCheckBox, QDialogButtonBox
from PyQt5 import QtCore
from math import sqrt, ceil
import json

class AllergyWindow(QDialog):
    checklist = []
    def __init__(self, header):
        super().__init__()
        with open('./data/settings.json', 'r') as f:
            self.setting_data = json.load(f)
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
        
        for prev_checked in self.setting_data['prev_allergy']:
            try:
                self.cboxes[header.index(prev_checked)].toggle()
            except ValueError:
                continue

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
        self.setting_data['prev_allergy'] = []
        for checkbox in self.cboxes:
            if checkbox.isChecked():
                checked.append(checkbox.text())
                self.setting_data['prev_allergy'].append(checkbox.text())
        with open('./data/settings.json', 'w') as f:
            json.dump(self.setting_data, f, indent = 2)
        self.checklist = checked
        self.close()