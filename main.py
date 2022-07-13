import sys
import pandas as pd
import os
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMainWindow, QAction, QTableWidget, QTableWidgetItem, QScrollArea, QGridLayout, QInputDialog, QMessageBox, QFileDialog, QDialog, QVBoxLayout, QDialogButtonBox, QProgressBar, QAbstractItemView, QHeaderView, QPushButton, QComboBox, QVBoxLayout
from PyQt5.QtWidgets import qApp
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtGui, QtWebEngineWidgets
import plotly.express as px
import time
import json

from allergy_checker import *
from advtable import ComboDelegate
from settings import *

class MyApp(QMainWindow):
    df = pd.DataFrame()
    allergy_df = pd.DataFrame()
    allergy_checked = False
    nutrition_checked = False
    log_df = pd.DataFrame(columns = ['일시', 'Before', 'After'])
    def __init__(self):
        super().__init__()
        with open('./data/settings.json', 'r') as f:
            self.setting_data = json.load(f)
        self.initdata()
        self.initUI()

    def initUI(self):
        screen = QDesktopWidget().availableGeometry()
        self.resize(int(screen.width()/2), int(screen.height()/2))

        widget = QWidget()
        layout = QGridLayout(widget)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        #scroll = QScrollArea()
        #scroll.setWidget(self.table)
        self.table.cellClicked.connect(self.cellinfo)
        self.table.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        nutritionContextAction = QAction('영양량 보기', self.table)
        ingredientContextAction = QAction('식재료 보기', self.table)
        nutritionContextAction.triggered.connect(self.cellnutrition)
        ingredientContextAction.triggered.connect(self.cellingredient)     
        self.table.addAction(nutritionContextAction)    
        self.table.addAction(ingredientContextAction)
        self.delegater = ComboDelegate()
        self.delegater.setItems(self.menu_items)
        self.delegater.closeEditor.connect(self.updateTable)
        self.table.setItemDelegate(self.delegater)     

        layout.addWidget(self.table, 0, 0)
        self.nuttable = QTableWidget()
        self.nuttable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #scroll = QScrollArea()
        #scroll.setWidget(self.nuttable)

        layout.addWidget(self.nuttable, 1, 0)
        
        graphbox = QVBoxLayout()
        self.nutcombo = QComboBox()
        self.nutcombo.currentTextChanged.connect(self.drawGraph)
        self.nutcombo.addItems(self.nutrition.columns.tolist())
        graphbox.addWidget(self.nutcombo)

        self.graphwindow = QtWebEngineWidgets.QWebEngineView(self)
        graphbox.addWidget(self.graphwindow)

        layout.addLayout(graphbox, 0, 1, 2, 1)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(0,2)
        layout.setRowStretch(1,1)

        settingsAction = QAction('설정', self)
        settingsAction.setStatusTip('프로그램 설정을 변경합니다.')
        settingsAction.triggered.connect(self.settings)
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

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        mainmenu = menubar.addMenu('메인')
        filemenu = menubar.addMenu('식단')
        checkmenu = menubar.addMenu('검사')

        mainmenu.addAction(settingsAction)
        mainmenu.addAction(exitAction)
        filemenu.addAction(newAction)
        filemenu.addAction(saveAction)
        filemenu.addAction(loadAction)
        checkmenu.addAction(allergyAction)
        checkmenu.addAction(nutritionAction)
        checkmenu.addAction(ingredientAction)           

        self.setWindowTitle('Dietkit')
        self.setWindowIcon(QIcon('icon.ico'))

        self.setCentralWidget(widget)
        self.statusBar().showMessage('식단 메뉴에서 새로 만들기 또는 불러오기를 통해 식단표 작성을 시작합니다.')
        self.show()

    def initdata(self):
        loading_screen = QDialog()
        loading_screen.resize(550, 75)
        loading_screen.setWindowTitle('데이터 불러오는중')
        vbox = QVBoxLayout()
        loading_bar = QProgressBar(loading_screen)
        vbox.addWidget(loading_bar)
        loading_screen.setLayout(vbox)
        loading_screen.show()
        loading_bar.setValue(0)
        qApp.processEvents()
        if os.path.exists(self.setting_data['paths']['ingredients']):
            self.ingredients = pd.read_csv(self.setting_data['paths']['ingredients'], encoding = 'cp949', index_col = 0)
        else:
            self.message_popup('기본 식재료 DB를 불러오지 못했습니다.\n데이터 설정을 확인 후 재시작해주십시오.')
        if os.path.exists(self.setting_data['paths']['menus']):
            temp = pd.read_csv(self.setting_data['paths']['menus'], encoding = 'cp949', index_col = None)
            self.menus = pd.DataFrame(data = temp['weight'].values, index = pd.MultiIndex.from_frame(temp.fillna(method = 'ffill')[['name', 'ingredient']]), columns = ['weight'])
            self.menu_items = sorted(self.menus.index.get_level_values(0).drop_duplicates().tolist())
            del temp
        else:
            self.message_popup('기본 메뉴 DB를 불러오지 못했습니다.\n데이터 설정을 확인 후 재시작해주십시오.')
        if os.path.exists(self.setting_data['paths']['allergy']):
            self.allergy = pd.read_csv(self.setting_data['paths']['allergy'], encoding = 'cp949', index_col = 0).astype(bool)
        else:
            self.message_popup('기본 알러지 DB를 불러오지 못했습니다.\n데이터 설정을 확인 후 재시작해주십시오.')
        if self.setting_data['nutsave_enable'] and os.path.exists(self.setting_data['paths']['nutritions']):
            self.nutrition = pd.read_csv(self.setting_data['paths']['nutritions'], encoding = 'cp949', index_col = 0)
        elif os.path.exists(self.setting_data['paths']['ingredients']) and os.path.exists(self.setting_data['paths']['menus']):
            self.nutrition = pd.DataFrame(index = self.menus.index.get_level_values(0).drop_duplicates().tolist(), columns = self.ingredients.columns, data = 0)
            num_menu = len(self.nutrition.index)
            progressed = 0
            try:
                for menu in self.nutrition.index:
                    for k, v in self.menus.xs(menu).iloc[:,0].to_dict().items():
                        self.nutrition.loc[menu] += self.ingredients.loc[k] * v / 100
                    progressed += 1
                    loading_bar.setValue(int(progressed / num_menu * 99))
                    qApp.processEvents()
            except KeyError:
                self.message_popup('메뉴 DB의 영양량을 계산하던 중 오류가 발생했습니다.\n메뉴의 식재료 중 DB에 포함되지 않은 것이 있을 수 있습니다.')
            if self.setting_data['nutsave_enable']:
                self.nutrition.to_csv(self.setting_data['paths']['nutritions'], encoding = 'cp949')
        self.nutrition_df = pd.DataFrame(columns = self.nutrition.columns)
        loading_screen.close()

    def setTable(self):
        self.allergy_df = pd.DataFrame(index = range(self.df.shape[0]), columns = range(self.df.shape[1]), data = [])
        for j in range(len(self.df.columns)):
            for i in range(len(self.df.index)):
                self.table.setItem(i,j,QTableWidgetItem(str(self.df.iloc[i, j])))
                self.table.item(i, j).setBackground(QtGui.QColor(255,255,255))
                #self.table.setCellWidget(i,j,self.menu_dropdown)
            self.table.horizontalHeader().setSectionResizeMode(j, QHeaderView.ResizeToContents)
            #self.table.horizontalHeader().setMinimumSectionSize(300)
        for i in range(len(self.df.index)):
            self.table.verticalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.setnutTable()
        self.drawGraph()
        
    def setnutTable(self):
        self.nuttable.setColumnCount(self.df.shape[1])
        self.nuttable.setRowCount(len(self.nutrition.columns))
        self.nuttable.setHorizontalHeaderLabels([str(i+1) for i in range(self.df.shape[1])])
        self.nuttable.setVerticalHeaderLabels(self.nutrition.columns.tolist())
        nut_error = False
        for col in range(len(self.df.columns)):
            self.nuttable.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
            self.nuttable.horizontalHeader().setMinimumSectionSize(75)
            menu_list = self.df.iloc[:, col].tolist()
            try:
                nutrition_sum = self.nutrition.loc[menu_list].sum(axis = 0)
                self.nutrition_df.loc[col] = nutrition_sum
            except KeyError:
                nut_error = True
            
            for idx in nutrition_sum.index:
                self.nuttable.setItem(nutrition_sum.index.tolist().index(idx), col, QTableWidgetItem(str(nutrition_sum.loc[idx].round(3))))
                if self.setting_data['criteria'][idx][0]:
                    if nutrition_sum.loc[idx] < self.setting_data['criteria'][idx][0]:
                        self.nuttable.item(nutrition_sum.index.tolist().index(idx), col).setBackground(QtGui.QColor(139,182,250))
                if self.setting_data['criteria'][idx][1]:
                    if nutrition_sum.loc[idx] > self.setting_data['criteria'][idx][1]:
                        self.nuttable.item(nutrition_sum.index.tolist().index(idx), col).setBackground(QtGui.QColor(255,169,140))
        if nut_error:
            self.message_popup('일부 열에서 유효하지 않은 메뉴가 있어 영양량 합을 계산하지 못했습니다.')
        for idx in range(len(self.nutrition.columns)):
            self.nuttable.verticalHeader().setSectionResizeMode(idx, QHeaderView.ResizeToContents)

    def initTable(self):
        row, dummy = QInputDialog.getInt(self, '식단표 생성', '행의 갯수')
        col, dummy = QInputDialog.getInt(self, '식단표 생성', '열의 갯수')
        self.table.setColumnCount(col)
        self.table.setRowCount(row)
        self.df = pd.DataFrame(index = range(row), columns = range(col), data = 'empty')
        self.setTable()
        self.setnutTable()
        self.drawGraph()
        self.statusBar().showMessage('식단표 생성이 완료되었습니다. 편집을 원하는 칸을 더블클릭하면 메뉴를 삽입할 수 있습니다.')

    def loadTable(self):
        fname = QFileDialog.getOpenFileName(self, '식단표 위치', './', filter = '*.csv')
        if fname[0] == '':
            return
        self.df = pd.read_csv(fname[0], index_col = 0, encoding = 'cp949')
        self.df.index = range(len(self.df.index))
        self.df.dropna(axis = 'columns', how = 'all', inplace = True)
        self.df.dropna(axis = 'rows', how = 'all', inplace = True)
        self.table.setColumnCount(self.df.shape[1])
        self.table.setRowCount(self.df.shape[0])
        self.setTable()
        self.statusBar().showMessage('식단표 불러오기가 완료되었습니다. 편집을 원하는 칸을 더블클릭하면 메뉴를 삽입할 수 있습니다.')

    def saveTable(self):
        fname = QFileDialog.getSaveFileName(self, '저장 위치', './', filter = '*.csv')
        if fname[0] != '':
            self.df.to_csv(fname[0], index = True, encoding = 'cp949')

    def updateTable(self):
        before = self.df.iloc[self.table.selectedIndexes()[0].row(), self.table.selectedIndexes()[0].column()]
        after = self.table.item(self.table.selectedIndexes()[0].row(), self.table.selectedIndexes()[0].column()).text()
        if before == after:
            return
        if self.setting_data['log_enable']:
            self.log_df.loc[len(self.log_df)] = [time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())), before, after]
        self.df.iloc[self.table.selectedIndexes()[0].row(), self.table.selectedIndexes()[0].column()] = self.table.item(self.table.selectedIndexes()[0].row(), self.table.selectedIndexes()[0].column()).text()
        self.allergy_df.iloc[self.table.selectedIndexes()[0].row(), self.table.selectedIndexes()[0].column()] = []
        self.table.item(self.table.selectedIndexes()[0].row(), self.table.selectedIndexes()[0].column()).setBackground(QtGui.QColor(255,255,255))
        self.setnutTable()
        self.drawGraph()
    
    def drawGraph(self, nutrition = 'Undefined'):
        if self.df.shape[0] == 0:
            return
        if nutrition == 'Undefined':
            nutrition = self.nutcombo.currentText()
        fig = px.bar(y = [v+1 for v in range(self.df.shape[1])], x = self.nutrition_df[nutrition].tolist(), orientation = 'h')
        fig.update_yaxes(title = 'Diet No.', range = [self.df.shape[1] + 0.5, 0.5])
        fig.update_xaxes(title = nutrition)
        fig.update_layout(showlegend=False)
        fig.update_traces(marker_color = 'lightgreen')
        if self.setting_data['criteria'][nutrition][0]:
            fig.add_shape(type="line", line_color="blue", line_width=3, opacity=1, line_dash="dot", y0=-1, y1=self.df.shape[1] + 1, x0=self.setting_data['criteria'][nutrition][0], x1=self.setting_data['criteria'][nutrition][0])
        if self.setting_data['criteria'][nutrition][1]:
            fig.add_shape(type="line", line_color="red", line_width=3, opacity=1, line_dash="dot", y0=-1, y1=self.df.shape[1] + 1, x0=self.setting_data['criteria'][nutrition][1], x1=self.setting_data['criteria'][nutrition][1])
        self.graphwindow.setHtml(fig.to_html(include_plotlyjs = 'cdn'))
        
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
            self.message_popup('선택한 메뉴의 정보를 불러올 수 없습니다.\nDB 상에 존재하지 않는 메뉴일 수 있습니다.')
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
            self.message_popup('선택한 메뉴의 정보를 불러올 수 없습니다.\nDB 상에 존재하지 않는 메뉴일 수 있습니다.')
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

        
    def checkallergy(self):
        win = AllergyWindow(self.allergy.columns.tolist())
        checklist = win.checklist
        if len(checklist) == 0:
            return
        self.allergy_df = pd.DataFrame(index = self.df.index, columns = self.df.columns, data = '')
        self.setTable()
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
        nutrition_df = pd.DataFrame(index = range(self.df.shape[1]), columns = self.ingredients.columns, data = 0.0)
        error_cols = []
        for col in range(self.df.shape[1]):
            try:
                for row in range(self.df.shape[0]):
                    nutrition_df.iloc[col] += self.nutrition.loc[self.df.iloc[row, col]]
            except KeyError:
                self.table.item(row, col).setBackground(QtGui.QColor(252,250,104))
                error_cols.append(row)
                continue
        if error_cols:
            nutrition_df.drop(error_cols, axis = 'index', inplace = True)
            self.message_popup('일부 식단에서 영양량 계산에 실패했습니다.\n에러가 발생한 메뉴가 노랗게 채색되었습니다.')
        fname = QFileDialog.getSaveFileName(self, '영양량 리스트의 저장 위치', './', filter = '*.csv')
        if fname[0] != '':
            try:
                nutrition_df.to_csv(fname[0], index = True, encoding = 'cp949')
            except PermissionError:
                #alternative_name = time.strftime('%Y-%m-%d-%I-%M-%S', time.localtime(time())) + '.csv'
                #ingredient_df.to_csv(alternative_name, index = True, encoding = 'cp949')
                self.message_popup('주어진 이름으로 파일을 저장하는데 실패했습니다.\n해당 파일이 열려있을 수 있습니다.')

    def checkingredient(self):
        ingredient_df = pd.DataFrame(columns=['식단번호', '메뉴일련번호', '메뉴', '식재료', '함량(g)'])
        ingredient_df = ingredient_df.set_index(['식단번호', '메뉴일련번호', '메뉴', '식재료'])
        error_cols = []
        for col in range(self.df.shape[1]):
            for row in range(self.df.shape[0]):    
                try:
                    for k, v in self.menus.xs(self.df.iloc[row, col]).iloc[:,0].to_dict().items():
                        ingredient_df.loc[(col, row, self.df.iloc[row, col], k)] = v
                except KeyError:
                    self.table.item(row, col).setBackground(QtGui.QColor(252,250,104))
                    error_cols.append(col)
                    continue
        if error_cols:
            self.message_popup('일부 식단에서 식재료 계산에 실패했습니다.\n에러가 발생한 메뉴가 노랗게 채색되었습니다.')
        fname = QFileDialog.getSaveFileName(self, '식재료 리스트의 저장 위치', './', filter = '*.csv')
        if fname[0] != '':
            try:
                ingredient_df.to_csv(fname[0], index = True, encoding = 'cp949')
            except PermissionError:
                #alternative_name = time.strftime('%Y-%m-%d-%I-%M-%S', time.localtime(time())) + '.csv'
                #ingredient_df.to_csv(alternative_name, index = True, encoding = 'cp949')
                self.message_popup('주어진 이름으로 파일을 저장하는데 실패했습니다.\n해당 파일이 열려있을 수 있습니다.')

    def settings(self):
        setting = SettingWindow()
        with open('./data/settings.json', 'r') as f:
            new_setting = json.load(f)
        if new_setting['paths'] != self.setting_data['paths']:
            self.message_popup('데이터 설정이 변경되었습니다.\n적용을 위해서 데이터를 다시 로드합니다.')
            self.initdata()
            self.delegater.setItems(self.menu_items)
            self.setTable()
        self.setting_data = new_setting

    def message_popup(self, message = '미구현'):
        a = QMessageBox()
        a.setText(message)
        a.setStandardButtons(QMessageBox.Ok)
        a.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    app.exec_()
    if ex.setting_data['log_enable']:
        ex.log_df.to_csv(ex.setting_data['paths']['log'] + '/' + 'log_' + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) + '.csv', index = False, encoding = 'cp949')
    sys.exit()