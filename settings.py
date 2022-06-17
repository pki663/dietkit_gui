from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QDialogButtonBox, QLabel, QPushButton, QWidget, QTabWidget, QFileDialog, QTableWidget, QTableWidgetItem
from PyQt5 import QtCore
import json
import os
from advtable import NumericDelegate

class SettingWindow(QDialog):
    checklist = []
    def __init__(self):
        with open('./data/settings.json', 'r') as f:
            self.setting_data = json.load(f)
        super().__init__()
        self.initUI()

    def initUI(self):
        # 메인 레이아웃
        self.setWindowTitle('설정')
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        data_tab = QWidget()
        log_tab = QWidget()
        criteria_tab = QWidget()
        tabs = QTabWidget()
        tabs.addTab(log_tab, '로그')
        tabs.addTab(data_tab, '데이터')
        tabs.addTab(criteria_tab, '영양기준')
        main_vbox = QVBoxLayout()
        main_vbox.addWidget(tabs)     

        # 로그 탭 레이아웃
        log_vbox = QVBoxLayout()
        
        self.log_cbox = QCheckBox('로그 기록 활성화')
        if self.setting_data['log_enable']:
            self.log_cbox.toggle()
        log_vbox.addWidget(self.log_cbox)
        
        hbox_log_path = QHBoxLayout()
        log_path = QLabel(self.setting_data['paths']['log'])
        hbox_log_path.addWidget(log_path)
        log_change = QPushButton('로그 위치 변경', self)
        log_change.clicked.connect(lambda: self.changePath('log', log_path))
        hbox_log_path.addWidget(log_change)
        log_vbox.addLayout(hbox_log_path)

        log_tab.setLayout(log_vbox)

        # 데이터 탭 레이아웃
        data_vbox = QVBoxLayout()
        
        hbox_ing_path = QHBoxLayout()
        ing_path = QLabel(self.setting_data['paths']['ingredients'])
        hbox_ing_path.addWidget(ing_path)
        ing_change = QPushButton('식재료 DB 변경', self)
        ing_change.clicked.connect(lambda: self.changeFile('ingredients', ing_path))
        hbox_ing_path.addWidget(ing_change)
        data_vbox.addLayout(hbox_ing_path)

        hbox_menu_path = QHBoxLayout()
        menu_path = QLabel(self.setting_data['paths']['menus'])
        hbox_menu_path.addWidget(menu_path)
        menu_change = QPushButton('메뉴 DB 변경', self)
        menu_change.clicked.connect(lambda: self.changeFile('menus', menu_path))
        hbox_menu_path.addWidget(menu_change)
        data_vbox.addLayout(hbox_menu_path)

        hbox_allergy_path = QHBoxLayout()
        allergy_path = QLabel(self.setting_data['paths']['allergy'])
        hbox_allergy_path.addWidget(allergy_path)
        allergy_change = QPushButton('알러지 DB 변경', self)
        allergy_change.clicked.connect(lambda: self.changeFile('allergy', allergy_path))
        hbox_allergy_path.addWidget(allergy_change)
        data_vbox.addLayout(hbox_allergy_path)

        data_vbox.addWidget(QLabel('고급기능: 영양 데이터 저장하기\n영양 데이터를 따로 저장하여 시작시 로딩을 단축시키나, 오류가 발생할 수 있습니다.\n오류가 발생한다면 이 기능을 비활성화 하십시오.'))
        self.nut_cbox = QCheckBox('영양 데이터 저장 활성화')
        if self.setting_data['nutsave_enable']:
            self.nut_cbox.toggle()
        data_vbox.addWidget(self.nut_cbox)

        hbox_nutrition_path = QHBoxLayout()
        nutrition_path = QLabel(self.setting_data['paths']['nutritions'])
        hbox_nutrition_path.addWidget(nutrition_path)
        nutrition_change = QPushButton('영양 데이터 위치 변경', self)
        nutrition_change.clicked.connect(lambda: self.changeFileSave('nutritions', nutrition_path))
        hbox_nutrition_path.addWidget(nutrition_change)
        data_vbox.addLayout(hbox_nutrition_path)

        data_tab.setLayout(data_vbox)

        # 영양기준 탭 레이아웃
        criteria_vbox = QVBoxLayout()
        criteria_vbox.addWidget(QLabel('각 영양소의 하한과 상한을 입력하십시오. 빈칸으로 두면 기준을 적용하지 않습니다.\n예: 1500 이상을 원하는 경우 하한에 1500을 입력하고 상한은 빈칸 유지'))
        self.crit_df = self.genNutTable()
        criteria_vbox.addWidget(self.crit_df)
        criteria_tab.setLayout(criteria_vbox)

        # 메인 레이아웃 마무리
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        main_vbox.addWidget(self.buttonBox, 0, QtCore.Qt.AlignHCenter)
        self.buttonBox.accepted.connect(self.applySetting)
        self.buttonBox.rejected.connect(self.close)

        self.setLayout(main_vbox)
        self.show()
        self.exec_()
    
    def changePath(self, variable, label_obj):
        dirname = QFileDialog.getExistingDirectory(self, '경로 위치', './')
        if dirname:
            self.setting_data['paths'][variable] = os.path.relpath(dirname)
            label_obj.setText(os.path.relpath(dirname))

    def changeFile(self, variable, label_obj):
        fname = QFileDialog.getOpenFileName(self, '데이터 위치', './', filter = '*.csv')
        if fname[0]:
            self.setting_data['paths'][variable] = os.path.relpath(fname[0])
            label_obj.setText(os.path.relpath(fname[0]))
    
    def changeFileSave(self, variable, label_obj):
        fname = QFileDialog.getSaveFileName(self, '데이터 위치', './', filter = '*.csv')
        if fname[0]:
            self.setting_data['paths'][variable] = os.path.relpath(fname[0])
            label_obj.setText(os.path.relpath(fname[0]))

    def genNutTable(self):
        with open(self.setting_data['paths']['ingredients'], 'r', encoding = 'cp949') as f:
            line = f.readline()
        nut_header = line.replace('\n', '').split(',')[1:]
        criteria_table = QTableWidget()
        criteria_table.setColumnCount(2)
        criteria_table.setRowCount(len(nut_header))
        criteria_table.setVerticalHeaderLabels(nut_header)
        criteria_table.setHorizontalHeaderLabels(['하한', '상한'])
        criteria_table.setItemDelegate(NumericDelegate())
        if self.setting_data['criteria']:
            for k, v in self.setting_data['criteria'].items():
                if v[0]:
                    criteria_table.setItem(nut_header.index(k), 0, QTableWidgetItem(str(v[0])))
                if v[1]:
                    criteria_table.setItem(nut_header.index(k), 1, QTableWidgetItem(str(v[1])))
        return criteria_table

    def applySetting(self):
        self.setting_data['log_enable'] = True if self.log_cbox.isChecked() else False
        self.setting_data['nutsave_enable'] = True if self.nut_cbox.isChecked() else False
        for row in range(self.crit_df.rowCount()):
            self.setting_data['criteria'][self.crit_df.verticalHeaderItem(row).text()] = [float(self.crit_df.item(row, 0).text()) if self.crit_df.item(row, 0) else None, float(self.crit_df.item(row, 1).text()) if self.crit_df.item(row, 1) else None]
        with open('./data/settings.json', 'w') as f:
            json.dump(self.setting_data, f, indent = 2)
        self.close()