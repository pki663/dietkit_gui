import sys
import pandas as pd
import os
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMainWindow, QAction, QTableWidget, QTableWidgetItem, QScrollArea, QGridLayout, QInputDialog, QMessageBox, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QDialogButtonBox, QPushButton
from PyQt5.QtWidgets import qApp
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtGui

class MyApp(QMainWindow):
    df = pd.DataFrame()
    allergy_df = pd.DataFrame()
    allergy_checked = False
    nutrition_checked = False

    def __init__(self):
        super().__init__()
        self.initdata()
        self.initUI()

    def initUI(self):
        screen = QDesktopWidget().availableGeometry()
        self.resize(int(screen.width()/2), int(screen.height()/2))

        widget = QWidget()
        layout = QGridLayout(widget)

        self.table = QTableWidget()
        #self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        scroll = QScrollArea()
        scroll.setWidget(self.table)
        self.table.cellDoubleClicked.connect(self.modifyTable)
        self.table.cellClicked.connect(self.cellinfo)
        self.table.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        nutritionContextAction = QAction('영양량 보기', self.table)
        ingredientContextAction = QAction('식재료 보기', self.table)
        nutritionContextAction.triggered.connect(self.cellnutrition)
        ingredientContextAction.triggered.connect(self.cellingredient)     
        self.table.addAction(nutritionContextAction)        
        self.table.addAction(ingredientContextAction)           

        layout.addWidget(self.table, 0, 0)

        exitAction = QAction('종료', self)
        exitAction.setStatusTip('프로그램을 종료합니다.')
        exitAction.triggered.connect(qApp.quit)
        newAction = QAction('새로 만들기', self)
        newAction.setStatusTip('새로운 빈 식단표를 만듭니다.')
        newAction.triggered.connect(self.initTable)
        saveAction = QAction('저장하기', self)
        saveAction.setStatusTip('현재 식단표를 저장합니다.')
        saveAction.triggered.connect(self.saveTable)
        loadAction = QAction('불러오기', self)
        loadAction.setStatusTip('저장된 식단표를 불러옵니다.')
        loadAction.triggered.connect(self.loadTable)
        allergyAction = QAction('알레르기 검사', self)
        allergyAction.setStatusTip('식단이 특정 알레르겐을 포함하는지 검사합니다.')
        allergyAction.triggered.connect(self.checkallergy)
        nutritionAction = QAction('영양량 분석', self)
        nutritionAction.setStatusTip('식단의 영양량을 계산합니다.')
        nutritionAction.triggered.connect(self.checknutrition)
        ingredientAction = QAction('식재료 분석', self)
        ingredientAction.setStatusTip('각 식단에 포함된 식재료들을 출력합니다.')
        ingredientAction.triggered.connect(self.checkingredient)
        ingredienteditAction = QAction('식재료 DB', self)
        ingredienteditAction.setStatusTip('식재료 DB를 편집합니다.')
        ingredienteditAction.triggered.connect(self.dummyfunc)
        menueditAction = QAction('메뉴 DB', self)
        menueditAction.setStatusTip('메뉴 DB를 편집합니다.')
        menueditAction.triggered.connect(self.dummyfunc)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        mainmenu = menubar.addMenu('메인')
        filemenu = menubar.addMenu('식단')
        checkmenu = menubar.addMenu('검사')
        datamenu = menubar.addMenu('데이터')

        mainmenu.addAction(exitAction)
        filemenu.addAction(newAction)
        filemenu.addAction(saveAction)
        filemenu.addAction(loadAction)
        checkmenu.addAction(allergyAction)
        checkmenu.addAction(nutritionAction)
        checkmenu.addAction(ingredientAction)
        datamenu.addAction(ingredienteditAction)                        
        datamenu.addAction(menueditAction)                

        self.setWindowTitle('Dietkit')
        self.setWindowIcon(QIcon('icon.png'))

        self.setCentralWidget(widget)
        self.statusBar().showMessage('식단 메뉴에서 새로 만들기 또는 불러오기를 통해 식단표 작성을 시작합니다.')
        self.show()

    def initdata(self):
        if os.path.exists('data/ingredients.csv'):
            self.ingredients = pd.read_csv('data/ingredients.csv', encoding = 'cp949', index_col = 0)
            #self.ing_dropdown = QComboBox(self)
            #self.ing_dropdown.addItems(self.ingredients.index.tolist())
            #self.ing_dropdown.setEditable(True)
        else:
            a = QMessageBox()
            a.setText('기본 식재료 DB를 불러오지 못했습니다.\n데이터 메뉴에서 수동으로 불러와주십시오.')
            a.setStandardButtons(QMessageBox.Ok)
            a.exec_()
        if os.path.exists('data/menus.csv'):
            temp = pd.read_csv('data/menus.csv', encoding = 'cp949', index_col = None)
            self.menus = pd.DataFrame(data = temp['weight'].values, index = pd.MultiIndex.from_frame(temp.fillna(method = 'ffill')[['name', 'ingredient']]), columns = ['weight'])
            del temp
            #self.menu_dropdown = QComboBox(self)
            #self.menu_dropdown.addItems(self.menus.index.get_level_values(0).drop_duplicates().tolist())
            #self.menu_dropdown.setEditable(True)
        else:
            a = QMessageBox()
            a.setText('기본 메뉴 DB를 불러오지 못했습니다.\n데이터 메뉴에서 수동으로 불러와주십시오.')
            a.setStandardButtons(QMessageBox.Ok)
            a.exec_()
        if os.path.exists('data/allergy.csv'):
            self.allergy = pd.read_csv('data/allergy.csv', encoding = 'cp949', index_col = 0).astype(bool)
            #self.allergy_dropdown = QComboBox(self)
            #self.allergy_dropdown.addItems(self.allergy.index.get_level_values(0).drop_duplicates().tolist())
            #self.allergy_dropdown.setEditable(True)
        else:
            a = QMessageBox()
            a.setText('기본 알러지 DB를 불러오지 못했습니다.\n데이터 메뉴에서 수동으로 불러와주십시오.')
            a.setStandardButtons(QMessageBox.Ok)
            a.exec_()
        if os.path.exists('data/ingredients.csv') and os.path.exists('data/menus.csv'):
            self.nutrition = pd.DataFrame(index = self.menus.index.get_level_values(0).drop_duplicates().tolist(), columns = self.ingredients.columns, data = 0)
            for menu in self.nutrition.index:
                for k, v in self.menus.xs(menu).iloc[:,0].to_dict().items():
                    self.nutrition.loc[menu] += self.ingredients.loc[k] * v / 100

    def setTable(self):
        for i in range(len(self.df.index)):
            for j in range(len(self.df.columns)):
                self.table.setItem(i,j,QTableWidgetItem(str(self.df.iloc[i, j])))
                self.table.item(i, j).setBackground(QtGui.QColor(255,255,255))
                #self.table.setCellWidget(i,j,self.menu_dropdown)

    def initTable(self):
        row, dummy = QInputDialog.getInt(self, '식단표 생성', '행의 갯수')
        col, dummy = QInputDialog.getInt(self, '식단표 생성', '열의 갯수')  
        self.table.setColumnCount(col)
        self.table.setRowCount(row)
        self.df = pd.DataFrame(index = range(row), columns = range(col), data = 'empty')
        self.allergy_df = pd.DataFrame(index = range(row), columns = range(col), data = [])
        self.setTable()
        self.statusBar().showMessage('식단표 생성이 완료되었습니다. 편집을 원하는 칸을 더블클릭하면 메뉴를 삽입할 수 있습니다.')

    def modifyTable(self, row, column):
        combo_items = sorted(self.menus.index.get_level_values(0).drop_duplicates().tolist())
        content, dummy = QInputDialog.getItem(self, "메뉴 선택", "선택한 칸에 들어갈 메뉴를 선택하세요.\n힌트: 메뉴명의 앞부분을 치고 →키를 누르면 일치하는 메뉴를 바로 찾을 수 있습니다.", combo_items, current = combo_items.index(self.df.iloc[row, column]), editable = True)
        self.df.iloc[row, column] = content
        self.allergy_df.iloc[row, column] = []
        self.table.setItem(row, column, QTableWidgetItem(content))
        self.table.item(row, column).setBackground(QtGui.QColor(255,255,255))

    def loadTable(self):
        fname = QFileDialog.getOpenFileName(self, '식단표 위치', './', filter = '*.csv')
        if fname[0] == '':
            return
        self.df = pd.read_csv(fname[0], index_col = 0, encoding = 'cp949')
        self.allergy_df = pd.DataFrame(index = range(self.df.shape[0]), columns = range(self.df.shape[1]), data = [])
        self.table.setColumnCount(self.df.shape[1])
        self.table.setRowCount(self.df.shape[0])
        self.setTable()
        self.statusBar().showMessage('식단표 불러오기가 완료되었습니다. 편집을 원하는 칸을 더블클릭하면 메뉴를 삽입할 수 있습니다.')

    def saveTable(self):
        fname = QFileDialog.getSaveFileName(self, '저장 위치', './', filter = '*.csv')
        if fname[0] != '':
            self.df.to_csv(fname[0], index = True, encoding = 'cp949')

    def cellinfo(self, row, column):
        message = ''
        if self.allergy_checked and len(self.allergy_df.iloc[row, column]) > 0:
            message += '알러지 문제가 발견됨: '
            message += str(self.allergy_df.iloc[row, column])
        self.statusBar().showMessage(message)

    def cellnutrition(self):
        menu_name = self.df.iloc[self.table.selectedIndexes()[0].row(), self.table.selectedIndexes()[0].column()]
        nutrition_info = self.nutrition.loc[menu_name]
        a = QDialog()
        a.resize(550, 800)
        a.setWindowTitle(menu_name + '의 영양량')
        vbox = QVBoxLayout()
        nutrition_table = QTableWidget()
        vbox.addWidget(nutrition_table)
        nutrition_table.setColumnCount(2)
        nutrition_table.setRowCount(len(self.nutrition.columns))
        nutrition_table.verticalHeader().hide()
        nutrition_table.setHorizontalHeaderLabels(['영양소', '함량'])
        count = 0
        for idx in nutrition_info.index:
            nutrition_table.setItem(count, 0, QTableWidgetItem(str(idx)))
            nutrition_table.setItem(count, 1, QTableWidgetItem(str(nutrition_info.loc[idx])))
            count += 1
        okbutton = QDialogButtonBox()
        okbutton.setOrientation(QtCore.Qt.Horizontal)
        okbutton.setStandardButtons(QDialogButtonBox.Ok)
        okbutton.accepted.connect(a.close)
        vbox.addWidget(okbutton, 0, QtCore.Qt.AlignHCenter)
        a.setLayout(vbox)
        a.show()
        a.exec_()

    def cellingredient(self):
        menu_name = self.df.iloc[self.table.selectedIndexes()[0].row(), self.table.selectedIndexes()[0].column()]
        ing_info = self.menus.xs(menu_name).iloc[:,0].to_dict().items()
        a = QDialog()
        a.resize(550, 800)
        a.setWindowTitle(menu_name + '의 성분표')
        vbox = QVBoxLayout()
        ingredient_table = QTableWidget()
        vbox.addWidget(ingredient_table)
        ingredient_table.setColumnCount(2)
        ingredient_table.setRowCount(len(ing_info))
        ingredient_table.verticalHeader().hide()
        ingredient_table.setHorizontalHeaderLabels(['식재료', '함량'])
        count = 0
        for k, v in ing_info:
            ingredient_table.setItem(count, 0, QTableWidgetItem(str(k)))
            ingredient_table.setItem(count, 1, QTableWidgetItem(str(v)))
            count += 1
        okbutton = QDialogButtonBox()
        okbutton.setOrientation(QtCore.Qt.Horizontal)
        okbutton.setStandardButtons(QDialogButtonBox.Ok)
        okbutton.accepted.connect(a.close)
        vbox.addWidget(okbutton, 0, QtCore.Qt.AlignHCenter)
        a.setLayout(vbox)
        a.show()
        a.exec_()
        
    def checkallergy(self):
        win = AllergyWindow()
        checklist = win.checklist
        if len(checklist) == 0:
            return
        self.allergy_df = pd.DataFrame(index = self.df.index, columns = self.df.columns, data = '')
        for row in range(self.df.shape[0]):
            for col in range(self.df.shape[1]):
                ings = self.menus.xs(self.df.iloc[row, col]).index.tolist()
                violations = self.allergy.loc[ings, checklist].sum(axis = 0).astype(bool)
                self.allergy_df.iloc[row, col] = violations.loc[violations].index.tolist()
                if len(self.allergy_df.iloc[row, col]) > 0:
                    self.table.item(row, col).setBackground(QtGui.QColor(255,169,140))
        self.allergy_checked = True

    def checknutrition(self):
        menu_nutrition = pd.DataFrame(index = self.df.index, columns = self.ingredients.columns, data = 0.0)
        for row in self.df.index:
            for col in self.df.columns:
                menu_nutrition.loc[row] += self.nutrition.loc[self.df.loc[row, col]]
        fname = QFileDialog.getSaveFileName(self, '영양량 리스트의 저장 위치', './', filter = '*.csv')
        if fname[0] != '':
            menu_nutrition.to_csv(fname[0], index = True, encoding = 'cp949')

    def checkingredient(self):
        ingredient_df = pd.DataFrame(columns=['식단번호', '메뉴일련번호', '메뉴', '식재료', '함량(g)'])
        ingredient_df = ingredient_df.set_index(['식단번호', '메뉴일련번호', '메뉴', '식재료'])
        for row in range(self.df.shape[0]):
            for col in range(self.df.shape[1]):
                for k, v in self.menus.xs(self.df.iloc[row, col]).iloc[:,0].to_dict().items():
                    ingredient_df.loc[(row, col, self.df.iloc[row, col], k)] = v
        fname = QFileDialog.getSaveFileName(self, '식재료 리스트의 저장 위치', './', filter = '*.csv')
        if fname[0] != '':
            ingredient_df.to_csv(fname[0], index = True, encoding = 'cp949')

    def dummyfunc(self):
        a = QMessageBox()
        a.setText('미구현')
        a.setStandardButtons(QMessageBox.Ok)
        a.exec_()

class AllergyWindow(QDialog):
    checklist = []
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('알러지 검사')
        vbox = QVBoxLayout()
        hbox_1 = QHBoxLayout()
        self.cbox_1 = QCheckBox('난류')
        hbox_1.addWidget(self.cbox_1)
        self.cbox_2 = QCheckBox('우유')
        hbox_1.addWidget(self.cbox_2)
        self.cbox_3 = QCheckBox('땅콩')
        hbox_1.addWidget(self.cbox_3)
        self.cbox_4 = QCheckBox('대두')
        hbox_1.addWidget(self.cbox_4)
        vbox.addLayout(hbox_1)
        hbox_2 = QHBoxLayout()
        self.cbox_5 = QCheckBox('밀')
        hbox_2.addWidget(self.cbox_5)
        self.cbox_6 = QCheckBox('메밀')
        hbox_2.addWidget(self.cbox_6)
        self.cbox_7 = QCheckBox('고등어')
        hbox_2.addWidget(self.cbox_7)
        self.cbox_8 = QCheckBox('게')
        hbox_2.addWidget(self.cbox_8)
        vbox.addLayout(hbox_2)
        hbox_3 = QHBoxLayout()
        self.cbox_9 = QCheckBox('새우')
        hbox_3.addWidget(self.cbox_9)
        self.cbox_10 = QCheckBox('돼지고기')
        hbox_3.addWidget(self.cbox_10)
        self.cbox_11 = QCheckBox('복숭아')
        hbox_3.addWidget(self.cbox_11)
        self.cbox_12 = QCheckBox('토마토')
        hbox_3.addWidget(self.cbox_12)
        vbox.addLayout(hbox_3)
        hbox_4 = QHBoxLayout()
        self.cbox_13 = QCheckBox('아황산류')
        hbox_4.addWidget(self.cbox_13)
        self.cbox_14 = QCheckBox('호두')
        hbox_4.addWidget(self.cbox_14)
        self.cbox_15 = QCheckBox('닭고기')
        hbox_4.addWidget(self.cbox_15)
        self.cbox_16 = QCheckBox('쇠고기')
        hbox_4.addWidget(self.cbox_16)
        vbox.addLayout(hbox_4)
        hbox_5 = QHBoxLayout()
        self.cbox_17 = QCheckBox('오징어')
        hbox_5.addWidget(self.cbox_17)
        self.cbox_18 = QCheckBox('조개류')
        hbox_5.addWidget(self.cbox_18)
        self.cbox_19 = QCheckBox('굴')
        hbox_5.addWidget(self.cbox_19)
        self.cbox_20 = QCheckBox('전복')
        hbox_5.addWidget(self.cbox_20)
        vbox.addLayout(hbox_5)
        hbox_6 = QHBoxLayout()
        self.cbox_21 = QCheckBox('홍합')
        hbox_6.addWidget(self.cbox_21)
        self.cbox_22 = QCheckBox('들깨')
        hbox_6.addWidget(self.cbox_22)
        self.cbox_23 = QCheckBox('잣')
        hbox_6.addWidget(self.cbox_23)
        self.cbox_24 = QCheckBox('아몬드')
        hbox_6.addWidget(self.cbox_24)
        vbox.addLayout(hbox_6)
        hbox_7 = QHBoxLayout()
        self.cbox_25 = QCheckBox('헤즐넛')
        hbox_7.addWidget(self.cbox_25)
        self.cbox_26 = QCheckBox('꼬막')
        hbox_7.addWidget(self.cbox_26)
        self.cbox_27 = QCheckBox('감자')
        hbox_7.addWidget(self.cbox_27)
        self.cbox_28 = QCheckBox('멸치')
        hbox_7.addWidget(self.cbox_28)
        vbox.addLayout(hbox_7)
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
        for checkbox in [self.cbox_1, self.cbox_2, self.cbox_3, self.cbox_4, self.cbox_5, self.cbox_6, self.cbox_7, self.cbox_8, self.cbox_9, self.cbox_10, self.cbox_11, self.cbox_12, self.cbox_13, self.cbox_14, self.cbox_15, self.cbox_16, self.cbox_17, self.cbox_18, self.cbox_19, self.cbox_20, self.cbox_21, self.cbox_22, self.cbox_23, self.cbox_24, self.cbox_25, self.cbox_26, self.cbox_27, self.cbox_28]:
            if checkbox.isChecked():
                checked.append(checkbox.text())
        self.checklist = checked
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())