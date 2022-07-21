from PyQt5.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QHBoxLayout, QCheckBox, QDialogButtonBox, QScrollArea, QFrame
from PyQt5 import QtCore
from math import sqrt, ceil
import json

class AllergyWindow(QDialog):
    checklist = []
    def __init__(self, header, allow_preset = False):
        super().__init__()
        with open('./data/settings.json', 'r') as f:
            self.setting_data = json.load(f)
        self.initUI(header, allow_preset)

    def initUI(self, header, allow_preset):
        self.setWindowTitle('알러지 검사')
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        col_count = ceil(sqrt(len(header)))
        row_count = ceil(len(header) / col_count)
        
        vbox = QVBoxLayout()
        grid = QGridLayout()
        
        self.cboxs = {}
        temp_idx = 0
        for label in header:
            self.cboxs[label] = QCheckBox(label)
            grid.addWidget(self.cboxs[label], divmod(temp_idx, col_count)[0], temp_idx % col_count)
            temp_idx += 1
        
        for prev_checked in self.setting_data['prev_allergy']:
            try:
                self.cboxs[prev_checked].toggle()
            except ValueError:
                continue
        
        if allow_preset and self.setting_data["allergy_preset"]:
            preset_grid = QGridLayout()
            self.preset_cboxs = {}
            temp_idx = 0
            for preset in self.setting_data["allergy_preset"].keys():
                self.preset_cboxs[preset] = QCheckBox(preset)
                preset_grid.addWidget(self.preset_cboxs[preset], divmod(temp_idx, col_count)[0], temp_idx % col_count)
                self.preset_cboxs[preset].toggled.connect(lambda: self.preset_checked(preset))
                temp_idx += 1
            vbox.addLayout(preset_grid)
            hline = QFrame()
            hline.setFrameShape(QFrame.HLine)
            hline.setFrameShadow(QFrame.Sunken)
            vbox.addWidget(hline)

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

    def preset_checked(self, preset):
        if self.preset_cboxs[preset].isChecked():
            for allergen in self.setting_data["allergy_preset"][preset]:
                self.cboxs[allergen].setCheckState(2)
                self.cboxs[allergen].setEnabled(False)
        else:
            for allergen in self.setting_data["allergy_preset"][preset]:
                self.cboxs[allergen].setCheckState(0)
                self.cboxs[allergen].setEnabled(True)
    
    def getChecklist(self):
        checked = []
        self.setting_data['prev_allergy'] = []
        for checkbox in self.cboxs.values():
            if checkbox.isChecked():
                checked.append(checkbox.text())
                self.setting_data['prev_allergy'].append(checkbox.text())
        with open('./data/settings.json', 'w') as f:
            json.dump(self.setting_data, f, indent = 2)
        self.checklist = checked
        self.close()