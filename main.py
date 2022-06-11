import sys
import pandas as pd
import os
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMainWindow, QAction, QTableWidget, QTableWidgetItem, QScrollArea, QGridLayout, QInputDialog, QMessageBox, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QDialogButtonBox, QPushButton, QProgressBar
from PyQt5.QtWidgets import qApp
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtGui
import time

from allergy_checker import *

class MyApp(QMainWindow):
    df = pd.DataFrame()
    allergy_df = pd.DataFrame()
    allergy_checked = False
    nutrition_checked = False

    def __init__(self):
        super().__init__()
        self.initUI()
        self.initdata()

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
        ingredientloadAction = QAction('식재료 DB 불러오기', self)
        ingredientloadAction.setStatusTip('식재료 DB를 불러옵니다.')
        ingredientloadAction.triggered.connect(self.loadingredient)
        menuloadAction = QAction('메뉴 DB 불러오기', self)
        menuloadAction.setStatusTip('메뉴 DB를 불러옵니다.')
        menuloadAction.triggered.connect(self.loadmenu)
        menunutritionAction = QAction('메뉴 DB 영양량 계산')
        menunutritionAction.setStatusTip('메뉴 DB의 영양량을 계산합니다.')
        menunutritionAction.triggered.connect(self.dummyfunc)

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
        datamenu.addAction(ingredientloadAction)                        
        datamenu.addAction(menuloadAction)                

        self.setWindowTitle('Dietkit')
        self.setWindowIcon(QIcon('icon.ico'))

        self.setCentralWidget(widget)
        self.statusBar().showMessage('식단 메뉴에서 새로 만들기 또는 불러오기를 통해 식단표 작성을 시작합니다.')
        self.show()

    def initdata(self):
        loading_screen = QDialog()
        loading_screen.resize(550, 75)
        loading_screen.setWindowTitle('시작중')
        vbox = QVBoxLayout()
        loading_bar = QProgressBar(loading_screen)
        vbox.addWidget(loading_bar)
        loading_screen.setLayout(vbox)
        loading_screen.show()
        loading_bar.setValue(0)
        qApp.processEvents()
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
            num_menu = len(self.nutrition.index)
            progressed = 0
            for menu in self.nutrition.index:
                for k, v in self.menus.xs(menu).iloc[:,0].to_dict().items():
                    self.nutrition.loc[menu] += self.ingredients.loc[k] * v / 100
                progressed += 1
                loading_bar.setValue(int(progressed / num_menu * 99))
                qApp.processEvents()
        loading_screen.close()

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
        self.df.index = range(len(self.df.index))
        self.df.dropna(axis = 'columns', how = 'all', inplace = True)
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
        try:
            menu_name = self.df.iloc[self.table.selectedIndexes()[0].row(), self.table.selectedIndexes()[0].column()]
            nutrition_info = self.nutrition.loc[menu_name]
        except KeyError:
            a = QMessageBox()
            a.resize(500,200)
            a.setText('선택한 메뉴의 정보를 불러올 수 없습니다.\nDB 상에 존재하지 않는 메뉴일 수 있습니다.')
            a.setStandardButtons(QMessageBox.Ok)
            a.exec_()
            return
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
        try:
            menu_name = self.df.iloc[self.table.selectedIndexes()[0].row(), self.table.selectedIndexes()[0].column()]
            ing_info = self.menus.xs(menu_name).iloc[:,0].to_dict().items()
        except KeyError:
            a = QMessageBox()
            a.resize(500,200)
            a.setText('선택한 메뉴의 정보를 불러올 수 없습니다.\nDB 상에 존재하지 않는 메뉴일 수 있습니다.')
            a.setStandardButtons(QMessageBox.Ok)
            a.exec_()
            return
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

    def loadingredient(self):
        fname = QFileDialog.getOpenFileName(self, '식재료 DB 위치', './', filter = '*.csv')
        if fname[0] == '':
            return
        self.ingredients = pd.read_csv(fname[0], encoding = 'cp949', index_col = 0)
        self.statusBar().showMessage('식재료 DB 불러오기가 완료되었습니다.')

    def loadmenu(self):
        fname = QFileDialog.getOpenFileName(self, '식재료 DB 위치', './', filter = '*.csv')
        if fname[0] == '':
            return
        temp = pd.read_csv(fname[0], encoding = 'cp949', index_col = None)
        self.menus = pd.DataFrame(data = temp['weight'].values, index = pd.MultiIndex.from_frame(temp.fillna(method = 'ffill')[['name', 'ingredient']]), columns = ['weight'])
        del temp
        self.statusBar().showMessage('메뉴 DB 불러오기가 완료되었습니다.')
        
    def checkallergy(self):
        win = AllergyWindow()
        checklist = win.checklist
        if len(checklist) == 0:
            return
        self.allergy_df = pd.DataFrame(index = self.df.index, columns = self.df.columns, data = '')
        for row in range(self.df.shape[0]):
            for col in range(self.df.shape[1]):
                try:
                    ings = self.menus.xs(self.df.iloc[row, col]).index.tolist()
                except KeyError:
                    self.table.item(row, col).setBackground(QtGui.QColor(252,250,104))
                    self.allergy_df.iloc[row, col] = 'DB 상에 존재하지 않는 메뉴'
                    continue
                violations = self.allergy.loc[ings, checklist].sum(axis = 0).astype(bool)
                self.allergy_df.iloc[row, col] = violations.loc[violations].index.tolist()
                if len(self.allergy_df.iloc[row, col]) > 0:
                    self.table.item(row, col).setBackground(QtGui.QColor(255,169,140))
        self.allergy_checked = True

    def checknutrition(self):
        nutrition_df = pd.DataFrame(index = range(self.df.shape[0]), columns = self.ingredients.columns, data = 0.0)
        error_rows = []
        for row in range(self.df.shape[0]):
            try:
                for col in range(self.df.shape[1]):
                    nutrition_df.iloc[row] += self.nutrition.loc[self.df.iloc[row, col]]
            except KeyError:
                self.table.item(row, col).setBackground(QtGui.QColor(252,250,104))
                error_rows.append(row)
                continue
        if error_rows:
            nutrition_df.drop(error_rows, axis = 'index', inplace = True)
            a = QMessageBox()
            a.setText('일부 식단에서 영양량 계산에 실패했습니다.\n에러가 발생한 메뉴가 노랗게 채색되었습니다.')
            a.setStandardButtons(QMessageBox.Ok)
            a.exec_()
        fname = QFileDialog.getSaveFileName(self, '영양량 리스트의 저장 위치', './', filter = '*.csv')
        if fname[0] != '':
            try:
                nutrition_df.to_csv(fname[0], index = True, encoding = 'cp949')
            except PermissionError:
                #alternative_name = time.strftime('%Y-%m-%d-%I-%M-%S', time.localtime(time())) + '.csv'
                #ingredient_df.to_csv(alternative_name, index = True, encoding = 'cp949')
                a = QMessageBox()
                a.setText('주어진 이름으로 파일을 저장하는데 실패했습니다.\n해당 파일이 열려있을 수 있습니다.')
                a.setStandardButtons(QMessageBox.Ok)
                a.exec_()

    def checkingredient(self):
        ingredient_df = pd.DataFrame(columns=['식단번호', '메뉴일련번호', '메뉴', '식재료', '함량(g)'])
        ingredient_df = ingredient_df.set_index(['식단번호', '메뉴일련번호', '메뉴', '식재료'])
        error_rows = []
        for row in range(self.df.shape[0]):
            for col in range(self.df.shape[1]):
                try:
                    for k, v in self.menus.xs(self.df.iloc[row, col]).iloc[:,0].to_dict().items():
                        ingredient_df.loc[(row, col, self.df.iloc[row, col], k)] = v
                except KeyError:
                    self.table.item(row, col).setBackground(QtGui.QColor(252,250,104))
                    error_rows.append((row, col))
                    continue
        if error_rows:
            a = QMessageBox()
            a.setText('일부 식단에서 식재료 계산에 실패했습니다.\n에러가 발생한 메뉴가 노랗게 채색되었습니다.')
            a.setStandardButtons(QMessageBox.Ok)
            a.exec_()
        fname = QFileDialog.getSaveFileName(self, '식재료 리스트의 저장 위치', './', filter = '*.csv')
        if fname[0] != '':
            try:
                ingredient_df.to_csv(fname[0], index = True, encoding = 'cp949')
            except PermissionError:
                #alternative_name = time.strftime('%Y-%m-%d-%I-%M-%S', time.localtime(time())) + '.csv'
                #ingredient_df.to_csv(alternative_name, index = True, encoding = 'cp949')
                a = QMessageBox()
                a.setText('주어진 이름으로 파일을 저장하는데 실패했습니다.\n해당 파일이 열려있을 수 있습니다.')
                a.setStandardButtons(QMessageBox.Ok)
                a.exec_()

    def dummyfunc(self):
        a = QMessageBox()
        a.setText('미구현')
        a.setStandardButtons(QMessageBox.Ok)
        a.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())